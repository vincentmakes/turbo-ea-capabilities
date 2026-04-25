import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";

export interface RawCapability {
  id: string;
  name: string;
  level: number;
  description?: string;
  aliases?: string[];
  industry?: string;
  references?: string[];
  in_scope?: string[];
  out_of_scope?: string[];
  deprecated?: boolean;
  deprecation_reason?: string;
  successor_id?: string;
  metadata?: Record<string, unknown>;
  children: RawCapability[];
}

export interface FlatCapability extends Omit<RawCapability, "children"> {
  parent_id: string | null;
  children: string[];
}

export interface IndexFile {
  files: string[];
}

export const REPO_ROOT = join(import.meta.dirname, "..", "..");
export const CATALOGUE_DIR = join(REPO_ROOT, "catalogue");
export const SCHEMA_PATH = join(REPO_ROOT, "schema", "capability.schema.json");
export const ID_REGEX = /^BC-\d+(\.\d+){0,3}$/;

export function readIndex(): IndexFile {
  const indexPath = join(CATALOGUE_DIR, "_index.yaml");
  if (!existsSync(indexPath)) {
    throw new Error(`Missing catalogue/_index.yaml at ${indexPath}`);
  }
  const parsed = YAML.parse(readFileSync(indexPath, "utf8")) as IndexFile;
  if (!parsed?.files || !Array.isArray(parsed.files)) {
    throw new Error("catalogue/_index.yaml must contain a 'files' array");
  }
  return parsed;
}

export function listYamlFiles(): string[] {
  // Underscore-prefixed files (e.g. _index.yaml, _value-streams.yaml) are
  // meta artefacts, not L1 capability files.
  return readdirSync(CATALOGUE_DIR)
    .filter((f) => f.endsWith(".yaml") && !f.startsWith("_"))
    .sort();
}

export function loadL1File(name: string): { source: string; tree: RawCapability } {
  const path = join(CATALOGUE_DIR, name);
  const source = readFileSync(path, "utf8");
  const tree = YAML.parse(source, { strict: true }) as RawCapability;
  return { source, tree };
}

export function loadAllL1Files(): { name: string; tree: RawCapability }[] {
  const index = readIndex();
  return index.files.map((f) => ({ name: f, tree: loadL1File(f).tree }));
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

export function loadValueStreams(): ValueStream[] {
  const path = join(CATALOGUE_DIR, "_value-streams.yaml");
  if (!existsSync(path)) return [];
  const parsed = YAML.parse(readFileSync(path, "utf8")) as
    | { value_streams?: ValueStream[] }
    | undefined;
  return parsed?.value_streams ?? [];
}

/** BFS-walk a tree, yielding nodes parent-before-child, with parent_id wired up. */
export function flatten(
  root: RawCapability,
  inheritedIndustry?: string
): FlatCapability[] {
  const out: FlatCapability[] = [];
  const queue: { node: RawCapability; parentId: string | null; industry?: string }[] = [
    { node: root, parentId: null, industry: inheritedIndustry ?? root.industry },
  ];
  while (queue.length > 0) {
    const { node, parentId, industry } = queue.shift()!;
    const effectiveIndustry = node.industry ?? industry;
    const flat: FlatCapability = {
      id: node.id,
      name: node.name,
      level: node.level,
      parent_id: parentId,
      ...(node.description !== undefined && { description: node.description }),
      ...(node.aliases !== undefined && { aliases: node.aliases }),
      ...(effectiveIndustry !== undefined && { industry: effectiveIndustry }),
      ...(node.references !== undefined && { references: node.references }),
      ...(node.in_scope !== undefined && { in_scope: node.in_scope }),
      ...(node.out_of_scope !== undefined && { out_of_scope: node.out_of_scope }),
      ...(node.deprecated !== undefined && { deprecated: node.deprecated }),
      ...(node.deprecation_reason !== undefined && {
        deprecation_reason: node.deprecation_reason,
      }),
      ...(node.successor_id !== undefined && { successor_id: node.successor_id }),
      ...(node.metadata !== undefined && { metadata: node.metadata }),
      children: (node.children ?? []).map((c) => c.id),
    };
    out.push(flat);
    for (const child of node.children ?? []) {
      queue.push({ node: child, parentId: node.id, industry: effectiveIndustry });
    }
  }
  return out;
}

/** Returns a slug derived from the L1 name (lowercased, hyphenated). */
export function l1Slug(root: RawCapability): string {
  return root.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}
