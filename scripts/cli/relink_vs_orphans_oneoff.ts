#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * Second pass: relink the residual orphan VS stages — stages whose
 * `process_ids` are still empty after the first relink_vs_oneoff pass.
 *
 *   npx tsx scripts/cli/relink_vs_orphans_oneoff.ts
 *
 * Two new tactics:
 *   1. Strip parentheticals from stage_name before matching ("Issue
 *      Capture (Banking Fin Crime)" → "Issue Capture"). This recovers
 *      industry-variant stages whose base name matches a Cross-Industry
 *      BP2.
 *   2. Search across the full BP forest (BP1, BP2, BP3) for name
 *      matches — including industry-specific BP1 trees — so industry
 *      stages can resolve to industry BP processes.
 *
 * Stages that still have no match after both tactics are left empty
 * (true orphans flagged for manual review).
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import { CATALOGUE_DIR, flattenBP, loadAllBP1Files } from "../lib/load.ts";

// Build name → ids index across the full BP forest at all depths.
const nameToIds = new Map<string, string[]>();
for (const { tree } of loadAllBP1Files()) {
  for (const node of flattenBP(tree)) {
    const list = nameToIds.get(node.name) ?? [];
    list.push(node.id);
    nameToIds.set(node.name, list);
  }
}

const stripParens = (s: string): string => s.replace(/\s*\([^)]*\)\s*$/, "").trim();

const vsPath = join(CATALOGUE_DIR, "_value-streams.yaml");
const vsDoc = YAML.parseDocument(readFileSync(vsPath, "utf8"));
const streams = vsDoc.get("value_streams");
if (!YAML.isSeq(streams)) {
  console.error("_value-streams.yaml has no value_streams sequence");
  process.exit(1);
}

let recoveredExact = 0;
let recoveredStripped = 0;
let stillOrphan = 0;
const residual: string[] = [];

for (const stream of streams.items) {
  if (!YAML.isMap(stream)) continue;
  const stages = stream.get("stages");
  if (!YAML.isSeq(stages)) continue;
  for (const stage of stages.items) {
    if (!YAML.isMap(stage)) continue;
    const pids = stage.get("process_ids");
    if (!YAML.isSeq(pids) || pids.items.length > 0) continue; // only operate on empty
    const stageName = stage.get("stage_name");
    if (typeof stageName !== "string") continue;

    let match = nameToIds.get(stageName);
    if (match && match.length > 0) {
      stage.set("process_ids", match);
      recoveredExact++;
      continue;
    }
    const stripped = stripParens(stageName);
    if (stripped !== stageName) {
      match = nameToIds.get(stripped);
      if (match && match.length > 0) {
        stage.set("process_ids", match);
        recoveredStripped++;
        continue;
      }
    }
    const stageId = stage.get("id");
    residual.push(`${stageId} '${stageName}'`);
    stillOrphan++;
  }
}

writeFileSync(vsPath, vsDoc.toString({ lineWidth: 0 }), "utf8");

console.log(
  `Recovered ${recoveredExact} via exact match across full BP forest;\n` +
    `Recovered ${recoveredStripped} via parens-stripped name match;\n` +
    `Residual orphans: ${stillOrphan}`
);
if (residual.length > 0) {
  console.log("\nResidual orphan stages (still no process_ids):");
  for (const r of residual.slice(0, 40)) console.log(`  ${r}`);
  if (residual.length > 40) console.log(`  ... and ${residual.length - 40} more`);
}
