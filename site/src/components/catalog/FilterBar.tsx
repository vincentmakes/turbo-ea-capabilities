// SPDX-License-Identifier: MIT
import { useEffect, useRef, useState } from "react";

interface FilterBarProps {
  query: string;
  onQuery: (q: string) => void;
  allLevels: number[];
  levels: Set<number>;
  onLevels: (s: Set<number>) => void;
  allIndustries: string[];
  industries: Set<string>;
  onIndustries: (s: Set<string>) => void;
  /** When provided, renders a "Value stream" multi-select. Empty array hides it. */
  valueStreamNames?: string[];
  valueStreamGroups?: { label: string; options: string[] }[];
  streams?: Set<string>;
  onStreams?: (s: Set<string>) => void;
  onReset: () => void;
}

export function FilterBar({
  query,
  onQuery,
  allLevels,
  levels,
  onLevels,
  allIndustries,
  industries,
  onIndustries,
  valueStreamNames,
  valueStreamGroups,
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
          highlight="Cross-Industry"
        />
      )}

      {valueStreamNames && valueStreamNames.length > 0 && streams && onStreams && (
        <MultiSelect
          label="Value stream"
          options={valueStreamNames}
          groups={valueStreamGroups}
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

interface MultiSelectProps {
  label: string;
  options: string[];
  groups?: { label: string; options: string[] }[];
  selected: Set<string>;
  onChange: (next: Set<string>) => void;
  highlight?: string;
}

export function MultiSelect({
  label,
  options,
  groups,
  selected,
  onChange,
  highlight,
}: MultiSelectProps) {
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
          {groups && groups.length > 0
            ? groups.map((g) => (
                <div key={g.label} class="multi-select-group">
                  <div class="multi-select-group-label">{g.label}</div>
                  {g.options.map((opt) => (
                    <label
                      key={`${g.label}::${opt}`}
                      class={`multi-select-option${opt === highlight ? " is-highlight" : ""}`}
                    >
                      <input
                        type="checkbox"
                        checked={selected.has(opt)}
                        onChange={() => toggle(opt)}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              ))
            : options.map((opt) => (
                <label
                  key={opt}
                  class={`multi-select-option${opt === highlight ? " is-highlight" : ""}`}
                >
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
