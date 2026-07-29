#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * Rewrite `process_ids` in `catalogue/_value-streams.yaml` according to
 * a {oldBpId: newBpId | null} mapping. Used after Cross-Industry BPs are
 * regenerated (their ids change), or when a process is re-parented.
 *
 *   npm run bp:relink-vs -- --map scripts/cli/_data/bp_relink.json
 *
 * Mapping JSON shape:
 *   {
 *     "BP-30.50.40": "BP-1000.30.20",   // re-point
 *     "BP-30.50.10": null               // drop the reference entirely
 *   }
 *
 * Validates that every resulting `process_ids` entry resolves to an
 * existing non-deprecated BP node (run after the new BPs are in place).
 * Preserves YAML formatting via `parseDocument`.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import {
  CATALOGUE_DIR,
  flattenBP,
  loadAllBP1Files,
} from "../lib/load.ts";
import { parseArgs } from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const mapPath = args.map && args.map !== "true" ? args.map : null;

if (!mapPath) {
  console.error("Usage: bp:relink-vs --map <path-to-mapping.json>");
  process.exit(2);
}

const mapping = JSON.parse(readFileSync(mapPath, "utf8")) as Record<string, string | null>;
for (const [k, v] of Object.entries(mapping)) {
  if (typeof k !== "string" || !k.startsWith("BP-")) {
    console.error(`Mapping key '${k}' is not a BP id.`);
    process.exit(1);
  }
  if (v !== null && (typeof v !== "string" || !v.startsWith("BP-"))) {
    console.error(`Mapping value for '${k}' must be null or a BP id, got '${v}'.`);
    process.exit(1);
  }
}

const vsPath = join(CATALOGUE_DIR, "_value-streams.yaml");
const vsSource = readFileSync(vsPath, "utf8");
const vsDoc = YAML.parseDocument(vsSource);

let rewrites = 0;
let drops = 0;
const streams = vsDoc.get("value_streams");
if (!YAML.isSeq(streams)) {
  console.error("_value-streams.yaml has no top-level `value_streams` sequence.");
  process.exit(1);
}

for (const stream of streams.items) {
  if (!YAML.isMap(stream)) continue;
  const stages = stream.get("stages");
  if (!YAML.isSeq(stages)) continue;
  for (const stage of stages.items) {
    if (!YAML.isMap(stage)) continue;
    const procIds = stage.get("process_ids");
    if (!YAML.isSeq(procIds)) continue;
    const next: string[] = [];
    for (const item of procIds.items) {
      const v = YAML.isScalar(item) ? String(item.value) : String(item);
      if (v in mapping) {
        const replacement = mapping[v];
        if (replacement === null) {
          drops++;
          continue;
        }
        next.push(replacement);
        rewrites++;
      } else {
        next.push(v);
      }
    }
    stage.set("process_ids", next);
  }
}

// Validate: every resulting process_id must resolve to an existing non-deprecated BP node.
const allBp = new Map<string, { deprecated?: boolean }>();
for (const { tree } of loadAllBP1Files()) {
  for (const node of flattenBP(tree)) {
    allBp.set(node.id, { deprecated: node.deprecated });
  }
}

// Re-parse the mutated doc to walk it and validate.
const mutated = vsDoc.toJS() as { value_streams?: Array<{ id?: string; stages?: Array<{ id?: string; process_ids?: string[] }> }> };
const errors: string[] = [];
for (const s of mutated.value_streams ?? []) {
  for (const stage of s.stages ?? []) {
    for (const pid of stage.process_ids ?? []) {
      const hit = allBp.get(pid);
      if (!hit) {
        errors.push(`Stream ${s.id} stage ${stage.id}: process_id '${pid}' does not resolve.`);
      } else if (hit.deprecated) {
        errors.push(`Stream ${s.id} stage ${stage.id}: process_id '${pid}' resolves to a deprecated node.`);
      }
    }
  }
}

if (errors.length > 0) {
  console.error(`bp:relink-vs validation failed with ${errors.length} error(s):`);
  for (const e of errors) console.error(`  ${e}`);
  process.exit(1);
}

writeFileSync(vsPath, vsDoc.toString({ lineWidth: 0 }), "utf8");

console.log(
  `Re-linked ${rewrites} process_id entries, dropped ${drops}; ${allBp.size} BP nodes available for resolution.`
);
