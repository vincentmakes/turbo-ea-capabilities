#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * One-off cleanup: strip `aliases` from every node in every Cross-Industry
 * BP1 file. Use after Phase 2 renaming concludes; leaves names, descriptions,
 * framework_refs, and realizes_capability_ids untouched.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import { PROCESSES_DIR } from "../lib/load.ts";

const files = [
  "BP1-develop-vision-and-strategy.yaml",
  "BP1-develop-and-manage-products-and-services.yaml",
  "BP1-market-and-sell-products-and-services.yaml",
  "BP1-manage-supply-chain-for-physical-products.yaml",
  "BP1-deliver-services.yaml",
  "BP1-manage-customer-service.yaml",
  "BP1-develop-and-manage-human-resources.yaml",
  "BP1-manage-information-technology-it.yaml",
  "BP1-manage-financial-resources.yaml",
  "BP1-acquire-construct-and-manage-assets.yaml",
  "BP1-manage-enterprise-risk-compliance-remediation-and-resiliency.yaml",
  "BP1-manage-external-relationships.yaml",
  "BP1-develop-and-manage-business-capabilities.yaml",
];

let stripped = 0;

function walk(node: unknown) {
  if (!node || typeof node !== "object") return;
  if (YAML.isMap(node)) {
    if (node.has("aliases")) {
      node.delete("aliases");
      stripped++;
    }
    const children = node.get("children");
    if (YAML.isSeq(children)) {
      for (const c of children.items) walk(c);
    }
  }
}

for (const f of files) {
  const path = join(PROCESSES_DIR, f);
  const doc = YAML.parseDocument(readFileSync(path, "utf8"));
  walk(doc.contents);
  writeFileSync(path, doc.toString({ lineWidth: 0 }), "utf8");
}

console.log(`Stripped ${stripped} aliases blocks across ${files.length} BP1 files.`);
