#!/usr/bin/env tsx
/**
 * Add a new macro capability to catalogue/_macro-capabilities.yaml.
 *
 *   npm run mc:add -- --name "People & Workplace" --capabilities BC-300,BC-700,BC-710
 *   npm run mc:add -- --name "Operations Excellence" --industries Cross-Industry --capabilities BC-800,BC-810 --description "Quality and HSE assurance."
 *
 * Picks the next sparse MC-N0 id (10/20/30...). Validates that capability_ids
 * are L1 (no dots), that no other macro already claims those L1s, and that
 * each L1 exists in the BC catalogue. Use mc_mv (TBD) or direct YAML edit to
 * move an L1 between macros.
 */
import YAML from "yaml";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import {
  CATALOGUE_DIR,
  MC_ID_REGEX,
  loadAllL1Files,
  loadMacroCapabilities,
} from "../lib/load.ts";
import { parseArgs } from "./_shared.ts";

const L1_ID_REGEX = /^BC-\d+$/;

const args = parseArgs(process.argv.slice(2));
const name = args.name;
const capsArg = args.capabilities;
if (!name || !capsArg) {
  console.error(
    "Usage: mc:add --name '<Macro Name>' --capabilities BC-100,BC-110[,...] [--industries 'Cross-Industry'] [--description '...']"
  );
  process.exit(2);
}
const industry = args.industries ?? "Cross-Industry";
const capabilityIds = capsArg
  .split(/[,;]/)
  .map((s) => s.trim())
  .filter(Boolean);

if (capabilityIds.length === 0) {
  console.error("--capabilities must list at least one L1 id");
  process.exit(2);
}
for (const cid of capabilityIds) {
  if (!L1_ID_REGEX.test(cid)) {
    console.error(`capability id '${cid}' is not L1 (expected BC-<N>, no dots).`);
    process.exit(2);
  }
}

// Validate L1 existence + collect already-claimed ids for MECE check.
const l1ById = new Map<string, string>(); // id -> name
for (const { tree } of loadAllL1Files()) {
  if (tree.level === 1) l1ById.set(tree.id, tree.name);
}
for (const cid of capabilityIds) {
  if (!l1ById.has(cid)) {
    console.error(`L1 '${cid}' not found in catalogue.`);
    process.exit(2);
  }
}

const existing = loadMacroCapabilities();
const claimed = new Map<string, string>(); // bc id -> macro id
for (const m of existing) {
  for (const cid of m.capability_ids ?? []) claimed.set(cid, m.id);
}
for (const cid of capabilityIds) {
  if (claimed.has(cid)) {
    console.error(
      `L1 '${cid}' is already claimed by macro ${claimed.get(cid)}. Macros are MECE; reassign there first.`
    );
    process.exit(2);
  }
}

const path = join(CATALOGUE_DIR, "_macro-capabilities.yaml");
if (!existsSync(path)) {
  console.error("catalogue/_macro-capabilities.yaml not found");
  process.exit(1);
}
const doc = YAML.parseDocument(readFileSync(path, "utf8"));
const macrosSeq = doc.get("macros") as YAML.YAMLSeq | null;
if (!macrosSeq) {
  console.error("_macro-capabilities.yaml is missing the 'macros' sequence");
  process.exit(1);
}

// Find next sparse id (max + 10, or 10 if empty).
const usedNumbers: number[] = [];
for (const item of macrosSeq.items as YAML.YAMLMap[]) {
  const id = String(item.get("id") ?? "");
  const m = id.match(/^MC-(\d+)$/);
  if (m) usedNumbers.push(Number(m[1]));
}
const nextN = usedNumbers.length === 0 ? 10 : Math.max(...usedNumbers) + 10;
const newId = `MC-${nextN}`;
if (!MC_ID_REGEX.test(newId)) {
  console.error(`internal error: computed id '${newId}' fails MC- pattern`);
  process.exit(1);
}

const newMacro = {
  id: newId,
  name,
  industry,
  ...(args.description ? { description: args.description } : {}),
  capability_ids: capabilityIds,
};
macrosSeq.add(doc.createNode(newMacro));

writeFileSync(path, doc.toString({ lineWidth: 0 }), "utf8");
console.log(
  `✔ Added macro ${newId} '${name}' (${industry}) over ${capabilityIds.length} L1(s): ${capabilityIds.join(", ")}`
);
