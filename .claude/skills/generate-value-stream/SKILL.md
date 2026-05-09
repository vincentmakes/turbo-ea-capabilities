---
name: generate-value-stream
description: Draft a governance-conformant value stream (VS) with stages linked to L1 capabilities and (optionally) business processes. User names the trigger and outcome (e.g. "Quote-to-Cash") plus industry applicability; skill drafts stages, resolves capability and process names to ids internally, and drives scripts/cli/vs_add.ts and vs_add_stage.ts. Supersedes /map-value-streams.
---

# generate-value-stream

Generate a single value stream end-to-end: stream metadata + ordered stages with `capability_ids` and `process_ids`. The user describes the value stream in plain language; you resolve to BC- and BP- ids and drive the CLI.

You **must** comply with `business-capability-governance-model.md` Part C §10 (value-stream rules) and Part B §9.4 (lint rules).

## Step 1 — Confirm the stream

Ask the user (if not already provided):

- **Name** — bookend pattern `<Trigger>-to-<Outcome>` (e.g. *Quote-to-Cash*, *First-Notice-to-Settlement*). Title Case, hyphenated.
- **Industries** — `Cross-Industry` (must stand alone) or one or more BC L1 industries.
- **Description** *(optional)* — 1–3 sentences on the end-to-end flow.

## Step 2 — Read context

1. Read `business-capability-governance-model.md` §10 for stream/stage rules.
2. Read `schema/value-stream.schema.json` to confirm shape.
3. Read `catalogue/_value-streams.yaml` to check the proposed name doesn't collide and to absorb local style.
4. Read `catalogue/_index.yaml` and the industry-relevant L1 capability files to know the BC vocabulary you can link to.
5. Read `catalogue/processes/_index.yaml` and any registered BP1 files to know which processes can be linked.

## Step 3 — Draft stages

Each stage has:

- **`stage_order`** — 1, 2, 3, … (visual rank; stages may share an order when an industry variant splits a step).
- **`stage_name`** — short noun phrase describing the step (e.g. *Order Capture*, *Selection & Hire*).
- **`capability_ids: [BC-...]`** — L1 capabilities exercised. Stages link **at L1 only**; sub-scope detail goes in `notes`. Multiple ids are fine — the same stage can exercise multiple parallel capabilities.
- **`process_ids: [BP-...]`** — business processes that realise the work at this stage. May be empty during rollout. May resolve at any BP depth.
- **`industry_variant`** *(optional)* — call out an industry-specific specialisation (e.g. *"Healthcare Providers"*) without forking the whole stream.
- **`notes`** *(optional)* — one or two clauses, semicolon-separated, with sub-scope detail.

Aim for 5–10 stages. If you need more, split into multiple streams.

## Step 4 — Resolve names to ids

1. For every capability name the user (or you) referenced, resolve to its L1 BC id by reading `catalogue/_index.yaml` then matching `name:` in each L1 file. Lint will reject anything but L1 ids in `capability_ids`.
2. For every process name, resolve to its BP id (any depth) by walking `catalogue/processes/`. If no matching process exists, leave `process_ids: []` and call out the gap; do NOT invent BP ids.
3. Show resolved ids back to the user as confirmation before writing.

## Step 5 — Drive the CLIs

```bash
npm run vs:add -- --name "Quote-to-Cash" --industries "Cross-Industry"

npm run vs:add-stage -- --stream VS-<n> --name "Quote Generation" \
  --capabilities BC-100,BC-130 [--processes BP-30.10.10] \
  [--industry-variant "..."] [--notes "..."]
```

`vs:add` picks the next sparse `VS-<n>` automatically. `vs:add-stage` picks the next sparse stage id and the next `stage_order`.

## Step 6 — Validate

Run `npm run lint`. Fix any error before declaring done.

## Common pitfalls

- **Capability ids must be L1.** If the conceptual fit is at L2 or below, anchor at the L1 and use `notes` to capture the sub-scope (per the L1-only rule).
- **Industry must be in the BC vocabulary.** Lint cross-checks against the catalogue's industry list; typos fail.
- **`Cross-Industry`** must stand alone in `industries` when present; you can't combine it with specific industries.
- **Process ids resolving at depth ≠ L1 is fine.** Unlike `capability_ids`, `process_ids` may target any BP depth (BP1, BP2, BP3, BP4).
