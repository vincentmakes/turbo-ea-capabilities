#!/usr/bin/env tsx
/**
 * Mark a capability deprecated.
 *
 *   npm run cap:deprecate -- --id BC-3.1.2 --successor BC-3.1.1 --reason "Merged into BC-3.1.1"
 */
import YAML from "yaml";
import {
  findNodeById,
  loadAllTrees,
  parseArgs,
  saveTree,
} from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const id = args.id;
const reason = args.reason;
if (!id || !reason) {
  console.error("Usage: cap:deprecate --id <BC-id> --reason '<text>' [--successor <BC-id>]");
  process.exit(2);
}

const { files } = loadAllTrees();
const fileEntry = files.find((f) => findNodeById(f.tree, id));
if (!fileEntry) {
  console.error(`Id ${id} not found.`);
  process.exit(1);
}

const visit = (yamlNode: YAML.YAMLMap): boolean => {
  if (yamlNode.get("id") === id) {
    yamlNode.set("deprecated", true);
    yamlNode.set("deprecation_reason", reason);
    if (args.successor) yamlNode.set("successor_id", args.successor);
    return true;
  }
  const childrenSeq = yamlNode.get("children") as YAML.YAMLSeq | null;
  if (!childrenSeq) return false;
  for (const child of childrenSeq.items as YAML.YAMLMap[]) {
    if (visit(child)) return true;
  }
  return false;
};

if (!visit(fileEntry.doc.contents as YAML.YAMLMap)) {
  console.error(`Failed to locate ${id} in document.`);
  process.exit(1);
}

saveTree(fileEntry.name, fileEntry.doc);
console.log(`✔ Deprecated ${id} in ${fileEntry.name}`);
