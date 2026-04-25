#!/usr/bin/env tsx
/**
 * Lint the YAML catalogue. Implements the rules in Initial_plan.md Phase 1
 * adapted to the BC-<L1>.<L2>... id convention defined in
 * business-capability-governance-model.md.
 *
 * Exits non-zero on any failure.
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import {
  CATALOGUE_DIR,
  ID_REGEX,
  SCHEMA_PATH,
  flatten,
  l1Slug,
  listYamlFiles,
  loadL1File,
  readIndex,
  type FlatCapability,
  type RawCapability,
} from "./lib/load.ts";

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

// ---------------------------------------------------------------------------
// 2. JSON Schema validation
// ---------------------------------------------------------------------------
const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf8"));
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
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

// ---------------------------------------------------------------------------
// 3-9. Structural rules per file
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
  const sorted = [...childIds].sort(compareCapabilityIds);
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

/** Compare BC-2.10 vs BC-2.2 numerically across each dotted segment. */
function compareCapabilityIds(a: string, b: string): number {
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

for (const { name, tree } of trees) {
  if (tree.level !== 1) {
    err(name, `Root id ${tree.id} must have level: 1`);
  }
  walkWithDepth(tree, 1, name, null);
}

// ---------------------------------------------------------------------------
// 10. Cross-file uniqueness + successor resolution
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
console.log(`✔ Lint passed: ${trees.length} file(s), ${allFlat.length} node(s).`);
