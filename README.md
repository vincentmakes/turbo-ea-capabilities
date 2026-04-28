# Business Capability Reference Catalogue

An **open-source Business Capability Reference Catalogue**. It is intentionally tool-agnostic and can be used in any Enterprise Architecture management solution — well beyond [Turbo EA](https://www.turbo-ea.org). This site exists to help enterprise architects get started with the implementation of an EA function, by providing a curated, opinionated baseline that teams can adopt, adapt, and extend.

<img width="1424" height="678" alt="Screenshot 2026-04-28 at 07 39 44" src="https://github.com/user-attachments/assets/f8deb601-74f2-4b39-92ba-d234ee0494b8" />


- **Browse online:** [`capabilities.turbo-ea.org`](https://capabilities.turbo-ea.org/) — searchable web catalogue.
- **Source of truth:** YAML files in [`catalogue/`](catalogue/).
- **Public site + JSON API:** [`capabilities.turbo-ea.org`](https://capabilities.turbo-ea.org/) (Cloudflare Pages).
- **Python package:** [`turbo-ea-capabilities`](https://pypi.org/project/turbo-ea-capabilities/) on PyPI — embeds the catalogue as bundled JSON for offline / airgapped consumers.
- **Blog & EA resources:** [`turbo-ea.org/blog`](https://www.turbo-ea.org/blog/).

All governance lives in [`business-capability-governance-model.md`](business-capability-governance-model.md): **Part A** covers the reference model (definition, levels, naming, identifiers, metadata); **Part B** covers operational governance (PR workflow, lint rules, versioning, promotion).

## Layout

```
turbo-ea-capabilities/
├── catalogue/              # YAML source of truth (one file per L1)
│   ├── _index.yaml
│   ├── _value-streams.yaml
│   ├── L1-*.yaml
│   └── i18n/               # Translation sidecars (one per locale × L1)
│       └── <bcp47>/
│           └── L1-*.yaml
├── schema/                 # JSON Schema 2020-12 for the YAML shape
│   ├── capability.schema.json
│   └── i18n.schema.json    # Schema for translation sidecar files
├── scripts/                # lint, build_api, build_pkg, cli helpers
├── packages/py/            # Python package (turbo_ea_capabilities)
├── site/                   # Astro static site for browse UI + JSON API
├── .claude/skills/         # Claude Code skills for AI-assisted authoring
├── CLAUDE.md               # Always-on guardrails for Claude Code sessions
└── .github/workflows/      # lint on PRs, deploy on push, publish on tag
```

## Quick start

```bash
# Install JS deps
npm ci

# Lint the catalogue (runs on every PR)
npm run lint

# Build everything: dist/api/*.json, dist/site/, packages/py/.../data/*.json
npm run build

# Local Astro dev server (after build)
npm run dev

# Python package
cd packages/py
pip install -e ".[dev]"
pytest
python -c "from turbo_ea_capabilities import load_all, VERSION; print(VERSION, len(load_all()))"
```

## Editing the catalogue

Use the helper CLIs to keep diffs clean:

```bash
npm run cap:add       -- --parent BC-2.1 --name "Forecast Reconciliation"
npm run cap:mv        -- --id BC-3.1.2 --new-parent BC-2.1
npm run cap:deprecate -- --id BC-3.1.2 --successor BC-3.1.1 --reason "Merged into BC-3.1.1"
```

All editing rules — what's a capability, how to name it, when to deprecate — are in [`business-capability-governance-model.md`](business-capability-governance-model.md).

## AI-assisted authoring with Claude Code

Three skills under [`.claude/skills/`](.claude/skills/) help you draft governance-conformant capabilities, value-stream mappings, and translations without writing YAML by hand. All skills enforce the rules in [`business-capability-governance-model.md`](business-capability-governance-model.md) and validate the result with `npm run lint` before suggesting a commit.

> **Names, not IDs.** You always refer to capabilities by their **name** (e.g. *"Manufacturing Operations Management"*, *"Human Capital Management"*). The skills resolve names to `BC-…` identifiers internally and only show the ID back as a confirmation. You never need to look up or type an ID.

### Install

1. Install [Claude Code](https://docs.anthropic.com/claude/docs/claude-code) (CLI, desktop app, or IDE extension).
2. Clone this repo and `cd` into it.
3. Run `npm ci` once so `npm run lint` and `cap:add` are available — the skills shell out to them.
4. Open a Claude Code session in the repo root. Skills under `.claude/skills/` are auto-discovered as slash commands; `CLAUDE.md` is auto-loaded as always-on guardrails.

No additional configuration is needed.

### Scenario 1 — Generate a complete L1 layer for a new industry *(generic — preferred for greenfield)*

Stand up a whole industry's capability layer in one go. **You name only the industry** — the skill proposes the full L1 set, anchored to the industry's reference framework (BIAN, ICH, ISA-95, ICAO, ACORD, eTOM, …). If the industry's frameworks aren't yet documented in the governance doc, the skill researches them and **adds them to §9.8 in the same flow** so future work has a stable anchor.

```
/generate-capability --industry Insurance
```

The skill will:

1. Read the governance model, schema, and any existing L1s in the closest industries for naming/depth tone.
2. **Audit `business-capability-governance-model.md` §9.8** for the target industry's reference frameworks. If the industry is missing or only listed under "Other industry anchors not yet exercised", research the canonical standards (capability/process anchor, regulatory regime, quality/safety, reporting, data interchange) and propose them. Examples — Insurance: ACORD + Solvency II + IFRS 17 + ISO 31000 + IAIS ICPs; Mining: ICMM + JORC/SAMREC + GISTM + ISO 14001/45001; Telco: eTOM + TM Forum SID + 3GPP + ETSI.
3. Propose a **complete L1 list** for the industry (typically 8–14 L1s — matching the existing distribution: Banking 11, Pharma 10, Defense 8, ATC 7) with one-line descriptions. **You don't name them — the skill does.**
4. Skip L1s that already exist as Cross-Industry capabilities (Financial, HR, IT, Procurement, etc.).
5. Show the §9.8 update + the L1 list + the proposed BC-id allocations together as **one combined approval**.
6. After approval, edit `business-capability-governance-model.md` §9.8 (promote the industry to its own subsection or add it from scratch), then draft 5–9 L2s + 3–7 L3s per L2 for every L1.
7. Write each `catalogue/L1-<kebab-case-name>.yaml` with the full L1→L2→L3 tree inline, citing the new §9.8 entries in `references`, and register them all in `catalogue/_index.yaml`.
8. Run `npm run lint && npm run build:api`.

### Scenario 2 — Create one new L1

Stand up a single new top-level capability when you already know it's the right shape (e.g. *Insurance Underwriting Management*, *Telco Network Operations Management*).

```
/generate-capability "Insurance Underwriting Management" --industry Insurance
```

The skill will:

1. Confirm the proposed L1 name passes the §5 naming tests (noun phrase, no verbs/vendors/value-stream names, 2–5 words, Title Case).
2. Pick the next sparse L1 ID automatically (e.g. `BC-2100`) and show it as a single confirmation alongside the name — not as a separate question.
3. Read peer L1s in the closest existing industry to absorb depth and tone.
4. Draft 5–9 L2 children + 3–7 L3 children per L2 for your review.
5. Cite relevant industry frameworks in `references`.
6. Write `catalogue/L1-<kebab-case-name>.yaml` and append the entry to `catalogue/_index.yaml`.
7. Run `npm run lint && npm run build:api`.

### Scenario 3 — Extend an existing L1

Add new L2 / L3 capabilities under an L1 you already have (e.g. fill out a sparse industry, add a missing branch).

```
/generate-capability "Manufacturing Operations Management"
```

The skill will:

1. Resolve the name to its L1 file. If the name is ambiguous it will list candidates and ask you to pick.
2. Read the L1, the governance model, and 1–2 peers in the same industry for naming style.
3. Ask which L2 you want to extend (by name) — or whether to add new L2s.
4. Draft the additions (5–9 L2s, 3–7 L3s per L2) for your review.
5. Drive `npm run cap:add` so IDs and sort order are computed by the existing TypeScript helper.
6. Patch `description`, `industry`, `in_scope`, `out_of_scope` on the new nodes only.
7. Run `npm run lint`; fix any failures.

### Scenario 4 — Autonomously map L1s to value streams

`/map-value-streams` decides on its own which streams an L1 participates in, picks the L2/L3 anchor for each stage, sets `industry_variant` where warranted, and presents **one batched proposal** for approval. It does **not** ask per-stage questions.

```
# one L1
/map-value-streams "Human Capital Management"

# several L1s at once
/map-value-streams "Human Capital Management" "Marketing Management" "Defense Personnel Management"

# everything in an industry
/map-value-streams --industry "Banking & Capital Markets"

# everything in the catalogue not yet covered
/map-value-streams --all
```

The skill will:

1. Resolve the L1 name(s) — or scan all L1s tagged with the given industry — to their files.
2. Read existing streams in `_value-streams.yaml` to avoid duplication.
3. Decide autonomously which canonical or industry-specific streams each L1 participates in (Hire-to-Retire, Order-to-Cash, Onboard-to-Activate, Trade-to-Settle, Adverse-Event-to-Action, Flight-Plan-to-Landing, …).
4. Anchor each stage at the appropriate L2 or L3 child (L1s are usually too broad).
5. Apply `industry_variant` only when stage logic genuinely differs.
6. Print the entire mapping as one table grouped by stream, showing capability names with resolved IDs in parentheses.
7. Wait for **a single approval of the whole batch** — accept "approve", "approve except <X>", or "redo with <change>".
8. Edit `_value-streams.yaml` preserving formatting and `stage_order`; run `npm run lint`.

### Scenario 5 — Translate the catalogue into another language

Generate or refresh sidecar translation files under `catalogue/i18n/<locale>/`. The English source files (`catalogue/L1-*.yaml`) are never modified — translations are purely additive. Locale-neutral fields (`id`, `level`, `industry`, `references`, `deprecated`, `successor_id`, `metadata`) are never duplicated in sidecars; they are inherited from the source at build time.

**Whole-Language mode** — translates every L1 in the catalogue in one go:

```
/translate-language French
/translate-language "Brazilian Portuguese"
/translate-language German
```

**Single-L1 mode** — translates or refreshes exactly one L1:

```
/translate-language "Human Capital Management" --language French
```

The skill will:

1. Resolve the language name to a BCP-47 tag (French → `fr`, Brazilian Portuguese → `pt-BR`, Simplified Chinese → `zh-Hans`, …) and display it once for confirmation.
2. Scan `catalogue/i18n/` for existing sidecars — defaulting to **skip-existing** strategy so prior manual edits are preserved; supports `--fill-gaps` and `--overwrite` modes.
3. Translate only the whitelisted fields: `name`, `description`, `aliases`, `in_scope`, `out_of_scope`. All other fields stay in the English source.
4. Maintain a consistent cross-L1 glossary so the same source term always maps to the same target-language equivalent throughout the catalogue.
5. Write sidecar YAML to `catalogue/i18n/<locale>/L1-<slug>.yaml`, mirroring the English source filename exactly so per-L1 CODEOWNERS apply transitively.
6. Run `npm run lint` to validate all sidecars against [`schema/i18n.schema.json`](schema/i18n.schema.json).

### After the skill runs

The skills do not commit or push for you. After lint passes:

```bash
git diff                              # review the YAML changes
git add catalogue/                    # or specific files
git commit -m "Add <capability>"
git push
```

Open a PR. CODEOWNERS for the touched L1 file is auto-requested for review. The CI pipeline runs the same `npm run lint` you ran locally — a failing lint blocks merge.

### Anti-patterns the skills will refuse

Both skills reject (and suggest a rewrite for) names that contain verbs, gerunds with objects, vendor / product / org / geography references, or value-stream names (*Order-to-Cash* is a stream, not a capability — it goes in `_value-streams.yaml`). The full anti-pattern list is in [`business-capability-governance-model.md`](business-capability-governance-model.md) §5.3.

## Static API

After `npm run build`, the following endpoints are available under `dist/api/` (and at `capabilities.turbo-ea.org/api/`):

| Path | Returns |
| --- | --- |
| `GET /api/version.json` | `{catalogue_version, schema_version, generated_at, node_count}` |
| `GET /api/capabilities.json` | Flat array of every node, sorted by id |
| `GET /api/tree.json` | Nested tree (one entry per L1) |
| `GET /api/by-l1/<slug>.json` | Single L1 nested subtree |
| `GET /api/capability/<id>.json` | One node + its direct children |
| `GET /api/locales.json` | List of available translation locales |
| `GET /api/i18n/<locale>.json` | All translated strings for a locale |

All responses are static, immutable per build, and cacheable by Cloudflare's edge. The English endpoints (`capabilities.json`, `tree.json`, etc.) are unaffected by translations — locale data is additive and ships separately under `/api/i18n/`.

## Licence

[MIT](LICENSE).
