---
name: generate-process
description: Draft governance-conformant L1/L2/L3 business processes (BP) for an APQC PCF category or industry-specific PCF. Three modes — Industry (user names ONLY an industry; skill proposes the cross-industry + industry-specific BP1 set), New BP1 (user names one new top-level Category), Extend (user names an existing BP1 to add Process Groups / Processes / Activities under). User speaks in NAMES; skill resolves to BP- ids internally and drives scripts/cli/bp_add.ts.
---

# generate-process

Generate governance-conformant business processes anchored on the APQC Process Classification Framework (PCF). Three modes mirror `generate-capability`:

- **Industry mode** — user names *only* an industry. You propose the BP1 (Category) set: APQC PCF Cross-Industry's 12 categories plus any industry-specific PCF categories that apply (Banking, Telecom, Insurance, Pharma, Petroleum, etc.). The user does *not* name individual BP1s.
- **New BP1 mode** — user names a single new Category (e.g. *"Manage Customer Service"*); you create one fresh `processes/BP1-*.yaml` and register it in `catalogue/processes/_index.yaml`.
- **Extend mode** — user names an existing BP1 (e.g. *"Develop Vision and Strategy"*); you add new BP2 (Process Group), BP3 (Process), and/or BP4 (Activity) children under it.

**The user surface is names, not ids.** Resolve names to ids internally and only show ids back as confirmation.

You **must** comply with `business-capability-governance-model.md` Part D §11 (process-layer rules) and Part B §9.4 (lint rules). Read those at runtime; do not paraphrase from memory.

## Resolving names to ids

1. **For a BP1 name** — read `catalogue/processes/_index.yaml`, then read each registered `BP1-*.yaml` and match against its `name:` field. Exact match wins; if absent, list closest 3–5 candidates and ask.
2. **For BP2/BP3/BP4** — recurse under the confirmed parent's `children:`.
3. Show resolved id once as confirmation (e.g. *"Resolved 'Manage Customer Service' → BP-60"*) but never require the user to type it.

## Step 1 — Establish context

1. Read `business-capability-governance-model.md` Part D (§11) for the process-layer rules. Read §9.4 for lint enforcement.
2. Read `schema/business-process.schema.json` to confirm the YAML shape, in particular `framework_refs` and `realizes_capability_ids` semantics.
3. Read `catalogue/processes/_index.yaml` to see registered BP1s.
4. If extending or producing industry-specific BPs, read 1–2 sibling BP1 files for the same industry first to absorb local naming style.

## Step 2 — Confirm scope with user

State explicitly which mode you're in, what you'll produce, and the proposed APQC PCF anchor (Cross-Industry 7.x by default; industry-specific PCFs by name when relevant). Ask the user to confirm before drafting.

## Step 3 — Draft the tree

- **Names are verb-phrased** (Title Case): *Develop Vision and Strategy*, *Process Sales Order*, *Reconcile Cash Receipts*. Distinct from capability names (which are noun phrases) — this is what makes a BP a BP.
- **Sparse 10/20/30 ids** at every level. Maximum depth L4 (Activity). Step / task granularity belongs in BPMN diagrams.
- **MECE within parent** at every level.
- **`framework_refs`** for each leaf (and ideally each non-leaf): pin the APQC PCF code in `external_id` with `framework: APQC-PCF` and the version (`7.4.0` is the current Cross-Industry version unless told otherwise). When BIAN / eTOM / ITIL / SCOR also map cleanly, add additional entries.
- **`realizes_capability_ids`** for each leaf BP4 (and selectively for BP3): list the L1–L4 BC ids the activity realizes. Resolve capability ids by reading `catalogue/L1-*.yaml`. Use the L1 cheat sheet from `.claude/skills/generate-capability/SKILL.md` if you need framework hints.
- **Industry tag**: Cross-Industry by default; specific industries when authoring an industry-specific PCF (e.g. Banking & Capital Markets, Telecommunications). Match the BC L1 industry vocabulary.

## Step 4 — Write to disk

Drive `npm run bp:add` for every node:

```bash
npm run bp:add -- --parent BP-<parent-id> --name "Develop Vision and Strategy" --realizes BC-100,BC-200
```

For new BP1s: create the file at `catalogue/processes/BP1-<slug>.yaml` directly (the helper assumes a parent exists), register it in `catalogue/processes/_index.yaml`, then use `bp:add` to populate children.

## Step 5 — Validate

Run `npm run lint`. Fix any error before declaring the work done — `npm run build` will fail downstream otherwise.

## Step 6 — Optional: link from value streams

If the new processes belong to existing value streams, propose stage `process_ids` updates separately via `vs:add-stage` (or by editing existing stages). Do NOT fold this into the BP authoring step; value-stream changes are reviewed by VS owners.
