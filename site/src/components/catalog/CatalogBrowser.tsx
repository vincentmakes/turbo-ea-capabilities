import { useEffect, useMemo, useRef, useState } from "react";
import { FilterBar } from "./FilterBar";
import {
  CATALOG_KINDS,
  type CatalogKind,
  type FlatNode,
  type ValueStream,
  type ValueStreamStage,
} from "./types";
import { compareIds, download, splitIndustry, toCsv } from "./exporters";

interface Props {
  kind: CatalogKind;
  data: FlatNode[];
  /** Pass to enable value-stream cross-reference filter and modal display.
   *  Omit on the value-streams page itself. */
  valueStreams?: ValueStream[];
}

export default function CatalogBrowser({ kind, data, valueStreams = [] }: Props) {
  const config = CATALOG_KINDS[kind];

  const byId = useMemo(() => {
    const m = new Map<string, FlatNode>();
    for (const c of data) m.set(c.id, c);
    return m;
  }, [data]);

  const byParent = useMemo(() => {
    const map = new Map<string | null, FlatNode[]>();
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

  const allLevels = useMemo(() => {
    const s = new Set<number>();
    for (const c of data) s.add(c.level);
    return Array.from(s).sort((a, b) => a - b);
  }, [data]);

  const allIndustries = useMemo(() => {
    const s = new Set<string>();
    for (const c of data) for (const ind of splitIndustry(c.industry)) s.add(ind);
    const sorted = Array.from(s).sort();
    const cross = sorted.filter((i) => i === "Cross-Industry");
    const rest = sorted.filter((i) => i !== "Cross-Industry");
    return [...cross, ...rest];
  }, [data]);

  const valueStreamNames = useMemo(
    () => valueStreams.map((v) => v.name).sort(),
    [valueStreams],
  );

  const valueStreamsByIndustry = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const stream of valueStreams) {
      for (const ind of stream.industries ?? []) {
        const list = map.get(ind) ?? [];
        list.push(stream.name);
        map.set(ind, list);
      }
    }
    for (const list of map.values()) list.sort();
    return map;
  }, [valueStreams]);

  /** node id → set of value-stream names it (or its ancestor) participates in. */
  const valueStreamsByNode = useMemo(() => {
    const map = new Map<string, Set<string>>();
    if (valueStreams.length === 0) return map;
    const add = (id: string, name: string) => {
      const set = map.get(id) ?? new Set<string>();
      set.add(name);
      map.set(id, set);
    };
    for (const stream of valueStreams) {
      for (const stage of stream.stages) {
        const refs =
          kind === "process"
            ? (stage.process_ids ?? [])
            : (stage.capability_ids ?? []);
        for (const refId of refs) {
          add(refId, stream.name);
          for (const d of descendantsOf.get(refId) ?? []) {
            add(d, stream.name);
          }
        }
      }
    }
    return map;
  }, [valueStreams, descendantsOf, kind]);

  const [query, setQuery] = useState("");
  const [levels, setLevels] = useState<Set<number>>(() => new Set(allLevels));
  const [industries, setIndustries] = useState<Set<string>>(new Set());
  const [streams, setStreams] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<Set<string>>(() => {
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
        const cs = valueStreamsByNode.get(c.id);
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
  }, [data, levels, industries, streams, query, valueStreamsByNode]);

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

  const maxLevel = useMemo(() => {
    let m = 1;
    for (const c of data) if (c.level > m) m = c.level;
    return m;
  }, [data]);

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

  const exportSelection = (kindOut: "csv" | "json") => {
    const rows = data
      .filter((c) => selected.has(c.id))
      .sort((a, b) => compareIds(a.id, b.id));
    if (rows.length === 0) return;
    if (kindOut === "json") {
      download(
        `${config.exportStem}-selection-${rows.length}.json`,
        JSON.stringify(rows, null, 2),
        "application/json",
      );
    } else {
      download(
        `${config.exportStem}-selection-${rows.length}.csv`,
        toCsv(rows, byId),
        "text/csv",
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

  const groupedRoots = new Map<string, FlatNode[]>();
  for (const root of roots) {
    const primaryIndustry = splitIndustry(root.industry)[0] ?? "Other";
    const bucket = groupedRoots.get(primaryIndustry) ?? [];
    bucket.push(root);
    groupedRoots.set(primaryIndustry, bucket);
  }
  const groupIndustryKeys = Array.from(groupedRoots.keys());
  const orderedGroupIndustries = [
    ...groupIndustryKeys.filter((n) => n === "Cross-Industry"),
    ...groupIndustryKeys.filter((n) => n !== "Cross-Industry").sort(),
  ];

  const valueStreamGroups = useMemo(() => {
    const groups: { label: string; options: string[] }[] = [];
    const cross = valueStreamsByIndustry.get("Cross-Industry") ?? [];
    if (cross.length > 0) groups.push({ label: "Cross-Industry", options: cross });
    const namedIndustries = Array.from(valueStreamsByIndustry.keys())
      .filter((k) => k !== "Cross-Industry")
      .filter((k) => industries.size === 0 || industries.has(k))
      .sort();
    for (const ind of namedIndustries) {
      const opts = valueStreamsByIndustry.get(ind) ?? [];
      if (opts.length > 0) groups.push({ label: ind, options: opts });
    }
    return groups;
  }, [valueStreamsByIndustry, industries]);

  return (
    <div class="catalogue-page">
      <div class="sticky-controls">
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
          valueStreamGroups={valueStreamGroups}
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
      </div>

      {roots.length === 0 ? (
        <div class="no-results">
          <h3>No matches</h3>
          <p>Adjust your filters or search query.</p>
        </div>
      ) : (
        <>
          {orderedGroupIndustries.map((industry) => (
            <section class="industry-group" key={industry}>
              <h2 class="industry-group-title">{industry}</h2>
              <div class="l1-grid">
                {(groupedRoots.get(industry) ?? []).map((r) => (
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
            </section>
          ))}
        </>
      )}

      {detail && (
        <DetailModal
          kind={kind}
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
// L1 Card (top-level column in the grid)
// ---------------------------------------------------------------------------
interface L1CardProps {
  node: FlatNode;
  byParent: Map<string | null, FlatNode[]>;
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
  node: FlatNode;
  byParent: Map<string | null, FlatNode[]>;
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
// ModalTreeNode
// ---------------------------------------------------------------------------
function ModalTreeNode({
  node,
  byParent,
}: {
  node: FlatNode;
  byParent: Map<string | null, FlatNode[]>;
}) {
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
// DetailModal
// ---------------------------------------------------------------------------
interface DetailModalProps {
  kind: CatalogKind;
  node: FlatNode;
  byId: Map<string, FlatNode>;
  byParent: Map<string | null, FlatNode[]>;
  valueStreams: ValueStream[];
  onOpen: (id: string) => void;
  onClose: () => void;
}

function DetailModal({
  kind,
  node,
  byId,
  byParent,
  valueStreams,
  onOpen,
  onClose,
}: DetailModalProps) {
  const config = CATALOG_KINDS[kind];

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

  const ancestors: FlatNode[] = [];
  let cursor = node.parent_id;
  while (cursor) {
    const a = byId.get(cursor);
    if (!a) break;
    ancestors.unshift(a);
    cursor = a.parent_id;
  }

  const root = ancestors[0] ?? node;
  const githubYamlUrl = config.githubPathFor(node, root.name);

  const directChildren = byParent.get(node.id) ?? [];

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

  // Capability-only: scan all stages for capability_ids matching node or ancestor
  const inStreams: { stream: string; stage: ValueStreamStage }[] = [];
  if (kind === "capability") {
    for (const s of valueStreams) {
      for (const stage of s.stages) {
        const matches = (stage.capability_ids ?? []).some(
          (cid) => cid === node.id || node.id.startsWith(cid + "."),
        );
        if (matches) {
          inStreams.push({ stream: s.name, stage });
        }
      }
    }
  } else if (kind === "process") {
    for (const s of valueStreams) {
      for (const stage of s.stages) {
        const matches = (stage.process_ids ?? []).some(
          (pid) => pid === node.id || node.id.startsWith(pid + "."),
        );
        if (matches) {
          inStreams.push({ stream: s.name, stage });
        }
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
          <nav class="detail-modal-breadcrumb" aria-label="Path">
            <a class="detail-modal-crumb" href={config.breadcrumbHref}>
              {config.breadcrumbLabel}
            </a>
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
            {kind === "process" && node.realizes_capability_ids && node.realizes_capability_ids.length > 0 && (
              <div>
                <div class="meta-key">Realizes capabilities</div>
                <div class="meta-val tag-list">
                  {node.realizes_capability_ids.map((cid) => (
                    <a key={cid} class="cap-industry" href={`/capability/${cid}`}>{cid}</a>
                  ))}
                </div>
              </div>
            )}
            {kind === "value-stream" && node.capability_ids && node.capability_ids.length > 0 && (
              <div>
                <div class="meta-key">Capabilities</div>
                <div class="meta-val tag-list">
                  {node.capability_ids.map((cid) => (
                    <a key={cid} class="cap-industry" href={`/capability/${cid}`}>{cid}</a>
                  ))}
                </div>
              </div>
            )}
            {kind === "value-stream" && node.process_ids && node.process_ids.length > 0 && (
              <div>
                <div class="meta-key">Processes</div>
                <div class="meta-val tag-list">
                  {node.process_ids.map((pid) => (
                    <a key={pid} class="cap-industry" href={`/business-process/${pid}`}>{pid}</a>
                  ))}
                </div>
              </div>
            )}
            {inStreams.length > 0 && (
              <div class="detail-modal-streams-cell">
                <div class="meta-key">Value streams</div>
                <ul class="meta-val detail-modal-streams">
                  {inStreams.map(({ stream, stage }, idx) => (
                    <li key={`${stream}-${stage.id}-${idx}`}>
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
              const rows: FlatNode[] = [node];
              const stack = [...directChildren];
              while (stack.length > 0) {
                const c = stack.pop()!;
                rows.push(c);
                for (const k of byParent.get(c.id) ?? []) stack.push(k);
              }
              rows.sort((a, b) => compareIds(a.id, b.id));
              download(
                `${node.id}-subtree-${rows.length}.csv`,
                toCsv(rows, byId),
                "text/csv",
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
