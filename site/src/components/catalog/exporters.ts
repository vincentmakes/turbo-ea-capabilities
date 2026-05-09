import type { FlatNode } from "./types";

/** Compare ids by their numeric segments after the leading `XX-` prefix.
 *  Works for `BC-`, `BP-`, `VS-` etc. Two-digit prefixes are stripped uniformly. */
export function compareIds(a: string, b: string): number {
  const sa = a.replace(/^[A-Z]+-/, "").split(".").map(Number);
  const sb = b.replace(/^[A-Z]+-/, "").split(".").map(Number);
  const len = Math.max(sa.length, sb.length);
  for (let i = 0; i < len; i++) {
    const av = sa[i] ?? -1;
    const bv = sb[i] ?? -1;
    if (av !== bv) return av - bv;
  }
  return 0;
}

export function splitIndustry(s: string | undefined): string[] {
  if (!s) return [];
  return s
    .split(";")
    .map((x) => x.trim())
    .filter(Boolean);
}

export function toCsv(rows: FlatNode[], byId: Map<string, FlatNode>): string {
  const headers = [
    "id",
    "name",
    "level",
    "path",
    "parent",
    "children",
    "industry",
    "deprecated",
    "successor",
    "description",
  ];
  const escape = (v: unknown) => {
    if (v === undefined || v === null) return "";
    const s = Array.isArray(v) ? v.join(";") : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const nameOf = (id: string | null | undefined) =>
    id ? (byId.get(id)?.name ?? id) : "";
  const pathOf = (node: FlatNode) => {
    const parts: string[] = [];
    let cursor: FlatNode | undefined = node;
    const seen = new Set<string>();
    while (cursor && !seen.has(cursor.id)) {
      seen.add(cursor.id);
      parts.unshift(cursor.name);
      cursor = cursor.parent_id ? byId.get(cursor.parent_id) : undefined;
    }
    return parts.join(" / ");
  };
  const lines = [headers.join(",")];
  for (const r of rows) {
    lines.push(
      [
        r.id,
        r.name,
        r.level,
        pathOf(r),
        nameOf(r.parent_id),
        r.children.map((id) => nameOf(id)).filter(Boolean).join(";"),
        r.industry ?? "",
        r.deprecated ?? false,
        nameOf(r.successor_id),
        r.description ?? "",
      ]
        .map(escape)
        .join(","),
    );
  }
  return lines.join("\n");
}

export function download(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
