/**
 * Adapter: flatten the value-stream catalogue into the same `FlatNode` shape
 * the generic `CatalogBrowser` consumes. Each stream becomes an L1 node and
 * each stage an L2 child, so the tree component renders streams identically
 * to capabilities and processes.
 */
import type { FlatNode, ValueStream } from "../components/catalog/types";

export function valueStreamsAsTree(streams: ValueStream[]): FlatNode[] {
  const out: FlatNode[] = [];
  for (const stream of streams) {
    const stageIds = (stream.stages ?? []).map((s) => s.id);
    out.push({
      id: stream.id,
      name: stream.name,
      level: 1,
      parent_id: null,
      children: stageIds,
      description: stream.description,
      industry: (stream.industries ?? []).join("; "),
    });
    for (const stage of stream.stages ?? []) {
      out.push({
        id: stage.id,
        name: stage.stage_name,
        level: 2,
        parent_id: stream.id,
        children: [],
        description: stage.description ?? stage.notes,
        industry:
          stage.industry_variant ||
          (stage.industries ?? []).join("; ") ||
          (stream.industries ?? []).join("; "),
        capability_ids: stage.capability_ids,
        process_ids: stage.process_ids,
      });
    }
  }
  return out;
}
