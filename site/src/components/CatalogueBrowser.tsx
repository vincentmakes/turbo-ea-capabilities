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

  /**
   * capabilityId → set of value-stream names containing it.
   * Stages map to L1 capability_ids; this index expands each stage to the
   * full subtree so any descendant is matched by the stream filter.
   */
  const valueStreamsByCapability = useMemo(() => {
    const map = new Map<string, Set<string>>();
    const add = (id: string, name: string) => {
      const set = map.get(id) ?? new Set<string>();
      set.add(name);
      map.set(id, set);
    };
    for (const stream of valueStreams) {
      for (const stage of stream.stages) {
        add(stage.capability_id, stream.name);
        for (const d of descendantsOf.get(stage.capability_id) ?? []) {
          add(d, stream.name);
        }
      }
    }
    return map;
  }, [valueStreams, descendantsOf]);

  // Filters / state --------------------------------------------------------
  const [query, setQuery] = useState("");
  const [levels, setLevels] = useState<Set<number>>(() => new Set(allLevels));
  const [industries, setIndustries] = useState<Set<string>>(new Set());
  const [streams, setStreams] = useState<Set<string>>(new Set());
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
      if (q) {
        const haystack = [c.id, c.name, c.description ?? "", (c.aliases ?? []).join(" ")]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [data, levels, industries, streams, query, valueStreamsByCapability]);

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

  // Level-stepper ----------------------------------------------------------
  // Nodes whose level is < maxLevel can have children; expanding one of them
  // reveals its level+1 children. So the deepest meaningful "expansion level"
  // is maxLevel - 1 (e.g. for L1/L2/L3 data, max stepper level is 2 = all L2
  // expanded, showing L3).
  const maxLevel = useMemo(() => {
    let m = 1;
    for (const c of data) if (c.level > m) m = c.level;
    return m;
  }, [data]);

  /** Group expandable nodes (those with children) by their level. */
  const expandablesByLevel = useMemo(() => {
    const m = new Map<number, string[]>();
    for (const c of data) {
      if ((byParent.get(c.id) ?? []).length === 0) continue;
      const list = m.get(c.level) ?? [];
      list.push(c.id);
      m.set(c.level, list);
    }
    return m;
  }, [data, byParent]);

  /** Deepest level L such that every expandable node with level <= L is open.
   *  0 means nothing expanded; L1 expanded → 1; L1+L2 expanded → 2; etc. */
  const currentLevel = useMemo(() => {
    let depth = 0;
    for (let lvl = 1; lvl <= maxLevel - 1; lvl++) {
      const ids = expandablesByLevel.get(lvl) ?? [];
      if (ids.length === 0) continue;
      if (ids.every((id) => expanded.has(id))) depth = lvl;
      else break;
    }
    return depth;
  }, [expanded, expandablesByLevel, maxLevel]);

  const expandOneLevel = () => {
    const target = Math.min(currentLevel + 1, Math.max(maxLevel - 1, 0));
    if (target === currentLevel) return;
    setExpanded((prev) => {
      const next = new Set(prev);
      for (let lvl = 1; lvl <= target; lvl++) {
        for (const id of expandablesByLevel.get(lvl) ?? []) next.add(id);
      }
      return next;
    });
  };

  const collapseOneLevel = () => {
    const target = Math.max(currentLevel - 1, 0);
    if (target === currentLevel) return;
    setExpanded(() => {
      const next = new Set<string>();
      for (let lvl = 1; lvl <= target; lvl++) {
        for (const id of expandablesByLevel.get(lvl) ?? []) next.add(id);
      }
      return next;
    });
  };

  const stepperMax = Math.max(maxLevel - 1, 0);

  // Per-L1 stepper state ---------------------------------------------------
  // For each L1 we precompute its expandable descendants grouped by level,
  // so the L1 card's +/− pill can step that branch one level at a time.
  const expandablesByLevelByL1 = useMemo(() => {
    const out = new Map<string, Map<number, string[]>>();
    const l1s = byParent.get(null) ?? [];
    for (const l1 of l1s) {
      const m = new Map<number, string[]>();
      if ((byParent.get(l1.id) ?? []).length > 0) m.set(1, [l1.id]);
      for (const dId of descendantsOf.get(l1.id) ?? []) {
        if ((byParent.get(dId) ?? []).length === 0) continue;
        const d = byId.get(dId);
        if (!d) continue;
        const list = m.get(d.level) ?? [];
        list.push(dId);
        m.set(d.level, list);
      }
      out.set(l1.id, m);
    }
    return out;
  }, [byParent, byId, descendantsOf]);

  /** Map of L1 id → its current branch expansion level (0 = collapsed). */
  const l1CurrentLevels = useMemo(() => {
    const out = new Map<string, number>();
    for (const [l1Id, levels] of expandablesByLevelByL1.entries()) {
      let depth = 0;
      for (let lvl = 1; lvl <= maxLevel - 1; lvl++) {
        const ids = levels.get(lvl) ?? [];
        if (ids.length === 0) continue;
        if (ids.every((id) => expanded.has(id))) depth = lvl;
        else break;
      }
      out.set(l1Id, depth);
    }
    return out;
  }, [expandablesByLevelByL1, expanded, maxLevel]);

  const expandL1Branch = (l1Id: string) => {
    const m = expandablesByLevelByL1.get(l1Id);
    if (!m) return;
    const cur = l1CurrentLevels.get(l1Id) ?? 0;
    const target = Math.min(cur + 1, stepperMax);
    if (target === cur) return;
    setExpanded((prev) => {
      const next = new Set(prev);
      for (let lvl = 1; lvl <= target; lvl++) {
        for (const id of m.get(lvl) ?? []) next.add(id);
      }
      return next;
    });
  };

  const collapseL1Branch = (l1Id: string) => {
    const m = expandablesByLevelByL1.get(l1Id);
    if (!m) return;
    const cur = l1CurrentLevels.get(l1Id) ?? 0;
    const target = Math.max(cur - 1, 0);
    if (target === cur) return;
    setExpanded((prev) => {
      const next = new Set(prev);
      for (let lvl = target + 1; lvl <= stepperMax; lvl++) {
        for (const id of m.get(lvl) ?? []) next.delete(id);
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
          <div class="level-stepper" role="group" aria-label="Expand by level">
            <button
              type="button"
              class="level-stepper-btn"
              onClick={collapseOneLevel}
              disabled={currentLevel <= 0}
              aria-label="Collapse one level"
              title="Collapse one level"
            >
              <span class="material-symbols-outlined" aria-hidden="true">remove</span>
            </button>
            <span class="level-stepper-label" aria-live="polite">
              <span class="level-stepper-label-full">Level </span>
              {currentLevel}
              <span class="level-stepper-label-sep"> / </span>
              {stepperMax}
            </span>
            <button
              type="button"
              class="level-stepper-btn"
              onClick={expandOneLevel}
              disabled={currentLevel >= stepperMax}
              aria-label="Expand one level"
              title="Expand one level"
            >
              <span class="material-symbols-outlined" aria-hidden="true">add</span>
            </button>
          </div>
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
              branchLevel={l1CurrentLevels.get(r.id) ?? 0}
              branchMax={stepperMax}
              onToggleExpand={toggleExpand}
              onToggleSelect={toggleSelect}
              onOpenDetail={setDetailId}
              onExpandBranch={expandL1Branch}
              onCollapseBranch={collapseL1Branch}
            />
          ))}
        </div>
      )}

      {detail && (
        <DetailModal
          node={detail}
          byId={byId}
          byParent={byParent}
          valueStreams={valueStreams}
          onOpen={setDetailId}
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
        <span class="material-symbols-outlined multi-select-caret" aria-hidden="true">
          expand_more
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
  branchLevel: number;
  branchMax: number;
  onToggleExpand: (id: string) => void;
  onToggleSelect: (id: string) => void;
  onOpenDetail: (id: string) => void;
  onExpandBranch: (id: string) => void;
  onCollapseBranch: (id: string) => void;
}

function L1Card({
  node,
  byParent,
  visible,
  expanded,
  selected,
  descendantsOf,
  branchLevel,
  branchMax,
  onToggleExpand,
  onToggleSelect,
  onOpenDetail,
  onExpandBranch,
  onCollapseBranch,
}: L1CardProps) {
  const kids = (byParent.get(node.id) ?? []).filter((c) => visible.has(c.id));
  const isOpen = expanded.has(node.id);
  const hasKids = kids.length > 0;
  const canExpand = hasKids && branchLevel < branchMax;
  const canCollapse = branchLevel > 0;

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
        <div
          class={`l1-stepper${hasKids ? "" : " is-empty"}`}
          role="group"
          aria-label={`Expand branch by level (currently ${branchLevel} of ${branchMax})`}
        >
          <button
            type="button"
            class="l1-stepper-btn"
            onClick={() => canCollapse && onCollapseBranch(node.id)}
            disabled={!canCollapse}
            aria-label="Collapse this branch one level"
            title="Collapse branch one level"
            tabIndex={hasKids ? 0 : -1}
          >
            <span class="material-symbols-outlined" aria-hidden="true">remove</span>
          </button>
          <button
            type="button"
            class="l1-stepper-btn"
            onClick={() => canExpand && onExpandBranch(node.id)}
            disabled={!canExpand}
            aria-label="Expand this branch one level"
            title="Expand branch one level"
            aria-expanded={isOpen}
            tabIndex={hasKids ? 0 : -1}
          >
            <span class="material-symbols-outlined" aria-hidden="true">add</span>
          </button>
        </div>
        <button
          type="button"
          class="l1-name"
          onClick={() => onOpenDetail(node.id)}
        >
          {node.name}
        </button>
        {hasKids && <span class="cap-count" title={`${kids.length} children`}>{kids.length}</span>}
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

  const isL2 = depth === 1;

  const toggle = (
    <button
      type="button"
      class={`cap-chevron${hasKids ? "" : " is-empty"}${isOpen ? " is-open" : ""}`}
      onClick={() => hasKids && onToggleExpand(node.id)}
      aria-expanded={isOpen}
      aria-label={hasKids ? (isOpen ? "Collapse" : "Expand") : ""}
      tabIndex={hasKids ? 0 : -1}
    >
      {hasKids && (
        <span class="material-symbols-outlined cap-chevron-icon" aria-hidden="true">
          chevron_right
        </span>
      )}
    </button>
  );

  const checkbox = (
    <input
      ref={checkboxRef}
      type="checkbox"
      class="l2-check"
      checked={checkState === "checked"}
      onChange={() => onToggleSelect(node.id)}
      aria-label={`Select ${node.id} ${node.name}`}
    />
  );

  return (
    <li class={`l2-row${selfSelected ? " is-selected" : ""}`} data-depth={depth}>
      {isL2 ? (
        <div class="l2-card">
          {checkbox}
          {toggle}
          <button
            type="button"
            class="l2-card-name"
            onClick={() => onOpenDetail(node.id)}
            title={node.description}
          >
            {node.name}
          </button>
          {hasKids && (
            <span class="l2-card-count" title={`${kids.length} L${node.level + 1} children`}>
              {kids.length}
            </span>
          )}
          {node.deprecated && <span class="cap-deprecated-badge">Dep.</span>}
        </div>
      ) : (
        <div class="l2-row-line">
          {checkbox}
          {toggle}
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
      )}
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
// ModalTreeNode — fully-expanded nested subtree inside the detail modal.
// All levels are rendered up-front (no click-to-deeper) so users see the
// whole branch with descriptions in one place.
// ---------------------------------------------------------------------------
interface ModalTreeNodeProps {
  node: FlatCap;
  byParent: Map<string | null, FlatCap[]>;
}

function ModalTreeNode({ node, byParent }: ModalTreeNodeProps) {
  const kids = byParent.get(node.id) ?? [];
  return (
    <div class="modal-tree-node" data-level={node.level}>
      <div class="modal-tree-card">
        <div class="modal-tree-card-head">
          <span class="cap-id">{node.id}</span>
          <span class="cap-level">L{node.level}</span>
          {node.deprecated && <span class="cap-deprecated-badge">Dep.</span>}
          <span class="modal-tree-card-name">{node.name}</span>
          {kids.length > 0 && (
            <span class="cap-count" title={`${kids.length} L${node.level + 1} children`}>
              {kids.length}
            </span>
          )}
        </div>
        {node.description && (
          <p class="modal-tree-card-desc">{node.description}</p>
        )}
      </div>
      {kids.length > 0 && (
        <div class="modal-tree-children">
          {kids.map((k) => (
            <ModalTreeNode key={k.id} node={k} byParent={byParent} />
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// DetailModal — wider card-based overlay (breadcrumb · hero · meta · subtree)
// ---------------------------------------------------------------------------
interface DetailModalProps {
  node: FlatCap;
  byId: Map<string, FlatCap>;
  byParent: Map<string | null, FlatCap[]>;
  valueStreams: ValueStream[];
  onOpen: (id: string) => void;
  onClose: () => void;
}

function DetailModal({
  node,
  byId,
  byParent,
  valueStreams,
  onOpen,
  onClose,
}: DetailModalProps) {
  useEffect(() => {
    const onEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onEsc);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onEsc);
      document.body.style.overflow = prevOverflow;
    };
  }, [onClose]);

  const ancestors: FlatCap[] = [];
  let cursor = node.parent_id;
  while (cursor) {
    const a = byId.get(cursor);
    if (!a) break;
    ancestors.unshift(a);
    cursor = a.parent_id;
  }

  // The L1 root of the branch — used to locate the source YAML on GitHub.
  // Each L1 has its own catalogue/L1-<slug>.yaml file containing the whole
  // subtree, so L1/L2/L3 all link to the same file.
  const l1 = ancestors[0] ?? node;
  const l1Slug = l1.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  const githubYamlUrl =
    `https://github.com/vincentmakes/turbo-ea-capabilities/blob/main/catalogue/L1-${l1Slug}.yaml`;

  const directChildren = byParent.get(node.id) ?? [];

  // Count of all descendants (direct + nested) for the section header.
  const descendantCount = (() => {
    let total = 0;
    const stack = [...directChildren];
    while (stack.length > 0) {
      const c = stack.pop()!;
      total++;
      for (const k of byParent.get(c.id) ?? []) stack.push(k);
    }
    return total;
  })();

  const inStreams: { stream: string; stage: ValueStreamStage }[] = [];
  for (const s of valueStreams) {
    for (const stage of s.stages) {
      if (
        stage.capability_id === node.id ||
        node.id.startsWith(stage.capability_id + ".")
      ) {
        inStreams.push({ stream: s.name, stage });
      }
    }
  }

  const industries = splitIndustry(node.industry);

  return (
    <div class="detail-modal-root">
      <div class="detail-modal-backdrop" onClick={onClose} />
      <aside
        class="detail-modal"
        role="dialog"
        aria-modal="true"
        aria-label={`${node.id} ${node.name}`}
      >
        <header class="detail-modal-header">
          <nav class="detail-modal-breadcrumb" aria-label="Capability path">
            <a class="detail-modal-crumb" href="/">Catalog</a>
            {ancestors.map((a) => (
              <span key={a.id} class="detail-modal-crumb-wrap">
                <span class="detail-modal-crumb-sep" aria-hidden="true">/</span>
                <button
                  type="button"
                  class="detail-modal-crumb"
                  onClick={() => onOpen(a.id)}
                >
                  {a.name}
                </button>
              </span>
            ))}
            <span class="detail-modal-crumb-sep" aria-hidden="true">/</span>
            <span class="detail-modal-crumb is-current" aria-current="page">{node.name}</span>
          </nav>
          <button
            type="button"
            class="detail-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            <span class="material-symbols-outlined" aria-hidden="true">close</span>
          </button>
        </header>

        <div class="detail-modal-body">
          <section class="detail-modal-hero">
            <div class="detail-modal-hero-meta">
              <span class="cap-id">{node.id}</span>
              <span class="cap-level">L{node.level}</span>
              {node.deprecated && <span class="cap-deprecated-badge">Deprecated</span>}
            </div>
            <h2 class="detail-modal-title">{node.name}</h2>
            {node.deprecated && node.deprecation_reason && (
              <div class="deprecation-banner">
                <strong>Deprecated.</strong> {node.deprecation_reason}
              </div>
            )}
            {node.description && (
              <p class="detail-modal-desc">{node.description}</p>
            )}
          </section>

          <section class="detail-meta-grid">
            {industries.length > 0 && (
              <div>
                <div class="meta-key">Industry</div>
                <div class="meta-val tag-list">
                  {industries.map((i) => (
                    <span key={i} class="cap-industry">{i}</span>
                  ))}
                </div>
              </div>
            )}
            {node.aliases && node.aliases.length > 0 && (
              <div>
                <div class="meta-key">Aliases</div>
                <div class="meta-val">{node.aliases.join(", ")}</div>
              </div>
            )}
            {node.references && node.references.length > 0 && (
              <div>
                <div class="meta-key">References</div>
                <div class="meta-val detail-modal-refs">
                  {node.references.map((r) => (
                    <a key={r} href={r} target="_blank" rel="noopener">{r}</a>
                  ))}
                </div>
              </div>
            )}
            {inStreams.length > 0 && (
              <div class="detail-modal-streams-cell">
                <div class="meta-key">Value streams</div>
                <ul class="meta-val detail-modal-streams">
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
          </section>

          {directChildren.length > 0 && (
            <section class="detail-modal-children">
              <h3 class="detail-modal-section-title">
                Subtree
                <span class="detail-modal-section-count">
                  {descendantCount} {descendantCount === 1 ? "descendant" : "descendants"}
                </span>
              </h3>
              <div class="modal-tree">
                {directChildren.map((c) => (
                  <ModalTreeNode key={c.id} node={c} byParent={byParent} />
                ))}
              </div>
            </section>
          )}
        </div>

        <footer class="detail-modal-footer">
          <a
            class="btn"
            href={githubYamlUrl}
            target="_blank"
            rel="noopener"
          >
            View on GitHub
          </a>
          <button
            type="button"
            class="btn"
            onClick={() => {
              const rows: FlatCap[] = [node];
              const stack = [...directChildren];
              while (stack.length > 0) {
                const c = stack.pop()!;
                rows.push(c);
                for (const k of byParent.get(c.id) ?? []) stack.push(k);
              }
              rows.sort((a, b) => compareIds(a.id, b.id));
              download(
                `${node.id}-subtree-${rows.length}.csv`,
                toCsv(rows),
                "text/csv"
              );
            }}
          >
            Export CSV ({descendantCount + 1})
          </button>
        </footer>
      </aside>
    </div>
  );
}
