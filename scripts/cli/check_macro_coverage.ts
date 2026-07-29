#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * Macro coverage check: every Cross-Industry BC L1 should belong to exactly
 * one macro capability in catalogue/_macro-capabilities.yaml. Reports:
 *   - orphans: Cross-Industry L1s no macro claims
 *   - double-claims: L1s referenced by more than one macro (MECE violation)
 *   - phantom refs: macro capability_ids pointing at unknown / non-L1 ids
 *   - empty macros: macros with no capability_ids
 *
 *   npx tsx scripts/cli/check_macro_coverage.ts        # report only
 *   npx tsx scripts/cli/check_macro_coverage.ts --strict   # exits non-zero on any issue
 */
import {
  loadAllL1Files,
  loadMacroCapabilities,
  MC_ID_REGEX,
} from "../lib/load.ts";

const L1_ID_REGEX = /^BC-\d+$/;

const strict = process.argv.includes("--strict");

// 1. Build the set of Cross-Industry L1 ids and a full L1 id index.
const crossIndustryL1s = new Map<string, string>(); // id -> name
const allL1s = new Map<string, string>(); // id -> name (all L1s, any industry)
for (const { tree } of loadAllL1Files()) {
  if (tree.level !== 1) continue;
  allL1s.set(tree.id, tree.name);
  const industry = tree.industry ?? "";
  if (industry.includes("Cross-Industry")) {
    crossIndustryL1s.set(tree.id, tree.name);
  }
}

// 2. Walk macros, collecting claims and detecting MECE violations.
const macros = loadMacroCapabilities();
const claims = new Map<string, string[]>(); // bc id -> [mc ids]
const phantomRefs: { mc: string; cid: string; reason: string }[] = [];
const emptyMacros: string[] = [];
const badMacroIds: string[] = [];

for (const macro of macros) {
  if (!MC_ID_REGEX.test(macro.id)) {
    badMacroIds.push(`'${macro.id}' fails ${MC_ID_REGEX} (expected MC-<n>)`);
  }
  const caps = macro.capability_ids ?? [];
  if (caps.length === 0) {
    emptyMacros.push(macro.id);
    continue;
  }
  for (const cid of caps) {
    if (!L1_ID_REGEX.test(cid)) {
      phantomRefs.push({ mc: macro.id, cid, reason: `not an L1 id (expected BC-<N>, no dots)` });
      continue;
    }
    if (!allL1s.has(cid)) {
      phantomRefs.push({ mc: macro.id, cid, reason: `not present in catalogue` });
      continue;
    }
    const list = claims.get(cid) ?? [];
    list.push(macro.id);
    claims.set(cid, list);
  }
}

// 3. Compute orphans and double-claims.
const orphans: { id: string; name: string }[] = [];
for (const [id, name] of crossIndustryL1s) {
  if (!claims.has(id)) orphans.push({ id, name });
}
const doubleClaims: { id: string; macros: string[]; name?: string }[] = [];
for (const [id, mcIds] of claims) {
  if (mcIds.length > 1) doubleClaims.push({ id, macros: mcIds, name: allL1s.get(id) });
}

// 4. Report.
const cxCount = crossIndustryL1s.size;
const claimedCount = cxCount - orphans.length;
const pct = cxCount === 0 ? 0 : ((100 * claimedCount) / cxCount).toFixed(1);
console.log(
  `Macro coverage: ${claimedCount} / ${cxCount} (${pct}%) Cross-Industry L1s belong to a macro; ${macros.length} macro(s) defined.`
);

let problems = 0;

if (orphans.length > 0) {
  console.log(`\nOrphan Cross-Industry L1s (no macro claims them):`);
  for (const o of orphans) console.log(`  ${o.id}  ${o.name}`);
  problems += orphans.length;
}
if (doubleClaims.length > 0) {
  console.log(`\nDouble-claimed L1s (MECE violation):`);
  for (const d of doubleClaims) {
    console.log(`  ${d.id}  ${d.name ?? ""}  claimed by ${d.macros.join(", ")}`);
  }
  problems += doubleClaims.length;
}
if (phantomRefs.length > 0) {
  console.log(`\nPhantom references in macros:`);
  for (const p of phantomRefs) console.log(`  ${p.mc} → ${p.cid}: ${p.reason}`);
  problems += phantomRefs.length;
}
if (emptyMacros.length > 0) {
  console.log(`\nEmpty macros (no capability_ids):`);
  for (const id of emptyMacros) console.log(`  ${id}`);
  problems += emptyMacros.length;
}
if (badMacroIds.length > 0) {
  console.log(`\nMalformed macro ids:`);
  for (const msg of badMacroIds) console.log(`  ${msg}`);
  problems += badMacroIds.length;
}

if (problems === 0) {
  console.log(`\n✔ All ${cxCount} Cross-Industry L1s belong to exactly one of ${macros.length} macro(s).`);
}

if (strict && problems > 0) process.exit(1);
