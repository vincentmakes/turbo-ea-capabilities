#!/usr/bin/env tsx
/**
 * Create a new BP1 file (root of a process category) and register it in
 * `catalogue/processes/_index.yaml`. Used by /generate-process when
 * synthesising a BP tree from a Value Stream.
 *
 *   npm run bp:bootstrap-bp1 -- --id BP-1000 --name "Order-to-Cash" \
 *     --industry Cross-Industry \
 *     --realizes BC-410,BC-420,BC-440 \
 *     --description "End-to-end revenue cycle..."
 *
 * Errors if the id is already taken or the slug collides with an
 * existing BP1 file. The created file has empty `children: []`; populate
 * with `npm run bp:add` once the root exists.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import {
  BP_ID_REGEX,
  PROCESSES_DIR,
  loadAllBP1Files,
  readProcessesIndex,
} from "../lib/load.ts";
import { parseArgs } from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const id = args.id;
const name = args.name;
const industry = args.industry ?? "Cross-Industry";
const realizesArg = args.realizes && args.realizes !== "true" ? args.realizes : "";
const description = args.description && args.description !== "true" ? args.description : undefined;

if (!id || !name) {
  console.error(
    "Usage: bp:bootstrap-bp1 --id BP-N0 --name '<VS Name>' [--industry <name>] " +
      "[--realizes BC-A,BC-B] [--description '<one-sentence summary>']"
  );
  process.exit(2);
}

if (!BP_ID_REGEX.test(id) || id.split(".").length !== 1) {
  console.error(`Id '${id}' must be a BP1 root (e.g. BP-1000), not a sub-id.`);
  process.exit(1);
}

const numericPart = Number(id.replace("BP-", ""));
if (!Number.isFinite(numericPart) || numericPart % 10 !== 0) {
  console.error(
    `Id '${id}' must follow sparse 10/20/30 numbering at the L1 root (e.g. BP-1000, BP-1010, BP-1020).`
  );
  process.exit(1);
}

const slug = name
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-|-$/g, "");
const filename = `BP1-${slug}.yaml`;
const filePath = join(PROCESSES_DIR, filename);

const existingTrees = loadAllBP1Files();
const idTaken = existingTrees.find((t) => t.tree.id === id);
if (idTaken) {
  console.error(`Id '${id}' already used by ${idTaken.name}.`);
  process.exit(1);
}
if (existsSync(filePath)) {
  console.error(`File ${filename} already exists at ${filePath}.`);
  process.exit(1);
}

const realizes = realizesArg
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

const doc = new YAML.Document();
const root: Record<string, unknown> = {
  id,
  name,
  level: 1,
  industry,
};
if (description) root.description = description;
if (realizes.length > 0) root.realizes_capability_ids = realizes;
root.children = [];
doc.contents = doc.createNode(root);

writeFileSync(filePath, doc.toString({ lineWidth: 0 }), "utf8");

// Register in _index.yaml (sorted ascending).
const index = readProcessesIndex();
if (!index.files.includes(filename)) {
  const next = [...index.files, filename].sort((a, b) => a.localeCompare(b));
  const indexPath = join(PROCESSES_DIR, "_index.yaml");
  const indexSource = readFileSync(indexPath, "utf8");
  const indexDoc = YAML.parseDocument(indexSource);
  indexDoc.set("files", next);
  writeFileSync(indexPath, indexDoc.toString({ lineWidth: 0 }), "utf8");
}

console.log(`Created ${filename} for ${id} '${name}' (${realizes.length} realises, industry=${industry}).`);
