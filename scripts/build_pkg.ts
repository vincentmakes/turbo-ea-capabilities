#!/usr/bin/env tsx
/**
 * Populate the Python package's data directory from the YAML source.
 * Runs build_api.ts first (so dist/api/version.json drives both outputs),
 * then copies the three files the runtime needs:
 *   capabilities.json
 *   tree.json
 *   version.json
 *
 * `data/*.json` is gitignored. Re-run before `python -m build`.
 */
import { execSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
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

console.log(
  `✔ build_pkg: copied ${filesToCopy.join(", ")} → packages/py/src/turbo_ea_capabilities/data/`
);
