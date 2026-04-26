---
name: map-value-streams
description: Autonomously propose stages in catalogue/_value-streams.yaml linking L1 capabilities (or all L1s of an industry) to end-to-end value streams. Stages map at L1 only; the skill decides which streams apply, flags coverage gaps when no stream fits, and presents ONE batched proposal — no per-stage interrogation. The user always speaks in NAMES; the skill resolves names to IDs internally.
---

# map-value-streams

Edit `catalogue/_value-streams.yaml` to map Business Capabilities onto end-to-end value streams. Value streams are an **orthogonal** artefact: they describe a flow that exercises multiple capabilities in sequence; they are *not* part of the capability hierarchy and must never appear as capability names (per `business-capability-governance-model.md` §2 and §5.3).

## Operating principle: autonomous, batched

This skill is **not** an interactive interrogator. The user names one or more L1s (or just an industry) and the skill does the thinking — picks the streams, picks the anchor capabilities, decides where `industry_variant` is warranted, and produces a **single batched proposal** for review. Do **not** ask the user "should this map to Hire-to-Retire?", "what should the stage_order be?", or any per-stage question. Decide, propose the whole mapping, and let the user approve or amend at the end.

Only ask the user when:

- the input name is genuinely ambiguous (multiple matches);
- a brand-new value stream is needed that has no precedent in the catalogue (in which case ask once with a rationale before drafting);
- the user explicitly asks for an interactive walkthrough.

**The user surface is names, not IDs.** Never ask the user to type or remember an `BC-…` identifier. Resolve names to IDs yourself (see *Resolving names to IDs* below). The `_value-streams.yaml` file *stores* `capability_id`, but that's an implementation detail — when conversing with the user, refer to capabilities by name.

## When to use

- `/map-value-streams "Human Capital Management"` — map a single L1 autonomously.
- `/map-value-streams "Human Capital Management" "Defense Personnel Management" "Marketing Management"` — map several L1s autonomously in one pass.
- `/map-value-streams --industry "Banking & Capital Markets"` — map every L1 in the industry autonomously.
- `/map-value-streams --all` — sweep the catalogue and map every L1 not yet covered.

## Resolving names to IDs

The user references capabilities by name; `_value-streams.yaml` stores `capability_id`. Resolve before writing:

1. **L1 names** — read `catalogue/_index.yaml`, then each `L1-*.yaml`, and match the user's input against the top-level `name:` field. L1 names are globally unique.
2. **Industry filter** — when given `--industry "<name>"`, scan all L1 files where `industry:` matches (treat the field as `;`-separated) and process each in turn.
3. If a name is ambiguous, list the closest 3–5 matches and ask the user to pick — do not guess.
4. Show the resolved name → ID mapping once at the start of Step 4 as confirmation, then refer to capabilities by name everywhere else in the conversation.

Stages reference the **L1 only**. The lint rule (`scripts/lint.ts` `L1_ID_REGEX`) rejects any deeper `capability_id`. Sub-scope (e.g. *AR vs GL within Financial Management*) belongs in the stage's `notes` field, not in a more specific ID.

## Step 1 — Establish context

1. Read **`catalogue/_value-streams.yaml`** in full to enumerate existing streams and the stages already mapped.
2. Read **`business-capability-governance-model.md`** §2 (capabilities ≠ value streams) and §9.4 (lint rules).
3. For each target L1 (resolved from the user's name), read its YAML file under `catalogue/L1-*.yaml` to understand its scope. The value-stream stage references the L1 itself; the site auto-expands to descendants when filtering, so sub-scope detail belongs in `notes`, not in a deeper `capability_id`.

## Step 2 — Identify candidate streams

Authoritative list lives in `catalogue/_value-streams.yaml`; read it at runtime for the source of truth. The tables below summarise the current 24 streams to help you spot fits quickly. Reuse these names exactly — never invent a near-synonym.

Cross-industry streams:

| Stream | Typical L1 anchors |
| --- | --- |
| **Hire-to-Retire** | BC-300 Human Capital Management; BC-400 Marketing (employer brand only) |
| **Order-to-Cash** | BC-410 Sales, BC-420 CRM, BC-440 Pricing, BC-200 Financial Management, BC-520 Supply Chain, BC-150 Legal |
| **Procure-to-Pay** | BC-500 Procurement, BC-510 Supplier Management, BC-200 Financial Management |
| **Issue-to-Resolution** | BC-140 Audit, BC-430 Customer Service, BC-720 Quality, BC-730 HSE, BC-620 Cybersecurity, BC-830 Knowledge |
| **Idea-to-Market** | BC-800 Innovation, BC-810 R&D, BC-820 Product Lifecycle, BC-840 IP, BC-400 Marketing, BC-410 Sales |
| **Plan-to-Inventory** | BC-520 Supply Chain, BC-530 Inventory, BC-1000 Production, BC-230 FP&A |
| **Record-to-Report** | BC-200 Finance, BC-210 Treasury, BC-220 Tax, BC-230 FP&A, BC-240 Investor Relations, BC-140 Audit, BC-130 Compliance |
| **Acquire-to-Retire** | BC-1040 Physical Asset, BC-1030 Plant Maintenance, BC-1110 Project Engineering, BC-1160 Commissioning, BC-200 Finance, BC-740 Sustainability |
| **Strategy-to-Execution** | BC-100 Strategic Management, BC-900 Project Portfolio, BC-910 Change, BC-920 Transformation |
| **Risk-to-Mitigation** | BC-120 Enterprise Risk, BC-130 Compliance, BC-520 Supply Chain (risk feed) |
| **Audit-to-Action** | BC-140 Internal Audit |
| **Threat-to-Mitigation** | BC-620 Cybersecurity, BC-160 Business Continuity, BC-830 Knowledge |
| **Prospect-to-Customer** | BC-400 Marketing, BC-410 Sales, BC-420 CRM, BC-430 Customer Service, BC-850 Corporate Communications |
| **Opportunity-to-Order** | BC-410 Sales, BC-420 CRM, BC-440 Pricing, BC-150 Legal |
| **Maintenance-Request-to-Closure** | BC-1030 Plant Maintenance, BC-1050 Field Service, BC-720 Quality, BC-200 Finance |
| **Crisis-to-Recovery** | BC-160 Business Continuity, BC-620 Cybersecurity, BC-600 IT, BC-850 Corporate Communications, BC-830 Knowledge, BC-120 Enterprise Risk |
| **ESG-to-Disclosure** | BC-740 Sustainability, BC-510 Supplier (ratings), BC-610 Information & Data, BC-140 Audit, BC-200 Finance, BC-240 Investor Relations |
| **Concept-to-Manufacture** | BC-1120 Design, BC-1100 Engineering Discipline, BC-1020 Manufacturing Engineering, BC-820 PLM, BC-1000 Production, BC-1010 Mfg Operations, BC-720 Quality, BC-1130 Engineering Document |

Industry-specific streams (use first when the L1 is industry-specific; canonical streams come second):

| Industry | Stream | Typical L1 anchors |
| --- | --- | --- |
| Banking | **Application-to-Funding** | BC-1320 Credit & Lending, BC-1300 Banking Customer, BC-1400 Financial Crime, BC-1310 Banking Product, BC-1340 Payments, BC-1410 Banking Risk |
| Pharma | **Discovery-to-Approval** | BC-1500 Drug Discovery, BC-1510 Drug Development, BC-1520 Clinical Trials, BC-1530 Regulatory Affairs, BC-1580 Medical Affairs, BC-1590 Pharma Commercial, BC-1600 Market Access |
| Pharma | **Adverse-Event-to-Action** | BC-1540 Pharmacovigilance, BC-1580 Medical Affairs, BC-1530 Regulatory Affairs, BC-850 Corporate Comms |
| Defense | **Capture-to-Contract** | BC-1750 Defense Capture & Bid, BC-1730 Intelligence Ops, BC-1810 Classified Info Sec, BC-1140 Engineering Tendering, BC-1790 Export Control, BC-150 Legal, BC-1760 Defense Programme |
| Defense | **Sustain-to-Disposition** | BC-1780 Defense Sustainment, BC-1720 Defense Logistics, BC-1060 Spare Parts, BC-1770 Defense Systems Engineering, BC-1800 Defense T&E, BC-1040 Physical Asset, BC-1810 Classified Info Sec |
| ATC | **Flight-to-Settle** | BC-1230 Aeronautical Information, BC-1210 ATC Ops, BC-1220 ATC Flow, BC-1270 Route Charges, BC-200 Finance |

### Coverage-gap detection

If a target L1's role is not represented by any of the streams above, do **not** force a fit and do **not** silently invent a new stream. Instead, emit a Coverage-gap notice in this format:

```
Coverage gap: <L1 name> (<BC-id>)
  No existing stream covers this capability's primary role of <one-sentence summary>.
  Suggested new streams:
    - <Suggested-Name-1> — <one-line rationale: what end-to-end flow it captures>
    - <Suggested-Name-2> — <alternative framing>
  Continuing with the streams that do fit. Add a new stream as a follow-up
  (manual edit to _value-streams.yaml) if the suggestion is right.
```

Continue with whatever streams *do* fit (often there will be a partial fit even when no stream is the primary one). The user can author the new stream manually or via a follow-up `/map-value-streams` invocation once defined.

## Step 3 — Decide stages autonomously

For every target L1 (or every L1 in the industry), decide on your own which streams it participates in and at which stage. Do this for the *entire batch* before showing anything to the user.

Heuristics — apply silently, don't ask:

- **Anchor at L1.** Lint enforces L1-only `capability_id`s; sub-scope (e.g. AR vs GL within Financial Management) goes in `notes`. If multiple aspects of the same L1 collaborate at a stage, still emit a single L1 entry and merge the rationale in `notes` with `;` separators (e.g. `"Pay design; Payroll execution"`).
- **Reuse existing streams** before flagging a gap. Use the Coverage-gap pattern from Step 2 when no stream fits — never invent a new stream silently.
- **Cross-Industry L1s usually map to canonical streams** (Hire-to-Retire for HR, Order-to-Cash for Sales, Procure-to-Pay for Procurement, Record-to-Report for Financial Management). Don't ask — apply.
- **Industry-specific L1s map first to industry-specific streams, then to canonical ones if relevant** (Banking Customer Management → Onboard-to-Activate primarily, Issue-to-Resolution secondarily).
- **`industry_variant` rule** — set it only when the same `stream` / `stage_order` / `stage_name` already has (or will have) a non-variant entry, *and* the capability you're anchoring is industry-specific in a way that diverges from the generic stage. Otherwise skip the field. Never use it just to tag industry.
- **`notes`** — emit one short phrase per stage so reviewers understand *why* the anchor was chosen. Don't ask the user for the note text — write it.

Per-stage fields you write:

- **`name`** — the value stream name (reuse existing names exactly).
- **`stage_order`** — integer; same `stage_order` allowed for parallel anchors at the same step.
- **`stage_name`** — short human-readable stage label.
- **`capability_id`** — written into YAML as the resolved BC-id; *spoken about* with the user as the capability's name.
- **`industry_variant`** *(optional)* — per the rule above.
- **`notes`** *(optional but encouraged)* — one phrase, written by you.

## Step 4 — Show the batched proposal

Present the **complete proposal in one go**, grouped by stream. Use the capability *name* as the human-facing column and show the resolved ID once in parentheses for traceability:

```
Stream: Hire-to-Retire
  stage_order  stage_name             capability                                  industry_variant  notes
  1            Workforce Planning     Human Capital Management (BC-300)                             Demand planning
  2            Sourcing & Attraction  Human Capital Management (BC-300)                             Sourcing
  3            Selection & Hire       Classified Information Security (BC-1810)   Defense           Clearance verification
  ...

Stream: Application-to-Funding (Banking)
  stage_order  stage_name             capability                                  industry_variant  notes
  1            Application Capture    Credit & Lending Management (BC-1320)       Banking           Origination intake
  2            KYC & Due Diligence    Banking Customer Management (BC-1300)       Banking           KYC / CDD
  ...
```

Ask the user for **a single approval of the whole batch** (or amendments). Acceptable responses:

- *"approve"* / *"go ahead"* — write everything.
- *"approve except <specific stages>"* — write everything but the listed exceptions.
- *"redo with X different"* — re-propose with the change applied.

Do **not** loop through stages asking for individual confirmation.

## Step 5 — Edit `catalogue/_value-streams.yaml`

- **Preserve YAML formatting and comments.** Use the same `yaml` Document approach as `scripts/cli/_shared.ts` if writing programmatically. For interactive edits, use the `Edit` tool to insert stages without reflowing the rest of the file.
- Insert stages within the existing `stages:` array of the matching `value_streams` entry, **maintaining `stage_order` ascending**. If multiple entries share the same `stage_order`, group them together.
- For a brand-new stream, append a new entry under `value_streams:` with at least `name` and `stages:`.

## Step 6 — Validate

```bash
npm run lint          # checks every capability_id resolves
npm run build:api     # rebuilds dist/api/value-streams.json; fails if any reference is broken
```

If lint fails:

- **Non-L1 capability_id** → the rule (`scripts/lint.ts` `L1_ID_REGEX`) requires L1 only. Truncate to the L1 prefix (e.g. `BC-300.10` → `BC-300`) and move the sub-scope into `notes`.
- **Unresolved capability_id** → the ID does not exist in the catalogue. Verify against `catalogue/L1-*.yaml`. Do not invent IDs.
- **YAML parse error** → check indentation and quoting (use `"..."` for names containing `&` or `:`).

## What this skill must not do

- Add value-stream names *inside* the capability hierarchy. Value streams live only in `_value-streams.yaml` (§2, §5.3 of the governance model).
- Reference a `capability_id` that doesn't exist — create the capability first via `/generate-capability`, then map it.
- Edit `dist/api/value-streams.json` directly (build artefact, regenerated by `npm run build:api`).
- Add an `industry_variant` purely to tag industry — it should reflect a real divergence in stage logic.
- Bulk-rewrite existing stages without explicit user authorisation.

## Hand-off

After lint and build pass:

> "Mapped <N> stages across <M> streams in `catalogue/_value-streams.yaml`. Open a PR; CODEOWNERS for `catalogue/` will be auto-requested for review."
