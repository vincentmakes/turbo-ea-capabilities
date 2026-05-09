#!/usr/bin/env python3
"""Wire process_ids into Real Estate and Public Sector value streams now that
BP-310 (Mining), BP-320/330 (Real Estate), BP-340/350/360 (Public Sector)
exist.

Usage:
    python3 scripts/wire_industry_vs_phase4.py --stream VS-340
    python3 scripts/wire_industry_vs_phase4.py --all
"""
from __future__ import annotations

import argparse
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")

MAPPING = {
    # ---------------------------------------------------------------- VS-340 Listing-to-Closing (Real Estate)
    ("VS-340", "Listing Pursuit & Win"): ["BP-330.10"],
    ("VS-340", "Listing Setup & Marketing"): ["BP-330.10"],
    ("VS-340", "Showing & Engagement"): ["BP-330.10"],
    ("VS-340", "Offer & Negotiation"): ["BP-330.10", "BP-330.20"],
    ("VS-340", "Contingency & Closing Coordination"): ["BP-330.20"],
    ("VS-340", "Closing Execution"): ["BP-330.20"],
    ("VS-340", "Commission Settlement"): ["BP-330.10", "BP-90.30"],

    # ---------------------------------------------------------------- VS-360 Mandate-to-Distribution (Real Estate fund mgmt)
    ("VS-360", "Mandate & Strategy Definition"): ["BP-330.30", "BP-320.10"],
    ("VS-360", "Vehicle Formation"): ["BP-330.30"],
    ("VS-360", "Capital Raising"): ["BP-330.30", "BP-120.10"],
    ("VS-360", "Capital Deployment"): ["BP-330.30", "BP-330.20"],
    ("VS-360", "NAV & Performance Management"): ["BP-330.30", "BP-90.30"],
    ("VS-360", "LP Reporting"): ["BP-330.30", "BP-90.30"],
    ("VS-360", "Distribution & Wind-Down"): ["BP-330.30"],

    # ---------------------------------------------------------------- VS-530 Site-to-Stabilisation (Real Estate development)
    ("VS-530", "Site Sourcing & Origination"): ["BP-330.20"],
    ("VS-530", "Feasibility & Underwriting"): ["BP-330.20", "BP-320.40"],
    ("VS-530", "Entitlement & Permitting"): ["BP-340.30", "BP-320.40"],
    ("VS-530", "Development Capitalisation"): ["BP-330.30"],
    ("VS-530", "Design & Construction Execution"): ["BP-100.20"],
    ("VS-530", "Lease-Up & Stabilisation"): ["BP-320.20"],
    ("VS-530", "Operational Handover"): ["BP-320.30", "BP-320.10"],

    # ---------------------------------------------------------------- VS-560 Sourcing-to-Onboarding (Real Estate acquisitions)
    ("VS-560", "Deal Sourcing"): ["BP-330.20"],
    ("VS-560", "Underwriting"): ["BP-330.20"],
    ("VS-560", "Due Diligence"): ["BP-330.20"],
    ("VS-560", "Structuring & Negotiation"): ["BP-330.20"],
    ("VS-560", "Closing & Settlement"): ["BP-330.20", "BP-90.70"],
    ("VS-560", "Operational Onboarding"): ["BP-320.30"],
    ("VS-560", "Asset Management Handover"): ["BP-320.10", "BP-320.30"],

    # ---------------------------------------------------------------- VS-30 Application-to-Benefit (Public Sector)
    ("VS-30", "Programme Configuration"): ["BP-340.20"],
    ("VS-30", "Application Intake"): ["BP-340.20"],
    ("VS-30", "Eligibility Determination"): ["BP-340.20"],
    ("VS-30", "Award Calculation"): ["BP-340.20"],
    ("VS-30", "Disbursement"): ["BP-340.20", "BP-90.70"],
    ("VS-30", "Continuing Eligibility"): ["BP-340.20"],
    ("VS-30", "Overpayment & Recovery"): ["BP-340.20", "BP-350.30"],
    ("VS-30", "Fraud Investigation"): ["BP-350.30"],

    # ---------------------------------------------------------------- VS-50 Application-to-Licence (Public Sector)
    ("VS-50", "Application Intake"): ["BP-340.30"],
    ("VS-50", "Eligibility & Qualification Assessment"): ["BP-340.30"],
    ("VS-50", "Licensing Decision"): ["BP-340.30"],
    ("VS-50", "Credential Issuance"): ["BP-340.30"],
    ("VS-50", "Inspection & Compliance Monitoring"): ["BP-350.30"],
    ("VS-50", "Enforcement & Sanction"): ["BP-350.30"],
    ("VS-50", "Renewal"): ["BP-340.30"],
    ("VS-50", "Register Disclosure"): ["BP-340.50"],

    # ---------------------------------------------------------------- VS-90 Bill-to-Statute (Public Sector legislative — limited BP coverage)
    ("VS-90", "Drafting Instruction"): ["BP-120.20"],
    ("VS-90", "Drafting"): ["BP-120.20"],
    ("VS-90", "Legal Vetting"): ["BP-120.20", "BP-120.40"],
    ("VS-90", "Impact Assessment"): ["BP-120.20"],
    ("VS-90", "Legislative Passage"): ["BP-120.20"],
    ("VS-90", "Promulgation"): ["BP-120.20", "BP-340.50"],
    ("VS-90", "Codification & Publication"): ["BP-340.50"],

    # ---------------------------------------------------------------- VS-210 Event-to-Record (Public Sector vital records)
    ("VS-210", "Event Notification"): ["BP-340.50"],
    ("VS-210", "Registration"): ["BP-340.50"],
    ("VS-210", "Certification & Issuance"): ["BP-340.10", "BP-340.50"],
    ("VS-210", "Authentication"): ["BP-340.10"],
    ("VS-210", "Disclosure & Search"): ["BP-340.10"],
    ("VS-210", "Record Maintenance & Privacy"): ["BP-340.50", "BP-340.10"],

    # ---------------------------------------------------------------- VS-220 Filing-to-Disposition (Public Sector judicial)
    ("VS-220", "Case Filing"): ["BP-350.40"],
    ("VS-220", "Docket & Scheduling"): ["BP-350.40"],
    ("VS-220", "Hearing & Trial"): ["BP-350.40"],
    ("VS-220", "Judgment & Sentencing"): ["BP-350.40"],
    ("VS-220", "Order Enforcement"): ["BP-350.30", "BP-350.40"],
    ("VS-220", "Custody & Supervision"): ["BP-350.40"],
    ("VS-220", "Records & Public Access"): ["BP-350.40"],

    # ---------------------------------------------------------------- VS-480 Registration-to-Certification (Public Sector elections)
    ("VS-480", "Voter Registration"): ["BP-340.10", "BP-340.50"],
    ("VS-480", "Boundary & Polling Place Setup"): ["BP-340.50"],
    ("VS-480", "Candidate Nomination"): ["BP-340.30"],
    ("VS-480", "Ballot Production"): ["BP-340.50"],
    ("VS-480", "Polling"): ["BP-340.50"],
    ("VS-480", "Counting & Tabulation"): ["BP-340.50"],
    ("VS-480", "Certification"): ["BP-340.30"],
    ("VS-480", "Campaign Finance Disclosure"): ["BP-340.50", "BP-350.10"],

    # ---------------------------------------------------------------- VS-490 Return-to-Collection (Public Sector tax)
    ("VS-490", "Taxpayer Registration"): ["BP-350.10"],
    ("VS-490", "Return Lodgement"): ["BP-350.10"],
    ("VS-490", "Assessment"): ["BP-350.10"],
    ("VS-490", "Payment Collection"): ["BP-350.10"],
    ("VS-490", "Refund & Credit"): ["BP-350.10"],
    ("VS-490", "Audit & Examination"): ["BP-350.10", "BP-350.30"],
    ("VS-490", "Debt Enforcement"): ["BP-350.10", "BP-350.30"],

    # ---------------------------------------------------------------- VS-540 Solicitation-to-Closeout (Public Sector grants/contracts)
    ("VS-540", "Programme Design"): ["BP-360.30", "BP-360.20"],
    ("VS-540", "Solicitation Publication"): ["BP-360.10"],
    ("VS-540", "Application Review"): ["BP-360.10"],
    ("VS-540", "Award & Agreement"): ["BP-360.10", "BP-360.30"],
    ("VS-540", "Recipient Monitoring"): ["BP-360.30", "BP-360.40"],
    ("VS-540", "Closeout & Audit Resolution"): ["BP-360.30", "BP-360.40"],

    # ---------------------------------------------------------------- VS-640 Visa-to-Admission (Public Sector)
    ("VS-640", "Visa Application"): ["BP-340.40"],
    ("VS-640", "Visa Decisioning"): ["BP-340.40"],
    ("VS-640", "Pre-Travel Authorisation"): ["BP-340.40"],
    ("VS-640", "Border Inspection"): ["BP-340.40"],
    ("VS-640", "Admission Decision"): ["BP-340.40"],
    ("VS-640", "Status Maintenance"): ["BP-340.40"],
    ("VS-640", "Removal & Return"): ["BP-340.40"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream", help="Single VS to wire (e.g. VS-340).")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not (args.stream or args.all):
        ap.error("Pass --stream <id> or --all")

    with open(PATH) as f:
        data = yaml.safe_load(f)

    target_streams = (
        {sid for (sid, _) in MAPPING.keys()} if args.all else {args.stream}
    )

    stages_updated = 0
    stages_skipped = 0
    seen = set()
    for stream in data["value_streams"]:
        if stream["id"] not in target_streams:
            continue
        for stage in stream["stages"]:
            key = (stream["id"], stage["stage_name"])
            if key not in MAPPING:
                continue
            seen.add(key)
            existing = stage.get("process_ids") or []
            if existing:
                stages_skipped += 1
                continue
            stage["process_ids"] = list(MAPPING[key])
            stages_updated += 1

    unmapped = {k for k in MAPPING.keys() if k[0] in target_streams} - seen
    if unmapped:
        print("⚠ Mapping keys with no matching stage:")
        for k in sorted(unmapped):
            print(f"   {k}")
        raise SystemExit(1)

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

    print(f"✔ Updated {stages_updated} stage(s); skipped {stages_skipped} already-mapped stage(s).")


if __name__ == "__main__":
    main()
