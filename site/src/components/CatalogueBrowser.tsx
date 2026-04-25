import { useEffect, useMemo, useRef, useState } from "react";

export interface FlatCap {
  id: string;
  name: string;
  level: number;
  parent_id: string | null;
  description?: string;
  aliases?: string[];
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
    "industry",
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
        r.industry ?? "",
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
  const allIndustries = useMemo(() => {
    const s = new Set<string>();
    for (const c of data) if (c.industry) s.add(c.industry);
    return Array.from(s).sort();
  }, [data]);

  const byId = useMemo(() => {
    const m = new Map<string, FlatCap>();
    for (const c of data) m.set(c.id, c);
    return m;
  }, [data]);

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

  const descendantsOf = useMemo(() => {
    const cache = new Map<string, string[]>();
    function walk(id: string): string[] {
      if (cache.has(id)) return cache.get(id)!;
      const out: string[] = [];
      const stack = [...(byParent.get(id) ?? [])];
      while (stack.length > 0) {
        const n = stack.pop()!;
        out.push(n.id);
        for (const k of byParent.get(n.id) ?? []) stack.push(k);
      }
      cache.set(id, out);
      return out;
    }
    for (const c of data) walk(c.id);
    return cache;
  }, [data, byParent]);

  const [query, setQuery] = useState("");
  const [levels, setLevels] = useState<Set<number>>(new Set([1, 2, 3, 4]));
  const [industries, setIndustries] = useState<Set<string>>(new Set());
  const [showDeprecated, setShowDeprecated] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<Set<string>>(() => {
    const s = new Set<string>();
    for (const c of data) if (c.level === 1) s.add(c.id);
    return s;
  });

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return data.filter((c) => {
      if (!levels.has(c.level)) return false;
      if (industries.size > 0 && (!c.industry || !industries.has(c.industry))) return false;
      if (!showDeprecated && c.deprecated) return false;
      if (q) {
        const haystack = [
          c.id,
          c.name,
          c.description ?? "",
          (c.aliases ?? []).join(" "),
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [data, levels, industries, showDeprecated, query]);

  // Always show ancestors of any visible node so the card tree stays navigable.
  const visibleSet = useMemo(() => {
    const ids = new Set(visible.map((c) => c.id));
    for (const c of visible) {
      let cursor = c.parent_id;
      while (cursor) {
        if (ids.has(cursor)) break;
        ids.add(cursor);
        cursor = byId.get(cursor)?.parent_id ?? null;
      }
    }
    return ids;
  }, [visible, byId]);

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const expandAll = () => {
    const s = new Set<string>();
    for (const c of data) s.add(c.id);
    setExpanded(s);
  };

  const collapseAll = () => setExpanded(new Set());

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      const subtree = [id, ...(descendantsOf.get(id) ?? [])];
      const allSelected = subtree.every((s) => next.has(s));
      if (allSelected) {
        for (const s of subtree) next.delete(s);
      } else {
        for (const s of subtree) next.add(s);
      }
      return next;
    });
  };

  const selectAllVisible = () => {
    setSelected((prev) => {
      const next = new Set(prev);
      for (const id of visibleSet) next.add(id);
      return next;
    });
  };

  const clearSelection = () => setSelected(new Set());

  const exportSelection = (kind: "csv" | "json") => {
    const rows = data
      .filter((c) => selected.has(c.id))
      .sort((a, b) => compareIds(a.id, b.id));
    if (rows.length === 0) return;
    const stamp = rows.length;
    if (kind === "json") {
      download(
        `capabilities-selection-${stamp}.json`,
        JSON.stringify(rows, null, 2),
        "application/json"
      );
    } else {
      download(`capabilities-selection-${stamp}.csv`, toCsv(rows), "text/csv");
    }
  };

  const roots = (byParent.get(null) ?? []).filter((r) => visibleSet.has(r.id));
  const selectionCount = selected.size;

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

        {allIndustries.length > 0 && (
          <div class="filter-group">
            <h3>Industry</h3>
            {allIndustries.map((ind) => (
              <label key={ind}>
                <input
                  type="checkbox"
                  checked={industries.has(ind)}
                  onChange={() => {
                    setIndustries((prev) => {
                      const next = new Set(prev);
                      next.has(ind) ? next.delete(ind) : next.add(ind);
                      return next;
                    });
                  }}
                />
                {ind}
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
              setIndustries(new Set());
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
            {selectionCount > 0 && (
              <>
                {" "}
                · <strong>{selectionCount}</strong> selected
              </>
            )}
          </div>
          <div class="toolbar-actions">
            <button class="btn btn-ghost" type="button" onClick={expandAll}>
              Expand all
            </button>
            <button class="btn btn-ghost" type="button" onClick={collapseAll}>
              Collapse all
            </button>
            <button class="btn btn-ghost" type="button" onClick={selectAllVisible}>
              Select visible
            </button>
            <button
              class="btn btn-ghost"
              type="button"
              onClick={clearSelection}
              disabled={selectionCount === 0}
            >
              Clear selection
            </button>
            <button
              class="btn"
              type="button"
              onClick={() => exportSelection("csv")}
              disabled={selectionCount === 0}
            >
              Export CSV{selectionCount > 0 && ` (${selectionCount})`}
            </button>
            <button
              class="btn btn-magenta"
              type="button"
              onClick={() => exportSelection("json")}
              disabled={selectionCount === 0}
            >
              Export JSON{selectionCount > 0 && ` (${selectionCount})`}
            </button>
          </div>
        </div>

        {roots.length === 0 ? (
          <div class="no-results">
            <h3>No matches</h3>
            <p>Adjust your filters or search query.</p>
          </div>
        ) : (
          <div class="card-tree">
            {roots.map((r) => (
              <CapabilityCard
                key={r.id}
                node={r}
                byParent={byParent}
                visible={visibleSet}
                expanded={expanded}
                selected={selected}
                descendantsOf={descendantsOf}
                onToggleExpand={toggleExpand}
                onToggleSelect={toggleSelect}
                depth={0}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface CardProps {
  node: FlatCap;
  byParent: Map<string | null, FlatCap[]>;
  visible: Set<string>;
  expanded: Set<string>;
  selected: Set<string>;
  descendantsOf: Map<string, string[]>;
  onToggleExpand: (id: string) => void;
  onToggleSelect: (id: string) => void;
  depth: number;
}

function CapabilityCard({
  node,
  byParent,
  visible,
  expanded,
  selected,
  descendantsOf,
  onToggleExpand,
  onToggleSelect,
  depth,
}: CardProps) {
  const kids = (byParent.get(node.id) ?? []).filter((c) => visible.has(c.id));
  const isOpen = expanded.has(node.id);
  const hasKids = kids.length > 0;
  const url = `/capability/${encodeURIComponent(node.id)}`;

  const subtree = descendantsOf.get(node.id) ?? [];
  const selectedInSubtree = subtree.filter((s) => selected.has(s)).length;
  const selfSelected = selected.has(node.id);
  const totalForState = subtree.length + 1;
  const selectedTotal = selectedInSubtree + (selfSelected ? 1 : 0);

  let checkState: "unchecked" | "checked" | "indeterminate" = "unchecked";
  if (selectedTotal === totalForState) checkState = "checked";
  else if (selectedTotal > 0) checkState = "indeterminate";

  const checkboxRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (checkboxRef.current) {
      checkboxRef.current.indeterminate = checkState === "indeterminate";
    }
  }, [checkState]);

  return (
    <div
      class={`cap-card${selfSelected ? " is-selected" : ""}`}
      data-depth={depth}
      data-level={node.level}
    >
      <div class="cap-card-header">
        <label class="cap-check" onClick={(e) => e.stopPropagation()}>
          <input
            ref={checkboxRef}
            type="checkbox"
            checked={checkState === "checked"}
            onChange={() => onToggleSelect(node.id)}
            aria-label={`Select ${node.id} ${node.name}`}
          />
        </label>
        <button
          type="button"
          class={`cap-chevron${hasKids ? "" : " is-empty"}`}
          onClick={() => hasKids && onToggleExpand(node.id)}
          aria-expanded={isOpen}
          aria-label={hasKids ? (isOpen ? "Collapse" : "Expand") : ""}
          tabIndex={hasKids ? 0 : -1}
        >
          {hasKids ? (isOpen ? "▾" : "▸") : ""}
        </button>
        <span class="cap-id">{node.id}</span>
        <a class="cap-name" href={url}>
          {node.name}
        </a>
        <span class="cap-level">L{node.level}</span>
        {node.industry && <span class="cap-industry">{node.industry}</span>}
        {node.deprecated && <span class="cap-deprecated-badge">Deprecated</span>}
        {hasKids && <span class="cap-count">{kids.length}</span>}
      </div>
      {isOpen && (
        <div class="cap-card-body">
          {node.description && <p class="cap-card-desc">{node.description}</p>}
          {hasKids && (
            <div class="cap-card-children">
              {kids.map((k) => (
                <CapabilityCard
                  key={k.id}
                  node={k}
                  byParent={byParent}
                  visible={visible}
                  expanded={expanded}
                  selected={selected}
                  descendantsOf={descendantsOf}
                  onToggleExpand={onToggleExpand}
                  onToggleSelect={onToggleSelect}
                  depth={depth + 1}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
