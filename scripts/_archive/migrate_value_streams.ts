#!/usr/bin/env tsx
/**
 * One-shot migration from the legacy value-stream shape to the schema-2 shape.
 *
 * Legacy:
 *   value_streams:
 *     - name: ...
 *       industries: [...]
 *       stages:
 *         - stage_order: 1
 *           stage_name: ...
 *           capability_id: BC-X      # singular
 *           industry_variant?: ...
 *           notes?: ...
 *
 * New:
 *   value_streams:
 *     - id: VS-10                    # sparse 10/20/30, alphabetical-by-name
 *       name: ...
 *       industries: [...]
 *       stages:
 *         - id: VS-10.10             # sparse 10/20/30, ordered by (stage_order, stage_name, industry_variant)
 *           stage_order: 1
 *           stage_name: ...
 *           capability_ids: [BC-X]   # plural array
 *           process_ids: []          # empty until APQC PCF import
 *           industry_variant?: ...
 *           notes?: ...
 *
 * Idempotent: detects if every stream already has an `id` and exits 0.
 *
 * Run once, commit the resulting _value-streams.yaml, then archive this
 * script under scripts/_archive/ in a follow-up PR.
 */
import YAML from "yaml";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { CATALOGUE_DIR } from "./lib/load.ts";

interface LegacyStage {
  stage_order: number;
  stage_name: string;
  capability_id: string;
  industries?: string[];
  industry_variant?: string;
  description?: string;
  notes?: string;
}

interface LegacyStream {
  id?: string;
  name: string;
  description?: string;
  industries: string[];
  stages: LegacyStage[];
}

interface NewStage {
  id: string;
  stage_order: number;
  stage_name: string;
  capability_ids: string[];
  process_ids: string[];
  industries?: string[];
  industry_variant?: string;
  description?: string;
  notes?: string;
}

interface NewStream {
  id: string;
  name: string;
  description?: string;
  industries: string[];
  stages: NewStage[];
}

const path = join(CATALOGUE_DIR, "_value-streams.yaml");
if (!existsSync(path)) {
  console.error("catalogue/_value-streams.yaml not found");
  process.exit(1);
}

const raw = readFileSync(path, "utf8");
const parsed = YAML.parse(raw) as { value_streams: LegacyStream[] };
const streams = parsed.value_streams ?? [];

if (streams.length > 0 && streams.every((s) => s.id)) {
  console.log(`✔ Already migrated: ${streams.length} stream(s) carry ids. No changes.`);
  process.exit(0);
}

// 1. Sort streams alphabetically by name → assign VS-10, VS-20, VS-30, ...
const sortedStreams = [...streams].sort((a, b) => a.name.localeCompare(b.name));
const newStreams: NewStream[] = sortedStreams.map((stream, sIdx) => {
  const streamId = `VS-${(sIdx + 1) * 10}`;

  // 2. Group rows by (stage_order, stage_name, industry_variant or '').
  //    Each group becomes one stage with capability_ids = unique list.
  //    Notes concatenated when distinct.
  type GroupKey = string;
  const keyOf = (s: LegacyStage): GroupKey =>
    `${s.stage_order}|${s.stage_name}|${s.industry_variant ?? ""}`;
  const groups = new Map<GroupKey, LegacyStage[]>();
  const order: GroupKey[] = [];
  for (const row of stream.stages ?? []) {
    const k = keyOf(row);
    if (!groups.has(k)) {
      groups.set(k, []);
      order.push(k);
    }
    groups.get(k)!.push(row);
  }

  // Sort groups by (stage_order, stage_name, industry_variant '' first).
  order.sort((aKey, bKey) => {
    const a = groups.get(aKey)![0];
    const b = groups.get(bKey)![0];
    if (a.stage_order !== b.stage_order) return a.stage_order - b.stage_order;
    if (a.stage_name !== b.stage_name) return a.stage_name.localeCompare(b.stage_name);
    const av = a.industry_variant ?? "";
    const bv = b.industry_variant ?? "";
    return av.localeCompare(bv);
  });

  const newStages: NewStage[] = order.map((k, gIdx) => {
    const rows = groups.get(k)!;
    const stageId = `${streamId}.${(gIdx + 1) * 10}`;
    const head = rows[0];
    // Unique capability_ids preserving first-seen order.
    const seenCaps = new Set<string>();
    const capability_ids: string[] = [];
    for (const r of rows) {
      if (!seenCaps.has(r.capability_id)) {
        seenCaps.add(r.capability_id);
        capability_ids.push(r.capability_id);
      }
    }
    // Notes: deduplicate, concatenate with '; '.
    const notesSet = new Set<string>();
    for (const r of rows) if (r.notes) notesSet.add(r.notes);
    const notes = notesSet.size > 0 ? Array.from(notesSet).join("; ") : undefined;
    // Description: first non-empty.
    const description = rows.map((r) => r.description).find((d) => d && d.length > 0);

    return {
      id: stageId,
      stage_order: head.stage_order,
      stage_name: head.stage_name,
      capability_ids,
      process_ids: [],
      ...(head.industries ? { industries: head.industries } : {}),
      ...(head.industry_variant ? { industry_variant: head.industry_variant } : {}),
      ...(description ? { description } : {}),
      ...(notes ? { notes } : {}),
    };
  });

  return {
    id: streamId,
    name: stream.name,
    ...(stream.description ? { description: stream.description } : {}),
    industries: stream.industries,
    stages: newStages,
  };
});

const preamble = `# Value Streams (orthogonal artefact, not part of the capability hierarchy).
# Each stream has a stable VS-<n> id (sparse 10/20/30 numbering); each stage
# has a stable VS-<n>.<m> id and links to L1 capabilities (\`capability_ids\`)
# and to business processes (\`process_ids\`) that realize the work. The site
# auto-expands an L1 to its descendants when filtering. Use 'notes' to capture
# sub-scope detail.
#
# Each stream declares an \`industries\` array using the canonical L1 industry
# vocabulary. \`Cross-Industry\`, when present, must stand alone.
`;

const out = preamble + YAML.stringify({ value_streams: newStreams }, { lineWidth: 0 });
writeFileSync(path, out, "utf8");

const totalStages = newStreams.reduce((acc, s) => acc + s.stages.length, 0);
console.log(`✔ Migrated ${newStreams.length} stream(s), ${totalStages} stage(s).`);
console.log(`  Stream ids: ${newStreams.map((s) => s.id).join(", ")}`);
