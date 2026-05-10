#!/usr/bin/env tsx
/**
 * Stamp `source_hash` on every sidecar entry whose source can be resolved.
 *
 *   npm run i18n:stamp                  # all locales, all kinds
 *   npm run i18n:stamp -- --locale fr   # one locale only
 *   npm run i18n:stamp -- --kind business-process
 *   npm run i18n:stamp -- --check       # dry-run; exits non-zero if any entry would change
 *   npm run i18n:stamp -- --clear-stale # remove source_hash from stale entries
 *                                       # (translation pending — /translate-language will refresh)
 *   npm run i18n:stamp -- --source BP1-foo.yaml   # restrict to one source
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
 *
 * --clear-stale: when an entry's stored hash no longer matches the source,
 * remove the source_hash key entirely (instead of refreshing it). This
 * is the right move during a renaming sweep where translations are about
 * to be retranslated and re-stamped in a follow-up PR — clearing keeps
 * lint green without papering over actual translation drift.
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
const sourceFilter = args.source && args.source !== "true" ? args.source : null;
const dryRun = args.check === "true";
const clearStale = args["clear-stale"] === "true";

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
let refreshed = 0;
let removed = 0;
let unchanged = 0;
let touched_files = 0;

for (const sidecar of loadAllSidecars()) {
  if (localeFilter && sidecar.locale !== localeFilter) continue;
  const kind = sidecar.data.kind ?? "capability";
  if (kindFilter && kind !== kindFilter) continue;
  if (sourceFilter && sidecar.data.source !== sourceFilter) continue;

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
    if (clearStale) {
      if (stored === undefined) {
        unchanged++;
        continue;
      }
      entry.delete("source_hash");
      removed++;
      changed = true;
    } else {
      if (stored === undefined) stamped++;
      else refreshed++;
      entry.set("source_hash", computed);
      changed = true;
    }
  }

  if (changed) {
    touched_files++;
    if (!dryRun) {
      writeFileSync(sidecar.path, doc.toString({ lineWidth: 0 }), "utf8");
    }
  }
}

const verb = dryRun ? "would" : "did";
const action = clearStale ? "clear" : "stamp";
if (clearStale) {
  console.log(
    `${verb} ${action} ${removed} stale entries, ${unchanged} unaffected, across ${touched_files} sidecar file(s).`
  );
} else {
  console.log(
    `${verb} ${action} ${stamped} new entries, refreshed ${refreshed}, ${unchanged} already current, across ${touched_files} sidecar file(s).`
  );
}
if (dryRun && touched_files > 0) process.exit(1);
