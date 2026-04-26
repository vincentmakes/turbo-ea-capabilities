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

1. Read **`business-capability-governance-model.md`** §3–§7 (levels, decomposition, naming, identifiers, metadata), §9.4 (lint rules), and §9.8 (reference frameworks — you will both *consult* and possibly *update* this section).
2. Read **`schema/capability.schema.json`** to confirm the exact YAML shape and required fields.
3. Read **`catalogue/_index.yaml`** to see all registered L1s.
4. Read **`catalogue/_value-streams.yaml`** so you have the existing 24 streams in context for Step 7.5 (value-stream mapping). Skim the canonical + industry-specific stream tables in `.claude/skills/map-value-streams/SKILL.md` Step 2 — they're the cheatsheet you'll use to score fit.
5. Identify the target industry. Read **2–3 peer L1s in the same industry** to absorb the local naming style, depth, and description tone. Examples:
   - Banking → `L1-banking-customer-management.yaml`, `L1-banking-credit-and-lending-management.yaml`
   - Pharma → `L1-pharmaceutical-manufacturing-management.yaml`, `L1-clinical-trials-management.yaml`
   - Manufacturing → `L1-manufacturing-operations-management.yaml`, `L1-production-planning-management.yaml`
   - ATC → `L1-air-traffic-control-operations-management.yaml`
   - Defense → `L1-mission-management.yaml`, `L1-weapon-systems-management.yaml`
   - Cross-Industry → `L1-financial-management.yaml`, `L1-human-capital-management.yaml`

## Step 1.5 — Industry framework audit (Industry mode and New L1 mode only)

Before drafting any capability, audit `business-capability-governance-model.md` §9.8 for the target industry's reference frameworks. The catalogue's posture is to *anchor* L1/L2 to industry frameworks where they exist (§9.8 closing paragraph), so before you propose L1s you need to know what to anchor against — and if that anchor is missing from §9.8, you add it.

Workflow:

1. **Look up** the target industry in §9.8. Three outcomes:
   - **Already a fully-fledged subsection** (e.g. *Banking & capital markets*, *Pharmaceuticals & life sciences*) — proceed; no §9.8 edit needed.
   - **Listed only under "Other industry anchors not yet exercised in the catalogue but recommended for adoption"** (currently: eTOM for Telco, ACORD for Insurance) — you must promote it to its own subsection and expand the standards list before drafting L1s.
   - **Absent entirely** — you must add a new subsection.
2. **Identify the canonical standards** for the industry. Use the reference cheat sheet below as a starting point; supplement from the user's domain knowledge or web research as needed. Cover, where applicable:
   - **Capability/process anchor** — the industry's process or service-domain framework (e.g. BIAN for Banking, eTOM for Telco, ACORD for Insurance, ICH/GxP for Pharma).
   - **Regulatory regime** — the principal supervisory or licensing regime (e.g. Basel III, Solvency II, MiFID, FAA/EASA/ICAO, FDA/EMA).
   - **Quality / safety standards** — ISO standards or industry-specific equivalents (e.g. ISO 9001/14001/45001, GMP, GxP, ISA-95, AS9100).
   - **Reporting / disclosure standards** — financial and non-financial (e.g. IFRS 17 for Insurance, JORC/SAMREC for Mining, IPIECA for Oil & Gas).
   - **Data / interchange standards** — messaging, taxonomy, master data (e.g. ISO 20022, FpML, SWIFT, ACORD XML, HL7/FHIR, ARTS).

   Cheat sheet for industries **not yet exercised** in the current catalogue (use as a research starting point, not as gospel — verify currency before citing):

   | Industry | Likely anchors |
   | --- | --- |
   | Insurance | ACORD (data), Solvency II / NAIC RBC (regulatory), IFRS 17 (reporting), ISO 31000 (risk), Lloyd's market practices, IAIS ICPs |
   | Telecommunications | eTOM / Frameworx (TM Forum), TM Forum SID (information), 3GPP, ETSI, ITU-T E.800 (QoS), GSMA |
   | Mining & Metals | ICMM Mining Principles, JORC / SAMREC / NI 43-101 / CRIRSCO (resource reporting), GISTM (tailings), GMG Group, ICMM Tailings |
   | Oil & Gas | API standards, IOGP, IPIECA, OGCI, IADC (drilling), SPE petroleum reserves, ISO 29001 |
   | Utilities (Power) | NERC CIP, IEC 61850, IEC 61968/61970 (CIM), CIGRE, ENTSO-E, FERC orders |
   | Utilities (Water) | ISO 24500-series, AWWA, WHO Water Safety Plans, EU Drinking Water Directive |
   | Healthcare Provider | HL7 / FHIR, SNOMED CT, ICD-10/11, IHE profiles, JCI accreditation, HITRUST |
   | Retail & Consumer Goods | ARTS / NRF data model, GS1 (barcodes, GTIN), GDSN, EDI 850/810, PCI DSS |
   | Logistics & Transportation | UN/CEFACT, GS1 Global Logistics, IATA Resolutions (air), IMO (maritime), AAR (rail) |
   | Public Sector / Government | TOGAF Government Reference Model, FEAF, NIST SP 800-53, OMB Circulars, eGovernment Frameworks |
   | Education | IMS Global, 1EdTech (LTI, QTI, OneRoster), CEDS (US), ISCED (UNESCO) |
   | Real Estate | OSCRE, RESO Data Dictionary, IPMS (measurement), RICS standards |
   | Agriculture | AgGateway, GS1 GLN/GTIN for food, GLOBALG.A.P., FAO codes, ISO 11783 (ISOBUS) |

3. **Show the proposed §9.8 change** to the user as part of the same scope-confirmation step (Step 2). Format:

   ```
   §9.8 will be updated:
   - Move "Insurance" from "Other industry anchors not yet exercised" into its own subsection
   - New "Insurance" subsection contents:
     - ACORD — insurance data standards
     - Solvency II / NAIC RBC — capital regulation
     - IFRS 17 — insurance contracts accounting
     - ISO 31000 — risk management
     - IAIS ICPs — international supervisory principles
   ```

   Get one combined approval (industry framework update + L1 proposal) — don't loop back for separate confirmation.

4. **After the user approves**, edit `business-capability-governance-model.md` §9.8:
   - If promoting from "not yet exercised", remove the line there.
   - Insert the new subsection in alphabetical order among existing industry subsections, using the same `**<Industry>**` heading + bulleted list format as the existing subsections.
   - Each bullet: `**<Standard>** — <one-line scope>.`
5. **Reference these standards in the new L1 YAML's `references` field** (Step 5) — this is the whole point of capturing them in §9.8. The link goes both ways: §9.8 is the catalogue of frameworks; YAML `references` cite them.

Skip this step in **Extend mode** — extending an existing L1 does not introduce a new industry. If the extension reveals a gap in §9.8 anyway, mention it to the user but treat fixing it as a separate follow-up rather than blocking the extension.

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
- **`references`** — where applicable, cite an industry framework. **The authoritative list is `business-capability-governance-model.md` §9.8** — read it at runtime and pick from there. If you discovered or added new frameworks during Step 1.5, cite those (you've already added them to §9.8). Citing a framework does **not** exempt a node from §5 (naming) or §4 (decomposition).

  Quick orientation (refer to §9.8 for the full list and any new entries you've added):

  | Industry | Anchors documented in §9.8 |
  | --- | --- |
  | Cross-Industry — process | APQC PCF, TOGAF, ITIL, TBM, DAMA-DMBOK |
  | Cross-Industry — risk/quality/sustainability | NIST CSF, ISO 27001/22301/9001/14001/45001/55000, GHG Protocol, TCFD, ESRS/CSRD, IFRS S1-S2, GRI |
  | Manufacturing & Engineering Services | ISA-95, RCM, FMEA, FTA, Lean/Six Sigma, AACE classes, ISO 19650, IEC 61511, HAZOP/HAZID |
  | Banking & Capital Markets | BIAN, Basel III, IFRS 9, ISO 20022, MiFID II/MiFIR, EMIR, FATF |
  | Pharmaceuticals & Life Sciences | ICH (E2/E6/E8/E9/Q1-Q12), GLP/GCP/GMP/GDP, GAMP 5, 21 CFR Part 11, CDISC |
  | Defense & Aerospace | DoD 5000, EIA-748, FAR/DFARS, DoDAF, MIL-HDBK-61/502, S1000D, ITAR/EAR, NISPOM/CMMC |
  | Air Traffic Control | ICAO Annexes 3/10/11/12/13/15/19, EUROCONTROL ATFCM/AIRAC, PBN, SWIM, AIXM, COSPAS-SARSAT |
  | *Other industries* | Audit and add to §9.8 in Step 1.5 — see that step's research cheat sheet. |

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

Also confirm:

- If Step 1.5 added a §9.8 entry, the new subsection is in alphabetical order, uses the existing format (`**<Standard>** — <one-line scope>.`), and is no longer listed under "Other industry anchors not yet exercised in the catalogue".
- The new YAML's `references` field cites at least one anchor from the §9.8 entry you just added (otherwise the §9.8 update is dead weight).

## Step 7.5 — Map to existing value streams (skip in Extend mode)

After lint passes, every new L1 should be evaluated against the catalogue's value streams so coverage stays in sync with the capability set. Extending an existing L1 (Extend mode) doesn't change its stream membership, so skip this step.

For each newly written L1:

1. **Score fit against every stream in `catalogue/_value-streams.yaml`.** Use the canonical and industry-specific tables in `.claude/skills/map-value-streams/SKILL.md` Step 2 as the cheatsheet — do not duplicate them here. Apply the same heuristics as `map-value-streams` Step 3 (cross-industry L1s → canonical streams; industry-specific L1s → industry stream first, then canonical).
2. **Decide stage placement.** For each fitting stream, choose `stage_order` and `stage_name` from the stream's existing stages. If the new L1 fits at a stage that doesn't yet exist, propose a new `stage_name` with the next sensible `stage_order`. Set `industry_variant` only when the L1 is industry-specific *and* the same stage already has a generic equivalent. Write a one-line `notes` per stage entry.
3. **Flag coverage gaps.** When no existing stream covers the new L1's primary role, emit a Coverage-gap notice (same format used by `map-value-streams`):

   ```
   Coverage gap: <new L1 name> (<BC-id>)
     No existing stream covers this capability's primary role of <one-sentence summary>.
     Suggested new streams:
       - <Suggested-Name-1> — <one-line rationale>
       - <Suggested-Name-2> — <alternative framing>
     Add via /map-value-streams or defer; the L1 is fully usable without a stream mapping.
   ```

   Limit suggestions to 1–2 names. **Do not draft stages for the suggested streams** — that's a separate, deliberate decision.
4. **Present one batched proposal**, grouped by stream, in the same table format as `map-value-streams` Step 4. Include any Coverage-gap notices alongside. Ask once for approval; acceptable responses: *approve*, *approve except X*, *redo with Y different*, *skip mapping*.
5. **On approval**, append the approved stages to `catalogue/_value-streams.yaml` (one entry per fit, dedupe within `stream + stage_order + stage_name + industry_variant`, merge notes with `;` if collapsing). Re-run `npm run lint` to confirm the L1-only rule and reference resolution still pass.
6. **On skip / decline**, leave `_value-streams.yaml` untouched. Carry any Coverage gaps forward to the Step 8 hand-off so the user has a record.

In **Industry mode**, batch all the new L1s into one proposal table (group by stream, then by L1 within each stream). The user gets one approval covering the whole industry's value-stream wiring.

## Step 8 — Hand off

After lint passes (and Step 7.5 completed or was skipped), summarise using *names* (not IDs):

- **Mappings written** — *"L1 / L2 / L3 in place for `<L1 name>`; mapped to `<N>` stream(s): `<comma-separated names>`. Open a PR; CODEOWNERS for `catalogue/` will be auto-requested."*
- **Coverage gap logged** — repeat the gap notice from Step 7.5 and recommend either (a) adding a new stream now via a manual edit to `_value-streams.yaml` followed by `/map-value-streams "<L1 name>"`, or (b) merging the L1 first and revisiting the stream gap as a follow-up. Do not block on this.
- **Mapping skipped** — *"L1 / L2 / L3 in place for `<L1 name>`; value-stream mapping skipped. Run `/map-value-streams \"<L1 name>\"` later when ready."*
- **Extend mode** — *"L2 / L3 added under `<parent L1 name>`. Validation passed. Existing stream mappings on the parent are unchanged."*

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
