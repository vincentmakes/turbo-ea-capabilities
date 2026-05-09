# Archived one-shot scripts

These scripts ran exactly once during a specific catalogue migration or import.
They are kept here for historical traceability — to reconstruct what produced
a given diff — but are not maintained and should not be run again. Further
authoring of capabilities, processes, and value streams goes through the
helper CLIs:

```bash
npm run cap:add | cap:mv | cap:deprecate
npm run bp:add  | bp:mv  | bp:deprecate
npm run vs:add  | vs:add-stage | vs:deprecate
```

## Inventory

| Script | What it did | When it ran |
|---|---|---|
| `migrate_value_streams.ts` | Rewrote `catalogue/_value-streams.yaml` from the legacy schema-1 shape (singular `capability_id`, no ids on streams or stages) to schema-2 (sparse `VS-N0` stream ids, sparse `VS-N0.M0` stage ids, plural `capability_ids[]`, empty `process_ids[]`). | One commit during the schema-2 rollout (PR #60). |
| `import_apqc_pcf.py` | Generated the 12 BP1 (Category) files plus their BP2 (Process Group) children for APQC PCF Cross-Industry. | One commit during the BP catalogue scaffolding (PR #61). |
| `wire_process_ids.py` | Populated `process_ids[]` on 204 stages across the five canonical Cross-Industry value streams (Hire-to-Retire, Idea-to-Market, Order-to-Cash, Procure-to-Pay, Record-to-Report). | One commit (PR #62). |
| `import_apqc_pcf_bp3.py` | BP3 (Process) drill-down across all 12 Cross-Industry BP1s. Re-emitted each BP1 file with BP1 + BP2 + BP3 levels and full APQC framework_refs and BC realizes_capability_ids. | Multiple commits during the BP3 expansion. |
| `import_industry_pcfs.py` | Authored the first industry-specific BP1 files (Banking, Insurance, Telecommunications) at BP1 + BP2 depth. | Multiple commits during the industry-PCF expansion. |

## How to revive one (don't, unless you really need to)

If a future migration needs the same shape, prefer copying and adapting the
relevant script into `scripts/` (not back into `_archive/`). Treat the
archived copy as documentation, not as live code.


## Phase 2 addendum

| Script | What it did | When it ran |
|---|---|---|
| `import_industry_pcfs_phase2.py` | Authored 11 industry-specific BP1 files (Healthcare ×2, Life Sciences ×2, Petroleum ×2, A&D ×1, Education ×2, Utilities ×2) at BP1 + BP2 depth, anchored on APQC industry PCFs and supporting frameworks per `business-capability-governance-model.md` §11.7. | One PR (multiple commits). |

## Phase 3 addendum

| Script | What it did | When it ran |
|---|---|---|
| `import_industry_pcfs_phase3.py` | Authored 3 more industry-specific BP1 files (Retail BP-280, Automotive OEM BP-290, Health Insurance Payor BP-300) at BP1 + BP2 depth, anchored on APQC industry PCFs per `business-capability-governance-model.md` §11.7. | One PR (multiple commits). |
| `wire_industry_vs_process_ids.py` | Populated `process_ids[]` on industry-specific value-stream stages now that the corresponding industry BP1+BP2 files exist (Banking VS-40, Insurance VS-240/VS-450, Telecom VS-510/VS-570, Healthcare VS-120/VS-180/VS-410, Pharma VS-20/VS-160, Oil & Gas VS-330, Defense VS-110/VS-590, Education VS-60/VS-430, Utilities VS-260/VS-550, Automotive VS-70/VS-630, Retail VS-610). | One PR (multiple per-industry commits). |

## Phase 4 addendum

| Script | What it did | When it ran |
|---|---|---|
| `import_industry_pcfs_phase4.py` | Authored 6 industry-specific BP1 files (Mining BP-310, Real Estate BP-320/330, Public Sector BP-340/350/360) at BP1 + BP2 depth. | One PR (multiple commits). |
| `wire_industry_vs_phase4.py` | Wired `process_ids[]` for Real Estate (VS-340/360/530/560) and Public Sector (VS-30/50/90/210/220/480/490/540/640) value streams. | One PR (multiple per-industry commits). |
| `import_industry_bp3.py` | BP3 drill-down for Pharma (BP-190/200), Banking (BP-130/140), Healthcare Provider (BP-170/180) — re-emitted each industry BP1 with BP1+BP2+BP3 levels. | One PR (one commit per industry). |
