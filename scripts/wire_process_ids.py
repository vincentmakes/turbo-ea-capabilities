#!/usr/bin/env python3
"""One-shot wiring of process_ids into the 5 canonical Cross-Industry value
streams: Hire-to-Retire, Idea-to-Market, Order-to-Cash, Procure-to-Pay,
Record-to-Report.

Maps each stage by `stage_name` to one or more APQC PCF BP2 ids that realise
the work. Industry-variant stages inherit the same cross-industry process
mapping — industry-specific PCFs (Banking BIAN, Telecom eTOM, etc.) are not
yet imported and would land in a follow-up PR.

Run once, commit the resulting catalogue/_value-streams.yaml, then archive
this script under scripts/_archive/ in a follow-up PR.
"""
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")

# (stream_id, stage_name) -> [BP ids]
# Matching is by exact stage_name string; all industry-variant rows for the
# same (stream, stage_name) get the same mapping unless explicitly overridden.
MAPPING = {
    # ---------------------------------------------------------------- Hire-to-Retire
    ("VS-280", "Workforce Planning"): ["BP-70.10"],
    ("VS-280", "Sourcing & Attraction"): ["BP-70.20"],
    ("VS-280", "Selection & Hire"): ["BP-70.20"],
    ("VS-280", "Onboarding"): ["BP-70.30"],
    ("VS-280", "Performance & Development"): ["BP-70.30"],
    ("VS-280", "Compensation & Benefits Administration"): ["BP-70.40", "BP-90.50"],
    ("VS-280", "Employee Experience & Engagement"): ["BP-70.40", "BP-70.70"],
    ("VS-280", "Internal Mobility & Career"): ["BP-70.30", "BP-70.50"],
    ("VS-280", "Offboarding & Alumni"): ["BP-70.50"],

    # ---------------------------------------------------------------- Idea-to-Market
    ("VS-290", "Idea Capture"): ["BP-20.20"],
    ("VS-290", "Concept & Feasibility"): ["BP-20.20"],
    ("VS-290", "Research & Prototyping"): ["BP-20.30"],
    ("VS-290", "Portfolio Selection"): ["BP-20.10"],
    ("VS-290", "Design & Development"): ["BP-20.30"],
    ("VS-290", "IP Protection"): ["BP-20.30", "BP-120.40"],
    ("VS-290", "Launch Readiness"): ["BP-20.40", "BP-20.50"],
    ("VS-290", "Market Introduction"): ["BP-30.40", "BP-30.50"],
    ("VS-290", "Post-Launch Performance"): ["BP-20.10"],

    # ---------------------------------------------------------------- Order-to-Cash
    ("VS-390", "Lead Capture & Qualification"): ["BP-30.10", "BP-30.50"],
    ("VS-390", "Quote & Configuration"): ["BP-30.50"],
    ("VS-390", "Contract & Order Capture"): ["BP-30.50"],
    ("VS-390", "Order Promising & Allocation"): ["BP-40.10"],
    ("VS-390", "Production / Service Delivery"): ["BP-40.30", "BP-50.30"],
    ("VS-390", "Outbound Logistics"): ["BP-40.40"],
    ("VS-390", "Customer Invoicing"): ["BP-90.20"],
    ("VS-390", "Cash Collection & Application"): ["BP-90.20", "BP-90.70"],
    ("VS-390", "Revenue Recognition"): ["BP-90.20", "BP-90.30"],

    # ---------------------------------------------------------------- Procure-to-Pay
    ("VS-420", "Need Identification & Requisition"): ["BP-40.20"],
    ("VS-420", "Sourcing"): ["BP-40.20"],
    ("VS-420", "Supplier Selection & Onboarding"): ["BP-40.20"],
    ("VS-420", "Contract & Purchase Order"): ["BP-40.20"],
    ("VS-420", "Goods/Services Receipt"): ["BP-40.20"],
    ("VS-420", "Invoice Receipt & Verification"): ["BP-90.60"],
    ("VS-420", "Payment Execution"): ["BP-90.60", "BP-90.70"],
    ("VS-420", "Reconciliation"): ["BP-90.30", "BP-90.60"],
    ("VS-420", "Supplier Performance Monitoring"): ["BP-40.20"],

    # ---------------------------------------------------------------- Record-to-Report
    ("VS-460", "Transaction Capture"): ["BP-90.10", "BP-90.30"],
    ("VS-460", "Sub-Ledger Close"): ["BP-90.20", "BP-90.30", "BP-90.40", "BP-90.60"],
    ("VS-460", "Reconciliation & Adjustments"): ["BP-90.30"],
    ("VS-460", "Consolidation"): ["BP-90.30", "BP-90.100"],
    ("VS-460", "Management Reporting"): ["BP-90.10", "BP-90.30"],
    ("VS-460", "Statutory & Regulatory Reporting"): ["BP-90.30", "BP-90.90"],
    ("VS-460", "Audit & Sign-Off"): ["BP-90.80"],
}


def main():
    with open(PATH) as f:
        data = yaml.safe_load(f)

    target_stream_ids = {sid for (sid, _) in MAPPING.keys()}
    stages_updated = 0
    stages_skipped_mapped = 0  # already had process_ids
    stage_keys_seen = set()

    for stream in data["value_streams"]:
        if stream["id"] not in target_stream_ids:
            continue
        for stage in stream["stages"]:
            key = (stream["id"], stage["stage_name"])
            if key not in MAPPING:
                continue
            stage_keys_seen.add(key)
            existing = stage.get("process_ids") or []
            if existing:
                stages_skipped_mapped += 1
                continue
            stage["process_ids"] = list(MAPPING[key])
            stages_updated += 1

    unmapped = set(MAPPING.keys()) - stage_keys_seen
    if unmapped:
        print("⚠ Mapping keys with no matching stage:")
        for k in sorted(unmapped):
            print(f"   {k}")
        raise SystemExit(1)

    # Re-emit with the same preamble we use in migrate_value_streams.ts.
    preamble = (
        "# Value Streams (orthogonal artefact, not part of the capability hierarchy).\n"
        "# Each stream has a stable VS-<n> id (sparse 10/20/30 numbering); each stage\n"
        "# has a stable VS-<n>.<m> id and links to L1 capabilities (`capability_ids`)\n"
        "# and to business processes (`process_ids`) that realize the work. The site\n"
        "# auto-expands an L1 to its descendants when filtering. Use 'notes' to capture\n"
        "# sub-scope detail.\n"
        "#\n"
        "# Each stream declares an `industries` array using the canonical L1 industry\n"
        "# vocabulary. `Cross-Industry`, when present, must stand alone.\n"
    )
    body = yaml.safe_dump({"value_streams": data["value_streams"]}, sort_keys=False, width=10**9, allow_unicode=True)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(preamble + body)

    print(f"✔ Updated {stages_updated} stage(s) across {len(target_stream_ids)} stream(s).")
    if stages_skipped_mapped:
        print(f"  Skipped {stages_skipped_mapped} stage(s) that already had process_ids.")


if __name__ == "__main__":
    main()
