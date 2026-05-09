import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
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
  /** Reverse indices, populated by build_api.ts. Empty in raw YAML. */
  realizes_processes?: string[];
  value_stream_stages?: string[];
}

export interface IndexFile {
  files: string[];
}

export const REPO_ROOT = join(import.meta.dirname, "..", "..");
export const CATALOGUE_DIR = join(REPO_ROOT, "catalogue");
export const I18N_DIR = join(CATALOGUE_DIR, "i18n");
export const PROCESSES_DIR = join(CATALOGUE_DIR, "processes");
export const SCHEMA_PATH = join(REPO_ROOT, "schema", "capability.schema.json");
export const I18N_SCHEMA_PATH = join(REPO_ROOT, "schema", "i18n.schema.json");
export const VALUE_STREAM_SCHEMA_PATH = join(
  REPO_ROOT,
  "schema",
  "value-stream.schema.json"
);
export const BUSINESS_PROCESS_SCHEMA_PATH = join(
  REPO_ROOT,
  "schema",
  "business-process.schema.json"
);
export const ID_REGEX = /^BC-\d+(\.\d+){0,3}$/;
export const BP_ID_REGEX = /^BP-\d+(\.\d+){0,3}$/;
export const VS_ID_REGEX = /^VS-\d+$/;
export const VS_STAGE_ID_REGEX = /^VS-\d+\.\d+$/;
export const BCP47_REGEX = /^[a-z]{2,3}(-[A-Z][a-z]{3})?(-([A-Z]{2}|[0-9]{3}))?$/;

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

// ---------------------------------------------------------------------------
// Value streams
// ---------------------------------------------------------------------------

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
  metadata?: Record<string, unknown>;
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

// ---------------------------------------------------------------------------
// Business processes
// ---------------------------------------------------------------------------

export interface FrameworkRef {
  /** Framework code. Validated against the enum in schema/business-process.schema.json. */
  framework: string;
  external_id: string;
  version?: string;
  url?: string;
}

export interface RawBusinessProcess {
  id: string;
  name: string;
  level: number;
  description?: string;
  aliases?: string[];
  industry?: string;
  references?: string[];
  framework_refs?: FrameworkRef[];
  realizes_capability_ids?: string[];
  in_scope?: string[];
  out_of_scope?: string[];
  deprecated?: boolean;
  deprecation_reason?: string;
  successor_id?: string;
  metadata?: Record<string, unknown>;
  children: RawBusinessProcess[];
}

export interface FlatBusinessProcess extends Omit<RawBusinessProcess, "children"> {
  parent_id: string | null;
  children: string[];
  /** Reverse index populated by build_api.ts. */
  realized_in_value_streams?: string[];
}

export function readProcessesIndex(): IndexFile {
  const indexPath = join(PROCESSES_DIR, "_index.yaml");
  if (!existsSync(indexPath)) {
    return { files: [] };
  }
  const parsed = YAML.parse(readFileSync(indexPath, "utf8")) as IndexFile;
  if (!parsed?.files || !Array.isArray(parsed.files)) {
    throw new Error("catalogue/processes/_index.yaml must contain a 'files' array");
  }
  return parsed;
}

export function listProcessFiles(): string[] {
  if (!existsSync(PROCESSES_DIR)) return [];
  return readdirSync(PROCESSES_DIR)
    .filter((f) => f.endsWith(".yaml") && !f.startsWith("_"))
    .sort();
}

export function loadBP1File(name: string): {
  source: string;
  tree: RawBusinessProcess;
} {
  const path = join(PROCESSES_DIR, name);
  const source = readFileSync(path, "utf8");
  const tree = YAML.parse(source, { strict: true }) as RawBusinessProcess;
  return { source, tree };
}

export function loadAllBP1Files(): { name: string; tree: RawBusinessProcess }[] {
  const index = readProcessesIndex();
  return index.files.map((f) => ({ name: f, tree: loadBP1File(f).tree }));
}

/** Returns a slug derived from the BP1 name (lowercased, hyphenated). */
export function bp1Slug(root: RawBusinessProcess): string {
  return root.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

/** BFS-walk a BP tree, yielding nodes parent-before-child, with parent_id wired up. */
export function flattenBP(
  root: RawBusinessProcess,
  inheritedIndustry?: string
): FlatBusinessProcess[] {
  const out: FlatBusinessProcess[] = [];
  const queue: { node: RawBusinessProcess; parentId: string | null; industry?: string }[] = [
    { node: root, parentId: null, industry: inheritedIndustry ?? root.industry },
  ];
  while (queue.length > 0) {
    const { node, parentId, industry } = queue.shift()!;
    const effectiveIndustry = node.industry ?? industry;
    const flat: FlatBusinessProcess = {
      id: node.id,
      name: node.name,
      level: node.level,
      parent_id: parentId,
      ...(node.description !== undefined && { description: node.description }),
      ...(node.aliases !== undefined && { aliases: node.aliases }),
      ...(effectiveIndustry !== undefined && { industry: effectiveIndustry }),
      ...(node.references !== undefined && { references: node.references }),
      ...(node.framework_refs !== undefined && { framework_refs: node.framework_refs }),
      ...(node.realizes_capability_ids !== undefined && {
        realizes_capability_ids: node.realizes_capability_ids,
      }),
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

export function loadBusinessProcesses(): FlatBusinessProcess[] {
  const out: FlatBusinessProcess[] = [];
  for (const { tree } of loadAllBP1Files()) {
    for (const node of flattenBP(tree)) out.push(node);
  }
  return out;
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

// ---------------------------------------------------------------------------
// Translation sidecars
// ---------------------------------------------------------------------------

export interface LocalizedFields {
  name?: string;
  stage_name?: string;
  description?: string;
  aliases?: string[];
  in_scope?: string[];
  out_of_scope?: string[];
  notes?: string;
  /** SHA-256 fingerprint of the source's translatable surface at translation time. Optional. */
  source_hash?: string;
}

export type SidecarKind = "capability" | "value-stream" | "business-process";

export interface Sidecar {
  kind?: SidecarKind;
  locale: string;
  source: string;
  entries: Record<string, LocalizedFields>;
  metadata?: Record<string, unknown>;
}

export interface SidecarFile {
  locale: string;
  /** Path within the locale dir (e.g. 'L1-foo.yaml' or 'processes/BP1-bar.yaml' or '_value-streams.yaml'). */
  file: string;
  /** Absolute path on disk. */
  path: string;
  data: Sidecar;
}

/** List BCP-47 locale directories under catalogue/i18n/ (sorted). */
export function listLocales(): string[] {
  if (!existsSync(I18N_DIR)) return [];
  return readdirSync(I18N_DIR)
    .filter((name) => {
      const p = join(I18N_DIR, name);
      return statSync(p).isDirectory() && BCP47_REGEX.test(name);
    })
    .sort();
}

/**
 * List sidecar yaml files within a locale directory. Includes top-level files
 * (capabilities, _value-streams.yaml) and `processes/*.yaml` if present.
 * Returned paths are relative to `catalogue/i18n/<locale>/`.
 */
export function listSidecarFiles(locale: string): string[] {
  const dir = join(I18N_DIR, locale);
  if (!existsSync(dir)) return [];
  const out: string[] = [];
  for (const f of readdirSync(dir).sort()) {
    if (f === "processes") {
      const procDir = join(dir, f);
      if (existsSync(procDir) && statSync(procDir).isDirectory()) {
        for (const p of readdirSync(procDir).sort()) {
          if (p.endsWith(".yaml") && !p.startsWith("_")) {
            out.push(join("processes", p));
          }
        }
      }
      continue;
    }
    if (!f.endsWith(".yaml")) continue;
    if (f.startsWith("_") && f !== "_value-streams.yaml") continue;
    out.push(f);
  }
  return out;
}

export function loadSidecar(locale: string, file: string): SidecarFile {
  const path = join(I18N_DIR, locale, file);
  const data = YAML.parse(readFileSync(path, "utf8"), { strict: true }) as Sidecar;
  return { locale, file, path, data };
}

export function loadAllSidecars(): SidecarFile[] {
  const out: SidecarFile[] = [];
  for (const locale of listLocales()) {
    for (const f of listSidecarFiles(locale)) {
      out.push(loadSidecar(locale, f));
    }
  }
  return out;
}
