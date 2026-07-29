#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * One-off: re-point VS stage `process_ids` at the new BP tree where the
 * existing references are broken (i.e. point at deleted Cross-Industry
 * BP nodes). Industry-specific VS stages whose references already
 * resolve are left untouched.
 *
 *   npx tsx scripts/cli/relink_vs_oneoff.ts
 *
 * Algorithm:
 *   1. Build a set of valid BP node ids from all on-disk BP1 trees.
 *   2. Build a stage_name → [BP2 ids] index from every BP1's level-2
 *      children (Cross-Industry only — those are the BP2s that mirror
 *      VS stages).
 *   3. For each VS stage:
 *      - If every existing process_id is valid → leave unchanged.
 *      - Otherwise try to find a BP2 whose name matches the stage's
 *        stage_name; if found, replace process_ids with that BP2 id.
 *      - If no match, clear process_ids (orphan, flagged for review).
 *
 * Preserves YAML formatting via parseDocument.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import {
  CATALOGUE_DIR,
  flattenBP,
  loadAllBP1Files,
} from "../lib/load.ts";

// Build set of all valid BP node ids and stage_name → BP2 id map.
const validIds = new Set<string>();
const nameToBp2 = new Map<string, string[]>();
for (const { tree } of loadAllBP1Files()) {
  for (const node of flattenBP(tree)) {
    validIds.add(node.id);
  }
  for (const child of tree.children ?? []) {
    if (child.level !== 2) continue;
    const list = nameToBp2.get(child.name) ?? [];
    list.push(child.id);
    nameToBp2.set(child.name, list);
  }
}

const vsPath = join(CATALOGUE_DIR, "_value-streams.yaml");
const vsDoc = YAML.parseDocument(readFileSync(vsPath, "utf8"));
const streams = vsDoc.get("value_streams");
if (!YAML.isSeq(streams)) {
  console.error("_value-streams.yaml has no value_streams sequence");
  process.exit(1);
}

let stagesValid = 0;
let stagesRewritten = 0;
let stagesEmptied = 0;
const orphans: string[] = [];

for (const stream of streams.items) {
  if (!YAML.isMap(stream)) continue;
  const stages = stream.get("stages");
  if (!YAML.isSeq(stages)) continue;
  for (const stage of stages.items) {
    if (!YAML.isMap(stage)) continue;
    const pidsNode = stage.get("process_ids");
    if (!YAML.isSeq(pidsNode)) continue;
    const pids = pidsNode.items.map((it) =>
      YAML.isScalar(it) ? String(it.value) : String(it)
    );
    const broken = pids.filter((p) => !validIds.has(p));
    if (broken.length === 0) {
      stagesValid++;
      continue;
    }
    const stageName = stage.get("stage_name");
    const stageId = stage.get("id");
    const matches =
      typeof stageName === "string" ? nameToBp2.get(stageName) : undefined;
    if (matches && matches.length > 0) {
      stage.set("process_ids", matches);
      stagesRewritten++;
    } else {
      stage.set("process_ids", []);
      stagesEmptied++;
      orphans.push(`${stageId} '${stageName}'`);
    }
  }
}

writeFileSync(vsPath, vsDoc.toString({ lineWidth: 0 }), "utf8");

console.log(
  `Stages with valid existing references (untouched): ${stagesValid}\n` +
    `Stages rewritten to new BP2 (matched stage_name): ${stagesRewritten}\n` +
    `Stages emptied (no matching BP2 — orphans): ${stagesEmptied}`
);
if (orphans.length > 0) {
  console.log("\nOrphan stages (process_ids cleared, manual review):");
  for (const o of orphans.slice(0, 60)) console.log(`  ${o}`);
  if (orphans.length > 60) console.log(`  ... and ${orphans.length - 60} more`);
}
