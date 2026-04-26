---
name: map-value-streams
description: Propose stages in catalogue/_value-streams.yaml that link one or more L1 capabilities to end-to-end value streams (Hire-to-Retire, Order-to-Cash, Procure-to-Pay, etc.), with optional industry variants. Use when the user asks to map an L1 (new or existing) to value streams, or to expand the catalogue's value-stream coverage across all L1s.
---

# map-value-streams

Edit `catalogue/_value-streams.yaml` to map Business Capabilities onto end-to-end value streams. Value streams are an **orthogonal** artefact: they describe a flow that exercises multiple capabilities in sequence; they are *not* part of the capability hierarchy and must never appear as capability names (per `business-capability-governance-model.md` §2 and §5.3).

## When to use

- User names an L1 (or list of L1s) to wire into existing value streams: `/map-value-streams BC-300 BC-1810`.
- User wants to expand the value-stream catalogue across all L1s in an industry.
- User wants to add a new value stream for an industry that doesn't have one yet.

## Step 1 — Establish context

1. Read **`catalogue/_value-streams.yaml`** in full to enumerate existing streams and the stages already mapped.
2. Read **`business-capability-governance-model.md`** §2 (capabilities ≠ value streams) and §9.4 (lint rules).
3. For each target L1, read its YAML file under `catalogue/L1-*.yaml` to understand its L2 children — the natural "anchor points" for a stage are usually L2 or L3, not L1 itself.

## Step 2 — Identify candidate streams

Canonical end-to-end streams (use existing names where possible to avoid duplication):

| Stream | Typical capabilities exercised |
| --- | --- |
| **Hire-to-Retire** | Workforce planning, sourcing, selection, onboarding, performance, exit |
| **Order-to-Cash** | Demand capture, order management, fulfilment, invoicing, collections |
| **Procure-to-Pay** | Sourcing, contracting, requisition, receipt, AP, payment |
| **Plan-to-Produce** *(manufacturing)* | Demand plan, MPS, MRP, work order, shop floor, finished goods |
| **Idea-to-Market** | Ideation, R&D, design, validation, launch |
| **Issue-to-Resolution** | Case capture, triage, resolution, knowledge update |
| **Quote-to-Cash** | Lead, quote, contract, order, invoice, payment |
| **Record-to-Report** | GL, intercompany, close, consolidation, statutory reporting |
| **Acquire-to-Retire** *(asset)* | Asset acquisition, deployment, maintenance, disposal |
| **Forecast-to-Stock** *(supply)* | Demand forecast, replenishment, inventory, fulfilment |

Industry-specific streams (used only when the flow diverges materially from a canonical stream):

| Industry | Streams |
| --- | --- |
| Banking | *Apply-to-Fund* (lending), *Trade-to-Settle* (capital markets), *Onboard-to-Activate* (KYC) |
| Pharma | *Discover-to-Approve* (drug development), *Trial-to-Submission* (clinical), *Adverse-Event-to-Action* (PV) |
| Defense | *Capture-to-Award* (bid), *Programme-Start-to-Sustainment*, *Mission-Plan-to-Debrief* |
| ATC | *Flight-Plan-to-Landing*, *Strip-to-Strip*, *Alert-to-Recovery* (SAR) |
| Engineering Services | *Tender-to-Handover*, *Design-to-Construction* |

If no existing or canonical stream fits, propose a new one **with rationale** and confirm with the user before writing.

## Step 3 — Draft stages for each target L1

For each target L1, identify which streams it participates in and at which stage. Stage anchors are usually **L2 or L3 IDs** (not the L1 itself) — a stream stage describes *one* step, and L1s are usually too broad.

For each proposed stage, decide:

- **`name`** — the value stream name (reuse existing names exactly to avoid duplicates).
- **`stage_order`** — integer; a stage may have multiple capability_ids at the same `stage_order` if several capabilities collaborate at that step (see existing Hire-to-Retire stages 2 and 3 for the pattern).
- **`stage_name`** — short human-readable stage label.
- **`capability_id`** — must resolve to an existing node in the catalogue. Lint rejects unresolvable IDs.
- **`industry_variant`** *(optional)* — only when the same stage genuinely differs by industry (e.g. `Defense` clearance verification at "Selection & Hire"). Do **not** add a variant just to tag the industry.
- **`notes`** *(optional)* — one short phrase clarifying *why* this capability is at this stage.

### Decision rule for `industry_variant`

Add a variant when:

- The capability anchored at that stage is industry-specific (e.g. Defense clearance, Pharma GxP audit), **and**
- A non-variant stage already exists for the same `stream` / `stage_order` / `stage_name`.

Skip the variant when the stage is universal even if the capability happens to be tagged with one industry — the inheritance lives on the capability, not the stage.

## Step 4 — Show the user before writing

Print the proposed stages as a table, grouped by stream:

```
Stream: Hire-to-Retire
  stage_order  stage_name             capability_id   industry_variant  notes
  1            Workforce Planning     BC-300.50                          Demand planning
  2            Sourcing & Attraction  BC-300.10                          Sourcing
  ...
```

Confirm with the user before editing the file.

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
