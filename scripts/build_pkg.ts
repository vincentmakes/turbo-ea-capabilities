#!/usr/bin/env tsx
/**
 * Populate the Python package's data directory from the YAML source.
 * Runs build_api.ts first (so dist/api/version.json drives both outputs),
 * then copies the runtime files. Translation data is copied additively under
 * data/i18n/<locale>.json and only when present.
 *
 * `data/**` is gitignored. Re-run before `python -m build`.
 */
import { execSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { REPO_ROOT } from "./lib/load.ts";

const DIST_API = join(REPO_ROOT, "dist", "api");
const PKG_DATA = join(
  REPO_ROOT,
  "packages",
  "py",
  "src",
  "turbo_ea_capabilities",
  "data"
);

if (!existsSync(join(DIST_API, "version.json"))) {
  console.log("dist/api not present; running build_api first.");
  execSync("npx tsx scripts/build_api.ts", { stdio: "inherit", cwd: REPO_ROOT });
}

mkdirSync(PKG_DATA, { recursive: true });

const filesToCopy = ["capabilities.json", "tree.json", "version.json"];
for (const f of filesToCopy) {
  const src = join(DIST_API, f);
  const dst = join(PKG_DATA, f);
  if (!existsSync(src)) {
    throw new Error(`Expected ${src} to exist after build_api`);
  }
  copyFileSync(src, dst);
}

// Optional: locales.json + per-locale i18n maps. build_api always emits
// locales.json (with at least 'en'); per-locale files only exist when
// catalogue/i18n/<locale>/ has sidecars.
const localesManifest = join(DIST_API, "locales.json");
if (existsSync(localesManifest)) {
  copyFileSync(localesManifest, join(PKG_DATA, "locales.json"));
}

const i18nSrc = join(DIST_API, "i18n");
const localeFiles: string[] = [];
if (existsSync(i18nSrc)) {
  const i18nDst = join(PKG_DATA, "i18n");
  mkdirSync(i18nDst, { recursive: true });
  for (const f of readdirSync(i18nSrc).filter((x) => x.endsWith(".json"))) {
    copyFileSync(join(i18nSrc, f), join(i18nDst, f));
    localeFiles.push(f);
  }
}

console.log(
  `✔ build_pkg: copied ${filesToCopy.join(", ")} → packages/py/src/turbo_ea_capabilities/data/`
);
if (localeFiles.length) {
  console.log(`  + locales: ${localeFiles.join(", ")}`);
}
