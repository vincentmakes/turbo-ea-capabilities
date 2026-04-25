#!/usr/bin/env tsx
/**
 * Add a new capability under an existing parent.
 *
 *   npm run cap:add -- --parent BC-2.1 --name "Forecast Reconciliation"
 *
 * Picks the next sibling id automatically (parent.id + .<n>).
 */
import YAML from "yaml";
import { existsSync } from "node:fs";
import { join } from "node:path";
import {
  CATALOGUE_DIR,
} from "../lib/load.ts";
import {
  compareIds,
  findNodeById,
  loadAllTrees,
  nextChildId,
  parseArgs,
  saveTree,
  type CliRawCapability,
} from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const parentId = args.parent;
const name = args.name;
if (!parentId || !name) {
  console.error("Usage: cap:add --parent <BC-id> --name '<Display Name>' [--description '...']");
  process.exit(2);
}

const { files } = loadAllTrees();
const fileEntry = files.find((f) => findNodeById(f.tree, parentId));
if (!fileEntry) {
  console.error(`Parent ${parentId} not found in any L1 file.`);
  process.exit(1);
}
if (!existsSync(join(CATALOGUE_DIR, fileEntry.name))) {
  console.error(`File ${fileEntry.name} missing on disk.`);
  process.exit(1);
}

const parentNode = findNodeById(fileEntry.tree, parentId)!;
if (parentNode.level >= 4) {
  console.error(
    `Cannot add child under ${parentId} (level=${parentNode.level}); max depth is L4.`
  );
  process.exit(1);
}
const newId = nextChildId(parentNode);
const newNode: CliRawCapability = {
  id: newId,
  name,
  level: parentNode.level + 1,
  ...(args.description ? { description: args.description } : {}),
  children: [],
};

// Mutate the YAML Document (preserves comments + ordering for siblings).
const doc = fileEntry.doc;
const visit = (yamlNode: YAML.YAMLMap, raw: CliRawCapability): boolean => {
  if (raw.id === parentId) {
    let childrenSeq = yamlNode.get("children") as YAML.YAMLSeq | null;
    if (!childrenSeq) {
      childrenSeq = doc.createNode([]) as YAML.YAMLSeq;
      yamlNode.set("children", childrenSeq);
    }
    childrenSeq.add(doc.createNode(newNode));
    // Re-sort siblings by id ascending so output is deterministic.
    const items = (childrenSeq.items as YAML.YAMLMap[]).slice();
    items.sort((a, b) => compareIds(String(a.get("id")), String(b.get("id"))));
    childrenSeq.items.length = 0;
    for (const it of items) childrenSeq.items.push(it);
    return true;
  }
  const childrenSeq = yamlNode.get("children") as YAML.YAMLSeq | null;
  if (!childrenSeq) return false;
  for (let i = 0; i < childrenSeq.items.length; i++) {
    const childYaml = childrenSeq.items[i] as YAML.YAMLMap;
    const childRaw = (raw.children ?? []).find(
      (c) => c.id === childYaml.get("id")
    );
    if (childRaw && visit(childYaml, childRaw)) return true;
  }
  return false;
};

if (!visit(doc.contents as YAML.YAMLMap, fileEntry.tree)) {
  console.error(`Failed to locate parent ${parentId} in document.`);
  process.exit(1);
}

saveTree(fileEntry.name, doc);
console.log(`✔ Added ${newId} '${name}' under ${parentId} in ${fileEntry.name}`);
