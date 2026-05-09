import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import {
  BP_ID_REGEX,
  CATALOGUE_DIR,
  ID_REGEX,
  PROCESSES_DIR,
  readIndex,
  readProcessesIndex,
} from "../lib/load.ts";

export interface CliRawCapability {
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
  children: CliRawCapability[];
}

export type IdPrefix = "BC" | "BP";

export interface PrefixConfig {
  prefix: IdPrefix;
  /** Catalogue directory holding the per-L1/BP1 YAML files. */
  baseDir: string;
  /** Regex the id must match. */
  pattern: RegExp;
}

export const BC_PREFIX: PrefixConfig = {
  prefix: "BC",
  baseDir: CATALOGUE_DIR,
  pattern: ID_REGEX,
};

export const BP_PREFIX: PrefixConfig = {
  prefix: "BP",
  baseDir: PROCESSES_DIR,
  pattern: BP_ID_REGEX,
};

export function parseArgs(argv: string[]): Record<string, string> {
  const out: Record<string, string> = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith("--")) {
        out[key] = "true";
      } else {
        out[key] = next;
        i++;
      }
    }
  }
  return out;
}

export function loadAllTrees(config: PrefixConfig = BC_PREFIX): {
  files: { name: string; tree: CliRawCapability; doc: YAML.Document }[];
} {
  const idx =
    config.prefix === "BC" ? readIndex() : readProcessesIndex();
  const files = idx.files.map((name) => {
    const path = join(config.baseDir, name);
    const source = readFileSync(path, "utf8");
    const doc = YAML.parseDocument(source);
    const tree = doc.toJS() as CliRawCapability;
    return { name, tree, doc };
  });
  return { files };
}

export function saveTree(name: string, doc: YAML.Document, config: PrefixConfig = BC_PREFIX) {
  writeFileSync(join(config.baseDir, name), doc.toString({ lineWidth: 0 }), "utf8");
}

export function findNodeById(
  root: CliRawCapability,
  id: string
): CliRawCapability | undefined {
  if (root.id === id) return root;
  for (const c of root.children ?? []) {
    const hit = findNodeById(c, id);
    if (hit) return hit;
  }
  return undefined;
}

/**
 * Pick the next sparse child id under `parent`. Children use 10/20/30/...
 * gaps so insertions never renumber siblings. Falls back to next-after-max
 * when the existing children don't follow the sparse pattern.
 */
export function nextChildId(
  parent: CliRawCapability,
  config: PrefixConfig = BC_PREFIX
): string {
  if (!config.pattern.test(parent.id)) {
    throw new Error(`Parent id ${parent.id} fails the ${config.prefix}- pattern`);
  }
  const used = (parent.children ?? [])
    .map((c) => Number(c.id.split(".").at(-1)))
    .filter((n) => Number.isFinite(n)) as number[];
  if (used.length === 0) return `${parent.id}.10`;
  const max = Math.max(...used);
  // Step 10 if the existing space is multiples of 10; otherwise +1 after max.
  const allSparse = used.every((n) => n % 10 === 0 && n >= 10);
  const next = allSparse ? max + 10 : max + 1;
  return `${parent.id}.${next}`;
}

export function compareIds(a: string, b: string): number {
  const sa = a.replace(/^(BC|BP|VS)-/, "").split(".").map(Number);
  const sb = b.replace(/^(BC|BP|VS)-/, "").split(".").map(Number);
  const len = Math.max(sa.length, sb.length);
  for (let i = 0; i < len; i++) {
    const av = sa[i] ?? -1;
    const bv = sb[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}
