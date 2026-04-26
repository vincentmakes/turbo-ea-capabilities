# turbo-ea-capabilities

An **open-source Business Capability Reference Catalogue**. It is intentionally tool-agnostic and can be used in any Enterprise Architecture management solution — well beyond [Turbo EA](https://www.turbo-ea.org). This site exists to help enterprise architects get started with the implementation of an EA function, by providing a curated, opinionated baseline that teams can adopt, adapt, and extend.

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
│   └── L1-*.yaml
├── schema/                 # JSON Schema 2020-12 for the YAML shape
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

Two skills under [`.claude/skills/`](.claude/skills/) help you draft governance-conformant capabilities and value-stream mappings without writing YAML by hand. Both skills enforce the rules in [`business-capability-governance-model.md`](business-capability-governance-model.md) and validate the result with `npm run lint` before suggesting a commit.

### Install

1. Install [Claude Code](https://docs.anthropic.com/claude/docs/claude-code) (CLI, desktop app, or IDE extension).
2. Clone this repo and `cd` into it.
3. Run `npm ci` once so `npm run lint` and `cap:add` are available — the skills shell out to them.
4. Open a Claude Code session in the repo root. Skills under `.claude/skills/` are auto-discovered as slash commands; `CLAUDE.md` is auto-loaded as always-on guardrails.

No additional configuration is needed.

### Scenario 1 — Extend an existing L1

Add new L2 / L3 capabilities under an L1 you already have (e.g. fill out a sparse industry, add a missing branch).

```
/generate-capability BC-1010
```

The skill will:

1. Read the target L1, the governance model, and 1–2 peers in the same industry for naming style.
2. Ask which L2 (and depth) you want to add.
3. Draft the L2 list (5–9 children, MECE, noun phrases) for your review.
4. Draft L3s (3–7 per L2) for your review.
5. Drive `npm run cap:add` so IDs and sort order are computed by the existing TypeScript helper.
6. Patch `description`, `industry`, `in_scope`, `out_of_scope` on the new nodes only.
7. Run `npm run lint`; fix any failures.

### Scenario 2 — Create a new L1 for a new or under-covered industry

Stand up a brand-new L1 (e.g. *Insurance Underwriting Management*, *Telco Network Operations Management*).

```
/generate-capability "Insurance Underwriting Management" --industry Insurance
```

The skill will:

1. Confirm the proposed L1 name passes the §5 naming tests (noun phrase, no verbs/vendors/value-stream names, 2–5 words, Title Case).
2. Pick the next sparse L1 ID (e.g. `BC-2100`) and confirm with you.
3. Read peer L1s in the closest existing industry to absorb depth and tone.
4. Draft 5–9 L2 children + 3–7 L3 children per L2 for your review.
5. Cite relevant industry frameworks in `references` (BIAN, ICH, ISA-95, ICAO, ACORD, eTOM, …) — see the cheat sheet in the skill.
6. Write `catalogue/L1-<kebab-case-name>.yaml` and append the entry to `catalogue/_index.yaml`.
7. Run `npm run lint && npm run build:api`.

### Scenario 3 — Map an L1 to value streams

Wire a capability into one or more end-to-end flows (Hire-to-Retire, Order-to-Cash, Procure-to-Pay, …) by adding stages to `catalogue/_value-streams.yaml`.

```
/map-value-streams BC-300
```

Or for several L1s at once:

```
/map-value-streams BC-300 BC-1810 BC-400
```

The skill will:

1. Read existing streams in `_value-streams.yaml` to avoid duplication.
2. Identify which canonical streams each L1 participates in (or propose a new one with rationale).
3. Anchor each stage at an L2 or L3 ID (L1s are usually too broad to be a stage).
4. Apply `industry_variant` only when stage logic genuinely differs by industry (not just to tag the industry).
5. Show the proposed stages as a table for your review.
6. Edit `_value-streams.yaml` preserving formatting and `stage_order`.
7. Run `npm run lint` (lint rejects unresolved `capability_id`).

### Scenario 4 — Expand value-stream coverage across all L1s

Bulk-map an industry's L1s into value streams — useful when you've added several new L1s and want them wired in consistently.

```
/map-value-streams --industry "Banking & Capital Markets"
```

The skill iterates the L1s tagged for that industry and proposes stages in existing streams (Apply-to-Fund, Trade-to-Settle, Onboard-to-Activate, etc.), one stream at a time, with confirmation before writing.

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

All responses are static, immutable per build, and cacheable by Cloudflare's edge.

## Licence

[MIT](LICENSE).
