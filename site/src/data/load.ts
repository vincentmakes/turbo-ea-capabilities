// SPDX-License-Identifier: MIT
/**
 * Build-time data loader: reads the JSON artefacts produced by
 * `scripts/build_api.ts`. The Astro site fails fast at build time if these
 * files are missing - run `npm run build:api` first (the workspace `npm run
 * build` does this automatically).
 */
import type { FlatCapability, FlatBusinessProcess, FrameworkRef, MacroCapability } from "../../../scripts/lib/load.ts";

import flatJson from "@catalogue-data/capabilities.json" with { type: "json" };
import treeJson from "@catalogue-data/tree.json" with { type: "json" };
import versionJson from "@catalogue-data/version.json" with { type: "json" };
import valueStreamsJson from "@catalogue-data/value-streams.json" with { type: "json" };
import bpFlatJson from "@catalogue-data/business-processes.json" with { type: "json" };
import bpTreeJson from "@catalogue-data/bp-tree.json" with { type: "json" };
import macrosJson from "@catalogue-data/macro-capabilities.json" with { type: "json" };

export interface NestedCapability extends Omit<FlatCapability, "children"> {
  children: NestedCapability[];
}

export interface NestedBusinessProcess extends Omit<FlatBusinessProcess, "children"> {
  children: NestedBusinessProcess[];
}

export interface VersionMeta {
  catalogue_version: string;
  schema_version: number;
  generated_at: string;
  node_count: number;
  process_count?: number;
  commit?: string;
  license?: string;
  code_license?: string;
  license_url?: string;
  attribution?: string;
}

export interface ValueStreamStage {
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

export interface ValueStream {
  id: string;
  name: string;
  description?: string;
  industries: string[];
  deprecated?: boolean;
  deprecation_reason?: string;
  successor_id?: string;
  stages: ValueStreamStage[];
}

export type { FrameworkRef, MacroCapability };

export const flat: FlatCapability[] = flatJson as unknown as FlatCapability[];
export const tree: NestedCapability[] = treeJson as unknown as NestedCapability[];
export const version: VersionMeta = versionJson as unknown as VersionMeta;
export const valueStreams: ValueStream[] =
  valueStreamsJson as unknown as ValueStream[];
export const bpFlat: FlatBusinessProcess[] =
  bpFlatJson as unknown as FlatBusinessProcess[];
export const bpTree: NestedBusinessProcess[] =
  bpTreeJson as unknown as NestedBusinessProcess[];
export const macros: MacroCapability[] =
  macrosJson as unknown as MacroCapability[];

const byId = new Map<string, FlatCapability>();
for (const c of flat) byId.set(c.id, c);

const bpById = new Map<string, FlatBusinessProcess>();
for (const b of bpFlat) bpById.set(b.id, b);

const vsById = new Map<string, ValueStream>();
for (const s of valueStreams) vsById.set(s.id, s);

const stageById = new Map<string, { stream: ValueStream; stage: ValueStreamStage }>();
for (const s of valueStreams) {
  for (const stage of s.stages ?? []) {
    stageById.set(stage.id, { stream: s, stage });
  }
}

const macroById = new Map<string, MacroCapability>();
for (const m of macros) macroById.set(m.id, m);

export function getById(id: string): FlatCapability | undefined {
  return byId.get(id);
}

export function getBpById(id: string): FlatBusinessProcess | undefined {
  return bpById.get(id);
}

export function getVsById(id: string): ValueStream | undefined {
  return vsById.get(id);
}

export function getMacroById(id: string): MacroCapability | undefined {
  return macroById.get(id);
}

export function getStageById(
  stageId: string
): { stream: ValueStream; stage: ValueStreamStage } | undefined {
  return stageById.get(stageId);
}

export function getAncestors(id: string): FlatCapability[] {
  const chain: FlatCapability[] = [];
  let cursor = byId.get(id);
  while (cursor?.parent_id) {
    const parent = byId.get(cursor.parent_id);
    if (!parent) break;
    chain.push(parent);
    cursor = parent;
  }
  return chain.reverse();
}

export function getBpAncestors(id: string): FlatBusinessProcess[] {
  const chain: FlatBusinessProcess[] = [];
  let cursor = bpById.get(id);
  while (cursor?.parent_id) {
    const parent = bpById.get(cursor.parent_id);
    if (!parent) break;
    chain.push(parent);
    cursor = parent;
  }
  return chain.reverse();
}

export function l1Slug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function l1List(): { slug: string; root: NestedCapability }[] {
  return tree.map((root) => ({ slug: l1Slug(root.name), root }));
}

export function bp1List(): { slug: string; root: NestedBusinessProcess }[] {
  return bpTree.map((root) => ({ slug: l1Slug(root.name), root }));
}

export function findSubtree(id: string): NestedCapability | undefined {
  function walk(node: NestedCapability): NestedCapability | undefined {
    if (node.id === id) return node;
    for (const c of node.children ?? []) {
      const hit = walk(c);
      if (hit) return hit;
    }
    return undefined;
  }
  for (const root of tree) {
    const hit = walk(root);
    if (hit) return hit;
  }
  return undefined;
}

export function findBpSubtree(id: string): NestedBusinessProcess | undefined {
  function walk(node: NestedBusinessProcess): NestedBusinessProcess | undefined {
    if (node.id === id) return node;
    for (const c of node.children ?? []) {
      const hit = walk(c);
      if (hit) return hit;
    }
    return undefined;
  }
  for (const root of bpTree) {
    const hit = walk(root);
    if (hit) return hit;
  }
  return undefined;
}

// ---------------------------------------------------------------------------
// Macro-layered capability view
//
// When the catalogue ships a `_macro-capabilities.yaml`, the site renders the
// macros as the top tier (visually replacing BC L1 at the executive layer):
// each MC- becomes a synthetic level-1 node, the BC L1s it claims slide down
// to level 2, their L2s to L3, their L3s to L4. The raw `flat` / `tree`
// arrays — and every downstream API consumer — keep BC L1 at level=1; the
// shift is purely a presentation layer for the in-browser catalogue.
//
// Industry-specific L1s (no `macro_id`) are unaffected: they stay at level 1
// with `parent_id: null` so they continue to render as L1 cards grouped by
// their industry alongside the cross-industry macros.
// ---------------------------------------------------------------------------

/** Synthesize a `FlatCapability`-shaped node for a macro, suitable for
 *  passing into the existing CatalogueBrowser at the L1 visual tier. */
function macroAsFlatCapability(macro: MacroCapability): FlatCapability {
  return {
    id: macro.id,
    name: macro.name,
    level: 1,
    parent_id: null,
    children: [...macro.capability_ids],
    description: macro.description,
    industry: macro.industry,
    references: macro.references,
    in_scope: macro.in_scope,
    out_of_scope: macro.out_of_scope,
    deprecated: macro.deprecated,
    deprecation_reason: macro.deprecation_reason,
    successor_id: macro.successor_id,
    metadata: macro.metadata,
    // BCs use `realizes_processes` / `value_stream_stages` reverse indices.
    // Macros don't participate in BP/VS graph; leave those unset.
  } as FlatCapability;
}

/** Return a flat array where:
 *   - each macro becomes a synthetic L1 node (its capability_ids are children);
 *   - every claimed BC L1 has level += 1 and `parent_id` re-pointed at its macro;
 *   - every descendant of a claimed L1 has level += 1 (parent_id unchanged);
 *   - unclaimed BC L1s (industry-specific) are returned unchanged.
 *  Pass directly into <CatalogueBrowser data={...} /> to render the macro tier.
 */
export function buildMacroLayeredFlat(
  source: FlatCapability[] = flat,
  macroSet: MacroCapability[] = macros,
): FlatCapability[] {
  if (macroSet.length === 0) return source;

  const macroByL1 = new Map<string, MacroCapability>();
  for (const m of macroSet) {
    for (const cid of m.capability_ids ?? []) macroByL1.set(cid, m);
  }
  // BC ids belonging to a macro'd L1 subtree need to shift down one level.
  const claimedL1 = new Set(macroByL1.keys());
  const inMacroSubtree = (node: FlatCapability): boolean => {
    const l1 = node.id.split(".")[0];
    return claimedL1.has(l1);
  };

  const out: FlatCapability[] = [];
  // 1. Macros first, level 1.
  for (const m of macroSet) out.push(macroAsFlatCapability(m));
  // 2. Then every existing capability, shifted iff in a macro'd subtree.
  for (const c of source) {
    if (!inMacroSubtree(c)) {
      out.push(c);
      continue;
    }
    if (c.level === 1) {
      const macro = macroByL1.get(c.id)!;
      out.push({ ...c, level: 2, parent_id: macro.id });
    } else {
      out.push({ ...c, level: c.level + 1 });
    }
  }
  return out;
}

/** Memoized convenience: the full catalogue with macro tier applied. */
export const flatWithMacros: FlatCapability[] = buildMacroLayeredFlat();

