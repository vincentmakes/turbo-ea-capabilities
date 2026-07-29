#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * One-off cleanup: fix APQC's slash-and-virgule names that read awkwardly
 * ("Produce/Assemble Product", "Service/solution", "Set/Develop Long-term
 * Enterprise Strategy", etc.). This is the second cleanup pass after the
 * Cross-Industry sweep — strictly renames where APQC's own punctuation is
 * the confusing element.
 */
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import { PROCESSES_DIR } from "../lib/load.ts";

// Map: BP id -> new name. ids stable; names edited.
const renames: Record<string, string> = {
  // Strategy
  "BP-10.20.30": "Set Long-Term Enterprise Strategy",
  // Products and services
  "BP-20.20.20": "Generate New Product and Service Concepts",
  "BP-20.20.30": "Define Product and Service Development Requirements",
  // Sales
  "BP-30.50.10": "Manage Leads and Opportunities",
  // Supply chain
  "BP-40.30.20": "Produce and Assemble Product",
  // IT services
  "BP-80.50.10": "Develop Service and Integration Strategy",
  "BP-80.50.20": "Manage Service and Solution Lifecycle",
  "BP-80.50.30": "Develop and Manage Service and Solution Architecture",
  "BP-80.60.10": "Develop and Manage Deployment Strategy",
  // Finance — critical for the user's "Credit Check" example
  "BP-90.20.10": "Perform Customer Credit Check",
  "BP-90.20.50": "Manage and Process Adjustments and Deductions",
  "BP-90.70.60": "Manage Financial Fraud and Disputes",
  "BP-90.100.30": "Monitor and Hedge Currency Exposure",
  // Risk and compliance
  "BP-110.30.30": "Identify and Dedicate Resources",
  // External
  "BP-120.40.80": "Provide Legal Advice and Counsel",
  "BP-120.40.90": "Negotiate and Document Agreements and Contracts",
};

let renamed = 0;

function walk(node: unknown) {
  if (!node || typeof node !== "object") return;
  if (YAML.isMap(node)) {
    const id = node.get("id");
    if (typeof id === "string" && id in renames) {
      node.set("name", renames[id]);
      renamed++;
    }
    const children = node.get("children");
    if (YAML.isSeq(children)) {
      for (const c of children.items) walk(c);
    }
  }
}

const files = readdirSync(PROCESSES_DIR).filter(
  (f) => f.startsWith("BP1-") && f.endsWith(".yaml")
);
for (const f of files) {
  const path = join(PROCESSES_DIR, f);
  const before = readFileSync(path, "utf8");
  const doc = YAML.parseDocument(before);
  const tally = renamed;
  walk(doc.contents);
  if (renamed > tally) {
    writeFileSync(path, doc.toString({ lineWidth: 0 }), "utf8");
  }
}

console.log(`Renamed ${renamed} of ${Object.keys(renames).length} targeted nodes.`);
