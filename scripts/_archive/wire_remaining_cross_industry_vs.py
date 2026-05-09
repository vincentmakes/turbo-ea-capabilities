#!/usr/bin/env python3
"""Wire process_ids for the 12 remaining unwired Cross-Industry VS streams.

VS-310 Issue-to-Resolution (108 stages with industry-variant suffixes) is
mapped by stage_name *prefix* — e.g. all 'Issue Capture (...)' variants
share the same cross-industry BP mapping; the variant names retain their
industry context for the site UI.
"""
from __future__ import annotations
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")

EXACT_MAPPING = {
    # VS-10 Acquire-to-Retire
    ("VS-10", "Asset Need & Justification"): ["BP-100.10"],
    ("VS-10", "Acquisition"): ["BP-100.10", "BP-40.20"],
    ("VS-10", "Commissioning & Capitalisation"): ["BP-100.20", "BP-90.40"],
    ("VS-10", "Operate & Maintain"): ["BP-100.30"],
    ("VS-10", "Risk & Reliability"): ["BP-110.10", "BP-100.30"],
    ("VS-10", "Asset Information Maintenance"): ["BP-100.30", "BP-80.60"],
    ("VS-10", "Decommissioning & Disposal"): ["BP-100.40"],
    # VS-80 Audit-to-Action
    ("VS-80", "Audit Universe & Plan"): ["BP-90.80", "BP-110.10"],
    ("VS-80", "Engagement Scoping"): ["BP-90.80", "BP-110.10"],
    ("VS-80", "Fieldwork"): ["BP-90.80"],
    ("VS-80", "Findings & Reporting"): ["BP-90.80", "BP-120.30"],
    ("VS-80", "Remediation Tracking"): ["BP-90.80", "BP-110.30"],
    ("VS-80", "Audit Quality Assurance"): ["BP-90.80", "BP-370.30"],
    # VS-140 Crisis-to-Recovery
    ("VS-140", "Continuity Planning"): ["BP-110.40"],
    ("VS-140", "Resilience Testing"): ["BP-110.40"],
    ("VS-140", "Detection & Activation"): ["BP-110.40", "BP-80.10"],
    ("VS-140", "Crisis Response"): ["BP-110.40", "BP-120.50"],
    ("VS-140", "Disaster Recovery"): ["BP-80.10", "BP-110.40"],
    ("VS-140", "Restoration"): ["BP-110.40"],
    ("VS-140", "Post-Crisis Review"): ["BP-110.40", "BP-370.30"],
    # VS-150 Discover-to-Automate
    ("VS-150", "Process Discovery"): ["BP-370.10"],
    ("VS-150", "Process Measurement"): ["BP-370.10", "BP-370.30"],
    ("VS-150", "Process Mining"): ["BP-370.10"],
    ("VS-150", "Process Redesign"): ["BP-370.10", "BP-370.40"],
    ("VS-150", "Process Automation"): ["BP-370.10", "BP-80.30"],
    # VS-200 ESG-to-Disclosure
    ("VS-200", "ESG Strategy & Materiality"): ["BP-110.20", "BP-10.30"],
    ("VS-200", "Data Collection"): ["BP-90.30", "BP-110.20"],
    ("VS-200", "Data Quality & Assurance"): ["BP-90.30", "BP-370.30"],
    ("VS-200", "Reporting & Disclosure"): ["BP-90.30", "BP-120.10"],
    ("VS-200", "Stakeholder Engagement"): ["BP-120.10", "BP-120.50"],
    ("VS-200", "Improvement Targets"): ["BP-110.20", "BP-370.20"],
    # VS-380 Opportunity-to-Order
    ("VS-380", "Opportunity Qualification"): ["BP-30.50"],
    ("VS-380", "Solution Scoping"): ["BP-30.50", "BP-20.30"],
    ("VS-380", "Quote & Configuration"): ["BP-30.50"],
    ("VS-380", "Pricing & Approvals"): ["BP-30.40", "BP-30.50"],
    ("VS-380", "Proposal Development"): ["BP-30.50"],
    ("VS-380", "Negotiation"): ["BP-30.50", "BP-120.40"],
    ("VS-380", "Contract & Order Booking"): ["BP-30.50", "BP-120.40"],
    ("VS-380", "Handover to Fulfilment"): ["BP-40.10", "BP-50.30"],
    # VS-400 Plan-to-Inventory
    ("VS-400", "Demand Planning"): ["BP-40.10"],
    ("VS-400", "Supply Planning"): ["BP-40.10"],
    ("VS-400", "S&OP Reconciliation"): ["BP-40.10", "BP-90.10"],
    ("VS-400", "Inventory Positioning"): ["BP-40.10", "BP-40.40"],
    ("VS-400", "Replenishment Execution"): ["BP-40.20", "BP-40.40"],
    ("VS-400", "Inventory Health Monitoring"): ["BP-40.40", "BP-90.10"],
    # VS-440 Prospect-to-Customer
    ("VS-440", "Market & Segment Strategy"): ["BP-30.10", "BP-30.20"],
    ("VS-440", "Brand & Positioning"): ["BP-30.20", "BP-30.40"],
    ("VS-440", "Demand Generation"): ["BP-30.40"],
    ("VS-440", "Lead Capture & Nurture"): ["BP-30.50", "BP-30.40"],
    ("VS-440", "Conversion"): ["BP-30.50"],
    ("VS-440", "Customer Onboarding"): ["BP-30.50", "BP-50.30"],
    ("VS-440", "Retention & Advocacy"): ["BP-30.50", "BP-60.20"],
    # VS-500 Risk-to-Mitigation
    ("VS-500", "Risk Appetite & Framework"): ["BP-110.10"],
    ("VS-500", "Risk Identification"): ["BP-110.10"],
    ("VS-500", "Risk Assessment"): ["BP-110.10"],
    ("VS-500", "Treatment & Control Design"): ["BP-110.10", "BP-90.80"],
    ("VS-500", "Monitoring"): ["BP-110.10", "BP-90.80"],
    ("VS-500", "Reporting & Escalation"): ["BP-110.10", "BP-120.30"],
    # VS-580 Strategy-to-Execution
    ("VS-580", "Strategy Formulation"): ["BP-10.20", "BP-10.10"],
    ("VS-580", "Portfolio Definition"): ["BP-10.30", "BP-370.20"],
    ("VS-580", "Programme & Project Setup"): ["BP-10.30", "BP-370.20"],
    ("VS-580", "Delivery & Governance"): ["BP-370.20"],
    ("VS-580", "Change Adoption"): ["BP-370.40"],
    ("VS-580", "Benefits Realisation"): ["BP-10.30", "BP-370.30"],
    # VS-600 Threat-to-Mitigation
    ("VS-600", "Security Posture Definition"): ["BP-80.10"],
    ("VS-600", "Threat Intelligence"): ["BP-80.10"],
    ("VS-600", "Vulnerability Discovery"): ["BP-80.10"],
    ("VS-600", "Detection"): ["BP-80.10"],
    ("VS-600", "Incident Response"): ["BP-80.10", "BP-110.40"],
    ("VS-600", "Identity & Access Hardening"): ["BP-80.10"],
    ("VS-600", "Awareness & Lessons Learned"): ["BP-80.10", "BP-370.30"],
}

PREFIX_MAPPING = [
    ("VS-310", "Issue Capture (",     ["BP-50.40", "BP-60.20"]),
    ("VS-310", "Investigation (",     ["BP-110.10", "BP-90.80"]),
    ("VS-310", "Resolution (",        ["BP-50.40", "BP-60.20", "BP-370.30"]),
    ("VS-310", "Lessons Learned (",   ["BP-370.30", "BP-110.10"]),
]


def lookup(stream_id, stage_name):
    if (stream_id, stage_name) in EXACT_MAPPING:
        return EXACT_MAPPING[(stream_id, stage_name)]
    for sid, prefix, bps in PREFIX_MAPPING:
        if stream_id == sid and stage_name.startswith(prefix):
            return bps
    return None


def main():
    with open(PATH) as f: data = yaml.safe_load(f)
    target_streams = {sid for (sid, _) in EXACT_MAPPING.keys()} | {sid for sid, _, _ in PREFIX_MAPPING}
    updated = 0
    skipped = 0
    no_match = []
    for stream in data["value_streams"]:
        if stream["id"] not in target_streams: continue
        for stage in stream["stages"]:
            bps = lookup(stream["id"], stage["stage_name"])
            if bps is None:
                if len(no_match) < 8:
                    no_match.append((stream["id"], stage["id"], stage["stage_name"]))
                continue
            existing = stage.get("process_ids") or []
            if existing:
                skipped += 1
                continue
            stage["process_ids"] = list(bps)
            updated += 1
    if no_match:
        print("⚠ No mapping (sample):")
        for s in no_match: print(f"   {s}")
    preamble = ("# Value Streams (orthogonal artefact, not part of the capability hierarchy).\n"
                "# Each stream has a stable VS-<n> id (sparse 10/20/30 numbering); each stage\n"
                "# has a stable VS-<n>.<m> id and links to L1 capabilities (`capability_ids`)\n"
                "# and to business processes (`process_ids`) that realize the work. The site\n"
                "# auto-expands an L1 to its descendants when filtering. Use 'notes' to capture\n"
                "# sub-scope detail.\n#\n"
                "# Each stream declares an `industries` array using the canonical L1 industry\n"
                "# vocabulary. `Cross-Industry`, when present, must stand alone.\n")
    body = yaml.safe_dump({"value_streams": data["value_streams"]}, sort_keys=False, width=10**9, allow_unicode=True)
    with open(PATH, "w", encoding="utf-8") as f: f.write(preamble + body)
    print(f"✔ Updated {updated} stage(s); skipped {skipped}.")


if __name__ == "__main__":
    main()
