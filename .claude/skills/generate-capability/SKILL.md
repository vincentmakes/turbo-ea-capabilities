---
name: generate-capability
description: Draft a new L1 (or extend an existing L1) with MECE L2/L3 children for a target industry. Use when the user asks to add capabilities, fill out a sparse industry, propose a new L1, or extend a branch. Drives the existing scripts/cli/add.ts so IDs and sort order match the linter.
---

# generate-capability

Generate governance-conformant Business Capabilities for new or existing industries. Two modes:

- **Extend mode** — user gives an existing L1 ID (e.g. `BC-1010`) or L2 ID; you add new children under it.
- **New L1 mode** — user names a new top-level capability (e.g. "Insurance Underwriting Management"); you create a fresh `L1-*.yaml` and register it in `_index.yaml`.

You **must** comply with `business-capability-governance-model.md` Part A (definition, levels, decomposition, naming, identifiers, metadata) and Part B (lint rules). Read those sections at runtime; do not paraphrase from memory.

## Step 1 — Establish context

1. Read **`business-capability-governance-model.md`** §3–§7 (levels, decomposition, naming, identifiers, metadata) and §9.4 (lint rules).
2. Read **`schema/capability.schema.json`** to confirm the exact YAML shape and required fields.
3. Read **`catalogue/_index.yaml`** to see all registered L1s.
4. Identify the target industry. Read **2–3 peer L1s in the same industry** to absorb the local naming style, depth, and description tone. Examples:
   - Banking → `L1-banking-customer-management.yaml`, `L1-banking-credit-and-lending-management.yaml`
   - Pharma → `L1-pharmaceutical-manufacturing-management.yaml`, `L1-clinical-trials-management.yaml`
   - Manufacturing → `L1-manufacturing-operations-management.yaml`, `L1-production-planning-management.yaml`
   - ATC → `L1-air-traffic-control-operations-management.yaml`
   - Defense → `L1-mission-management.yaml`, `L1-weapon-systems-management.yaml`
   - Cross-Industry → `L1-financial-management.yaml`, `L1-human-capital-management.yaml`

## Step 2 — Confirm scope with the user

Ask the user to confirm before drafting:

1. **Mode** — Extend an existing L1/L2 (give the parent ID) or create a new L1?
2. **Target name** — proposed L1/L2 name (apply naming rules from §5: noun phrase, Title Case, 2–5 words, no verbs/vendors/value-stream names).
3. **Industry tag** — `Cross-Industry`, single industry, or `;`-separated list. New industry? Add it consistently with peers.
4. **Depth** — how far to decompose (L2 only, L2+L3, etc.). Default: L2 with L3 children where governance value is clear.

## Step 3 — Draft and review L2s

- Aim for **5–9 L2 children** under an L1 (per §3 typical counts adapted to L1 size).
- Each L2 must be MECE relative to its parent (§4.1).
- Name = noun phrase. Run the three §5.4 tests in your head: noun test, independence test, stability test.
- Show the user the L2 list with one-line descriptions before drafting L3s. Iterate until confirmed.

## Step 4 — Draft L3s (when needed)

- Aim for **3–7 L3 children per L2**, sparser is fine — symmetry is not required (§4.5).
- Stop decomposing when (§4.4):
  - the next breakdown would describe *how* (process / activity);
  - it duplicates another branch;
  - no distinct owner / application footprint / decision lives at that level.
- Show the user the full L1 → L2 → L3 tree before writing files.

## Step 5 — Enrich metadata

For every node (especially L2 per §7), provide:

- **`description`** — 1–3 sentences, outcome-oriented, business language. No "how", no vendors.
- **`in_scope`** — short list of concrete outcomes covered (helps reviewers).
- **`out_of_scope`** — short list of outcomes *not* covered (clarifies MECE boundaries).
- **`references`** — where applicable, cite an industry framework. Cheat sheet:

  | Industry | Anchors |
  | --- | --- |
  | Cross-Industry — process | APQC PCF, TOGAF, ITIL, TBM |
  | Cross-Industry — data | DAMA-DMBOK |
  | Cross-Industry — risk/security | NIST CSF, ISO 27001, ISO 22301 |
  | Cross-Industry — quality/HSE | ISO 9001, ISO 14001, ISO 45001, ISO 55000 |
  | Cross-Industry — sustainability | GHG Protocol, TCFD, ESRS/CSRD, IFRS S1-S2, GRI |
  | Manufacturing & Industrial | ISA-95, RCM, FMEA, FTA, Lean/Six Sigma |
  | Engineering Services | AACE cost classes, ISO 19650 (BIM), IEC 61511, HAZOP/HAZID |
  | Banking & Capital Markets | BIAN, Basel III, IFRS 9, ISO 20022, MiFID II/MiFIR, EMIR, FATF |
  | Pharmaceuticals & Life Sciences | ICH (E2/E6/E8/E9/Q1-Q12), GLP/GCP/GMP/GDP, GAMP 5, 21 CFR Part 11, CDISC |
  | Defense & Aerospace | DoD 5000, EIA-748, FAR/DFARS, DoDAF, MIL-HDBK-61/502, S1000D, ITAR/EAR, NISPOM/CMMC |
  | Air Traffic Control | ICAO Annexes 3/10/11/12/13/15/19, EUROCONTROL ATFCM/AIRAC, PBN, SWIM, AIXM, COSPAS-SARSAT |
  | Insurance | ACORD |
  | Telecommunications | eTOM |

  Citing a framework does **not** exempt a node from §5 (naming) or §4 (decomposition).

## Step 6 — Write to the catalogue

### Extend mode (preferred — reuses existing tooling)

For each new node, drive the helper CLI so IDs and sort order are computed by the existing TypeScript code (`scripts/cli/add.ts`):

```bash
npm run cap:add -- --parent BC-1010 --name "Plant Energy Management"
npm run cap:add -- --parent BC-1010.80 --name "Energy Demand Forecasting"
```

After each `cap:add`, look up the new node's ID in the YAML and patch `description`, `industry` (if overriding parent), `in_scope`, `out_of_scope` via direct YAML edits — only on the freshly created node, never reformat the rest of the file.

### New L1 mode (file write — there is no `cap:add` for L1)

1. Choose the next available L1 ID. Inspect existing IDs in `catalogue/` (BC-100, BC-200, …). Use a sparse value (e.g. next free hundreds-block) and confirm with the user.
2. Write `catalogue/L1-<kebab-case-name>.yaml` following the shape of a peer L1 file. Required top-level fields per `schema/capability.schema.json`: `id`, `name`, `level: 1`, `children`. Recommended: `industry`, `description`.
3. Register the new file in `catalogue/_index.yaml` (append under `files:`). Lint enforces this.
4. Add L2/L3 children either inline in the new file or by running `cap:add` against the new L1 ID.

Sample shape (do not commit verbatim — adapt names, IDs, descriptions):

```yaml
# Insurance Underwriting Management
id: BC-2100
name: Insurance Underwriting Management
level: 1
industry: Insurance
description: |
  Risk evaluation, pricing, and acceptance of insurance applications across
  life, P&C, and specialty lines.
children:
  - id: BC-2100.10
    name: Risk Assessment Management
    level: 2
    industry: Insurance
    description: |
      Evaluation of applicant risk profile against underwriting guidelines.
    children:
      - id: BC-2100.10.10
        name: Risk Data Capture
        level: 3
        industry: Insurance
        description: |
          Collection of risk-relevant data from applicant, third-party, and telematics sources.
        children: []
```

## Step 7 — Validate

Run, in order:

```bash
npm run lint          # MUST pass before commit
npm run build:api     # confirms tree builds
```

If lint fails, fix the YAML — do **not** loosen the schema or lint rules. Common failures and fixes:

- **Schema validation** → check field names against `schema/capability.schema.json`.
- **Id pattern** → use `BC-<L1>[.<L2>[.<L3>[.<L4>]]]`, digits only, dot-separated.
- **Sort order** → siblings must be ascending by ID; `cap:add` handles this. If you hand-edited, re-sort.
- **Unique slug** → `name` slug across L1 files must not collide with an existing L1.
- **Index** → every L1 file must appear in `catalogue/_index.yaml`.

## Step 8 — Hand off

After lint passes, suggest the next step:

> "L1 / L2 / L3 in place. Run `/map-value-streams BC-<new-id>` to wire this capability into value streams in `catalogue/_value-streams.yaml`."

## Anti-patterns to refuse

Reject (or rewrite) names that:

- Contain verbs (*Manage*, *Process*, *Handle*, *Execute*, *Perform*, *Deliver*).
- Are gerunds with objects (*Producing Spare Parts*, *Selling to Customers*).
- Reference a tool, vendor, system, or technology (*SAP Master Data*, *Salesforce CRM*).
- Reference an organisational unit, geography, or business unit (*EMEA Sales Planning*).
- Read as a process step (*Initial …*, *Final …*, *Step 1 — …*).
- Represent a value stream or end-to-end flow (*Order-to-Cash*, *Procure-to-Pay*) — those go in `_value-streams.yaml`, not the hierarchy.
- Duplicate another branch (sign of poor MECE).
- Are longer than 5 words (sign of compound concepts that should split).

If a user proposes one, suggest a conformant rewrite and explain which §5 rule was violated.

## What this skill must not do

- Edit `dist/api/**` or `packages/py/src/turbo_ea_capabilities/data/**` (build artefacts).
- Edit `schema/capability.schema.json` or `scripts/lint.ts` to make a draft pass.
- Add multi-parent edges (use a "shared service" relationship instead — §4.3).
- Decompose past **L4** (§4.6).
- Reuse a retired ID (§6.3).
- Bulk-regenerate an existing L1 the user did not explicitly authorise.
