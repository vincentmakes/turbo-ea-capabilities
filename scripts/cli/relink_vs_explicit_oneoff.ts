#!/usr/bin/env tsx
/**
 * Third pass: apply explicit per-VS-stage-id overrides to set
 * `process_ids` on residual orphan stages whose stage_name doesn't match
 * any BP node by name.
 *
 *   npx tsx scripts/cli/relink_vs_explicit_oneoff.ts
 *
 * Mapping JSON: scripts/cli/_data/orphan_stage_to_bp_overrides.json
 * Shape: { "VS-N.M": ["BP-..."] | ["BP-...", "BP-..."], ... }
 * Keys starting with "_" are documentation and ignored.
 *
 * Validates that every override BP id resolves to a non-deprecated
 * BP node before writing. Preserves YAML formatting.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import { CATALOGUE_DIR, flattenBP, loadAllBP1Files } from "../lib/load.ts";

const overridesPath = join(import.meta.dirname, "_data", "orphan_stage_to_bp_overrides.json");
const overridesRaw = JSON.parse(readFileSync(overridesPath, "utf8")) as Record<string, unknown>;
const overrides = new Map<string, string[]>();
for (const [k, v] of Object.entries(overridesRaw)) {
  if (k.startsWith("_")) continue;
  if (!Array.isArray(v)) continue;
  overrides.set(k, v as string[]);
}

// Validate every override BP id resolves.
const validIds = new Map<string, boolean>(); // id -> deprecated
for (const { tree } of loadAllBP1Files()) {
  for (const node of flattenBP(tree)) validIds.set(node.id, !!node.deprecated);
}
const invalid: string[] = [];
for (const [stage, bps] of overrides) {
  for (const bp of bps) {
    if (!validIds.has(bp)) invalid.push(`${stage} → ${bp} (does not resolve)`);
    else if (validIds.get(bp)) invalid.push(`${stage} → ${bp} (deprecated)`);
  }
}
if (invalid.length > 0) {
  console.error("Override validation failed:");
  for (const m of invalid) console.error(`  ${m}`);
  process.exit(1);
}

const vsPath = join(CATALOGUE_DIR, "_value-streams.yaml");
const vsDoc = YAML.parseDocument(readFileSync(vsPath, "utf8"));
const streams = vsDoc.get("value_streams");
if (!YAML.isSeq(streams)) {
  console.error("_value-streams.yaml has no value_streams sequence");
  process.exit(1);
}

let applied = 0;
let notFound = 0;
const seenStages = new Set<string>();

for (const stream of streams.items) {
  if (!YAML.isMap(stream)) continue;
  const stages = stream.get("stages");
  if (!YAML.isSeq(stages)) continue;
  for (const stage of stages.items) {
    if (!YAML.isMap(stage)) continue;
    const stageId = stage.get("id");
    if (typeof stageId !== "string") continue;
    if (overrides.has(stageId)) {
      stage.set("process_ids", overrides.get(stageId)!);
      seenStages.add(stageId);
      applied++;
    }
  }
}

for (const k of overrides.keys()) {
  if (!seenStages.has(k)) {
    console.warn(`Override key '${k}' did not match any VS stage`);
    notFound++;
  }
}

writeFileSync(vsPath, vsDoc.toString({ lineWidth: 0 }), "utf8");
console.log(`Applied ${applied} explicit overrides; ${notFound} keys did not match a VS stage.`);
