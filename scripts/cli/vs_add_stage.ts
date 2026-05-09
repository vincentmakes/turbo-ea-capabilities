#!/usr/bin/env tsx
/**
 * Add a stage to an existing value stream.
 *
 *   npm run vs:add-stage -- --stream VS-30 --name "Quote Generation" --capabilities BC-100
 *   npm run vs:add-stage -- --stream VS-30 --name "Fulfilment" --capabilities BC-100,BC-200 --processes BP-10.10
 *
 * Picks the next sparse stage id (parent.10/20/30...) and the next stage_order.
 */
import YAML from "yaml";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { CATALOGUE_DIR } from "../lib/load.ts";
import { parseArgs } from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const streamId = args.stream;
const stageName = args.name;
const capsArg = args.capabilities;
if (!streamId || !stageName || !capsArg) {
  console.error(
    "Usage: vs:add-stage --stream <VS-id> --name '<Stage Name>' --capabilities <BC-id[,BC-id,...]> " +
      "[--processes <BP-id[,BP-id,...]>] [--industry-variant '...'] [--notes '...']"
  );
  process.exit(2);
}
const capabilityIds = capsArg.split(",").map((s) => s.trim()).filter(Boolean);
const processIds = (args.processes ?? "")
  .split(",")
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

const stream = (streamsSeq.items as YAML.YAMLMap[]).find(
  (s) => s.get("id") === streamId
);
if (!stream) {
  console.error(`Stream ${streamId} not found.`);
  process.exit(1);
}

let stagesSeq = stream.get("stages") as YAML.YAMLSeq | null;
if (!stagesSeq) {
  stagesSeq = doc.createNode([]) as YAML.YAMLSeq;
  stream.set("stages", stagesSeq);
}
const stageItems = stagesSeq.items as YAML.YAMLMap[];

const usedNumbers: number[] = [];
let maxOrder = 0;
for (const it of stageItems) {
  const sid = String(it.get("id") ?? "");
  const m = sid.match(/^VS-\d+\.(\d+)$/);
  if (m) usedNumbers.push(Number(m[1]));
  const order = Number(it.get("stage_order") ?? 0);
  if (Number.isFinite(order)) maxOrder = Math.max(maxOrder, order);
}
const nextN = usedNumbers.length === 0 ? 10 : Math.max(...usedNumbers) + 10;
const newId = `${streamId}.${nextN}`;
const stageOrder = maxOrder + 1;

const newStage = {
  id: newId,
  stage_order: stageOrder,
  stage_name: stageName,
  capability_ids: capabilityIds,
  process_ids: processIds,
  ...(args["industry-variant"] ? { industry_variant: args["industry-variant"] } : {}),
  ...(args.notes ? { notes: args.notes } : {}),
};
stagesSeq.add(doc.createNode(newStage));

writeFileSync(path, doc.toString({ lineWidth: 0 }), "utf8");
console.log(`✔ Added stage ${newId} '${stageName}' (order ${stageOrder}) to ${streamId}`);
