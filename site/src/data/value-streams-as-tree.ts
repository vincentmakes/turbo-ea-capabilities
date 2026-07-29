// SPDX-License-Identifier: MIT
/**
 * Adapter: flatten the value-stream catalogue into the same `FlatNode` shape
 * the generic `CatalogBrowser` consumes. Each stream becomes an L1 node.
 *
 * Stages with the same `(stage_order, stage_name)` are merged into a single
 * L2 node — the YAML lists them once per industry variant, but for the tree
 * UI we collapse them so the user sees one row per logical stage. Variant
 * notes and cross-links are aggregated.
 */
import type { FlatNode, ValueStream, ValueStreamStage } from "../components/catalog/types";

interface StageGroup {
  /** Canonical id for the merged stage — the smallest VS-XX.YY id of the
   *  rows in the group, so sort order matches the YAML. */
  id: string;
  stage_order: number;
  stage_name: string;
  rows: ValueStreamStage[];
}

function groupStages(stream: ValueStream): StageGroup[] {
  const sorted = (stream.stages ?? []).slice().sort((a, b) => {
    if (a.stage_order !== b.stage_order) return a.stage_order - b.stage_order;
    return a.stage_name.localeCompare(b.stage_name);
  });
  const groups = new Map<string, StageGroup>();
  for (const row of sorted) {
    const key = `${row.stage_order}::${row.stage_name}`;
    let g = groups.get(key);
    if (!g) {
      g = { id: row.id, stage_order: row.stage_order, stage_name: row.stage_name, rows: [] };
      groups.set(key, g);
    }
    g.rows.push(row);
  }
  return Array.from(groups.values());
}

function uniq(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const v of values) {
    if (!seen.has(v)) {
      seen.add(v);
      out.push(v);
    }
  }
  return out;
}

function describeGroup(group: StageGroup): string | undefined {
  const lines: string[] = [];
  for (const row of group.rows) {
    const variant = row.industry_variant ?? "Cross-Industry";
    const note = row.notes ?? row.description;
    if (note) lines.push(`${variant}: ${note}`);
    else lines.push(variant);
  }
  return lines.length > 0 ? lines.join(" • ") : undefined;
}

export function valueStreamsAsTree(streams: ValueStream[]): FlatNode[] {
  const out: FlatNode[] = [];
  for (const stream of streams) {
    const groups = groupStages(stream);
    out.push({
      id: stream.id,
      name: stream.name,
      level: 1,
      parent_id: null,
      children: groups.map((g) => g.id),
      description: stream.description,
      industry: (stream.industries ?? []).join("; "),
    });
    for (const group of groups) {
      const capability_ids = uniq(
        group.rows.flatMap((r) => r.capability_ids ?? []),
      );
      const process_ids = uniq(
        group.rows.flatMap((r) => r.process_ids ?? []),
      );
      const variantInds = uniq(
        group.rows
          .map((r) => r.industry_variant)
          .filter((v): v is string => Boolean(v)),
      );
      const industry =
        variantInds.length > 0
          ? variantInds.join("; ")
          : (stream.industries ?? []).join("; ");
      out.push({
        id: group.id,
        name: group.stage_name,
        level: 2,
        parent_id: stream.id,
        children: [],
        description: describeGroup(group),
        industry,
        capability_ids,
        process_ids,
      });
    }
  }
  return out;
}
