---
name: map-value-streams
description: Autonomously propose stages in catalogue/_value-streams.yaml linking L1 capabilities (or all L1s of an industry) to end-to-end value streams. The skill decides which streams apply, picks the anchor L2/L3 for each stage, and presents ONE batched proposal — no per-stage interrogation. The user always speaks in NAMES; the skill resolves names to IDs internally.
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
2. **L2 / L3 names** — when the user says *"map the KYC capability under Banking Customer Management to Onboard-to-Activate"*, resolve `Banking Customer Management` → its L1 file, then walk `children:` to find an L2 (or L3) named *"KYC & Customer Due Diligence Management"*. Anchor stages at L2 or L3, not L1, because L1s are usually too broad to be a single stage.
3. **Industry filter** — when given `--industry "<name>"`, scan all L1 files where `industry:` matches (treat the field as `;`-separated) and process each in turn.
4. If a name is ambiguous, list the closest 3–5 matches and ask the user to pick — do not guess.
5. Show the resolved name → ID mapping once at the start of Step 4 as confirmation, then refer to capabilities by name everywhere else in the conversation.

## Step 1 — Establish context

1. Read **`catalogue/_value-streams.yaml`** in full to enumerate existing streams and the stages already mapped.
2. Read **`business-capability-governance-model.md`** §2 (capabilities ≠ value streams) and §9.4 (lint rules).
3. For each target L1 (resolved from the user's name), read its YAML file under `catalogue/L1-*.yaml` to understand its L2 children — the natural "anchor points" for a stage are usually L2 or L3, not L1 itself.

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

## Step 3 — Decide stages autonomously

For every target L1 (or every L1 in the industry), decide on your own which streams it participates in and at which stage. Do this for the *entire batch* before showing anything to the user.

Heuristics — apply silently, don't ask:

- **Anchor at L2 or L3.** A stream stage is one step. L1s are too broad. Pick the L2 (or L3) child whose scope matches the stage. If multiple children of the same L1 collaborate at a stage, emit multiple entries with the same `stage_order` (this is the documented pattern in existing Hire-to-Retire stages 2/3).
- **Reuse existing streams** before inventing new ones. Only invent a new stream when no canonical or industry-specific stream in the tables above fits — and then emit it with a one-line rationale alongside the proposal.
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
  stage_order  stage_name             capability                                   industry_variant  notes
  1            Workforce Planning     Workforce Planning (BC-300.50)                                 Demand planning
  2            Sourcing & Attraction  Talent Acquisition (BC-300.10)                                 Sourcing
  3            Selection & Hire       Personnel Security Vetting (BC-1810.10)      Defense           Clearance verification
  ...

Stream: Onboard-to-Activate (Banking)
  stage_order  stage_name             capability                                   industry_variant  notes
  1            Application Capture    Application Capture (BC-1300.10.10)                            Initial intake
  2            Identity Verification  Identity Verification (BC-1300.10.20)                          KYC docs
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
