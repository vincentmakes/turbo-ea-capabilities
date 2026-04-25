#!/usr/bin/env tsx
/**
 * Build the static JSON API artefacts from the YAML source. Outputs:
 *   dist/api/version.json
 *   dist/api/capabilities.json
 *   dist/api/tree.json
 *   dist/api/by-l1/<slug>.json
 *   dist/api/capability/<id>.json
 */
import { execSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  REPO_ROOT,
  flatten,
  l1Slug,
  loadAllL1Files,
  loadValueStreams,
  type FlatCapability,
  type RawCapability,
} from "./lib/load.ts";

const DIST_API = join(REPO_ROOT, "dist", "api");

const SCHEMA_VERSION = 1;

function getCatalogueVersion(): string {
  // Prefer an exact tag at HEAD; otherwise calver YYYY.MM.DD from build time.
  try {
    const exact = execSync("git describe --tags --exact-match HEAD 2>/dev/null", {
      encoding: "utf8",
    }).trim();
    if (exact) return exact.replace(/^v/, "");
  } catch {
    /* no exact tag */
  }
  const d = new Date();
  const yyyy = d.getUTCFullYear();
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${yyyy}.${mm}.${dd}`;
}

function getCatalogueCommit(): string | undefined {
  try {
    const sha = execSync("git rev-parse --short HEAD 2>/dev/null", {
      encoding: "utf8",
    }).trim();
    return sha || undefined;
  } catch {
    return undefined;
  }
}

function deterministicSort<T extends { id: string }>(arr: T[]): T[] {
  return [...arr].sort((a, b) => compareIds(a.id, b.id));
}

function compareIds(a: string, b: string): number {
  const splitA = a.replace(/^BC-/, "").split(".").map(Number);
  const splitB = b.replace(/^BC-/, "").split(".").map(Number);
  const len = Math.max(splitA.length, splitB.length);
  for (let i = 0; i < len; i++) {
    const av = splitA[i] ?? -1;
    const bv = splitB[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}

function mkdir(path: string) {
  mkdirSync(path, { recursive: true });
}

function writeJson(path: string, data: unknown) {
  writeFileSync(path, JSON.stringify(data, null, 2) + "\n", "utf8");
}

interface NestedCapability extends Omit<FlatCapability, "children" | "parent_id"> {
  parent_id: string | null;
  children: NestedCapability[];
}

function nest(root: RawCapability, inheritedIndustry?: string): NestedCapability {
  const flat = flatten(root, inheritedIndustry);
  const byId = new Map<string, NestedCapability>();
  for (const f of flat) {
    const node: NestedCapability = { ...f, children: [] };
    byId.set(f.id, node);
  }
  for (const f of flat) {
    if (f.parent_id) {
      const parent = byId.get(f.parent_id);
      if (parent) parent.children.push(byId.get(f.id)!);
    }
  }
  for (const node of byId.values()) {
    node.children.sort((a, b) => compareIds(a.id, b.id));
  }
  return byId.get(root.id)!;
}

// ---------------------------------------------------------------------------
// Build
// ---------------------------------------------------------------------------
const files = loadAllL1Files();

// Flat
const flatAll: FlatCapability[] = [];
for (const { tree } of files) {
  for (const node of flatten(tree)) flatAll.push(node);
}
const flatSorted = deterministicSort(flatAll);

// Tree (array of L1s)
const treeAll: NestedCapability[] = files.map(({ tree }) => nest(tree));
treeAll.sort((a, b) => compareIds(a.id, b.id));

// Validate invariants
const ids = new Set<string>();
for (const f of flatSorted) {
  if (ids.has(f.id)) throw new Error(`Duplicate id during build: ${f.id}`);
  ids.add(f.id);
}
for (const f of flatSorted) {
  if (f.successor_id && !ids.has(f.successor_id)) {
    throw new Error(`Build invariant: successor_id ${f.successor_id} does not resolve`);
  }
  if (f.level !== 1 && f.parent_id === null) {
    throw new Error(`Build invariant: non-root ${f.id} has no parent_id`);
  }
}

// version.json
const commit = getCatalogueCommit();
const version = {
  catalogue_version: getCatalogueVersion(),
  schema_version: SCHEMA_VERSION,
  generated_at: new Date().toISOString(),
  node_count: flatSorted.length,
  ...(commit && { commit }),
};

mkdir(DIST_API);
mkdir(join(DIST_API, "by-l1"));
mkdir(join(DIST_API, "capability"));

writeJson(join(DIST_API, "version.json"), version);
writeJson(join(DIST_API, "capabilities.json"), flatSorted);
writeJson(join(DIST_API, "tree.json"), treeAll);

// Value streams: orthogonal artefact, NOT merged into capability records so
// the capabilities export stays clean. The site joins them client-side for
// the value-stream filter.
const valueStreams = loadValueStreams();
const knownIds = new Set(flatSorted.map((c) => c.id));
for (const stream of valueStreams) {
  for (const stage of stream.stages) {
    if (!knownIds.has(stage.capability_id)) {
      throw new Error(
        `Value stream '${stream.name}' references unknown capability ${stage.capability_id}`
      );
    }
  }
}
writeJson(join(DIST_API, "value-streams.json"), valueStreams);

for (const { tree } of files) {
  const slug = l1Slug(tree);
  writeJson(join(DIST_API, "by-l1", `${slug}.json`), nest(tree));
}

for (const node of flatSorted) {
  writeJson(join(DIST_API, "capability", `${node.id}.json`), node);
}

// pretty summary
console.log(
  `✔ build_api: ${flatSorted.length} node(s), ${files.length} L1 file(s) → dist/api/`
);
console.log(
  `  catalogue_version=${version.catalogue_version} schema_version=${version.schema_version}`
);

// Re-export the version object so build_pkg.ts can pick it up without
// re-deriving it from git.
const VERSION_CACHE = join(REPO_ROOT, "dist", "api", "version.json");
readFileSync(VERSION_CACHE, "utf8"); // sanity check
