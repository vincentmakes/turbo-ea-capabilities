#!/usr/bin/env tsx
/**
 * One-off: delete the 13 Cross-Industry BP1 files (BP-10..BP-120, BP-370),
 * their entries in `processes/_index.yaml`, and their sidecar translations
 * across every BCP-47 locale directory under `catalogue/i18n/`. Used once
 * during the BC+VS regeneration sweep — never to be run again.
 *
 *   npx tsx scripts/cli/bp_wipe_cross_industry_oneoff.ts
 *
 * Lint will fail immediately afterward because every Cross-Industry VS
 * stage's `process_ids` now points at deleted nodes; that's expected and
 * resolved by Step 5 of the regeneration plan (bp:relink-vs).
 */
import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import { I18N_DIR, PROCESSES_DIR, listLocales } from "../lib/load.ts";

const TARGETS = [
  "BP1-acquire-construct-and-manage-assets.yaml",
  "BP1-deliver-services.yaml",
  "BP1-develop-and-manage-business-capabilities.yaml",
  "BP1-develop-and-manage-human-resources.yaml",
  "BP1-develop-and-manage-products-and-services.yaml",
  "BP1-develop-vision-and-strategy.yaml",
  "BP1-manage-customer-service.yaml",
  "BP1-manage-enterprise-risk-compliance-remediation-and-resiliency.yaml",
  "BP1-manage-external-relationships.yaml",
  "BP1-manage-financial-resources.yaml",
  "BP1-manage-information-technology-it.yaml",
  "BP1-manage-supply-chain-for-physical-products.yaml",
  "BP1-market-and-sell-products-and-services.yaml",
];

let bp1Removed = 0;
let sidecarsRemoved = 0;

for (const file of TARGETS) {
  const p = join(PROCESSES_DIR, file);
  if (existsSync(p)) {
    rmSync(p);
    bp1Removed++;
  }
}

for (const locale of listLocales()) {
  for (const file of TARGETS) {
    const p = join(I18N_DIR, locale, "processes", file);
    if (existsSync(p)) {
      rmSync(p);
      sidecarsRemoved++;
    }
  }
}

// Drop targeted entries from processes/_index.yaml.
const indexPath = join(PROCESSES_DIR, "_index.yaml");
const indexDoc = YAML.parseDocument(readFileSync(indexPath, "utf8"));
const filesNode = indexDoc.get("files");
let indexEntriesRemoved = 0;
if (YAML.isSeq(filesNode)) {
  const target = new Set(TARGETS);
  const kept = filesNode.items
    .map((item) => (YAML.isScalar(item) ? String(item.value) : String(item)))
    .filter((name) => {
      if (target.has(name)) {
        indexEntriesRemoved++;
        return false;
      }
      return true;
    });
  indexDoc.set("files", kept);
  writeFileSync(indexPath, indexDoc.toString({ lineWidth: 0 }), "utf8");
}

console.log(
  `Wiped ${bp1Removed} BP1 file(s), ${sidecarsRemoved} sidecar(s), ${indexEntriesRemoved} index entr(y/ies). ` +
    `Lint will now fail on broken VS process_ids; resolve via bp:relink-vs after regeneration.`
);
