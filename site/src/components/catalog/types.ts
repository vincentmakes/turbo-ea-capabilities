/**
 * Shared types for the generic catalogue browser. All three artefacts
 * (capabilities, business processes, value streams) flatten into the same
 * `FlatNode` shape so a single React tree component can render them.
 */

export type CatalogKind = "capability" | "process" | "value-stream";

export interface FlatNode {
  id: string;
  name: string;
  level: number;
  parent_id: string | null;
  children: string[];
  description?: string;
  aliases?: string[];
  industry?: string;
  references?: string[];
  deprecated?: boolean;
  deprecation_reason?: string;
  successor_id?: string;
  /** Capability-only reverse indices (populated by build_api.ts). */
  realizes_processes?: string[];
  value_stream_stages?: string[];
  /** Process-only forward + reverse indices. */
  realizes_capability_ids?: string[];
  realized_in_value_streams?: string[];
  /** Value-stream stage cross-links. */
  capability_ids?: string[];
  process_ids?: string[];
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
  stages: ValueStreamStage[];
}

export interface CatalogKindConfig {
  /** Display label for the breadcrumb root link in the detail modal. */
  breadcrumbLabel: string;
  /** Route for the breadcrumb root link. */
  breadcrumbHref: string;
  /** Filename stem used when exporting selections. */
  exportStem: string;
  /** Returns the GitHub `blob/main/...` URL for a node's source YAML. */
  githubPathFor: (
    node: FlatNode,
    rootName: string,
  ) => string;
}

const REPO_BLOB =
  "https://github.com/vincentmakes/turbo-ea-capabilities/blob/main";

function fileSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export const CATALOG_KINDS: Record<CatalogKind, CatalogKindConfig> = {
  capability: {
    breadcrumbLabel: "Capabilities",
    breadcrumbHref: "/capabilities",
    exportStem: "capabilities",
    githubPathFor: (node, rootName) => {
      // Macros live in the dedicated single-file artefact. Routing logic:
      // - The node itself is a macro → macro file.
      // - The node sits inside a macro-rooted subtree → the ancestor walk
      //   lands on the MC; rootName is then the macro display name, but the
      //   capability YAML for the BC L1 is still the right target. We detect
      //   this by sniffing the *node* id prefix: BC ids point at their L1
      //   file, MC ids point at the macro file.
      if (node.id.startsWith("MC-")) {
        return `${REPO_BLOB}/catalogue/_macro-capabilities.yaml`;
      }
      return `${REPO_BLOB}/catalogue/L1-${fileSlug(rootName)}.yaml`;
    },
  },
  process: {
    breadcrumbLabel: "Processes",
    breadcrumbHref: "/business-processes",
    exportStem: "processes",
    githubPathFor: (_node, rootName) =>
      `${REPO_BLOB}/catalogue/processes/BP1-${fileSlug(rootName)}.yaml`,
  },
  "value-stream": {
    breadcrumbLabel: "Value Streams",
    breadcrumbHref: "/value-streams",
    exportStem: "value-streams",
    githubPathFor: () => `${REPO_BLOB}/catalogue/_value-streams.yaml`,
  },
};
