#!/usr/bin/env tsx
// SPDX-License-Identifier: MIT
/**
 * i18n coverage check: report which (BP1 × locale) sidecar files are
 * missing and which locales are missing capability or value-stream
 * sidecars. Also dumps a manifest the operator can hand to
 * /translate-language one source at a time.
 *
 *   npx tsx scripts/cli/check_i18n_coverage.ts          # report only
 *   npx tsx scripts/cli/check_i18n_coverage.ts --strict # exit non-zero on any gap
 *
 * Output JSON manifest is written to scripts/cli/_data/i18n_gaps.json
 * unless --no-manifest is passed.
 */
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  CATALOGUE_DIR,
  I18N_DIR,
  listLocales,
  loadMacroCapabilities,
  readIndex,
  readProcessesIndex,
} from "../lib/load.ts";

const strict = process.argv.includes("--strict");
const writeManifest = !process.argv.includes("--no-manifest");

const capFiles = readIndex().files;
const bpFiles = readProcessesIndex().files;
const locales = listLocales();
const macroFileExists = existsSync(join(CATALOGUE_DIR, "_macro-capabilities.yaml"));
const macrosPresent = macroFileExists && loadMacroCapabilities().length > 0;

interface Gap {
  kind: "capability" | "business-process" | "value-stream" | "macro-capability";
  source: string;
  locale: string;
}
const gaps: Gap[] = [];

for (const locale of locales) {
  for (const f of capFiles) {
    if (!existsSync(join(I18N_DIR, locale, f))) gaps.push({ kind: "capability", source: f, locale });
  }
  for (const f of bpFiles) {
    if (!existsSync(join(I18N_DIR, locale, "processes", f))) gaps.push({ kind: "business-process", source: f, locale });
  }
  if (!existsSync(join(I18N_DIR, locale, "_value-streams.yaml"))) {
    gaps.push({ kind: "value-stream", source: "_value-streams.yaml", locale });
  }
  if (macrosPresent && !existsSync(join(I18N_DIR, locale, "_macro-capabilities.yaml"))) {
    gaps.push({ kind: "macro-capability", source: "_macro-capabilities.yaml", locale });
  }
}

const perLocale = capFiles.length + bpFiles.length + 1 + (macrosPresent ? 1 : 0);
const total = perLocale * locales.length;
const present = total - gaps.length;
const pct = total === 0 ? 0 : ((100 * present) / total).toFixed(1);

console.log(`i18n coverage: ${present} / ${total} (${pct}%) sidecar files present across ${locales.length} locale(s).`);

const byKind: Record<string, number> = {
  capability: 0,
  "business-process": 0,
  "value-stream": 0,
  "macro-capability": 0,
};
for (const g of gaps) byKind[g.kind]++;
for (const [k, n] of Object.entries(byKind)) {
  console.log(`  ${k.padEnd(18)} ${n} missing`);
}

if (gaps.length > 0) {
  const byBp = new Map<string, string[]>();
  for (const g of gaps.filter((g) => g.kind === "business-process")) {
    const list = byBp.get(g.source) ?? [];
    list.push(g.locale);
    byBp.set(g.source, list);
  }
  if (byBp.size > 0) {
    console.log(`\nBP1 sidecars missing in any locale (${byBp.size} BP1s):`);
    for (const [bp, ls] of byBp) console.log(`  ${bp}: ${ls.join(",")}`);
  }
}

if (writeManifest) {
  const dir = join(import.meta.dirname, "_data");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "i18n_gaps.json"), JSON.stringify(gaps, null, 2));
  console.log(`\nManifest written to scripts/cli/_data/i18n_gaps.json`);
  console.log(`Hand to /translate-language: one source per invocation, e.g.`);
  console.log(`  /translate-language fr "Order-to-Cash"`);
}

if (strict && gaps.length > 0) process.exit(1);
