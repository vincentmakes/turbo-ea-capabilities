#!/usr/bin/env tsx
/**
 * Build the static JSON API artefacts from the YAML source. Outputs:
 *   dist/api/version.json
 *   dist/api/capabilities.json
 *   dist/api/tree.json
 *   dist/api/by-l1/<slug>.json
 *   dist/api/capability/<id>.json    (nested subtree rooted at <id>)
 *   dist/api/value-streams.json
 *   dist/api/business-processes.json
 *   dist/api/bp-tree.json
 *   dist/api/by-bp1/<slug>.json
 *   dist/api/business-process/<id>.json
 *   dist/api/locales.json
 *   dist/api/i18n/<locale>.json
 */
import { execSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  REPO_ROOT,
  bp1Slug,
  flatten,
  flattenBP,
  l1Slug,
  listLocales,
  listSidecarFiles,
  loadAllBP1Files,
  loadAllL1Files,
  loadSidecar,
  loadValueStreams,
  type FlatBusinessProcess,
  type FlatCapability,
  type LocalizedFields,
  type RawBusinessProcess,
  type RawCapability,
} from "./lib/load.ts";

const DIST_API = join(REPO_ROOT, "dist", "api");

const SCHEMA_VERSION = 2;

function getCommitCount(): number | undefined {
  try {
    // Many CI / hosted-deploy environments (Cloudflare Pages, Vercel, …)
    // shallow-clone the repo, which makes `git rev-list --count HEAD` return
    // a tiny number and produces nonsense versions like `2026.5.9.1`. Try to
    // unshallow first; fall through quietly if there's no network or the
    // remote isn't reachable.
    const isShallow = execSync("git rev-parse --is-shallow-repository 2>/dev/null", {
      encoding: "utf8",
    }).trim() === "true";
    if (isShallow) {
      try {
        execSync("git fetch --unshallow --quiet 2>/dev/null", { stdio: "ignore" });
      } catch {
        /* no network or restricted; fall through with whatever count we have */
      }
    }
    const n = execSync("git rev-list --count HEAD 2>/dev/null", {
      encoding: "utf8",
    }).trim();
    const parsed = Number.parseInt(n, 10);
    return Number.isFinite(parsed) ? parsed : undefined;
  } catch {
    return undefined;
  }
}

function getCatalogueVersion(commitCount: number | undefined): string {
  // Prefer an exact tag at HEAD (clean release). Otherwise emit a PEP 440
  // 4-segment release `<YYYY>.<M>.<D>.<N>` where N is the total commit count
  // on this branch — strictly monotonic across rebuilds so PyPI never rejects
  // a duplicate. Leading zeros are intentionally omitted to match PEP 440
  // normalization (2026.04.30 → 2026.4.30).
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
  const m = d.getUTCMonth() + 1;
  const day = d.getUTCDate();
  const base = `${yyyy}.${m}.${day}`;
  return commitCount !== undefined ? `${base}.${commitCount}` : base;
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
  const splitA = a.replace(/^(BC|BP|VS)-/, "").split(".").map(Number);
  const splitB = b.replace(/^(BC|BP|VS)-/, "").split(".").map(Number);
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

interface NestedBusinessProcess
  extends Omit<FlatBusinessProcess, "children" | "parent_id"> {
  parent_id: string | null;
  children: NestedBusinessProcess[];
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

function nestBP(
  root: RawBusinessProcess,
  inheritedIndustry?: string
): NestedBusinessProcess {
  const flat = flattenBP(root, inheritedIndustry);
  const byId = new Map<string, NestedBusinessProcess>();
  for (const f of flat) {
    const node: NestedBusinessProcess = { ...f, children: [] };
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
const bpFiles = loadAllBP1Files();

// Flat (capabilities)
const flatAll: FlatCapability[] = [];
for (const { tree } of files) {
  for (const node of flatten(tree)) flatAll.push(node);
}
const flatSorted = deterministicSort(flatAll);

// Flat (business processes)
const bpFlatAll: FlatBusinessProcess[] = [];
for (const { tree } of bpFiles) {
  for (const node of flattenBP(tree)) bpFlatAll.push(node);
}
const bpFlatSorted = deterministicSort(bpFlatAll);

// Trees (array of L1s / BP1s)
const treeAll: NestedCapability[] = files.map(({ tree }) => nest(tree));
treeAll.sort((a, b) => compareIds(a.id, b.id));

const bpTreeAll: NestedBusinessProcess[] = bpFiles.map(({ tree }) => nestBP(tree));
bpTreeAll.sort((a, b) => compareIds(a.id, b.id));

// Validate invariants (capabilities)
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

// Validate invariants (business processes)
const bpIds = new Set<string>();
for (const f of bpFlatSorted) {
  if (bpIds.has(f.id)) throw new Error(`Duplicate BP id during build: ${f.id}`);
  bpIds.add(f.id);
}
for (const f of bpFlatSorted) {
  if (f.successor_id && !bpIds.has(f.successor_id)) {
    throw new Error(`Build invariant: BP successor_id ${f.successor_id} does not resolve`);
  }
  if (f.level !== 1 && f.parent_id === null) {
    throw new Error(`Build invariant: non-root BP ${f.id} has no parent_id`);
  }
}

// version.json
const commit = getCatalogueCommit();
const commitCount = getCommitCount();
const version = {
  catalogue_version: getCatalogueVersion(commitCount),
  schema_version: SCHEMA_VERSION,
  generated_at: new Date().toISOString(),
  node_count: flatSorted.length,
  process_count: bpFlatSorted.length,
  ...(commit && { commit }),
  ...(commitCount !== undefined && { commit_count: commitCount }),
};

mkdir(DIST_API);
mkdir(join(DIST_API, "by-l1"));
mkdir(join(DIST_API, "capability"));
mkdir(join(DIST_API, "by-bp1"));
mkdir(join(DIST_API, "business-process"));

writeJson(join(DIST_API, "version.json"), version);

// ---------------------------------------------------------------------------
// Value streams
// ---------------------------------------------------------------------------
const valueStreams = loadValueStreams();
const knownIds = new Set(flatSorted.map((c) => c.id));
for (const stream of valueStreams) {
  for (const stage of stream.stages) {
    for (const cid of stage.capability_ids ?? []) {
      if (!knownIds.has(cid)) {
        throw new Error(
          `Value stream '${stream.name}' (${stream.id}) stage ${stage.id} references unknown capability ${cid}`
        );
      }
    }
    for (const pid of stage.process_ids ?? []) {
      if (!bpIds.has(pid)) {
        throw new Error(
          `Value stream '${stream.name}' (${stream.id}) stage ${stage.id} references unknown business process ${pid}`
        );
      }
    }
  }
}
writeJson(join(DIST_API, "value-streams.json"), valueStreams);

// ---------------------------------------------------------------------------
// Reverse indices: which processes realize each capability, which value-stream
// stages mention each capability or process. Authoring stays single-source on
// the BP side (`realizes_capability_ids`) and on the VS side (stage ids); the
// reverse direction is computed here so the site/Python don't have to.
// ---------------------------------------------------------------------------
const capToProcesses = new Map<string, string[]>();
for (const bp of bpFlatSorted) {
  for (const bcId of bp.realizes_capability_ids ?? []) {
    if (!capToProcesses.has(bcId)) capToProcesses.set(bcId, []);
    capToProcesses.get(bcId)!.push(bp.id);
  }
}

const capToVsStages = new Map<string, string[]>();
const procToVsStages = new Map<string, string[]>();
for (const stream of valueStreams) {
  for (const stage of stream.stages ?? []) {
    for (const cid of stage.capability_ids ?? []) {
      if (!capToVsStages.has(cid)) capToVsStages.set(cid, []);
      capToVsStages.get(cid)!.push(stage.id);
    }
    for (const pid of stage.process_ids ?? []) {
      if (!procToVsStages.has(pid)) procToVsStages.set(pid, []);
      procToVsStages.get(pid)!.push(stage.id);
    }
  }
}

function attachCapReverseIndices(node: FlatCapability): FlatCapability {
  const realizes = capToProcesses.get(node.id);
  const vsStages = capToVsStages.get(node.id);
  return {
    ...node,
    ...(realizes && realizes.length > 0 && { realizes_processes: [...realizes].sort(compareIds) }),
    ...(vsStages && vsStages.length > 0 && { value_stream_stages: [...vsStages].sort(compareIds) }),
  };
}

function attachBpReverseIndices(node: FlatBusinessProcess): FlatBusinessProcess {
  const vsStages = procToVsStages.get(node.id);
  return {
    ...node,
    ...(vsStages && vsStages.length > 0 && {
      realized_in_value_streams: [...vsStages].sort(compareIds),
    }),
  };
}

const flatWithBacklinks = flatSorted.map(attachCapReverseIndices);
const bpFlatWithBacklinks = bpFlatSorted.map(attachBpReverseIndices);

writeJson(join(DIST_API, "capabilities.json"), flatWithBacklinks);
writeJson(join(DIST_API, "tree.json"), treeAll);

writeJson(join(DIST_API, "business-processes.json"), bpFlatWithBacklinks);
writeJson(join(DIST_API, "bp-tree.json"), bpTreeAll);

for (const { tree } of files) {
  const slug = l1Slug(tree);
  writeJson(join(DIST_API, "by-l1", `${slug}.json`), nest(tree));
}

for (const { tree } of bpFiles) {
  const slug = bp1Slug(tree);
  writeJson(join(DIST_API, "by-bp1", `${slug}.json`), nestBP(tree));
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

const bpSubtreeById = new Map<string, NestedBusinessProcess>();
function indexBpSubtrees(node: NestedBusinessProcess) {
  bpSubtreeById.set(node.id, node);
  for (const child of node.children) indexBpSubtrees(child);
}
for (const root of bpTreeAll) indexBpSubtrees(root);

for (const node of bpFlatSorted) {
  const subtree = bpSubtreeById.get(node.id);
  if (!subtree) throw new Error(`Build invariant: missing BP subtree for ${node.id}`);
  writeJson(join(DIST_API, "business-process", `${node.id}.json`), subtree);
}

// ---------------------------------------------------------------------------
// Translation sidecars: emit one merged flat map per locale plus a summary.
// English source data files are unchanged; translations are an additive
// overlay so older consumers keep working untouched. Capability, BP, and
// value-stream entries share a per-locale namespace — id prefixes (BC/BP/VS)
// keep them from colliding.
// ---------------------------------------------------------------------------
const I18N_DIST = join(DIST_API, "i18n");
mkdir(I18N_DIST);

interface LocaleSummary {
  locale: string;
  total: number;
  translated: number;
  l1_files: number;
  bp1_files: number;
  process_count: number;
  processes_translated: number;
  value_stream_count: number;
  value_streams_translated: number;
}

const localeSummaries: LocaleSummary[] = [];
const totalNodes = flatSorted.length;
const totalProcesses = bpFlatSorted.length;
const totalVsEntries =
  valueStreams.length +
  valueStreams.reduce((acc, s) => acc + (s.stages?.length ?? 0), 0);

for (const locale of listLocales()) {
  const merged: Record<string, LocalizedFields> = {};
  let l1Count = 0;
  let bp1Count = 0;
  let vsTouched = false;
  for (const file of listSidecarFiles(locale)) {
    const { data } = loadSidecar(locale, file);
    if (file.startsWith("processes/")) bp1Count++;
    else if (file === "_value-streams.yaml") vsTouched = true;
    else l1Count++;
    for (const [id, fields] of Object.entries(data.entries)) {
      // Schema validation in lint guarantees no cross-source collisions, but
      // last-write-wins if a user has bypassed lint. Lint will catch it next
      // run.
      merged[id] = fields;
    }
  }
  // Sort keys deterministically (BC- first, BP- second, VS- third).
  const sortedIds = Object.keys(merged).sort((a, b) => {
    const aPrefix = a.split("-")[0];
    const bPrefix = b.split("-")[0];
    if (aPrefix !== bPrefix) {
      const order = { BC: 0, BP: 1, VS: 2 } as Record<string, number>;
      return (order[aPrefix] ?? 9) - (order[bPrefix] ?? 9);
    }
    return compareIds(a, b);
  });
  const orderedMerged: Record<string, LocalizedFields> = {};
  for (const id of sortedIds) orderedMerged[id] = merged[id];
  writeJson(join(I18N_DIST, `${locale}.json`), orderedMerged);

  const translated = sortedIds.filter(
    (id) => id.startsWith("BC-") && (merged[id].name !== undefined)
  ).length;
  const processesTranslated = sortedIds.filter(
    (id) => id.startsWith("BP-") && (merged[id].name !== undefined)
  ).length;
  const vsTranslated = sortedIds.filter(
    (id) => id.startsWith("VS-") && (merged[id].name !== undefined || merged[id].stage_name !== undefined)
  ).length;
  void vsTouched;
  localeSummaries.push({
    locale,
    total: totalNodes,
    translated,
    l1_files: l1Count,
    bp1_files: bp1Count,
    process_count: totalProcesses,
    processes_translated: processesTranslated,
    value_stream_count: totalVsEntries,
    value_streams_translated: vsTranslated,
  });
}

// English is implicit and always 100% — list it for client convenience.
const localesManifest = {
  default: "en",
  locales: ["en", ...localeSummaries.map((s) => s.locale)],
  coverage: {
    en: {
      total: totalNodes,
      translated: totalNodes,
      l1_files: files.length,
      bp1_files: bpFiles.length,
      process_count: totalProcesses,
      processes_translated: totalProcesses,
      value_stream_count: totalVsEntries,
      value_streams_translated: totalVsEntries,
    },
    ...Object.fromEntries(
      localeSummaries.map((s) => [s.locale, s as Omit<LocaleSummary, "locale">])
    ),
  },
};
writeJson(join(DIST_API, "locales.json"), localesManifest);

// pretty summary
console.log(
  `✔ build_api: ${flatSorted.length} cap, ${bpFlatSorted.length} bp, ${valueStreams.length} vs → dist/api/`
);
console.log(
  `  catalogue_version=${version.catalogue_version} schema_version=${version.schema_version}`
);
if (localeSummaries.length) {
  console.log(
    `  locales: ${localeSummaries
      .map((s) => `${s.locale} (${s.translated}/${s.total} cap, ${s.processes_translated}/${s.process_count} bp)`)
      .join(", ")}`
  );
}

// Re-export the version object so build_pkg.ts can pick it up without
// re-deriving it from git.
const VERSION_CACHE = join(REPO_ROOT, "dist", "api", "version.json");
readFileSync(VERSION_CACHE, "utf8"); // sanity check
