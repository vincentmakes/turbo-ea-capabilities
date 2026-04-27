#!/usr/bin/env tsx
/**
 * Build the static JSON API artefacts from the YAML source. Outputs:
 *   dist/api/version.json
 *   dist/api/capabilities.json
 *   dist/api/tree.json
 *   dist/api/by-l1/<slug>.json
 *   dist/api/capability/<id>.json    (nested subtree rooted at <id>)
 *   dist/api/locales.json
 *   dist/api/i18n/<locale>.json
 */
import { execSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  REPO_ROOT,
  flatten,
  l1Slug,
  listLocales,
  listSidecarFiles,
  loadAllL1Files,
  loadSidecar,
  loadValueStreams,
  type FlatCapability,
  type LocalizedFields,
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

const subtreeById = new Map<string, NestedCapability>();
function indexSubtrees(node: NestedCapability) {
  subtreeById.set(node.id, node);
  for (const child of node.children) indexSubtrees(child);
}
for (const root of treeAll) indexSubtrees(root);

for (const node of flatSorted) {
  const subtree = subtreeById.get(node.id);
  if (!subtree) throw new Error(`Build invariant: missing subtree for ${node.id}`);
  writeJson(join(DIST_API, "capability", `${node.id}.json`), subtree);
}

// ---------------------------------------------------------------------------
// Translation sidecars: emit one merged flat map per locale plus a summary.
// English source data files are unchanged; translations are an additive
// overlay so older consumers keep working untouched.
// ---------------------------------------------------------------------------
const I18N_DIST = join(DIST_API, "i18n");
mkdir(I18N_DIST);

const localeSummaries: Array<{
  locale: string;
  total: number;
  translated: number;
  l1_files: number;
}> = [];
const totalNodes = flatSorted.length;

for (const locale of listLocales()) {
  const merged: Record<string, LocalizedFields> = {};
  let l1Count = 0;
  for (const file of listSidecarFiles(locale)) {
    const { data } = loadSidecar(locale, file);
    l1Count++;
    for (const [id, fields] of Object.entries(data.entries)) {
      // Schema validation in lint guarantees no cross-L1 collisions, but if a
      // user has bypassed lint, last-write-wins. Lint will catch it next run.
      merged[id] = fields;
    }
  }
  // Sort keys deterministically by capability id for stable diffs.
  const sortedIds = Object.keys(merged).sort(compareIds);
  const orderedMerged: Record<string, LocalizedFields> = {};
  for (const id of sortedIds) orderedMerged[id] = merged[id];
  writeJson(join(I18N_DIST, `${locale}.json`), orderedMerged);
  const translated = sortedIds.filter((id) => merged[id].name).length;
  localeSummaries.push({ locale, total: totalNodes, translated, l1_files: l1Count });
}

// English is implicit and always 100% — list it for client convenience.
const localesManifest = {
  default: "en",
  locales: ["en", ...localeSummaries.map((s) => s.locale)],
  coverage: {
    en: { total: totalNodes, translated: totalNodes, l1_files: files.length },
    ...Object.fromEntries(
      localeSummaries.map((s) => [
        s.locale,
        { total: s.total, translated: s.translated, l1_files: s.l1_files },
      ])
    ),
  },
};
writeJson(join(DIST_API, "locales.json"), localesManifest);

// pretty summary
console.log(
  `✔ build_api: ${flatSorted.length} node(s), ${files.length} L1 file(s) → dist/api/`
);
console.log(
  `  catalogue_version=${version.catalogue_version} schema_version=${version.schema_version}`
);
if (localeSummaries.length) {
  console.log(
    `  locales: ${localeSummaries
      .map((s) => `${s.locale} (${s.translated}/${s.total})`)
      .join(", ")}`
  );
}

// Re-export the version object so build_pkg.ts can pick it up without
// re-deriving it from git.
const VERSION_CACHE = join(REPO_ROOT, "dist", "api", "version.json");
readFileSync(VERSION_CACHE, "utf8"); // sanity check
