#!/usr/bin/env python3
"""Wire process_ids into industry-specific value streams whose anchoring
BP1 files now exist (Banking, Insurance, Telecom from PR #63; Healthcare,
Life Sciences, Petroleum, A&D, Education, Utilities from PR #64; Retail,
Automotive, Health Payor from this PR).

Mirrors scripts/_archive/wire_process_ids.py but for industry-specific
streams. After commit, archive alongside the other one-shots.

Usage:
    python3 scripts/wire_industry_vs_process_ids.py --stream VS-40
    python3 scripts/wire_industry_vs_process_ids.py --all
"""
from __future__ import annotations

import argparse
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")

# (stream_id, stage_name) -> [BP ids]
# Stage matching is by exact stage_name; all industry-variant rows for the
# same (stream, stage_name) get the same mapping.
MAPPING = {
    # ---------------------------------------------------------------- VS-20 Adverse-Event-to-Action (Pharma)
    ("VS-20", "Case Intake"): ["BP-200.40"],
    ("VS-20", "Case Triage & Coding"): ["BP-200.40"],
    ("VS-20", "Causality & Medical Review"): ["BP-200.40"],
    ("VS-20", "Signal Detection"): ["BP-200.40"],
    ("VS-20", "Risk Assessment & RMP Update"): ["BP-200.40"],
    ("VS-20", "Regulatory Reporting"): ["BP-200.40", "BP-200.50"],
    ("VS-20", "Label & Communication Updates"): ["BP-200.50"],
    ("VS-20", "Audit & Inspection Readiness"): ["BP-200.50", "BP-90.80"],

    # ---------------------------------------------------------------- VS-40 Application-to-Funding (Banking)
    ("VS-40", "Application Capture"): ["BP-130.20"],
    ("VS-40", "KYC & Due Diligence"): ["BP-130.20"],
    ("VS-40", "Underwriting & Decisioning"): ["BP-130.20"],
    ("VS-40", "Pricing & Offer"): ["BP-130.20"],
    ("VS-40", "Documentation & Booking"): ["BP-130.20", "BP-90.30"],
    ("VS-40", "Disbursement"): ["BP-130.20", "BP-90.70"],
    ("VS-40", "Servicing & Collections"): ["BP-130.20"],
    ("VS-40", "Portfolio Monitoring"): ["BP-130.20"],

    # ---------------------------------------------------------------- VS-60 Apply-to-Graduate (Education)
    ("VS-60", "Outreach & Recruitment"): ["BP-240.10"],
    ("VS-60", "Application & Admissions"): ["BP-240.10"],
    ("VS-60", "Enrolment & Registration"): ["BP-240.20"],
    ("VS-60", "Teaching & Learning Delivery"): ["BP-240.30"],
    ("VS-60", "Student Support"): ["BP-240.50"],
    ("VS-60", "Assessment & Examination"): ["BP-240.40"],
    ("VS-60", "Award & Credentialing"): ["BP-240.40", "BP-240.60"],

    # ---------------------------------------------------------------- VS-70 Appoint-to-Operate (Automotive)
    ("VS-70", "Network Strategy & Coverage"): ["BP-290.20"],
    ("VS-70", "Application & Vetting"): ["BP-290.20"],
    ("VS-70", "Agreement Execution"): ["BP-290.20"],
    ("VS-70", "Onboarding & Certification"): ["BP-290.20"],
    ("VS-70", "Standards Compliance"): ["BP-290.20"],
    ("VS-70", "Performance Management"): ["BP-290.20"],
    ("VS-70", "Termination & Transition"): ["BP-290.20"],

    # ---------------------------------------------------------------- VS-110 Capture-to-Contract (Defense)
    ("VS-110", "Customer Intelligence"): ["BP-230.10"],
    ("VS-110", "Capture Strategy"): ["BP-230.10"],
    ("VS-110", "Teaming & Subcontracting"): ["BP-230.10", "BP-230.50"],
    ("VS-110", "Bid & Proposal"): ["BP-230.10"],
    ("VS-110", "Pricing & Cost Estimation"): ["BP-230.10"],
    ("VS-110", "Compliance & Export Review"): ["BP-230.50"],
    ("VS-110", "Contract Negotiation & Award"): ["BP-230.20"],

    # ---------------------------------------------------------------- VS-120 Claim-to-Reimbursement (Healthcare)
    ("VS-120", "Charge Capture"): ["BP-180.50"],
    ("VS-120", "Coding"): ["BP-180.50"],
    ("VS-120", "Claim Production & Submission"): ["BP-180.50"],
    ("VS-120", "Adjudication & Denial Management"): ["BP-300.30"],
    ("VS-120", "Cash Posting & Reconciliation"): ["BP-90.20"],
    ("VS-120", "Patient Billing & Collections"): ["BP-90.20"],
    ("VS-120", "Underpayment Recovery"): ["BP-90.20"],

    # ---------------------------------------------------------------- VS-160 Discovery-to-Approval (Pharma)
    ("VS-160", "Target Discovery"): ["BP-190.10"],
    ("VS-160", "Hit & Lead Discovery"): ["BP-190.10"],
    ("VS-160", "Pre-Clinical Development"): ["BP-190.20"],
    ("VS-160", "Clinical Trial Design"): ["BP-190.30"],
    ("VS-160", "Clinical Trials Execution"): ["BP-190.30", "BP-190.40"],
    ("VS-160", "Phase Progression"): ["BP-190.30"],
    ("VS-160", "Regulatory Submission"): ["BP-190.50"],
    ("VS-160", "Approval & Launch Readiness"): ["BP-190.50", "BP-200.50"],
    ("VS-160", "Post-Marketing Surveillance"): ["BP-200.40"],

    # ---------------------------------------------------------------- VS-180 Encounter-to-Discharge (Healthcare)
    ("VS-180", "Pre-Encounter Access"): ["BP-170.10"],
    ("VS-180", "Registration & Admission"): ["BP-170.10"],
    ("VS-180", "Clinical Care Delivery"): ["BP-170.30"],
    ("VS-180", "Diagnostic & Therapeutic Services"): ["BP-180.10", "BP-180.20", "BP-180.30"],
    ("VS-180", "Clinical Documentation"): ["BP-180.50"],
    ("VS-180", "Care Coordination"): ["BP-170.40"],
    ("VS-180", "Discharge & Transition"): ["BP-170.50"],

    # ---------------------------------------------------------------- VS-240 First-Notice-to-Settlement (Insurance)
    ("VS-240", "FNOL Intake"): ["BP-150.40"],
    ("VS-240", "Triage & Coverage"): ["BP-150.40"],
    ("VS-240", "Investigation & Adjustment"): ["BP-150.40"],
    ("VS-240", "Reserving"): ["BP-150.40", "BP-150.60"],
    ("VS-240", "Settlement"): ["BP-150.40", "BP-90.70"],
    ("VS-240", "Recovery & Subrogation"): ["BP-150.40", "BP-150.50"],

    # ---------------------------------------------------------------- VS-260 Generate-to-Settle (Utilities)
    ("VS-260", "Generation Scheduling"): ["BP-260.10"],
    ("VS-260", "Wholesale Trading & Position Management"): ["BP-220.30", "BP-260.10"],
    ("VS-260", "Generation Operations"): ["BP-260.10"],
    ("VS-260", "System Balancing & Dispatch"): ["BP-260.30"],
    ("VS-260", "Distributed Energy Coordination"): ["BP-260.50"],
    ("VS-260", "Physical Delivery"): ["BP-260.30"],
    ("VS-260", "Metering & Imbalance Calculation"): ["BP-270.10"],
    ("VS-260", "Trade Settlement & Reporting"): ["BP-270.20", "BP-270.50"],

    # ---------------------------------------------------------------- VS-330 Lease-to-Production (Oil & Gas)
    ("VS-330", "Acreage Acquisition"): ["BP-210.10"],
    ("VS-330", "Prospect Maturation"): ["BP-210.20"],
    ("VS-330", "Exploration Drilling"): ["BP-210.20"],
    ("VS-330", "Reserves Maturation"): ["BP-210.30", "BP-210.50"],
    ("VS-330", "Field Development Sanction"): ["BP-210.40"],
    ("VS-330", "Development Execution"): ["BP-210.40"],
    ("VS-330", "First Production"): ["BP-220.10"],
    ("VS-330", "Operations Handover"): ["BP-220.10"],

    # ---------------------------------------------------------------- VS-410 Population-Health-to-Outcome (Healthcare)
    ("VS-410", "Population Identification"): ["BP-300.40"],
    ("VS-410", "Risk Stratification"): ["BP-300.40"],
    ("VS-410", "Care Gap Identification"): ["BP-300.40", "BP-180.50"],
    ("VS-410", "Outreach & Intervention"): ["BP-170.30", "BP-300.40"],
    ("VS-410", "Care Delivery"): ["BP-170.30"],
    ("VS-410", "Outcomes Measurement"): ["BP-170.60", "BP-180.60"],

    # ---------------------------------------------------------------- VS-430 Proposal-to-Impact (Education)
    ("VS-430", "Opportunity Identification"): ["BP-250.30"],
    ("VS-430", "Proposal Development"): ["BP-250.30"],
    ("VS-430", "Award & Setup"): ["BP-250.30"],
    ("VS-430", "Ethics & Integrity Oversight"): ["BP-250.30"],
    ("VS-430", "Research Conduct"): ["BP-250.30"],
    ("VS-430", "Output & Dissemination"): ["BP-250.30"],
    ("VS-430", "Impact Assessment"): ["BP-250.30"],

    # ---------------------------------------------------------------- VS-450 Quote-to-Bind (Insurance)
    ("VS-450", "Submission Intake"): ["BP-150.20", "BP-150.70"],
    ("VS-450", "Risk Evaluation & Pricing"): ["BP-150.20"],
    ("VS-450", "Quote Production"): ["BP-150.20"],
    ("VS-450", "Reinsurance Check"): ["BP-150.50"],
    ("VS-450", "Underwriting Decision"): ["BP-150.20"],
    ("VS-450", "Bind"): ["BP-150.20", "BP-150.30"],
    ("VS-450", "Policy Issuance"): ["BP-150.30"],
    ("VS-450", "Reinsurance Cession Setup"): ["BP-150.50"],

    # ---------------------------------------------------------------- VS-510 Settle-Inter-Operator (Telecom)
    ("VS-510", "Wholesale Agreement"): ["BP-160.50"],
    ("VS-510", "Usage Capture"): ["BP-160.20"],
    ("VS-510", "Rating & Charging"): ["BP-90.20"],
    ("VS-510", "Inter-Operator Settlement"): ["BP-160.50"],
    ("VS-510", "Dispute & Reconciliation"): ["BP-160.50"],

    # ---------------------------------------------------------------- VS-550 Source-to-Tap (Utilities)
    ("VS-550", "Resource Planning & Authorisation"): ["BP-260.60"],
    ("VS-550", "Catchment Stewardship"): ["BP-260.20"],
    ("VS-550", "Raw Water Abstraction"): ["BP-260.20"],
    ("VS-550", "Treatment"): ["BP-260.20"],
    ("VS-550", "Drinking Water Quality Assurance"): ["BP-260.20", "BP-110.30"],
    ("VS-550", "Bulk Storage & Transmission"): ["BP-260.30"],
    ("VS-550", "Distribution"): ["BP-260.30"],
    ("VS-550", "Customer Supply & Metering"): ["BP-270.10"],

    # ---------------------------------------------------------------- VS-570 Spectrum-to-Deployment (Telecom)
    ("VS-570", "Spectrum Strategy"): ["BP-160.50"],
    ("VS-570", "Licence Acquisition"): ["BP-160.50", "BP-120.20"],
    ("VS-570", "Frequency Assignment & Coordination"): ["BP-160.50"],
    ("VS-570", "Network Deployment"): ["BP-160.10"],
    ("VS-570", "Interference & Compliance"): ["BP-160.50", "BP-110.10"],
    ("VS-570", "Renewal & Reframing"): ["BP-160.50"],

    # ---------------------------------------------------------------- VS-590 Sustain-to-Disposition (Defense)
    ("VS-590", "Sustainment Planning"): ["BP-230.60"],
    ("VS-590", "Operate & Maintain"): ["BP-230.60", "BP-100.30"],
    ("VS-590", "Spares & Repairs"): ["BP-230.60"],
    ("VS-590", "Technical Documentation"): ["BP-230.40"],
    ("VS-590", "Obsolescence Management"): ["BP-230.60"],
    ("VS-590", "Capability Upgrades"): ["BP-230.30", "BP-230.40"],
    ("VS-590", "Disposal & Disposition"): ["BP-230.70"],

    # ---------------------------------------------------------------- VS-610 Trade-Plan-to-Settle (Retail)
    ("VS-610", "Trade Plan Development"): ["BP-30.40", "BP-280.20"],
    ("VS-610", "Fund Allocation"): ["BP-30.40"],
    ("VS-610", "Promotion Execution"): ["BP-30.40", "BP-280.20"],
    ("VS-610", "Deduction & Claim Handling"): ["BP-90.60"],
    ("VS-610", "Post-Event Lift Measurement"): ["BP-30.40", "BP-280.20"],

    # ---------------------------------------------------------------- VS-630 Validate-to-Authorise (Automotive)
    ("VS-630", "ODD Definition"): ["BP-290.10"],
    ("VS-630", "Scenario Coverage Build"): ["BP-290.10"],
    ("VS-630", "Validation Execution"): ["BP-290.10"],
    ("VS-630", "Safety Case Authoring"): ["BP-290.10", "BP-290.40"],
    ("VS-630", "Regulatory Authorisation"): ["BP-290.10", "BP-290.40"],
    ("VS-630", "Deployment Monitoring"): ["BP-290.40", "BP-290.60"],
    ("VS-630", "Incident Reporting & Iteration"): ["BP-290.40"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream", help="Single VS to wire (e.g. VS-40).")
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
