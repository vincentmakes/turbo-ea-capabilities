#!/usr/bin/env tsx
/**
 * Stamp `source_hash` on every sidecar entry whose source can be resolved.
 *
 *   npm run i18n:stamp                  # all locales, all kinds
 *   npm run i18n:stamp -- --locale fr   # one locale only
 *   npm run i18n:stamp -- --kind business-process
 *   npm run i18n:stamp -- --check       # dry-run; exits non-zero if any entry would change
 *
 * Use after authoring or refreshing translations so lint can detect English
 * source drift on subsequent edits. Idempotent: re-running on an
 * up-to-date catalogue produces no diff.
 *
 * Source-of-truth rules:
 *   - kind: capability       → recompute from BC node fields
 *   - kind: business-process → recompute from BP node fields
 *   - kind: value-stream     → stream-level uses stream fields, stage-level
 *                              uses stage fields
 * Entries pointing at deleted source nodes are left untouched (lint will
 * flag them as orphans separately).
 */
import { readFileSync, writeFileSync } from "node:fs";
import YAML from "yaml";
import {
  flatten,
  flattenBP,
  loadAllBP1Files,
  loadAllL1Files,
  loadAllSidecars,
  loadValueStreams,
} from "../lib/load.ts";
import {
  hashCapabilityLikeSource,
  hashValueStreamSource,
  hashValueStreamStageSource,
} from "../lib/i18n_hash.ts";
import { parseArgs } from "./_shared.ts";

const args = parseArgs(process.argv.slice(2));
const localeFilter = args.locale && args.locale !== "true" ? args.locale : null;
const kindFilter = args.kind && args.kind !== "true" ? args.kind : null;
const dryRun = args.check === "true";

const capabilityById = new Map<string, ReturnType<typeof flatten>[number]>();
for (const { tree } of loadAllL1Files()) {
  for (const node of flatten(tree)) capabilityById.set(node.id, node);
}
const businessProcessById = new Map<string, ReturnType<typeof flattenBP>[number]>();
for (const { tree } of loadAllBP1Files()) {
  for (const node of flattenBP(tree)) businessProcessById.set(node.id, node);
}
const streams = loadValueStreams();
const streamById = new Map(streams.filter((s) => s.id).map((s) => [s.id, s] as const));
const stageById = new Map<string, (typeof streams)[number]["stages"][number]>();
for (const s of streams) {
  for (const st of s.stages ?? []) {
    if (st.id) stageById.set(st.id, st);
  }
}

let stamped = 0;
let cleared = 0;
let unchanged = 0;
let touched_files = 0;

for (const sidecar of loadAllSidecars()) {
  if (localeFilter && sidecar.locale !== localeFilter) continue;
  const kind = sidecar.data.kind ?? "capability";
  if (kindFilter && kind !== kindFilter) continue;

  const doc = YAML.parseDocument(readFileSync(sidecar.path, "utf8"));
  const entriesNode = doc.get("entries");
  if (!YAML.isMap(entriesNode)) continue;

  let changed = false;
  for (const id of Object.keys(sidecar.data.entries)) {
    const entry = entriesNode.get(id);
    if (!YAML.isMap(entry)) continue;

    let computed: string | null = null;
    if (kind === "capability") {
      const src = capabilityById.get(id);
      if (src) computed = hashCapabilityLikeSource(src);
    } else if (kind === "business-process") {
      const src = businessProcessById.get(id);
      if (src) computed = hashCapabilityLikeSource(src);
    } else if (kind === "value-stream") {
      const stream = streamById.get(id);
      if (stream) computed = hashValueStreamSource(stream);
      else {
        const stage = stageById.get(id);
        if (stage) computed = hashValueStreamStageSource(stage);
      }
    }
    if (computed === null) continue; // orphan — lint reports separately

    const stored = entry.get("source_hash");
    if (stored === computed) {
      unchanged++;
      continue;
    }
    if (stored === undefined) stamped++;
    else cleared++;
    entry.set("source_hash", computed);
    changed = true;
  }

  if (changed) {
    touched_files++;
    if (!dryRun) {
      writeFileSync(sidecar.path, doc.toString({ lineWidth: 0 }), "utf8");
    }
  }
}

const verb = dryRun ? "would stamp" : "stamped";
console.log(
  `${verb} ${stamped} new entries, refreshed ${cleared}, ${unchanged} already current, across ${touched_files} sidecar file(s).`
);
if (dryRun && touched_files > 0) process.exit(1);
