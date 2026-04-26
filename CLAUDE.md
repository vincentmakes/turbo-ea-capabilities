# CLAUDE.md

Always-on guardrails for any Claude Code session in this repo. Procedural workflows live in `.claude/skills/`; this file only encodes the invariants that protect the catalogue from accidental damage.

## What this repo is

An open-source Business Capability Reference Catalogue. YAML files in `catalogue/` are the **single source of truth**. Everything else (`dist/api/*.json`, the bundled Python package data, the Astro site) is built from those YAML files.

## Invariants — do not break these

- **Source of truth:** edit only `catalogue/*.yaml` and `schema/capability.schema.json`. Never hand-edit `dist/api/**` or `packages/py/src/turbo_ea_capabilities/data/**`. Both are build artefacts and are wiped by the next `npm run build`.
- **ID format:** `BC-<L1>[.<L2>[.<L3>[.<L4>]]]`. Max depth is **L4**. If L5 feels needed, the model has slipped into process territory — push it to the process layer.
- **MECE:** within any parent, children must be Mutually Exclusive and Collectively Exhaustive.
- **Names are noun phrases:** Title Case, 2–5 words, no verbs, no articles, no vendor / product / org / geography names, no value-stream names (e.g. *Order-to-Cash* is a value stream, not a capability).
- **Sparse numbering:** new siblings use 10, 20, 30, … to leave room for inserts. Retired IDs are **never reused**.
- **Single parent:** a capability has exactly one parent. For multi-use, model a *shared service* relationship — not a multi-parent edge.
- **Deprecation:** `deprecated: true` requires `deprecation_reason` and (when applicable) `successor_id`.
- **Industry tag:** `Cross-Industry`, a single industry name, or `;`-separated list. L2+ inherits from L1 unless overridden.

## Translations — sidecar invariants

- **Source = English; translations = sidecars.** `catalogue/L1-*.yaml` is the canonical English source of truth. Translations live at `catalogue/i18n/<bcp47>/L1-<same-slug>.yaml` and are validated against `schema/i18n.schema.json`.
- **Translatable fields whitelist:** `name`, `description`, `aliases`, `in_scope`, `out_of_scope`. **Never** translate `id`, `level`, `industry`, `references`, `deprecated`, `successor_id`, or `metadata` — those stay in the English source and are inherited by every locale.
- **One sidecar per (locale, L1).** Filename mirrors the source slug so per-L1 CODEOWNERS apply transitively.
- **No orphans.** Every entry id in a sidecar must resolve to a node in the source L1 tree. After a `cap:mv` or `cap:deprecate` the corresponding sidecar entries must be updated or removed in the same PR — lint blocks otherwise.
- **Locale tag = directory name.** `catalogue/i18n/fr-CA/...` files must declare `locale: fr-CA`. BCP-47 only.
- **Bundle layout is additive.** `dist/api/capabilities.json`, `tree.json`, etc. stay English. Locale data ships separately under `dist/api/i18n/<locale>.json` and `dist/api/locales.json` — old consumers are unaffected.

## Use the existing helpers — don't reinvent

```bash
npm run cap:add        -- --parent BC-100.10 --name "Forecast Reconciliation"
npm run cap:mv         -- --id BC-300.10 --new-parent BC-100.10
npm run cap:deprecate  -- --id BC-300.10 --successor BC-100.10 --reason "Merged"
npm run lint           # required before commit
npm run build          # generates dist/api/, site/, package data
```

`scripts/cli/add.ts`, `mv.ts`, and `deprecate.ts` preserve YAML formatting and compute next IDs deterministically. Driving them is safer than emitting YAML by hand.

## Workflow

1. Branch off `main` (or work on the feature branch you were assigned).
2. Use the helper CLIs or edit YAML directly under `catalogue/`.
3. Run `npm run lint` — a failing lint is a hard block on merge.
4. Open a PR. `CODEOWNERS` for the L1 file you touched is auto-requested for review.

## Skills available in this repo

- `/generate-capability` — draft new L1s or extend existing ones with MECE L2/L3 trees, industry-aware references, and metadata. Drives `cap:add` for ID safety.
- `/map-value-streams` — propose stages in `catalogue/_value-streams.yaml` for one or more L1s, with optional industry variants.
- `/translate-language` — generate or refresh sidecar translations under `catalogue/i18n/<locale>/`. Whole-Language mode covers every L1; Single-L1 mode covers one. Writes sidecar YAML directly and re-runs `npm run lint`.

## Canonical docs

- [`business-capability-governance-model.md`](business-capability-governance-model.md) — **Part A** reference model (definition, levels, decomposition, naming, identifiers, metadata, worked example) and **Part B** operational governance (PR workflow, lint rules, versioning, promotion).
- [`schema/capability.schema.json`](schema/capability.schema.json) — authoritative JSON Schema for catalogue YAML.
- [`catalogue/_index.yaml`](catalogue/_index.yaml) — registry of all L1 files; lint enforces every L1 file is indexed.
- [`catalogue/_value-streams.yaml`](catalogue/_value-streams.yaml) — orthogonal value-stream artefact; stages reference capability IDs.
- [`schema/i18n.schema.json`](schema/i18n.schema.json) — JSON Schema for translation sidecar files under `catalogue/i18n/<locale>/`.
