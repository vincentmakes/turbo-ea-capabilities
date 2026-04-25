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

interface Props {
  data: FlatCap[];
  valueStreams: ValueStream[];
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

function splitIndustry(s: string | undefined): string[] {
  if (!s) return [];
  return s
    .split(";")
    .map((x) => x.trim())
    .filter(Boolean);
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

export default function CatalogueBrowser({ data, valueStreams }: Props) {
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
    for (const c of data) {
      const out: string[] = [];
      const stack = [...(byParent.get(c.id) ?? [])];
      while (stack.length > 0) {
        const n = stack.pop()!;
        out.push(n.id);
        for (const k of byParent.get(n.id) ?? []) stack.push(k);
      }
      cache.set(c.id, out);
    }
    return cache;
  }, [data, byParent]);

  // Derived facets ---------------------------------------------------------
  const allLevels = useMemo(() => {
    const s = new Set<number>();
    for (const c of data) s.add(c.level);
    return Array.from(s).sort((a, b) => a - b);
  }, [data]);

  const allIndustries = useMemo(() => {
    const s = new Set<string>();
    for (const c of data) for (const ind of splitIndustry(c.industry)) s.add(ind);
    return Array.from(s).sort();
  }, [data]);

  const valueStreamNames = useMemo(
    () => valueStreams.map((v) => v.name).sort(),
    [valueStreams]
  );

  /** capabilityId → set of value-stream names containing it. */
  const valueStreamsByCapability = useMemo(() => {
    const map = new Map<string, Set<string>>();
    for (const stream of valueStreams) {
      for (const stage of stream.stages) {
        const set = map.get(stage.capability_id) ?? new Set<string>();
        set.add(stream.name);
        map.set(stage.capability_id, set);
      }
    }
    return map;
  }, [valueStreams]);

  // Filters / state --------------------------------------------------------
  const [query, setQuery] = useState("");
  const [levels, setLevels] = useState<Set<number>>(() => new Set(allLevels));
  const [industries, setIndustries] = useState<Set<string>>(new Set());
  const [streams, setStreams] = useState<Set<string>>(new Set());
  const [showDeprecated, setShowDeprecated] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<Set<string>>(() => {
    // L1s expanded by default
    const s = new Set<string>();
    for (const c of data) if (c.level === 1) s.add(c.id);
    return s;
  });
  const [detailId, setDetailId] = useState<string | null>(null);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return data.filter((c) => {
      if (!levels.has(c.level)) return false;
      if (industries.size > 0) {
        const inds = splitIndustry(c.industry);
        if (!inds.some((i) => industries.has(i))) return false;
      }
      if (streams.size > 0) {
        const cs = valueStreamsByCapability.get(c.id);
        if (!cs) return false;
        let hit = false;
        for (const s of streams) if (cs.has(s)) { hit = true; break; }
        if (!hit) return false;
      }
      if (!showDeprecated && c.deprecated) return false;
      if (q) {
        const haystack = [c.id, c.name, c.description ?? "", (c.aliases ?? []).join(" ")]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [data, levels, industries, streams, showDeprecated, query, valueStreamsByCapability]);

  // Always include ancestors of any visible node so each L1 column shows.
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

  // Selection helpers ------------------------------------------------------
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
    if (kind === "json") {
      download(
        `capabilities-selection-${rows.length}.json`,
        JSON.stringify(rows, null, 2),
        "application/json"
      );
    } else {
      download(
        `capabilities-selection-${rows.length}.csv`,
        toCsv(rows),
        "text/csv"
      );
    }
  };

  const resetFilters = () => {
    setQuery("");
    setLevels(new Set(allLevels));
    setIndustries(new Set());
    setStreams(new Set());
    setShowDeprecated(false);
  };

  const roots = (byParent.get(null) ?? []).filter((r) => visibleSet.has(r.id));
  const selectionCount = selected.size;
  const detail = detailId ? byId.get(detailId) ?? null : null;

  return (
    <div class="catalogue-page">
      <FilterBar
        query={query}
        onQuery={setQuery}
        allLevels={allLevels}
        levels={levels}
        onLevels={setLevels}
        allIndustries={allIndustries}
        industries={industries}
        onIndustries={setIndustries}
        valueStreamNames={valueStreamNames}
        streams={streams}
        onStreams={setStreams}
        showDeprecated={showDeprecated}
        onShowDeprecated={setShowDeprecated}
        onReset={resetFilters}
      />

      <div class="action-bar">
        <div class="action-bar-info">
          <strong>{visible.length}</strong> match
          {visible.length !== data.length && (
            <>
              {" · "}
              <strong>{data.length}</strong> total
            </>
          )}
          {selectionCount > 0 && (
            <>
              {" · "}
              <strong>{selectionCount}</strong> selected
            </>
          )}
        </div>
        <div class="action-bar-buttons">
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
        <div class="l1-grid">
          {roots.map((r) => (
            <L1Card
              key={r.id}
              node={r}
              byParent={byParent}
              visible={visibleSet}
              expanded={expanded}
              selected={selected}
              descendantsOf={descendantsOf}
              onToggleExpand={toggleExpand}
              onToggleSelect={toggleSelect}
              onOpenDetail={setDetailId}
            />
          ))}
        </div>
      )}

      {detail && (
        <DetailPanel
          node={detail}
          valueStreams={valueStreams}
          onClose={() => setDetailId(null)}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// FilterBar
// ---------------------------------------------------------------------------
interface FilterBarProps {
  query: string;
  onQuery: (q: string) => void;
  allLevels: number[];
  levels: Set<number>;
  onLevels: (s: Set<number>) => void;
  allIndustries: string[];
  industries: Set<string>;
  onIndustries: (s: Set<string>) => void;
  valueStreamNames: string[];
  streams: Set<string>;
  onStreams: (s: Set<string>) => void;
  showDeprecated: boolean;
  onShowDeprecated: (v: boolean) => void;
  onReset: () => void;
}

function FilterBar({
  query,
  onQuery,
  allLevels,
  levels,
  onLevels,
  allIndustries,
  industries,
  onIndustries,
  valueStreamNames,
  streams,
  onStreams,
  showDeprecated,
  onShowDeprecated,
  onReset,
}: FilterBarProps) {
  return (
    <div class="filter-bar">
      <div class="filter-search">
        <input
          type="search"
          class="search-input"
          placeholder="Search id, name, description…"
          value={query}
          onInput={(e) => onQuery((e.target as HTMLInputElement).value)}
        />
      </div>

      <div class="filter-levels">
        <span class="filter-label">Level</span>
        {allLevels.map((lvl) => (
          <label key={lvl} class="level-chip">
            <input
              type="checkbox"
              checked={levels.has(lvl)}
              onChange={() => {
                const next = new Set(levels);
                next.has(lvl) ? next.delete(lvl) : next.add(lvl);
                onLevels(next);
              }}
            />
            <span>L{lvl}</span>
          </label>
        ))}
      </div>

      {allIndustries.length > 1 && (
        <MultiSelect
          label="Industry"
          options={allIndustries}
          selected={industries}
          onChange={onIndustries}
        />
      )}

      {valueStreamNames.length > 0 && (
        <MultiSelect
          label="Value stream"
          options={valueStreamNames}
          selected={streams}
          onChange={onStreams}
        />
      )}

      <label class="dep-toggle">
        <input
          type="checkbox"
          checked={showDeprecated}
          onChange={() => onShowDeprecated(!showDeprecated)}
        />
        <span>Deprecated</span>
      </label>

      <button class="btn btn-ghost" type="button" onClick={onReset}>
        Reset
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MultiSelect dropdown
// ---------------------------------------------------------------------------
interface MultiSelectProps {
  label: string;
  options: string[];
  selected: Set<string>;
  onChange: (next: Set<string>) => void;
}

function MultiSelect({ label, options, selected, onChange }: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onEsc);
    };
  }, [open]);

  const summary =
    selected.size === 0
      ? "All"
      : selected.size === 1
        ? Array.from(selected)[0]
        : `${selected.size} selected`;

  const toggle = (opt: string) => {
    const next = new Set(selected);
    next.has(opt) ? next.delete(opt) : next.add(opt);
    onChange(next);
  };

  return (
    <div class="multi-select" ref={ref}>
      <button
        type="button"
        class={`multi-select-trigger${selected.size > 0 ? " is-active" : ""}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span class="filter-label">{label}</span>
        <span class="multi-select-summary">{summary}</span>
        <span class="multi-select-caret" aria-hidden="true">
          ▾
        </span>
      </button>
      {open && (
        <div class="multi-select-menu" role="listbox">
          {selected.size > 0 && (
            <button
              type="button"
              class="multi-select-clear"
              onClick={() => onChange(new Set())}
            >
              Clear ({selected.size})
            </button>
          )}
          {options.map((opt) => (
            <label key={opt} class="multi-select-option">
              <input
                type="checkbox"
                checked={selected.has(opt)}
                onChange={() => toggle(opt)}
              />
              <span>{opt}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// L1 Card (top-level column in the grid)
// ---------------------------------------------------------------------------
interface L1CardProps {
  node: FlatCap;
  byParent: Map<string | null, FlatCap[]>;
  visible: Set<string>;
  expanded: Set<string>;
  selected: Set<string>;
  descendantsOf: Map<string, string[]>;
  onToggleExpand: (id: string) => void;
  onToggleSelect: (id: string) => void;
  onOpenDetail: (id: string) => void;
}

function L1Card({
  node,
  byParent,
  visible,
  expanded,
  selected,
  descendantsOf,
  onToggleExpand,
  onToggleSelect,
  onOpenDetail,
}: L1CardProps) {
  const kids = (byParent.get(node.id) ?? []).filter((c) => visible.has(c.id));
  const isOpen = expanded.has(node.id);
  const hasKids = kids.length > 0;

  const subtree = descendantsOf.get(node.id) ?? [];
  const totalForState = subtree.length + 1;
  const selfSelected = selected.has(node.id);
  const selectedInSubtree = subtree.filter((s) => selected.has(s)).length;
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
    <section class={`l1-card${selfSelected ? " is-selected" : ""}`}>
      <header class="l1-card-header">
        <input
          ref={checkboxRef}
          type="checkbox"
          class="l1-check"
          checked={checkState === "checked"}
          onChange={() => onToggleSelect(node.id)}
          aria-label={`Select ${node.id} ${node.name}`}
        />
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
        <button
          type="button"
          class="l1-name"
          onClick={() => onOpenDetail(node.id)}
        >
          {node.name}
        </button>
        {hasKids && <span class="cap-count">{kids.length}</span>}
      </header>
      {isOpen && hasKids && (
        <ul class="l2-list">
          {kids.map((k) => (
            <ChildRow
              key={k.id}
              node={k}
              byParent={byParent}
              visible={visible}
              expanded={expanded}
              selected={selected}
              descendantsOf={descendantsOf}
              onToggleExpand={onToggleExpand}
              onToggleSelect={onToggleSelect}
              onOpenDetail={onOpenDetail}
              depth={1}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Recursive child row (L2+)
// ---------------------------------------------------------------------------
interface ChildRowProps {
  node: FlatCap;
  byParent: Map<string | null, FlatCap[]>;
  visible: Set<string>;
  expanded: Set<string>;
  selected: Set<string>;
  descendantsOf: Map<string, string[]>;
  onToggleExpand: (id: string) => void;
  onToggleSelect: (id: string) => void;
  onOpenDetail: (id: string) => void;
  depth: number;
}

function ChildRow({
  node,
  byParent,
  visible,
  expanded,
  selected,
  descendantsOf,
  onToggleExpand,
  onToggleSelect,
  onOpenDetail,
  depth,
}: ChildRowProps) {
  const kids = (byParent.get(node.id) ?? []).filter((c) => visible.has(c.id));
  const isOpen = expanded.has(node.id);
  const hasKids = kids.length > 0;

  const subtree = descendantsOf.get(node.id) ?? [];
  const totalForState = subtree.length + 1;
  const selfSelected = selected.has(node.id);
  const selectedInSubtree = subtree.filter((s) => selected.has(s)).length;
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
    <li class={`l2-row${selfSelected ? " is-selected" : ""}`} data-depth={depth}>
      <div class="l2-row-line">
        <input
          ref={checkboxRef}
          type="checkbox"
          class="l2-check"
          checked={checkState === "checked"}
          onChange={() => onToggleSelect(node.id)}
          aria-label={`Select ${node.id} ${node.name}`}
        />
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
        <span class="cap-id cap-id-sm">{node.id}</span>
        <button
          type="button"
          class="l2-name"
          onClick={() => onOpenDetail(node.id)}
          title={node.description}
        >
          {node.name}
        </button>
        {node.deprecated && <span class="cap-deprecated-badge">Dep.</span>}
      </div>
      {isOpen && hasKids && (
        <ul class="l2-children">
          {kids.map((k) => (
            <ChildRow
              key={k.id}
              node={k}
              byParent={byParent}
              visible={visible}
              expanded={expanded}
              selected={selected}
              descendantsOf={descendantsOf}
              onToggleExpand={onToggleExpand}
              onToggleSelect={onToggleSelect}
              onOpenDetail={onOpenDetail}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

// ---------------------------------------------------------------------------
// DetailPanel — slide-in overlay on the right
// ---------------------------------------------------------------------------
interface DetailPanelProps {
  node: FlatCap;
  valueStreams: ValueStream[];
  onClose: () => void;
}

function DetailPanel({ node, valueStreams, onClose }: DetailPanelProps) {
  useEffect(() => {
    const onEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onEsc);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onEsc);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const inStreams: { stream: string; stage: ValueStreamStage }[] = [];
  for (const s of valueStreams) {
    for (const stage of s.stages) {
      if (stage.capability_id === node.id)
        inStreams.push({ stream: s.name, stage });
    }
  }

  const industries = splitIndustry(node.industry);

  return (
    <div class="detail-panel-root">
      <div class="detail-panel-backdrop" onClick={onClose} />
      <aside class="detail-panel" role="dialog" aria-label={`${node.id} ${node.name}`}>
        <header class="detail-panel-header">
          <div class="detail-panel-meta">
            <span class="cap-id">{node.id}</span>
            <span class="cap-level">L{node.level}</span>
            {node.deprecated && (
              <span class="cap-deprecated-badge">Deprecated</span>
            )}
          </div>
          <button
            type="button"
            class="detail-panel-close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </header>
        <div class="detail-panel-body">
          <h2 class="detail-panel-title">{node.name}</h2>
          {industries.length > 0 && (
            <div class="detail-panel-row">
              <div class="meta-key">Industry</div>
              <div class="meta-val">
                {industries.map((i) => (
                  <span key={i} class="cap-industry">
                    {i}
                  </span>
                ))}
              </div>
            </div>
          )}
          {node.description && (
            <div class="detail-panel-row">
              <div class="meta-key">Description</div>
              <p class="meta-val detail-panel-desc">{node.description}</p>
            </div>
          )}
          {node.aliases && node.aliases.length > 0 && (
            <div class="detail-panel-row">
              <div class="meta-key">Aliases</div>
              <div class="meta-val">{node.aliases.join(", ")}</div>
            </div>
          )}
          {inStreams.length > 0 && (
            <div class="detail-panel-row">
              <div class="meta-key">Value streams</div>
              <ul class="meta-val detail-panel-streams">
                {inStreams.map(({ stream, stage }, idx) => (
                  <li key={`${stream}-${stage.stage_order}-${idx}`}>
                    <strong>{stream}</strong>
                    {" · stage "}
                    {stage.stage_order} ({stage.stage_name})
                    {stage.industry_variant && stage.industry_variant !== "All" && (
                      <> · {stage.industry_variant}</>
                    )}
                    {stage.notes && <em> — {stage.notes}</em>}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {node.deprecated && node.deprecation_reason && (
            <div class="detail-panel-row">
              <div class="meta-key">Deprecation reason</div>
              <p class="meta-val">{node.deprecation_reason}</p>
            </div>
          )}
        </div>
        <footer class="detail-panel-footer">
          <a class="btn" href={`/capability/${encodeURIComponent(node.id)}`}>
            Open detail page
          </a>
          <a class="btn btn-ghost" href={`/api/capability/${node.id}.json`}>
            Raw JSON
          </a>
        </footer>
      </aside>
    </div>
  );
}
