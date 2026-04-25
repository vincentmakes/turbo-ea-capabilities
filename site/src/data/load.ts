/**
 * Build-time data loader: reads the JSON artefacts produced by
 * `scripts/build_api.ts`. The Astro site fails fast at build time if these
 * files are missing - run `npm run build:api` first (the workspace `npm run
 * build` does this automatically).
 */
import type { FlatCapability } from "../../../scripts/lib/load.ts";

import flatJson from "@catalogue-data/capabilities.json" with { type: "json" };
import treeJson from "@catalogue-data/tree.json" with { type: "json" };
import versionJson from "@catalogue-data/version.json" with { type: "json" };
import valueStreamsJson from "@catalogue-data/value-streams.json" with { type: "json" };

export interface NestedCapability extends Omit<FlatCapability, "children"> {
  children: NestedCapability[];
}

export interface VersionMeta {
  catalogue_version: string;
  schema_version: number;
  generated_at: string;
  node_count: number;
  commit?: string;
}

export interface ValueStreamStage {
  stage_order: number;
  stage_name: string;
  capability_id: string;
  industry_variant?: string;
  notes?: string;
}

export interface ValueStream {
  name: string;
  stages: ValueStreamStage[];
}

export const flat: FlatCapability[] = flatJson as unknown as FlatCapability[];
export const tree: NestedCapability[] = treeJson as unknown as NestedCapability[];
export const version: VersionMeta = versionJson as unknown as VersionMeta;
export const valueStreams: ValueStream[] =
  valueStreamsJson as unknown as ValueStream[];

const byId = new Map<string, FlatCapability>();
for (const c of flat) byId.set(c.id, c);

export function getById(id: string): FlatCapability | undefined {
  return byId.get(id);
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

export function l1Slug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function l1List(): { slug: string; root: NestedCapability }[] {
  return tree.map((root) => ({ slug: l1Slug(root.name), root }));
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
