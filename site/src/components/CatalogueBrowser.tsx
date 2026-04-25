import { useMemo, useState } from "react";

export interface FlatCap {
  id: string;
  name: string;
  level: number;
  parent_id: string | null;
  description?: string;
  aliases?: string[];
  owner?: string;
  tags?: string[];
  industry?: string;
  references?: string[];
  deprecated?: boolean;
  deprecation_reason?: string;
  successor_id?: string;
  children: string[];
}

interface Props {
  data: FlatCap[];
}

type ViewMode = "tree" | "table";

function compareIds(a: string, b: string): number {
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

function toCsv(rows: FlatCap[]): string {
  const headers = [
    "id",
    "name",
    "level",
    "parent_id",
    "owner",
    "industry",
    "tags",
    "deprecated",
    "successor_id",
    "description",
  ];
  const escape = (v: unknown) => {
    if (v === undefined || v === null) return "";
    const s = Array.isArray(v) ? v.join(";") : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [headers.join(",")];
  for (const r of rows) {
    lines.push(
      [
        r.id,
        r.name,
        r.level,
        r.parent_id ?? "",
        r.owner ?? "",
        r.industry ?? "",
        r.tags ?? [],
        r.deprecated ?? false,
        r.successor_id ?? "",
        r.description ?? "",
      ]
        .map(escape)
        .join(",")
    );
  }
  return lines.join("\n");
}

function download(filename: string, content: string, mime: string) {
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

export default function CatalogueBrowser({ data }: Props) {
  const allOwners = useMemo(() => {
    const s = new Set<string>();
    for (const c of data) if (c.owner) s.add(c.owner);
    return Array.from(s).sort();
  }, [data]);

  const allTags = useMemo(() => {
    const s = new Set<string>();
    for (const c of data) for (const t of c.tags ?? []) s.add(t);
    return Array.from(s).sort();
  }, [data]);

  const [view, setView] = useState<ViewMode>("tree");
  const [query, setQuery] = useState("");
  const [levels, setLevels] = useState<Set<number>>(new Set([1, 2, 3, 4]));
  const [owners, setOwners] = useState<Set<string>>(new Set());
  const [tags, setTags] = useState<Set<string>>(new Set());
  const [showDeprecated, setShowDeprecated] = useState(false);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return data.filter((c) => {
      if (!levels.has(c.level)) return false;
      if (owners.size > 0 && (!c.owner || !owners.has(c.owner))) return false;
      if (tags.size > 0) {
        const hit = (c.tags ?? []).some((t) => tags.has(t));
        if (!hit) return false;
      }
      if (!showDeprecated && c.deprecated) return false;
      if (q) {
        const haystack = [
          c.id,
          c.name,
          c.description ?? "",
          (c.aliases ?? []).join(" "),
          (c.tags ?? []).join(" "),
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [data, levels, owners, tags, showDeprecated, query]);

  // For tree view: always show ancestors of any matching node so the
  // tree remains navigable.
  const visibleSet = useMemo(() => {
    const ids = new Set(visible.map((c) => c.id));
    const byId = new Map(data.map((c) => [c.id, c]));
    for (const c of visible) {
      let cursor = c.parent_id;
      while (cursor) {
        if (ids.has(cursor)) break;
        ids.add(cursor);
        cursor = byId.get(cursor)?.parent_id ?? null;
      }
    }
    return ids;
  }, [data, visible]);

  const exportFiltered = (kind: "csv" | "json") => {
    const rows = [...visible].sort((a, b) => compareIds(a.id, b.id));
    if (kind === "json") {
      download(
        "capabilities-filtered.json",
        JSON.stringify(rows, null, 2),
        "application/json"
      );
    } else {
      download("capabilities-filtered.csv", toCsv(rows), "text/csv");
    }
  };

  return (
    <div class="catalogue-layout">
      <aside class="filter-panel">
        <h3>Search</h3>
        <div class="search-input-wrapper" style={{ marginBottom: 16 }}>
          <input
            type="search"
            class="search-input"
            placeholder="Search id, name, description…"
            value={query}
            onInput={(e) => setQuery((e.target as HTMLInputElement).value)}
          />
        </div>

        <div class="filter-group">
          <h3>Level</h3>
          {[1, 2, 3, 4].map((lvl) => (
            <label key={lvl}>
              <input
                type="checkbox"
                checked={levels.has(lvl)}
                onChange={() => {
                  setLevels((prev) => {
                    const next = new Set(prev);
                    next.has(lvl) ? next.delete(lvl) : next.add(lvl);
                    return next;
                  });
                }}
              />
              L{lvl}
            </label>
          ))}
        </div>

        {allOwners.length > 0 && (
          <div class="filter-group">
            <h3>Owner</h3>
            {allOwners.map((o) => (
              <label key={o}>
                <input
                  type="checkbox"
                  checked={owners.has(o)}
                  onChange={() => {
                    setOwners((prev) => {
                      const next = new Set(prev);
                      next.has(o) ? next.delete(o) : next.add(o);
                      return next;
                    });
                  }}
                />
                {o}
              </label>
            ))}
          </div>
        )}

        {allTags.length > 0 && (
          <div class="filter-group">
            <h3>Tag</h3>
            {allTags.map((t) => (
              <label key={t}>
                <input
                  type="checkbox"
                  checked={tags.has(t)}
                  onChange={() => {
                    setTags((prev) => {
                      const next = new Set(prev);
                      next.has(t) ? next.delete(t) : next.add(t);
                      return next;
                    });
                  }}
                />
                {t}
              </label>
            ))}
          </div>
        )}

        <div class="filter-group">
          <h3>State</h3>
          <label>
            <input
              type="checkbox"
              checked={showDeprecated}
              onChange={() => setShowDeprecated((v) => !v)}
            />
            Show deprecated
          </label>
        </div>

        <div class="filter-actions">
          <button
            class="btn"
            type="button"
            onClick={() => {
              setQuery("");
              setLevels(new Set([1, 2, 3, 4]));
              setOwners(new Set());
              setTags(new Set());
              setShowDeprecated(false);
            }}
          >
            Reset filters
          </button>
        </div>
      </aside>

      <div>
        <div class="toolbar">
          <div class="search-results-info">
            <strong>{visible.length}</strong> capabilities match
            {visible.length !== data.length && (
              <>
                {" "}
                · <strong>{data.length}</strong> total
              </>
            )}
          </div>
          <div class="toolbar-actions">
            <div class="view-toggle">
              <button
                class={view === "tree" ? "active" : ""}
                onClick={() => setView("tree")}
                type="button"
              >
                Tree
              </button>
              <button
                class={view === "table" ? "active" : ""}
                onClick={() => setView("table")}
                type="button"
              >
                Table
              </button>
            </div>
            <button class="btn" type="button" onClick={() => exportFiltered("csv")}>
              Export CSV
            </button>
            <button
              class="btn btn-magenta"
              type="button"
              onClick={() => exportFiltered("json")}
            >
              Export JSON
            </button>
          </div>
        </div>

        {visible.length === 0 ? (
          <div class="no-results">
            <h3>No matches</h3>
            <p>Adjust your filters or search query.</p>
          </div>
        ) : view === "tree" ? (
          <TreeView data={data} visible={visibleSet} />
        ) : (
          <TableView rows={visible} />
        )}
      </div>
    </div>
  );
}

function TreeView({ data, visible }: { data: FlatCap[]; visible: Set<string> }) {
  const byParent = useMemo(() => {
    const map = new Map<string | null, FlatCap[]>();
    for (const c of data) {
      const list = map.get(c.parent_id) ?? [];
      list.push(c);
      map.set(c.parent_id, list);
    }
    for (const list of map.values()) list.sort((a, b) => compareIds(a.id, b.id));
    return map;
  }, [data]);

  const roots = byParent.get(null) ?? [];

  return (
    <div class="cap-tree">
      <ul>
        {roots
          .filter((r) => visible.has(r.id))
          .map((r) => (
            <Node key={r.id} node={r} byParent={byParent} visible={visible} depth={0} />
          ))}
      </ul>
    </div>
  );
}

function Node({
  node,
  byParent,
  visible,
  depth,
}: {
  node: FlatCap;
  byParent: Map<string | null, FlatCap[]>;
  visible: Set<string>;
  depth: number;
}) {
  const kids = (byParent.get(node.id) ?? []).filter((c) => visible.has(c.id));
  const url = `/capability/${encodeURIComponent(node.id)}`;
  if (kids.length === 0) {
    return (
      <li class="cap-node">
        <div class="cap-leaf">
          <span class="cap-id">{node.id}</span>
          <a class="cap-name" href={url}>
            {node.name}
          </a>
          <span class="cap-level">L{node.level}</span>
          {node.deprecated && <span class="cap-deprecated-badge">Deprecated</span>}
        </div>
      </li>
    );
  }
  return (
    <li class="cap-node">
      <details open={depth < 1}>
        <summary>
          <span class="cap-id">{node.id}</span>
          <a class="cap-name" href={url} onClick={(e) => e.stopPropagation()}>
            {node.name}
          </a>
          <span class="cap-level">L{node.level}</span>
          {node.deprecated && <span class="cap-deprecated-badge">Deprecated</span>}
        </summary>
        <ul>
          {kids.map((k) => (
            <Node
              key={k.id}
              node={k}
              byParent={byParent}
              visible={visible}
              depth={depth + 1}
            />
          ))}
        </ul>
      </details>
    </li>
  );
}

function TableView({ rows }: { rows: FlatCap[] }) {
  const sorted = useMemo(() => [...rows].sort((a, b) => compareIds(a.id, b.id)), [rows]);
  return (
    <table class="cap-table">
      <thead>
        <tr>
          <th>Id</th>
          <th>Level</th>
          <th>Name</th>
          <th>Owner</th>
          <th>Tags</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((r) => (
          <tr key={r.id}>
            <td>
              <span class="cap-id">{r.id}</span>
            </td>
            <td>
              <span class="cap-level">L{r.level}</span>
            </td>
            <td>
              <a class="cap-name" href={`/capability/${encodeURIComponent(r.id)}`}>
                {r.name}
              </a>
            </td>
            <td>{r.owner ?? "—"}</td>
            <td>
              {r.tags && r.tags.length > 0 ? (
                <div class="tag-list">
                  {r.tags.map((t) => (
                    <span key={t} class="tag-pill">
                      {t}
                    </span>
                  ))}
                </div>
              ) : (
                "—"
              )}
            </td>
            <td>
              {r.deprecated ? (
                <span class="cap-deprecated-badge">Deprecated</span>
              ) : (
                <span style={{ color: "var(--color-success)", fontSize: 12, fontWeight: 600 }}>
                  Active
                </span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
