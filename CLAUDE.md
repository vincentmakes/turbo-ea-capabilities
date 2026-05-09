# CLAUDE.md

Always-on guardrails for any Claude Code session in this repo. Procedural workflows live in `.claude/skills/`; this file only encodes the invariants that protect the catalogue from accidental damage.

## What this repo is

An open-source Business Architecture Reference Catalogue with **three orthogonal artefacts**: capabilities (BC) describe WHAT, business processes (BP) describe HOW, value streams (VS) describe end-to-end value delivery. YAML files in `catalogue/` are the **single source of truth**. Everything else (`dist/api/*.json`, the bundled Python package data, the Astro site) is built from those YAML files.

## Invariants — capabilities (BC-)

- **Source of truth:** edit only `catalogue/*.yaml` and `schema/capability.schema.json`. Never hand-edit `dist/api/**` or `packages/py/src/turbo_ea_capabilities/data/**`. Both are build artefacts and are wiped by the next `npm run build`.
- **ID format:** `BC-<L1>[.<L2>[.<L3>[.<L4>]]]`. Max depth is **L4**. If L5 feels needed, the model has slipped into process territory — push it into the process layer (`BP-` ids).
- **MECE:** within any parent, children must be Mutually Exclusive and Collectively Exhaustive.
- **Names are noun phrases:** Title Case, 2–5 words, no verbs, no articles, no vendor / product / org / geography names, no value-stream names (e.g. *Order-to-Cash* is a value stream, not a capability).
- **Sparse numbering:** new siblings use 10, 20, 30, … to leave room for inserts. Retired IDs are **never reused**.
- **Single parent:** a capability has exactly one parent. For multi-use, model a *shared service* relationship — not a multi-parent edge.
- **Deprecation:** `deprecated: true` requires `deprecation_reason` and (when applicable) `successor_id`.
- **Industry tag:** `Cross-Industry`, a single industry name, or `;`-separated list. L2+ inherits from L1 unless overridden.

## Invariants — value streams (VS-)

- **Source of truth:** `catalogue/_value-streams.yaml` (single file). Schema: `schema/value-stream.schema.json`.
- **Stream id:** `VS-<n>` sparse 10/20/30. Names use the bookend pattern `<Trigger>-to-<Outcome>`.
- **Stage id:** `VS-<n>.<m>` sparse 10/20/30. Stable across reorderings — `stage_order` is the visual rank, not part of identity.
- **Stage `capability_ids` are L1 only.** Use `notes` to capture sub-scope detail. Stage `process_ids` may resolve at any BP depth.
- Industry vocabulary inherited from BC L1s. `Cross-Industry` must stand alone.

## Invariants — business processes (BP-)

- **Source of truth:** `catalogue/processes/BP1-<slug>.yaml` (one file per Category), indexed in `catalogue/processes/_index.yaml`. Schema: `schema/business-process.schema.json`.
- **ID format:** `BP-<L1>[.<L2>[.<L3>[.<L4>]]]` mirroring BC. Max depth **L4** (Category → Group → Process → Activity per APQC PCF). BPMN-level steps belong in diagrams, not the catalogue.
- **Names are verb-phrased** (unlike capabilities): *Develop Vision and Strategy*, *Process Sales Order*.
- **Industry tag:** same scheme as capabilities. BC L1 industry vocabulary is the master list.
- **`realizes_capability_ids`** is the single source of truth for the BC↔BP link; the reverse `Capability.realizes_processes` is derived at build time.
- **`framework_refs`** for structured cross-walks to APQC-PCF, BIAN, eTOM, ITIL, SCOR, DCOR, COBIT, SHRM-BoCK, ISO-55000, ISO-31000, COSO-ERM, TOGAF, BIZBOK, ACORD, ICMM. Multiple entries per node are expected — pin a primary framework whose vernacular drives the node's name, and retain APQC-PCF as a secondary cross-walk on Cross-Industry BPs for continuity. Used alongside (not instead of) the free-form `references[]` URI list.

## Translations — sidecar invariants

- **Source = English; translations = sidecars.** `catalogue/L1-*.yaml` etc. are the canonical English source. Translations live at `catalogue/i18n/<bcp47>/...` and are validated against `schema/i18n.schema.json`. Each sidecar declares `kind: capability | value-stream | business-process`.
- **Locations:**
  - capability → `catalogue/i18n/<locale>/L1-<slug>.yaml`, `source: L1-<slug>.yaml`
  - business-process → `catalogue/i18n/<locale>/processes/BP1-<slug>.yaml`, `source: BP1-<slug>.yaml`
  - value-stream → `catalogue/i18n/<locale>/_value-streams.yaml`, `source: _value-streams.yaml`
- **Translatable fields whitelist:** capability/business-process — `name`, `description`, `aliases`, `in_scope`, `out_of_scope`. value-stream — stream-level `name`, `description`; stage-level `stage_name`, `description`, `notes`. **Never** translate ids, levels, industry, references, framework_refs, deprecated, successor_id, or metadata.
- **No orphans.** Every entry id in a sidecar must resolve to a node in the declared source. After a `cap:mv`/`cap:deprecate`/`bp:mv`/`bp:deprecate`/`vs:deprecate` the corresponding sidecar entries must be updated or removed in the same PR — lint blocks otherwise.
- **Locale tag = directory name.** `catalogue/i18n/fr-CA/...` files must declare `locale: fr-CA`. BCP-47 only.
- **Bundle layout is additive.** `dist/api/capabilities.json`, `business-processes.json`, `value-streams.json`, `tree.json`, `bp-tree.json` stay English. Locale data ships separately under `dist/api/i18n/<locale>.json` and `dist/api/locales.json` — old consumers are unaffected.

## Use the existing helpers — don't reinvent

```bash
# Capabilities
npm run cap:add        -- --parent BC-100.10 --name "Forecast Reconciliation"
npm run cap:mv         -- --id BC-300.10 --new-parent BC-100.10
npm run cap:deprecate  -- --id BC-300.10 --successor BC-100.10 --reason "Merged"

# Business processes
npm run bp:add         -- --parent BP-10.10 --name "Forecast Reconciliation" --realizes BC-100.10
npm run bp:mv          -- --id BP-30.10.20 --new-parent BP-20.10
npm run bp:deprecate   -- --id BP-30.10.20 --successor BP-30.10.10 --reason "Merged"

# Value streams
npm run vs:add         -- --name "Quote-to-Cash" --industries Cross-Industry
npm run vs:add-stage   -- --stream VS-30 --name "Quote Generation" --capabilities BC-100 [--processes BP-10.10]
npm run vs:deprecate   -- --id VS-30 --successor VS-40 --reason "Merged"

# Validation / build
npm run lint           # required before commit
npm run build          # generates dist/api/, site/, package data
```

The CLI scripts under `scripts/cli/` preserve YAML formatting and compute next IDs deterministically (sparse 10/20/30). Driving them is safer than emitting YAML by hand.

## Workflow

1. Branch off `main` (or work on the feature branch you were assigned).
2. Use the helper CLIs or edit YAML directly under `catalogue/`.
3. Run `npm run lint` — a failing lint is a hard block on merge.
4. Open a PR. `CODEOWNERS` for the L1 / BP1 file you touched is auto-requested for review.

## Skills available in this repo

- `/generate-capability` — draft new L1s or extend existing ones with MECE L2/L3 trees, industry-aware references, and metadata. Drives `cap:add` for ID safety.
- `/generate-process` — draft new BP1 process trees with MECE structure, APQC PCF alignment, and `framework_refs`. Drives `bp:add`.
- `/generate-value-stream` — propose new value streams with stages linked to capabilities and (optionally) processes. Drives `vs:add` / `vs:add-stage`.
- `/map-value-streams` — legacy alias for value-stream mapping; superseded by `/generate-value-stream`.
- `/translate-language` — generate or refresh sidecar translations under `catalogue/i18n/<locale>/`. Handles all three kinds (capability, business-process, value-stream).

## Canonical docs

- [`business-capability-governance-model.md`](business-capability-governance-model.md) — Parts A–E. Reference model (Part A), operational governance (Part B), value-stream layer (Part C), process layer (Part D), cross-layer linkage (Part E).
- [`schema/capability.schema.json`](schema/capability.schema.json) — JSON Schema for capability YAML.
- [`schema/value-stream.schema.json`](schema/value-stream.schema.json) — JSON Schema for `_value-streams.yaml`.
- [`schema/business-process.schema.json`](schema/business-process.schema.json) — JSON Schema for `processes/BP1-*.yaml`.
- [`schema/i18n.schema.json`](schema/i18n.schema.json) — JSON Schema for translation sidecars (all three kinds via `kind` discriminator).
- [`catalogue/_index.yaml`](catalogue/_index.yaml) — registry of all L1 capability files; lint enforces every L1 file is indexed.
- [`catalogue/processes/_index.yaml`](catalogue/processes/_index.yaml) — registry of all BP1 process files; same enforcement.
- [`catalogue/_value-streams.yaml`](catalogue/_value-streams.yaml) — value-stream artefact.
