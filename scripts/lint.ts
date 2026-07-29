#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * Lint the YAML catalogue. Validates capabilities (BC), value streams (VS),
 * business processes (BP), and translation sidecars against their JSON
 * schemas plus a layer of structural rules from
 * business-capability-governance-model.md.
 *
 * Exits non-zero on any failure.
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import YAML from "yaml";
import {
  BCP47_REGEX,
  BP_ID_REGEX,
  BUSINESS_PROCESS_SCHEMA_PATH,
  CATALOGUE_DIR,
  I18N_SCHEMA_PATH,
  ID_REGEX,
  MACRO_CAPABILITY_SCHEMA_PATH,
  MC_ID_REGEX,
  PROCESSES_DIR,
  SCHEMA_PATH,
  VALUE_STREAM_SCHEMA_PATH,
  VS_ID_REGEX,
  VS_STAGE_ID_REGEX,
  flatten,
  flattenBP,
  l1Slug,
  bp1Slug,
  listProcessFiles,
  listYamlFiles,
  loadAllSidecars,
  loadBP1File,
  loadL1File,
  loadMacroCapabilities,
  loadValueStreams,
  readIndex,
  readProcessesIndex,
  type FlatCapability,
  type FlatBusinessProcess,
  type MacroCapability,
  type RawCapability,
  type RawBusinessProcess,
  type SidecarKind,
} from "./lib/load.ts";
import {
  hashCapabilityLikeSource,
  hashMacroCapabilitySource,
  hashValueStreamSource,
  hashValueStreamStageSource,
} from "./lib/i18n_hash.ts";

const L1_ID_REGEX = /^BC-\d+$/;

interface LintError {
  file: string;
  message: string;
}

const errors: LintError[] = [];
const err = (file: string, message: string) => errors.push({ file, message });

// ---------------------------------------------------------------------------
// 1. Index integrity (every file registered, every entry resolves)
// ---------------------------------------------------------------------------
const index = readIndex();
const indexedSet = new Set(index.files);
const onDisk = listYamlFiles();
for (const f of onDisk) {
  if (!indexedSet.has(f)) {
    err("_index.yaml", `Found ${f} on disk but not registered in _index.yaml`);
  }
}
for (const f of index.files) {
  if (!existsSync(join(CATALOGUE_DIR, f))) {
    err("_index.yaml", `Registered file ${f} not found on disk`);
  }
}

// Process index parallels capability index. Empty by default until BP1 files land.
const processesIndex = readProcessesIndex();
const processesIndexedSet = new Set(processesIndex.files);
const processesOnDisk = listProcessFiles();
for (const f of processesOnDisk) {
  if (!processesIndexedSet.has(f)) {
    err(
      "processes/_index.yaml",
      `Found ${f} on disk but not registered in catalogue/processes/_index.yaml`
    );
  }
}
for (const f of processesIndex.files) {
  if (!existsSync(join(PROCESSES_DIR, f))) {
    err(
      "processes/_index.yaml",
      `Registered file ${f} not found on disk under catalogue/processes/`
    );
  }
}

// ---------------------------------------------------------------------------
// 2. JSON Schema validation (capabilities)
// ---------------------------------------------------------------------------
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);

const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf8"));
const validate = ajv.compile(schema);

const trees: { name: string; tree: RawCapability }[] = [];
for (const f of index.files) {
  if (!existsSync(join(CATALOGUE_DIR, f))) continue;
  let parsed: RawCapability | undefined;
  try {
    parsed = loadL1File(f).tree;
  } catch (e) {
    err(f, `YAML parse error: ${(e as Error).message}`);
    continue;
  }
  if (!parsed || typeof parsed !== "object") {
    err(f, "File did not parse to an object");
    continue;
  }
  if (!validate(parsed)) {
    for (const e of validate.errors ?? []) {
      err(f, `schema: ${e.instancePath || "/"} ${e.message}`);
    }
  }
  trees.push({ name: f, tree: parsed });
}

// JSON schema validation (business processes)
const bpSchema = JSON.parse(readFileSync(BUSINESS_PROCESS_SCHEMA_PATH, "utf8"));
const validateBP = ajv.compile(bpSchema);
const bpTrees: { name: string; tree: RawBusinessProcess }[] = [];
for (const f of processesIndex.files) {
  if (!existsSync(join(PROCESSES_DIR, f))) continue;
  let parsed: RawBusinessProcess | undefined;
  try {
    parsed = loadBP1File(f).tree;
  } catch (e) {
    err(`processes/${f}`, `YAML parse error: ${(e as Error).message}`);
    continue;
  }
  if (!parsed || typeof parsed !== "object") {
    err(`processes/${f}`, "File did not parse to an object");
    continue;
  }
  if (!validateBP(parsed)) {
    for (const e of validateBP.errors ?? []) {
      err(`processes/${f}`, `schema: ${e.instancePath || "/"} ${e.message}`);
    }
  }
  bpTrees.push({ name: f, tree: parsed });
}

// ---------------------------------------------------------------------------
// 3-9. Structural rules per capability file
// ---------------------------------------------------------------------------
function walkWithDepth(
  node: RawCapability,
  depth: number,
  file: string,
  parentId: string | null
) {
  if (!ID_REGEX.test(node.id)) {
    err(
      file,
      `id '${node.id}' does not match ${ID_REGEX} (BC-<L1>[.<L2>[.<L3>[.<L4>]]])`
    );
  }
  if (node.level !== depth) {
    err(
      file,
      `id ${node.id}: level=${node.level} but tree depth=${depth}; level must equal depth (root=1)`
    );
  }
  if (parentId !== null && !node.id.startsWith(parentId + ".")) {
    err(
      file,
      `id ${node.id}: must extend parent id ${parentId} (e.g., ${parentId}.N)`
    );
  }
  if (node.deprecated && !node.deprecation_reason) {
    err(file, `id ${node.id}: deprecated=true requires deprecation_reason`);
  }
  // Children sorted ascending by id
  const childIds = (node.children ?? []).map((c) => c.id);
  const sorted = [...childIds].sort((a, b) => compareDottedIds(a, b, "BC"));
  for (let i = 0; i < childIds.length; i++) {
    if (childIds[i] !== sorted[i]) {
      err(
        file,
        `Children of ${node.id} are not sorted by id ascending. Got [${childIds.join(", ")}], expected [${sorted.join(", ")}]`
      );
      break;
    }
  }
  for (const child of node.children ?? []) {
    walkWithDepth(child, depth + 1, file, node.id);
  }
}

/** Compare e.g. BC-2.10 vs BC-2.2 numerically across each dotted segment. */
function compareDottedIds(a: string, b: string, prefix: "BC" | "BP"): number {
  const splitA = a.replace(new RegExp(`^${prefix}-`), "").split(".").map(Number);
  const splitB = b.replace(new RegExp(`^${prefix}-`), "").split(".").map(Number);
  const len = Math.max(splitA.length, splitB.length);
  for (let i = 0; i < len; i++) {
    const av = splitA[i] ?? -1;
    const bv = splitB[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}

for (const { name, tree } of trees) {
  if (tree.level !== 1) {
    err(name, `Root id ${tree.id} must have level: 1`);
  }
  walkWithDepth(tree, 1, name, null);
}

// Same structural rules for BP trees.
function walkBPWithDepth(
  node: RawBusinessProcess,
  depth: number,
  file: string,
  parentId: string | null
) {
  if (!BP_ID_REGEX.test(node.id)) {
    err(
      file,
      `BP ${node.id}: id does not match ${BP_ID_REGEX} (BP-<L1>[.<L2>[.<L3>[.<L4>]]])`
    );
  }
  if (node.level !== depth) {
    err(
      file,
      `BP ${node.id}: level=${node.level} but tree depth=${depth}; level must equal depth (root=1)`
    );
  }
  if (parentId !== null && !node.id.startsWith(parentId + ".")) {
    err(
      file,
      `BP ${node.id}: must extend parent id ${parentId} (e.g., ${parentId}.N)`
    );
  }
  if (node.deprecated && !node.deprecation_reason) {
    err(file, `BP ${node.id}: deprecated=true requires deprecation_reason`);
  }
  const childIds = (node.children ?? []).map((c) => c.id);
  const sorted = [...childIds].sort((a, b) => compareDottedIds(a, b, "BP"));
  for (let i = 0; i < childIds.length; i++) {
    if (childIds[i] !== sorted[i]) {
      err(
        file,
        `BP ${node.id}: children are not sorted by id ascending. Got [${childIds.join(", ")}], expected [${sorted.join(", ")}]`
      );
      break;
    }
  }
  for (const child of node.children ?? []) {
    walkBPWithDepth(child, depth + 1, file, node.id);
  }
}

for (const { name, tree } of bpTrees) {
  if (tree.level !== 1) {
    err(`processes/${name}`, `Root BP ${tree.id} must have level: 1`);
  }
  walkBPWithDepth(tree, 1, `processes/${name}`, null);
}

// ---------------------------------------------------------------------------
// 10. Cross-file uniqueness + successor resolution (capabilities)
// ---------------------------------------------------------------------------
const allFlat: { file: string; node: FlatCapability }[] = [];
for (const { name, tree } of trees) {
  for (const node of flatten(tree)) {
    allFlat.push({ file: name, node });
  }
}

const idIndex = new Map<string, string>(); // id -> first file it was seen in
for (const { file, node } of allFlat) {
  const seen = idIndex.get(node.id);
  if (seen) {
    err(file, `Duplicate id ${node.id} (also in ${seen})`);
  } else {
    idIndex.set(node.id, file);
  }
}

const slugSet = new Map<string, string>();
for (const { name, tree } of trees) {
  const slug = l1Slug(tree);
  const existing = slugSet.get(slug);
  if (existing) {
    err(name, `L1 slug '${slug}' collides with ${existing}`);
  } else {
    slugSet.set(slug, name);
  }
}

for (const { file, node } of allFlat) {
  if (node.successor_id && !idIndex.has(node.successor_id)) {
    err(
      file,
      `id ${node.id}: successor_id '${node.successor_id}' does not resolve to any catalogue node`
    );
  }
}

// Cross-file uniqueness + successor resolution (business processes).
const allFlatBP: { file: string; node: FlatBusinessProcess }[] = [];
for (const { name, tree } of bpTrees) {
  for (const node of flattenBP(tree)) {
    allFlatBP.push({ file: name, node });
  }
}
const bpIdIndex = new Map<string, string>(); // BP id -> first file
for (const { file, node } of allFlatBP) {
  const seen = bpIdIndex.get(node.id);
  if (seen) {
    err(`processes/${file}`, `BP ${node.id}: duplicate id (also in processes/${seen})`);
  } else {
    bpIdIndex.set(node.id, file);
  }
}
const bpSlugSet = new Map<string, string>();
for (const { name, tree } of bpTrees) {
  const slug = bp1Slug(tree);
  const existing = bpSlugSet.get(slug);
  if (existing) {
    err(`processes/${name}`, `BP1 slug '${slug}' collides with processes/${existing}`);
  } else {
    bpSlugSet.set(slug, name);
  }
}
for (const { file, node } of allFlatBP) {
  if (node.successor_id && !bpIdIndex.has(node.successor_id)) {
    err(
      `processes/${file}`,
      `BP ${node.id}: successor_id '${node.successor_id}' does not resolve to any process node`
    );
  }
}

// Industry vocabulary derived from L1 capabilities — single source of truth.
const l1Set = new Set(
  allFlat.filter(({ node }) => node.level === 1).map(({ node }) => node.id)
);
const industryVocab = new Set<string>();
for (const { node } of allFlat) {
  if (node.level !== 1 || !node.industry) continue;
  for (const part of node.industry.split(";").map((s) => s.trim()).filter(Boolean)) {
    if (part !== "Cross-Industry") industryVocab.add(part);
  }
}

// BP industry must match BC vocabulary; inheritance from BP1 enforced.
const bp1IndustryByRoot = new Map<string, Set<string>>();
for (const { tree } of bpTrees) {
  const inds = new Set<string>();
  if (tree.industry) {
    for (const part of tree.industry.split(";").map((s) => s.trim()).filter(Boolean)) {
      inds.add(part);
    }
  }
  if (inds.size === 0) inds.add("Cross-Industry");
  bp1IndustryByRoot.set(tree.id, inds);
}
function bp1IdOf(bpId: string): string {
  return bpId.split(".")[0];
}
for (const { file, node } of allFlatBP) {
  if (!node.industry) continue;
  const declared = node.industry
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);
  for (const ind of declared) {
    if (ind === "Cross-Industry") continue;
    if (!industryVocab.has(ind)) {
      const valid = ["Cross-Industry", ...Array.from(industryVocab).sort()].join(", ");
      err(
        `processes/${file}`,
        `BP ${node.id}: industry '${ind}' not in catalogue vocabulary; valid values: ${valid}`
      );
    }
  }
  // Inheritance check: declared industries must intersect the root BP1's set,
  // unless the root is Cross-Industry (then any industry is allowed as override).
  const rootInds = bp1IndustryByRoot.get(bp1IdOf(node.id));
  if (rootInds && !rootInds.has("Cross-Industry") && node.id !== bp1IdOf(node.id)) {
    const overlap = declared.some((d) => rootInds.has(d));
    if (!overlap) {
      err(
        `processes/${file}`,
        `BP ${node.id}: industry '${node.industry}' not present on root BP ${bp1IdOf(node.id)}; remove or override at BP1`
      );
    }
  }
}

// realizes_capability_ids must resolve to a known BC node.
for (const { file, node } of allFlatBP) {
  for (const bcId of node.realizes_capability_ids ?? []) {
    if (!idIndex.has(bcId)) {
      err(
        `processes/${file}`,
        `BP ${node.id}: realizes_capability_ids '${bcId}' does not resolve to any capability node`
      );
    }
  }
}

// ---------------------------------------------------------------------------
// 11. Value streams: schema, ids, capability/process resolution.
//
// Each stream must declare an `industries` array drawn from the catalogue's
// L1 industry vocabulary (or `Cross-Industry`, which must stand alone).
// Stage `capability_ids` must be L1; sub-scope detail belongs in `notes`.
// Stage `process_ids` must resolve to a non-deprecated BP node.
// ---------------------------------------------------------------------------
const vsSchema = JSON.parse(readFileSync(VALUE_STREAM_SCHEMA_PATH, "utf8"));
const validateVS = ajv.compile(vsSchema);

const vsFilePath = join(CATALOGUE_DIR, "_value-streams.yaml");
if (existsSync(vsFilePath)) {
  const rawObj = YAML.parse(readFileSync(vsFilePath, "utf8"));
  if (rawObj && !validateVS(rawObj)) {
    for (const e of validateVS.errors ?? []) {
      err("_value-streams.yaml", `schema: ${e.instancePath || "/"} ${e.message}`);
    }
  }
}

const streams = loadValueStreams();
const seenStreamIds = new Set<string>();
for (const stream of streams) {
  // id presence/format
  if (!stream.id) {
    err(
      "_value-streams.yaml",
      `Stream '${stream.name}': missing required 'id' (expected VS-<n>)`
    );
  } else if (!VS_ID_REGEX.test(stream.id)) {
    err(
      "_value-streams.yaml",
      `Stream '${stream.name}': id '${stream.id}' does not match ${VS_ID_REGEX}`
    );
  } else if (seenStreamIds.has(stream.id)) {
    err(
      "_value-streams.yaml",
      `Stream '${stream.name}': id '${stream.id}' duplicates an earlier stream`
    );
  } else {
    seenStreamIds.add(stream.id);
  }

  // industries vocabulary
  if (!Array.isArray(stream.industries) || stream.industries.length === 0) {
    err(
      "_value-streams.yaml",
      `Stream '${stream.name}': missing required 'industries' array (use [Cross-Industry] for cross-industry streams)`
    );
  } else {
    const inds = stream.industries.map((i) => i.trim());
    if (inds.includes("Cross-Industry") && inds.length > 1) {
      err(
        "_value-streams.yaml",
        `Stream '${stream.name}': 'Cross-Industry' must be the only entry in industries when present`
      );
    }
    for (const ind of inds) {
      if (ind === "Cross-Industry") continue;
      if (!industryVocab.has(ind)) {
        const valid = ["Cross-Industry", ...Array.from(industryVocab).sort()].join(", ");
        err(
          "_value-streams.yaml",
          `Stream '${stream.name}': industry '${ind}' not in catalogue vocabulary; valid values: ${valid}`
        );
      }
    }
  }

  if (stream.deprecated && !stream.deprecation_reason) {
    err(
      "_value-streams.yaml",
      `Stream '${stream.name}' (${stream.id ?? "?"}): deprecated=true requires deprecation_reason`
    );
  }
  if (stream.successor_id && !seenStreamIds.has(stream.successor_id)) {
    // successor may resolve to a later stream — re-check after the loop.
  }

  // stages
  const seenStageIds = new Set<string>();
  for (const stage of stream.stages ?? []) {
    if (!stage.id) {
      err(
        "_value-streams.yaml",
        `Stream '${stream.id ?? stream.name}' / stage '${stage.stage_name}': missing required 'id' (expected ${stream.id ?? "VS-<n>"}.<m>)`
      );
    } else if (!VS_STAGE_ID_REGEX.test(stage.id)) {
      err(
        "_value-streams.yaml",
        `Stream '${stream.id ?? stream.name}' / stage '${stage.stage_name}': id '${stage.id}' does not match ${VS_STAGE_ID_REGEX}`
      );
    } else {
      if (stream.id && !stage.id.startsWith(stream.id + ".")) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id}' / stage '${stage.stage_name}': stage id '${stage.id}' must extend stream id '${stream.id}.<m>'`
        );
      }
      if (seenStageIds.has(stage.id)) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id ?? stream.name}': stage id '${stage.id}' duplicates an earlier stage`
        );
      } else {
        seenStageIds.add(stage.id);
      }
    }

    // capability_ids: must be L1
    const capIds = stage.capability_ids ?? [];
    if (capIds.length === 0) {
      err(
        "_value-streams.yaml",
        `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': capability_ids[] must contain at least one L1`
      );
    }
    for (let i = 0; i < capIds.length; i++) {
      const cid = capIds[i];
      if (!L1_ID_REGEX.test(cid)) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': capability_ids[${i}] '${cid}' is not L1. ` +
            `Use the L1 (e.g. ${cid.split(".")[0]}) and put sub-scope in 'notes'.`
        );
      } else if (!l1Set.has(cid)) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': L1 ${cid} not found in catalogue`
        );
      }
    }
    // process_ids: each must resolve to a non-deprecated BP node.
    const procIds = stage.process_ids ?? [];
    for (let i = 0; i < procIds.length; i++) {
      const pid = procIds[i];
      if (!BP_ID_REGEX.test(pid)) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': process_ids[${i}] '${pid}' fails the BP- pattern`
        );
        continue;
      }
      if (!bpIdIndex.has(pid)) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': process_ids[${i}] '${pid}' does not resolve to any business-process node`
        );
        continue;
      }
      const bpFile = bpIdIndex.get(pid)!;
      const bpNode = allFlatBP.find((x) => x.node.id === pid);
      if (bpNode?.node.deprecated) {
        err(
          "_value-streams.yaml",
          `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': process_ids[${i}] '${pid}' is deprecated (in processes/${bpFile}); use successor or remove`
        );
      }
    }
    // stage industries: same vocabulary
    if (Array.isArray(stage.industries)) {
      for (const ind of stage.industries) {
        if (ind === "Cross-Industry") continue;
        if (!industryVocab.has(ind)) {
          const valid = ["Cross-Industry", ...Array.from(industryVocab).sort()].join(", ");
          err(
            "_value-streams.yaml",
            `Stream '${stream.id ?? stream.name}' / stage '${stage.id ?? stage.stage_name}': industry '${ind}' not in catalogue vocabulary; valid values: ${valid}`
          );
        }
      }
    }
  }
}

// successor_id resolution — second pass once all stream ids are known.
for (const stream of streams) {
  if (stream.successor_id && !seenStreamIds.has(stream.successor_id)) {
    err(
      "_value-streams.yaml",
      `Stream '${stream.id ?? stream.name}': successor_id '${stream.successor_id}' does not resolve`
    );
  }
}

// ---------------------------------------------------------------------------
// 11b. Macro capabilities: schema, MC-id format, MECE, L1-only references,
// industry vocabulary. Macros are an orthogonal overlay above L1 — they don't
// enter the BC tree and don't participate in VS/BP links.
// ---------------------------------------------------------------------------
const mcSchema = JSON.parse(readFileSync(MACRO_CAPABILITY_SCHEMA_PATH, "utf8"));
const validateMC = ajv.compile(mcSchema);

const mcFilePath = join(CATALOGUE_DIR, "_macro-capabilities.yaml");
if (existsSync(mcFilePath)) {
  const rawObj = YAML.parse(readFileSync(mcFilePath, "utf8"));
  if (rawObj && !validateMC(rawObj)) {
    for (const e of validateMC.errors ?? []) {
      err("_macro-capabilities.yaml", `schema: ${e.instancePath || "/"} ${e.message}`);
    }
  }
}

const macros: MacroCapability[] = loadMacroCapabilities();
const seenMacroIds = new Set<string>();
const seenMacroSlugs = new Map<string, string>();
const macroById = new Map<string, MacroCapability>();
const macroClaims = new Map<string, string[]>(); // BC L1 id -> [MC ids]

for (const macro of macros) {
  if (!macro.id) {
    err("_macro-capabilities.yaml", `Macro '${macro.name ?? "<?>"}': missing required 'id' (expected MC-<n>)`);
  } else if (!MC_ID_REGEX.test(macro.id)) {
    err(
      "_macro-capabilities.yaml",
      `Macro '${macro.name ?? macro.id}': id '${macro.id}' does not match ${MC_ID_REGEX}`
    );
  } else if (seenMacroIds.has(macro.id)) {
    err(
      "_macro-capabilities.yaml",
      `Macro '${macro.name ?? macro.id}': id '${macro.id}' duplicates an earlier macro`
    );
  } else {
    seenMacroIds.add(macro.id);
    macroById.set(macro.id, macro);
  }

  // Name uniqueness via slug.
  if (macro.name) {
    const slug = macro.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
    const existing = seenMacroSlugs.get(slug);
    if (existing) {
      err(
        "_macro-capabilities.yaml",
        `Macro '${macro.id ?? macro.name}': name '${macro.name}' collides with ${existing} (slug '${slug}')`
      );
    } else {
      seenMacroSlugs.set(slug, macro.id ?? macro.name);
    }
  }

  // Industry vocabulary check (allow 'Cross-Industry' standalone or
  // ';'-separated entries from the L1 industry vocab).
  if (macro.industry) {
    const parts = macro.industry
      .split(";")
      .map((s) => s.trim())
      .filter(Boolean);
    if (parts.includes("Cross-Industry") && parts.length > 1) {
      err(
        "_macro-capabilities.yaml",
        `Macro '${macro.id ?? macro.name}': 'Cross-Industry' must stand alone in industry`
      );
    }
    for (const p of parts) {
      if (p === "Cross-Industry") continue;
      if (!industryVocab.has(p)) {
        const valid = ["Cross-Industry", ...Array.from(industryVocab).sort()].join(", ");
        err(
          "_macro-capabilities.yaml",
          `Macro '${macro.id ?? macro.name}': industry '${p}' not in catalogue vocabulary; valid values: ${valid}`
        );
      }
    }
  }

  if (macro.deprecated && !macro.deprecation_reason) {
    err(
      "_macro-capabilities.yaml",
      `Macro '${macro.id ?? macro.name}': deprecated=true requires deprecation_reason`
    );
  }

  // capability_ids: must be L1 and resolve to a catalogue node.
  const caps = macro.capability_ids ?? [];
  if (caps.length === 0) {
    err(
      "_macro-capabilities.yaml",
      `Macro '${macro.id ?? macro.name}': capability_ids[] must contain at least one L1`
    );
  }
  for (let i = 0; i < caps.length; i++) {
    const cid = caps[i];
    if (!L1_ID_REGEX.test(cid)) {
      err(
        "_macro-capabilities.yaml",
        `Macro '${macro.id ?? macro.name}': capability_ids[${i}] '${cid}' is not L1 (expected BC-<N>, no dots)`
      );
      continue;
    }
    if (!l1Set.has(cid)) {
      err(
        "_macro-capabilities.yaml",
        `Macro '${macro.id ?? macro.name}': capability_ids[${i}] '${cid}' not found in catalogue`
      );
      continue;
    }
    const list = macroClaims.get(cid) ?? [];
    list.push(macro.id ?? macro.name ?? "<?>");
    macroClaims.set(cid, list);
  }
}

// MECE check: each L1 referenced by at most one macro.
for (const [cid, mcIds] of macroClaims) {
  if (mcIds.length > 1) {
    err(
      "_macro-capabilities.yaml",
      `L1 '${cid}' claimed by multiple macros (${mcIds.join(", ")}); macros must be MECE`
    );
  }
}

// Successor resolution.
for (const macro of macros) {
  if (macro.successor_id && !seenMacroIds.has(macro.successor_id)) {
    err(
      "_macro-capabilities.yaml",
      `Macro '${macro.id ?? macro.name}': successor_id '${macro.successor_id}' does not resolve`
    );
  }
}

// ---------------------------------------------------------------------------
// 12. Translation sidecars: schema, locale-tag/dir match, source resolution,
//     orphaned entry ids. Sidecars are optional; if catalogue/i18n/ does not
//     exist, this section is a no-op.
// ---------------------------------------------------------------------------
const i18nSchema = JSON.parse(readFileSync(I18N_SCHEMA_PATH, "utf8"));
const validateI18n = ajv.compile(i18nSchema);
const indexedFileSet = new Set(index.files);
const processesIndexedFileSet = new Set(processesIndex.files);
let sidecarCount = 0;

// Source lookups for staleness hash recomputation.
const capabilityById = new Map<string, FlatCapability>();
for (const { node } of allFlat) capabilityById.set(node.id, node);
const businessProcessById = new Map<string, FlatBusinessProcess>();
for (const { node } of allFlatBP) businessProcessById.set(node.id, node);
const streamById = new Map<string, (typeof streams)[number]>();
const stageById = new Map<string, (typeof streams)[number]["stages"][number]>();
for (const stream of streams) {
  if (stream.id) streamById.set(stream.id, stream);
  for (const stage of stream.stages ?? []) {
    if (stage.id) stageById.set(stage.id, stage);
  }
}

for (const { locale, file, data } of loadAllSidecars()) {
  const tag = `i18n/${locale}/${file}`;
  sidecarCount++;
  if (!validateI18n(data)) {
    for (const e of validateI18n.errors ?? []) {
      err(tag, `schema: ${e.instancePath || "/"} ${e.message}`);
    }
    continue;
  }
  if (!BCP47_REGEX.test(locale)) {
    err(tag, `directory '${locale}' is not a valid BCP-47 tag`);
  }
  if (data.locale !== locale) {
    err(tag, `locale field '${data.locale}' must equal directory name '${locale}'`);
  }
  const kind: SidecarKind = data.kind ?? "capability";

  // source resolution + orphan / scope check, dispatched on kind.
  if (kind === "capability") {
    if (!indexedFileSet.has(data.source)) {
      err(tag, `source '${data.source}' is not registered in catalogue/_index.yaml`);
    }
    let sourceTreeIds: Set<string> | null = null;
    const sourceTree = trees.find(({ name }) => name === data.source);
    if (sourceTree) {
      sourceTreeIds = new Set(flatten(sourceTree.tree).map((n) => n.id));
    }
    for (const id of Object.keys(data.entries)) {
      if (!ID_REGEX.test(id)) {
        err(tag, `entry '${id}' is not a capability id (kind: capability expects BC-...)`);
        continue;
      }
      if (!idIndex.has(id)) {
        err(tag, `entry '${id}' does not resolve to any catalogue node`);
        continue;
      }
      if (sourceTreeIds && !sourceTreeIds.has(id)) {
        err(
          tag,
          `entry '${id}' is not part of source '${data.source}' (cross-L1 entry — move to the correct sidecar)`
        );
      }
      // Staleness check: if the entry pinned a source_hash, recompute and
      // compare against the current English source. Mismatch → drift.
      const stored = data.entries[id]?.source_hash;
      if (stored) {
        const src = capabilityById.get(id);
        if (src) {
          const current = hashCapabilityLikeSource(src);
          if (current !== stored) {
            err(
              tag,
              `entry '${id}' is stale: source_hash '${stored}' no longer matches source '${data.source}' (current: '${current}'). Retranslate and re-stamp via 'npm run i18n:stamp'.`
            );
          }
        }
      }
    }
  } else if (kind === "business-process") {
    if (!processesIndexedFileSet.has(data.source)) {
      err(
        tag,
        `source '${data.source}' is not registered in catalogue/processes/_index.yaml`
      );
    }
    let sourceTreeIds: Set<string> | null = null;
    const sourceTree = bpTrees.find(({ name }) => name === data.source);
    if (sourceTree) {
      sourceTreeIds = new Set(flattenBP(sourceTree.tree).map((n) => n.id));
    }
    for (const id of Object.keys(data.entries)) {
      if (!BP_ID_REGEX.test(id)) {
        err(tag, `entry '${id}' is not a process id (kind: business-process expects BP-...)`);
        continue;
      }
      if (!bpIdIndex.has(id)) {
        err(tag, `entry '${id}' does not resolve to any business-process node`);
        continue;
      }
      if (sourceTreeIds && !sourceTreeIds.has(id)) {
        err(
          tag,
          `entry '${id}' is not part of source '${data.source}' (cross-BP1 entry — move to the correct sidecar)`
        );
      }
      const stored = data.entries[id]?.source_hash;
      if (stored) {
        const src = businessProcessById.get(id);
        if (src) {
          const current = hashCapabilityLikeSource(src);
          if (current !== stored) {
            err(
              tag,
              `entry '${id}' is stale: source_hash '${stored}' no longer matches source '${data.source}' (current: '${current}'). Retranslate and re-stamp via 'npm run i18n:stamp'.`
            );
          }
        }
      }
    }
  } else if (kind === "macro-capability") {
    if (data.source !== "_macro-capabilities.yaml") {
      err(
        tag,
        `source '${data.source}' must be '_macro-capabilities.yaml' for kind: macro-capability`
      );
    }
    for (const id of Object.keys(data.entries)) {
      if (!MC_ID_REGEX.test(id)) {
        err(
          tag,
          `entry '${id}' is not a macro-capability id (kind: macro-capability expects MC-<n>)`
        );
        continue;
      }
      if (!macroById.has(id)) {
        err(tag, `entry '${id}' does not resolve to any macro capability`);
        continue;
      }
      const stored = data.entries[id]?.source_hash;
      if (stored) {
        const src = macroById.get(id);
        if (src) {
          const current = hashMacroCapabilitySource(src);
          if (current !== stored) {
            err(
              tag,
              `entry '${id}' is stale: source_hash '${stored}' no longer matches '_macro-capabilities.yaml' (current: '${current}'). Retranslate and re-stamp via 'npm run i18n:stamp'.`
            );
          }
        }
      }
    }
  } else if (kind === "value-stream") {
    if (data.source !== "_value-streams.yaml") {
      err(tag, `source '${data.source}' must be '_value-streams.yaml' for kind: value-stream`);
    }
    const streamIds = new Set(streams.map((s) => s.id));
    const stageIds = new Set<string>();
    const stageToStream = new Map<string, string>();
    for (const s of streams) {
      for (const st of s.stages ?? []) {
        stageIds.add(st.id);
        stageToStream.set(st.id, s.id);
      }
    }
    for (const id of Object.keys(data.entries)) {
      if (VS_ID_REGEX.test(id)) {
        if (!streamIds.has(id)) {
          err(tag, `entry '${id}' does not resolve to any value stream`);
          continue;
        }
        const stored = data.entries[id]?.source_hash;
        if (stored) {
          const src = streamById.get(id);
          if (src) {
            const current = hashValueStreamSource(src);
            if (current !== stored) {
              err(
                tag,
                `entry '${id}' is stale: source_hash '${stored}' no longer matches '_value-streams.yaml' (current: '${current}'). Retranslate and re-stamp via 'npm run i18n:stamp'.`
              );
            }
          }
        }
      } else if (VS_STAGE_ID_REGEX.test(id)) {
        if (!stageIds.has(id)) {
          err(tag, `entry '${id}' does not resolve to any value-stream stage`);
          continue;
        }
        const stored = data.entries[id]?.source_hash;
        if (stored) {
          const src = stageById.get(id);
          if (src) {
            const current = hashValueStreamStageSource(src);
            if (current !== stored) {
              err(
                tag,
                `entry '${id}' is stale: source_hash '${stored}' no longer matches '_value-streams.yaml' (current: '${current}'). Retranslate and re-stamp via 'npm run i18n:stamp'.`
              );
            }
          }
        }
      } else {
        err(tag, `entry '${id}' is not a value-stream id (expected VS-<n> or VS-<n>.<m>)`);
      }
    }
  }
}

// ---------------------------------------------------------------------------
// 13. BC coverage check (warning, not error). Every Cross-Industry BC L1
// should have at least one BP claiming to realize it. Process orphans
// are reported as warnings — they don't fail the build, but they signal
// gaps in the BP layer that should be closed.
// ---------------------------------------------------------------------------
const warnings: LintError[] = [];
const cxL1Ids = new Set<string>();
for (const { node } of allFlat) {
  if (node.level !== 1) continue;
  const industry = node.industry ?? "";
  if (!industry.includes("Cross-Industry")) continue;
  cxL1Ids.add(node.id);
}
const realisedBcIds = new Set<string>();
for (const { node } of allFlatBP) {
  for (const bcId of node.realizes_capability_ids ?? []) realisedBcIds.add(bcId);
}
for (const id of cxL1Ids) {
  if (!realisedBcIds.has(id)) {
    warnings.push({
      file: "bc-coverage",
      message: `Cross-Industry BC L1 '${id}' has no BP realising it (orphan capability — extend an existing BP1 or add a new one).`,
    });
  }
}

// Macro coverage (warning). Every Cross-Industry L1 should belong to one macro.
// Empty catalogue (macros.length === 0) skips this check so older snapshots
// without the macro layer don't suddenly warn.
if (macros.length > 0) {
  for (const id of cxL1Ids) {
    if (!macroClaims.has(id)) {
      warnings.push({
        file: "macro-coverage",
        message: `Cross-Industry BC L1 '${id}' is not claimed by any macro (add it to _macro-capabilities.yaml or run \`npm run check:macro-coverage\`).`,
      });
    }
  }
}

// ---------------------------------------------------------------------------
// Report
// ---------------------------------------------------------------------------
if (errors.length > 0) {
  console.error(`\n✘ Lint failed with ${errors.length} error(s):\n`);
  for (const { file, message } of errors) {
    console.error(`  [${file}] ${message}`);
  }
  console.error("");
  process.exit(1);
}
if (warnings.length > 0) {
  console.warn(`\n⚠ ${warnings.length} warning(s):`);
  for (const { file, message } of warnings) {
    console.warn(`  [${file}] ${message}`);
  }
  console.warn("");
}
console.log(
  `✔ Lint passed: ${trees.length} L1 file(s), ${allFlat.length} capability node(s), ${bpTrees.length} BP1 file(s), ${allFlatBP.length} process node(s), ${streams.length} value stream(s), ${macros.length} macro(s), ${sidecarCount} sidecar(s).`
);
