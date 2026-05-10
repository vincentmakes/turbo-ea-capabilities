---
name: generate-process
description: Synthesise a governance-conformant business-process tree (BP1 + L2/L3) from one Cross-Industry Value Stream and the Business Capabilities its stages exercise. Two modes — Synthesize-from-VS (primary) when the user names a value stream; Extend-VS (maintenance) when the user names a VS already represented as a BP1 plus a new stage. The user speaks in NAMES (VS name, stage name); the skill resolves to ids internally and drives the bp:bootstrap-bp1 + bp:add CLIs.
---

# generate-process

Generate a Cross-Industry business-process tree by deriving structure from the **Value Stream** the work belongs to and the **Business Capabilities** its stages realise. APQC PCF is no longer the source of truth for Cross-Industry process design; BC + VS are. Industry-specific BP1s (Banking, Telecom, Insurance, etc.) are out of scope of this skill — they remain anchored on their domain frameworks (BIAN, eTOM, ACORD, ICMM, industry-PCFs) and are authored manually.

## Modes

- **Synthesize-from-VS** *(primary)* — user names a Cross-Industry value stream (e.g. *"Order-to-Cash"*, *"Hire-to-Retire"*). You produce one fresh `catalogue/processes/BP1-<slug>.yaml` whose name matches the VS name verbatim, with one BP2 per VS stage and 3–7 verb-phrased BP3 activities per BP2.
- **Extend-VS** *(maintenance)* — user names a VS already represented as a BP1 plus a new stage that was just added to `_value-streams.yaml`. You add the corresponding BP2 subtree under the existing BP1 and decompose its BP3s.

**The user surface is names, not ids.** Resolve names to ids internally; only show ids back as confirmation.

You **must** comply with `business-capability-governance-model.md` Part D §11 (process-layer rules), Part C §10 (value-stream rules — the VS file is your input), and Part B §9.4 (lint rules). Read those at runtime; do not paraphrase from memory.

## Resolving names to ids

1. **VS name** — read `catalogue/_value-streams.yaml`, find the stream where `name` matches (case-insensitive). Exact match wins; ambiguous matches surface 3–5 candidates and ask. The VS `id` (e.g. `VS-30`) is what you carry through internally.
2. **Stage name** *(extend-VS)* — recurse under the resolved stream's `stages[]`, match against `stage_name`.
3. **Capability ids** — already present in each VS stage's `capability_ids` (always L1 BC-ids). Resolve their L2 children by reading `catalogue/L1-<slug>.yaml` for each L1 (you'll need L2 names to draft BP3 verb-phrases).
4. **BP id range** — Cross-Industry BP1s use a sparse range starting at **BP-1000** (10/20/30 between siblings: BP-1000, BP-1010, BP-1020, …). Industry-specific BP1s already occupy BP-130..BP-490; do not collide.
5. Show resolved id once as confirmation (*"Resolved 'Order-to-Cash' → VS-30 → BP-1000"*) but never require the user to type it.

## Step 1 — Establish context

1. Read `business-capability-governance-model.md` §11 (process layer), §10 (VS layer), §9.4 (lint rules).
2. Read `schema/business-process.schema.json` and `schema/value-stream.schema.json` to confirm field shapes.
3. Read `catalogue/processes/_index.yaml` to see registered BP1s and pick the next available BP-N0 id in the BP-1000+ range.
4. Read `catalogue/_value-streams.yaml` for the named stream and all its stages.
5. Read each BC L1 referenced by any stage's `capability_ids` so you have access to L2 capability names for BP3 drafting.

## Step 2 — Confirm scope with user

State explicitly:

- Which mode (Synthesize-from-VS or Extend-VS) and which VS / stage you resolved to.
- The resolved BP1 id (synthesise) or parent BP-id (extend).
- The number of BP2s to create (one per stage) and your draft BP3 count per BP2 (typically 3–7).
- The set of BCs whose L2s you'll consult for BP3 verb-phrasing.
- Framework cross-walk strategy (e.g. SCOR for Order-to-Cash / Procure-to-Pay / Plan-to-Inventory; ITIL for Issue-to-Resolution / Threat-to-Mitigation; COSO-ERM + ISO 31000 for Risk-to-Mitigation; SHRM-BoCK for Hire-to-Retire; ISO 55000 for Acquire-to-Retire). Cite frameworks structurally where they fit, not as primary naming source. APQC PCF is **not** required.

Ask the user to confirm scope before drafting nodes.

## Step 3 — Draft the BP1 root

Apply the §11.3 two-tier naming rule:

- **BP1 name = VS name verbatim** (bookend pattern: `Order-to-Cash`, `Hire-to-Retire`, `Procure-to-Pay`). Not verb-phrased.
- **BP1 description** = a one-sentence operational summary of the value stream; the source VS description if it reads well, otherwise a tightening of it.
- **`industry: Cross-Industry`** mandatory.
- **`realizes_capability_ids`** = union of every stage's `capability_ids`, deduped, sorted ascending.
- **`framework_refs`** = primary anchor selected per VS domain (see Step 2). Do not include APQC-PCF unless a specific PCF code genuinely fits the BP1 root.

Create the BP1 file via:

```bash
npm run bp:bootstrap-bp1 -- --id BP-1000 --name "Order-to-Cash" --industry Cross-Industry \
  --realizes BC-410,BC-420,BC-440,BC-200,BC-520,BC-530 \
  --description "End-to-end revenue cycle: from quote through order capture, fulfilment, invoicing, cash application, and close."
```

This helper creates `catalogue/processes/BP1-order-to-cash.yaml` and registers it in `_index.yaml`.

## Step 4 — Draft BP2 nodes (one per VS stage)

Walk the VS's `stages[]` in `stage_order`. For each stage:

- **BP2 name** = stage's `stage_name` verbatim. The stage may be noun-phrased (`Quote Generation`, `Issue Capture`, `Handover to Fulfilment`) or verb-phrased; use whichever the stage carries — BP2 mirrors the stage.
- **BP2 description** = stage's `description` if usable; otherwise a tightening.
- **`realizes_capability_ids`** = stage's `capability_ids` verbatim.
- **`framework_refs`** = whichever framework's vocabulary best fits the stage (e.g. SCOR sP / sS / sM / sD / sR / sE for supply-chain stages; ITIL Service Desk / Incident Management / Change Enablement for service stages).
- Sparse 10/20/30 numbering: BP-1000.10, BP-1000.20, BP-1000.30, …

Add via:

```bash
npm run bp:add -- --parent BP-1000 --name "Quote Generation" --realizes BC-410
```

Order BP2 children to match `stage_order`.

## Step 5 — Decompose each BP2 into BP3 activities

For each BP2:

1. List the BCs the parent stage realises (from `capability_ids`).
2. For each BC L1, fetch its L2 children.
3. Draft 3–7 BP3 activities that, together, are MECE for the work the stage performs. Each BP3 must:
   - Have a **verb-phrased Title Case name** (`Capture Customer Order`, `Verify Customer Credit`, `Allocate Inventory to Order`, `Generate Customer Invoice`, `Apply Customer Payment`, `Resolve Customer Disputes`).
   - Cite specific `realizes_capability_ids` — typically a subset of the parent BP2's set, possibly drilling into L2 BCs where one specific L2 is exercised.
   - Include `framework_refs` only when a recognised framework practice clearly maps (don't force).
4. Sparse 10/20/30 within parent.

Add via `bp:add`:

```bash
npm run bp:add -- --parent BP-1000.30 --name "Verify Customer Credit" --realizes BC-410.10,BC-200.20
```

Use the BC L2 cheat-sheet bullets in `.claude/skills/generate-capability/SKILL.md` if you need help phrasing operational verbs from capability nouns.

**Stop at L3.** No BP4. BPMN-level granularity does not belong in this catalogue.

## Step 6 — Re-link VS process_ids to the new BP3s

The VS file's stages have `process_ids` pointing at the old (deleted or to-be-deleted) BP tree. Update them to point at your new BP3 ids — the natural choice is the BP3 that most directly represents the stage's primary activity.

Build a small `{old_id: new_id}` mapping (or null to drop), then:

```bash
npm run bp:relink-vs -- --map scripts/cli/_data/bp_relink_<vs-slug>.json
```

If you're synthesising from a VS that has no prior `process_ids` (because Step 3 in the regen plan already wiped them), populate them fresh by editing the VS file directly with the new BP3 ids you just minted.

## Step 7 — Validate

Run `npm run lint`. The lint must pass:

- BP id pattern, level, sparse numbering, MECE within parent.
- All `realizes_capability_ids` resolve to existing BC nodes.
- All VS `process_ids` resolve to non-deprecated BP nodes.
- `_index.yaml` registers the new BP1 file.
- BC-coverage check (when added in Step 6 of the regen plan) reports 0 orphan Cross-Industry BC L1s.

Run `npm run build` to confirm `dist/api/business-processes.json`, `bp-tree.json`, `by-bp1/<slug>.json`, and `value-streams.json` regenerate cleanly.

## Step 8 — Optional: aliases (don't)

§11.3 disables aliases by governance. Do not populate `aliases[]`. If a synonym matters for findability, raise it as a description-language tweak instead.

## Anti-patterns to refuse

- **Adding APQC PCF cross-walks to a Cross-Industry BP without cause.** APQC's structure is taxonomic; this skill anchors on VS+BC instead. Cite APQC only if a specific PCF code is genuinely useful as evidence — never as the primary framework_refs entry.
- **Verb-phrasing the BP1 root.** `Run Order-to-Cash` is wrong. The bookend name is the name.
- **Aliases of any kind on any node.** One canonical name per node.
- **Going to BP4.** If you find yourself drafting an L4, the L3 is too coarse — re-decompose.
- **Drafting a BP1 without a corresponding VS.** Cross-Industry BPs must trace to a VS; if no VS exists for the work, the right move is to add the VS first via `/generate-value-stream`.
