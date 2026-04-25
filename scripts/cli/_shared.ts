import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import YAML from "yaml";
import { CATALOGUE_DIR, ID_REGEX, readIndex } from "../lib/load.ts";

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

export function loadAllTrees(): {
  files: { name: string; tree: CliRawCapability; doc: YAML.Document }[];
} {
  const idx = readIndex();
  const files = idx.files.map((name) => {
    const path = join(CATALOGUE_DIR, name);
    const source = readFileSync(path, "utf8");
    const doc = YAML.parseDocument(source);
    const tree = doc.toJS() as CliRawCapability;
    return { name, tree, doc };
  });
  return { files };
}

export function saveTree(name: string, doc: YAML.Document) {
  writeFileSync(join(CATALOGUE_DIR, name), doc.toString({ lineWidth: 0 }), "utf8");
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

export function nextChildId(parent: CliRawCapability): string {
  if (!ID_REGEX.test(parent.id)) {
    throw new Error(`Parent id ${parent.id} fails the BC- pattern`);
  }
  const used = (parent.children ?? [])
    .map((c) => Number(c.id.split(".").at(-1)))
    .filter((n) => Number.isFinite(n)) as number[];
  const next = used.length === 0 ? 1 : Math.max(...used) + 1;
  return `${parent.id}.${next}`;
}

export function compareIds(a: string, b: string): number {
  const sa = a.replace(/^BC-/, "").split(".").map(Number);
  const sb = b.replace(/^BC-/, "").split(".").map(Number);
  const len = Math.max(sa.length, sb.length);
  for (let i = 0; i < len; i++) {
    const av = sa[i] ?? -1;
    const bv = sb[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}
