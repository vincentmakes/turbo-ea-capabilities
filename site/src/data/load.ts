/**
 * Build-time data loader: reads the JSON artefacts produced by
 * `scripts/build_api.ts`. The Astro site fails fast at build time if these
 * files are missing - run `npm run build:api` first (the workspace `npm run
 * build` does this automatically).
 */
import type { FlatCapability, FlatBusinessProcess, FrameworkRef } from "../../../scripts/lib/load.ts";

import flatJson from "@catalogue-data/capabilities.json" with { type: "json" };
import treeJson from "@catalogue-data/tree.json" with { type: "json" };
import versionJson from "@catalogue-data/version.json" with { type: "json" };
import valueStreamsJson from "@catalogue-data/value-streams.json" with { type: "json" };
import bpFlatJson from "@catalogue-data/business-processes.json" with { type: "json" };
import bpTreeJson from "@catalogue-data/bp-tree.json" with { type: "json" };

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

export type { FrameworkRef };

export const flat: FlatCapability[] = flatJson as unknown as FlatCapability[];
export const tree: NestedCapability[] = treeJson as unknown as NestedCapability[];
export const version: VersionMeta = versionJson as unknown as VersionMeta;
export const valueStreams: ValueStream[] =
  valueStreamsJson as unknown as ValueStream[];
export const bpFlat: FlatBusinessProcess[] =
  bpFlatJson as unknown as FlatBusinessProcess[];
export const bpTree: NestedBusinessProcess[] =
  bpTreeJson as unknown as NestedBusinessProcess[];

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

export function getById(id: string): FlatCapability | undefined {
  return byId.get(id);
}

export function getBpById(id: string): FlatBusinessProcess | undefined {
  return bpById.get(id);
}

export function getVsById(id: string): ValueStream | undefined {
  return vsById.get(id);
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
