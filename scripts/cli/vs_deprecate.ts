#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * Mark a value stream deprecated.
 *
 *   npm run vs:deprecate -- --id VS-30 --successor VS-40 --reason "Merged into VS-40"
 */
import YAML from "yaml";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { CATALOGUE_DIR } from "../lib/load.ts";
import { parseArgs } from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const id = args.id;
const reason = args.reason;
if (!id || !reason) {
  console.error("Usage: vs:deprecate --id <VS-id> --reason '<text>' [--successor <VS-id>]");
  process.exit(2);
}

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

const stream = (streamsSeq.items as YAML.YAMLMap[]).find((s) => s.get("id") === id);
if (!stream) {
  console.error(`Stream ${id} not found.`);
  process.exit(1);
}

stream.set("deprecated", true);
stream.set("deprecation_reason", reason);
if (args.successor) stream.set("successor_id", args.successor);

writeFileSync(path, doc.toString({ lineWidth: 0 }), "utf8");
console.log(`✔ Deprecated value stream ${id}`);
