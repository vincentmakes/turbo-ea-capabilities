---
name: generate-capability
description: Draft governance-conformant L1/L2/L3 capabilities for a target industry. Three modes — Industry (user names ONLY an industry; skill proposes the full L1 set), New L1 (user names one new L1), Extend (user names an existing L1 to add children to). The user always speaks in NAMES; the skill resolves names to IDs internally and drives scripts/cli/add.ts.
---

# generate-capability

Generate governance-conformant Business Capabilities. Three modes:

- **Industry mode** *(generic — preferred for greenfield)* — user names *only* an industry (e.g. *"Insurance"*, *"Telecommunications"*, *"Mining"*) and asks for a complete capability layer. You propose the full **set of L1s** for that industry, then L2s and L3s under each, anchored to the relevant industry framework (BIAN, ICH, ISA-95, ICAO, ACORD, eTOM, …). The user does *not* name individual L1s.
- **New L1 mode** — user names a single new top-level capability (e.g. *"Insurance Underwriting Management"*); you create one fresh `L1-*.yaml` and register it.
- **Extend mode** — user names an existing L1 (e.g. *"Manufacturing Operations Management"*); you add new L2/L3 children under it.

**The user surface is names, not IDs.** Never ask the user to type or remember an `BC-…` identifier. Resolve names to IDs yourself (see *Resolving names to IDs* below) and only show IDs back to the user as confirmation.

You **must** comply with `business-capability-governance-model.md` Part A (definition, levels, decomposition, naming, identifiers, metadata) and Part B (lint rules). Read those sections at runtime; do not paraphrase from memory.

## Resolving names to IDs

The user references capabilities by name. Internally you need IDs to drive `cap:add --parent <ID>` and to write YAML. Resolve as follows:

1. **For an L1 name** — read `catalogue/_index.yaml`, then read each listed `L1-*.yaml` and match against its top-level `name:` field. L1 names are globally unique (lint enforces L1 slug uniqueness). Exact match wins; if nothing matches exactly, list the closest 3–5 candidates and ask the user to pick.
2. **For an L2 name under a confirmed L1** — read that L1 file, walk `children:`, match by `name:`. L2 names are unique within their parent.
3. **For an L3 name** — same recursion under the confirmed L2.
4. **Show the resolved ID once** as confirmation (e.g. *"Resolved 'Manufacturing Operations Management' → BC-1010 — confirm?"*) but never require the user to type it.

If a name is ambiguous (substring match against multiple L1s, or a typo), show the candidates and ask — do not guess.

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

Detect the mode from the user's request and confirm before drafting:

1. **Industry mode** — user mentions only an industry (e.g. *"Generate capabilities for Insurance"*, *"Build out Telecommunications"*). Confirm: industry name, expected L1 count (default 8–14 per industry — match the existing distribution: Banking has 11, Pharma 10, Defense 8, ATC 7), depth (L1+L2+L3 vs L1+L2 only). Do **not** ask the user to name the L1s — propose them yourself in Step 3.
2. **New L1 mode** — user names exactly one new L1. Confirm name passes §5 naming tests, industry tag, depth.
3. **Extend mode** — user names an existing L1. Resolve via *Resolving names to IDs*. Ask which L2 to extend (list existing L2 children by name) or whether to add new L2s.

In all three modes, never ask the user to type or pick a `BC-…` ID.

## Step 3 — Draft the structure

### Industry mode — propose the full L1 set first

Before any L2/L3 work, draft the **complete L1 list** for the industry. Anchor on the industry's reference framework (see the cheat sheet in Step 5) but re-express every name in conformant noun-phrase form. Examples to illustrate the shape — not a prescription:

- **Insurance** (anchor: ACORD): *Insurance Product Management, Underwriting Management, Policy Administration Management, Claims Management, Reinsurance Management, Insurance Distribution Management, Actuarial Management, Insurance Risk Management, Insurance Customer Management*.
- **Telecommunications** (anchor: eTOM): *Network Operations Management, Service Assurance Management, Service Fulfilment Management, Subscriber Management, Telecom Product Catalogue Management, Telecom Billing Management, Spectrum & Frequency Management, Network Capacity Management, Roaming & Interconnect Management*.
- **Mining**: *Mineral Resource Management, Mine Planning Management, Mine Operations Management, Mineral Processing Management, Mine Safety Management, Mine Closure & Rehabilitation Management, Tailings Management*.

Apply MECE at the L1 level too: each L1 must be a distinct *ability* the enterprise needs. Do **not** invent L1s that duplicate the Cross-Industry catalogue (Financial Management, HR, IT, Procurement, etc. already exist) — only propose L1s that are genuinely industry-specific or genuinely shared across a defined subset.

Show the proposed L1 list with one-line descriptions and proposed industry tags. **One review checkpoint here**, not per-L1.

### Then for every L1 — draft L2s, then L3s

- Aim for **5–9 L2 children** under each L1 (per §3 typical counts adapted to L1 size).
- Each L2 must be MECE relative to its parent (§4.1).
- Name = noun phrase. Run the three §5.4 tests in your head: noun test, independence test, stability test.
- Then draft 3–7 L3s per L2.
- In Industry mode, present the **full L1 → L2 → L3 tree** in one batched proposal for review (one approval, not per-L1). In New L1 / Extend mode, the smaller scope is shown in one go too.

## Step 4 — Decomposition rules reminder

When drafting L3s (in any mode):

- Aim for **3–7 L3 children per L2**, sparser is fine — symmetry is not required (§4.5).
- Stop decomposing when (§4.4):
  - the next breakdown would describe *how* (process / activity);
  - it duplicates another branch;
  - no distinct owner / application footprint / decision lives at that level.
- Maximum depth is **L4** (§4.6) — almost always L3 is enough.

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

You already resolved the parent name to an ID in Step 2. Drive the helper CLI for each new node so IDs and sort order are computed by the existing TypeScript code (`scripts/cli/add.ts`):

```bash
# parent ID was resolved from the user's name "Manufacturing Operations Management"
npm run cap:add -- --parent BC-1010 --name "Plant Energy Management"

# resolved from "Manufacturing Operations Management" / "Plant Energy Management"
npm run cap:add -- --parent BC-1010.80 --name "Energy Demand Forecasting"
```

After each `cap:add`, look up the new node's ID in the YAML and patch `description`, `industry` (if overriding parent), `in_scope`, `out_of_scope` via direct YAML edits — only on the freshly created node, never reformat the rest of the file.

When reporting progress to the user, refer to nodes by name. Show the assigned ID once at the end as a reference (e.g. *"Added 'Plant Energy Management' as BC-1010.80"*) so they have something to cite in a PR description.

### New L1 mode and Industry mode (file write — there is no `cap:add` for L1)

1. Choose sparse L1 IDs. Inspect existing IDs in `catalogue/` (BC-100, BC-200, …, the industry blocks like BC-1000-1099 manufacturing, BC-1300-1399 banking, etc.). Pick a free hundreds-block for the industry; in Industry mode allocate sequential sparse IDs within that block (e.g. BC-2100, BC-2110, BC-2120, …). Show the assignment table once as a confirmation alongside names — not as separate per-L1 questions.
2. For each new L1, write `catalogue/L1-<kebab-case-name>.yaml` with the full L1 → L2 → L3 tree inline. Required top-level fields per `schema/capability.schema.json`: `id`, `name`, `level: 1`, `children`. Recommended: `industry`, `description`.
3. Register every new file in `catalogue/_index.yaml` (append under `files:`). Lint enforces this.
4. In Industry mode, batch-write all the new L1 files in one pass before running lint, so a single lint run validates the whole industry.

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

After lint passes, suggest the next step using *names* (not IDs):

- **Industry mode** — *"<N> L1s, <M> L2s, <K> L3s in place for <Industry>. Run `/map-value-streams --industry \"<Industry>\"` to wire all of them into value streams autonomously."*
- **New L1 / Extend mode** — *"L1 / L2 / L3 in place. Run `/map-value-streams \"<L1 name>\"` to wire this capability into value streams."*

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
