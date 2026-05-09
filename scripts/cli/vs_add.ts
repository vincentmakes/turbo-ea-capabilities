#!/usr/bin/env tsx
/**
 * Add a new value stream to catalogue/_value-streams.yaml.
 *
 *   npm run vs:add -- --name "Quote-to-Cash" --industries Cross-Industry
 *   npm run vs:add -- --name "Claim-to-Payment" --industries "Insurance" --description "FNOL → settlement."
 *
 * Picks the next sparse VS-N0 id (10/20/30...).
 */
import YAML from "yaml";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { CATALOGUE_DIR } from "../lib/load.ts";
import { parseArgs } from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const name = args.name;
const industriesArg = args.industries;
if (!name || !industriesArg) {
  console.error(
    "Usage: vs:add --name '<Stream Name>' --industries '<A;B>' [--description '...']"
  );
  process.exit(2);
}
const industries = industriesArg
  .split(/[;,]/)
  .map((s) => s.trim())
  .filter(Boolean);

const path = join(CATALOGUE_DIR, "_value-streams.yaml");
if (!existsSync(path)) {
  console.error("catalogue/_value-streams.yaml not found");
  process.exit(1);
}
const doc = YAML.parseDocument(readFileSync(path, "utf8"));
const streamsSeq = doc.get("value_streams") as YAML.YAMLSeq | null;
if (!streamsSeq) {
  console.error("_value-streams.yaml is missing the 'value_streams' sequence");
  process.exit(1);
}

// Find next sparse id (max + 10, or 10 if empty).
const usedNumbers: number[] = [];
for (const item of streamsSeq.items as YAML.YAMLMap[]) {
  const id = String(item.get("id") ?? "");
  const m = id.match(/^VS-(\d+)$/);
  if (m) usedNumbers.push(Number(m[1]));
}
const nextN = usedNumbers.length === 0 ? 10 : Math.max(...usedNumbers) + 10;
const newId = `VS-${nextN}`;

const newStream = {
  id: newId,
  name,
  industries,
  ...(args.description ? { description: args.description } : {}),
  stages: [],
};
streamsSeq.add(doc.createNode(newStream));

writeFileSync(path, doc.toString({ lineWidth: 0 }), "utf8");
console.log(`✔ Added value stream ${newId} '${name}' (${industries.join(", ")})`);
console.log(`  Next: 'npm run vs:add-stage -- --stream ${newId} --name <stage> --capabilities <BC-id>'`);
