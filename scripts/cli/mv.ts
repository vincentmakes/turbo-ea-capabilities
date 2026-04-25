#!/usr/bin/env tsx
/**
 * Move a capability subtree under a new parent. The whole subtree is renumbered
 * to fit under the new parent. The old id is recorded in metadata.replaces so
 * callers can map historical references; if you want hard idempotency for
 * downstream consumers (e.g. Turbo EA), prefer deprecate + add new node.
 *
 *   npm run cap:mv -- --id BC-3.1.2 --new-parent BC-2.1
 */
import YAML from "yaml";
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
const id = args.id;
const newParent = args["new-parent"];
if (!id || !newParent) {
  console.error("Usage: cap:mv --id <BC-id> --new-parent <BC-id>");
  process.exit(2);
}

const { files } = loadAllTrees();
const sourceEntry = files.find((f) => findNodeById(f.tree, id));
const targetEntry = files.find((f) => findNodeById(f.tree, newParent));
if (!sourceEntry || !targetEntry) {
  console.error(`Could not locate source ${id} or target ${newParent}.`);
  process.exit(1);
}

const targetNode = findNodeById(targetEntry.tree, newParent)!;
if (targetNode.level >= 4) {
  console.error(`Target ${newParent} is at L${targetNode.level}; max depth is L4.`);
  process.exit(1);
}
const newId = nextChildId(targetNode);

// Detach from source -------------------------------------------------------
let detached: YAML.YAMLMap | null = null;
const detach = (yamlNode: YAML.YAMLMap): boolean => {
  const childrenSeq = yamlNode.get("children") as YAML.YAMLSeq | null;
  if (!childrenSeq) return false;
  for (let i = 0; i < childrenSeq.items.length; i++) {
    const child = childrenSeq.items[i] as YAML.YAMLMap;
    if (child.get("id") === id) {
      detached = child;
      childrenSeq.items.splice(i, 1);
      return true;
    }
    if (detach(child)) return true;
  }
  return false;
};

if (!detach(sourceEntry.doc.contents as YAML.YAMLMap)) {
  console.error(`Failed to detach ${id}`);
  process.exit(1);
}
if (!detached) {
  console.error(`Detached node was null for ${id}`);
  process.exit(1);
}
const detachedNode: YAML.YAMLMap = detached;

// Renumber detached subtree to the new id space ----------------------------
function renumber(node: YAML.YAMLMap, newNodeId: string, depth: number) {
  const oldId = String(node.get("id"));
  node.set("id", newNodeId);
  node.set("level", depth);
  // Track previous id so historical references can be migrated by tooling.
  let metadata = node.get("metadata") as YAML.YAMLMap | null;
  if (!metadata) {
    metadata = sourceEntry!.doc.createNode({}) as YAML.YAMLMap;
    node.set("metadata", metadata);
  }
  const replaces = (metadata.get("replaces") as string | undefined) ?? "";
  metadata.set("replaces", replaces ? `${replaces},${oldId}` : oldId);

  const childrenSeq = node.get("children") as YAML.YAMLSeq | null;
  if (!childrenSeq) return;
  const items = childrenSeq.items as YAML.YAMLMap[];
  items.sort((a, b) => compareIds(String(a.get("id")), String(b.get("id"))));
  items.forEach((child, idx) => {
    renumber(child, `${newNodeId}.${idx + 1}`, depth + 1);
  });
}
renumber(detachedNode, newId, targetNode.level + 1);

// Attach to target ---------------------------------------------------------
function attach(yamlNode: YAML.YAMLMap, parentId: string): boolean {
  if (yamlNode.get("id") === parentId) {
    let childrenSeq = yamlNode.get("children") as YAML.YAMLSeq | null;
    if (!childrenSeq) {
      childrenSeq = targetEntry!.doc.createNode([]) as YAML.YAMLSeq;
      yamlNode.set("children", childrenSeq);
    }
    childrenSeq.add(detachedNode);
    const items = childrenSeq.items as YAML.YAMLMap[];
    items.sort((a, b) => compareIds(String(a.get("id")), String(b.get("id"))));
    childrenSeq.items.length = 0;
    for (const it of items) childrenSeq.items.push(it);
    return true;
  }
  const childrenSeq = yamlNode.get("children") as YAML.YAMLSeq | null;
  if (!childrenSeq) return false;
  for (const child of childrenSeq.items as YAML.YAMLMap[]) {
    if (attach(child, parentId)) return true;
  }
  return false;
}

if (!attach(targetEntry.doc.contents as YAML.YAMLMap, newParent)) {
  console.error(`Failed to attach detached subtree under ${newParent}`);
  process.exit(1);
}

saveTree(sourceEntry.name, sourceEntry.doc);
if (sourceEntry.name !== targetEntry.name) saveTree(targetEntry.name, targetEntry.doc);

console.log(`✔ Moved ${id} → ${newId} under ${newParent}`);
console.log(`  Old id retained in metadata.replaces for traceability.`);
// Suppress unused import warning for CliRawCapability — kept for type clarity.
void ({} as CliRawCapability);
