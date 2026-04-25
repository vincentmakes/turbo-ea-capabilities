# Governance

The full governance and naming conventions live in [`business-capability-governance-model.md`](business-capability-governance-model.md). This file describes the **operational** rules of working in this repository — how to propose, review, and ship a change.

## Source of truth

The catalogue is **YAML in `catalogue/`**, full stop. Every node, every field, every value lives there.

- The schema in [`schema/capability.schema.json`](schema/capability.schema.json) is authoritative. Lint rejects anything that does not validate against it.
- `dist/api/*.json` and the bundled Python package data are **build artefacts** — never edited by hand and never a source of truth.
- The original `business-capability-catalogue.xlsx` was a one-time seed and has been removed from the repo. It is not part of the workflow. Re-importing from a spreadsheet is not supported. The historical bootstrap script (`scripts/ingest_xlsx.py`) is kept for archaeology only and must not be used to introduce new records.
- Any new capability, value-stream stage, or metadata change **must** be introduced as a YAML edit in a pull request that passes `npm run lint`. There is no other path.

## How to propose a change

1. Branch off `main`.
2. Edit the relevant `catalogue/L1-*.yaml` (or `catalogue/_value-streams.yaml` for value-stream links), or use the helper CLIs:
   ```bash
   npm run cap:add        -- --parent BC-100.10 --name "Forecast Reconciliation"
   npm run cap:mv         -- --id BC-300.10 --new-parent BC-100.10
   npm run cap:deprecate  -- --id BC-300.10 --successor BC-100.10 --reason "Merged"
   ```
3. Run `npm run lint` locally; CI runs the same checks on every PR. Lint enforces the schema and every rule in the table below — a failing lint is a hard block on merge.
4. Open the PR. `CODEOWNERS` for the L1 file you touched is auto-requested for review.
5. On merge to `main`, the Cloudflare Pages site redeploys.
6. On a `v*` git tag, the Python package publishes to PyPI.

## Lint rules (enforced by CI)

The catalogue is the source of truth and must remain machine-checkable. `scripts/lint.ts` enforces:

| Check | Rule |
| --- | --- |
| YAML | All files parse as YAML 1.2 strict. |
| Schema | Every node validates against `schema/capability.schema.json`. |
| Id pattern | `^BC-\d+(\.\d+){0,3}$` — matches `business-capability-governance-model.md` §6. |
| Levels | `level` equals tree depth (root = 1). |
| Hierarchy | Each child id extends its parent id (`BC-2.1` under `BC-2`, `BC-2.1.3` under `BC-2.1`). |
| Sort order | Siblings sorted ascending by id (deterministic diffs). |
| Uniqueness | No id appears in more than one place. |
| Successors | `successor_id` resolves to an existing node. |
| Deprecation | `deprecated: true` requires a `deprecation_reason`. |
| Index | Every catalogue file is registered in `catalogue/_index.yaml`. |
| L1 slugs | `name` slugs across L1 files do not collide. |

## Versioning

Two independent version numbers ship in `version.json`:

- **`catalogue_version`** — semver tag on `main`. Bump:
  - **MAJOR** for structural changes (L1 reshuffle, breaking renames).
  - **MINOR** for additions of new capabilities.
  - **PATCH** for description tweaks, typo fixes, metadata refinements.

- **`schema_version`** — integer that bumps **only** when the field set or value semantics change in a non-additive way. Pinned in the Python package as `SCHEMA_VERSION`.

The two are independent: `catalogue_version` 1.4.2 and 1.5.0 can both have `schema_version` 1. Consumers pin the schema, not the catalogue version.

## Promotion path

| Branch | Effect |
| --- | --- |
| Feature branch / PR | CI lint runs; CF Pages preview URL deploys. |
| Merge to `main` | CF Pages production redeploys. |
| Tag `vX.Y.Z` on `main` | Python package builds and publishes to PyPI. |

## Where the code-of-record rules live

- **What a capability is, naming convention, decomposition rules** → `business-capability-governance-model.md`.
- **Operational rules (this file)** → `governance.md`.
- **Schema definition** → `schema/capability.schema.json`.
- **Lint implementation** → `scripts/lint.ts`.
- **Value streams (orthogonal artefact)** → `catalogue/_value-streams.yaml`. Stages must reference an existing capability id; `build_api` fails the build otherwise.

## What does *not* drive governance

- **Spreadsheets / XLSX / CSV.** Not a source. Ingest scripts produce YAML; YAML produces JSON; nothing flows the other way.
- **Hand-edited JSON in `dist/api/`.** Generated artefacts. Edits are wiped by the next build.
- **Edits made directly to the bundled Python package data.** Same — overwritten by `npm run build:pkg`.
