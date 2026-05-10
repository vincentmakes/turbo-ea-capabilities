#!/usr/bin/env tsx
/**
 * BC coverage check: every Cross-Industry BC L1 should have at least one
 * BP node with `realizes_capability_ids` claiming it. Reports orphans
 * (BC L1s with no realising BP) and oversaturation hotspots (BCs realised
 * by an unusual number of BP nodes — usually a sign of over-citation).
 *
 *   npx tsx scripts/cli/check_bc_coverage.ts        # report only
 *   npx tsx scripts/cli/check_bc_coverage.ts --strict   # exits non-zero on any orphan
 *
 * Run after Step 4 of the BC+VS regeneration sweep to verify that the
 * regenerated BP layer covers what the BC catalogue says exists. Long-
 * term this should be wired into `npm run lint` as a warning.
 */
import {
  flatten,
  flattenBP,
  loadAllBP1Files,
  loadAllL1Files,
} from "../lib/load.ts";

const strict = process.argv.includes("--strict");

// 1. Build the set of Cross-Industry BC L1 ids.
const crossIndustryL1s = new Map<string, string>(); // id -> name
for (const { tree } of loadAllL1Files()) {
  if (tree.level !== 1) continue;
  const industry = tree.industry ?? "";
  if (!industry.includes("Cross-Industry")) continue;
  crossIndustryL1s.set(tree.id, tree.name);
}

// 2. Walk every BP and collect realising-BP counts per BC.
const bcToBps = new Map<string, string[]>();
for (const { tree } of loadAllBP1Files()) {
  for (const node of flattenBP(tree)) {
    for (const bcId of node.realizes_capability_ids ?? []) {
      const list = bcToBps.get(bcId) ?? [];
      list.push(node.id);
      bcToBps.set(bcId, list);
    }
  }
}

// 3. Report orphans + oversaturation.
const orphans: { id: string; name: string }[] = [];
for (const [id, name] of crossIndustryL1s) {
  if (!bcToBps.has(id)) orphans.push({ id, name });
}

const cxL1Count = crossIndustryL1s.size;
const realisedCount = cxL1Count - orphans.length;
const pct = ((100 * realisedCount) / cxL1Count).toFixed(1);

console.log(`BC coverage: ${realisedCount} / ${cxL1Count} (${pct}%) Cross-Industry BC L1s have at least one realising BP.`);
if (orphans.length > 0) {
  console.log(`\nOrphan BC L1s (no BP claims to realize them):`);
  for (const o of orphans) console.log(`  ${o.id}  ${o.name}`);
}

// Oversaturation: BCs realised by an unusually high number of BP nodes.
const counts = [...bcToBps.entries()].map(([id, list]) => ({ id, count: list.length }));
counts.sort((a, b) => b.count - a.count);
const top = counts.slice(0, 10);
console.log(`\nTop 10 BCs by BP realisation count (sanity check):`);
for (const t of top) console.log(`  ${t.id.padEnd(8)} ${String(t.count).padStart(3)} BPs`);

if (strict && orphans.length > 0) process.exit(1);
