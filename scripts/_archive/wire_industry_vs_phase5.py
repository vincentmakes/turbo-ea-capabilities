#!/usr/bin/env python3
"""Wire process_ids for the 12 gap-industry value streams now that BP-380..490 exist."""
from __future__ import annotations
import argparse, os, yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")

MAPPING = {
    # ---------- VS-100 Brief-to-Campaign (Media)
    ("VS-100", "Brief Intake"): ["BP-390.50"],
    ("VS-100", "Audience & Avail Planning"): ["BP-390.50", "BP-390.60"],
    ("VS-100", "Media Plan Development"): ["BP-390.50", "BP-30.40"],
    ("VS-100", "Booking & Insertion Order"): ["BP-390.50"],
    ("VS-100", "Creative Onboarding & Trafficking"): ["BP-390.40", "BP-390.50"],
    ("VS-100", "Campaign Delivery"): ["BP-390.40", "BP-390.50"],
    ("VS-100", "Measurement & Reconciliation"): ["BP-390.60"],
    ("VS-100", "Billing & Settlement"): ["BP-90.20", "BP-390.50"],
    # ---------- VS-170 Disruption-to-Recovery (Travel)
    ("VS-170", "Disruption Detection"): ["BP-380.20", "BP-110.20"],
    ("VS-170", "Operational Decision"): ["BP-380.60", "BP-380.20"],
    ("VS-170", "Traveller Reaccommodation"): ["BP-380.20", "BP-380.10"],
    ("VS-170", "Communications"): ["BP-380.20", "BP-120.50"],
    ("VS-170", "Care of Passengers"): ["BP-380.20", "BP-380.60"],
    ("VS-170", "Compensation Closure"): ["BP-380.20", "BP-90.60"],
    ("VS-170", "Post-Event Review"): ["BP-110.20", "BP-380.20"],
    # ---------- VS-190 Engagement-to-Realisation (Prof Services + Real Estate)
    ("VS-190", "Engagement Acceptance"): ["BP-400.10", "BP-400.50"],
    ("VS-190", "Mobilisation"): ["BP-400.10", "BP-400.20"],
    ("VS-190", "Delivery"): ["BP-400.10"],
    ("VS-190", "Quality Review"): ["BP-400.50"],
    ("VS-190", "Issuance"): ["BP-400.10"],
    ("VS-190", "Billing & Realisation"): ["BP-400.10", "BP-90.20"],
    ("VS-190", "File Lock-Down & Retention"): ["BP-400.40", "BP-400.10"],
    # ---------- VS-230 Firmware-to-Field (Electrical)
    ("VS-230", "Firmware Build & Sign"): ["BP-460.10", "BP-80.30"],
    ("VS-230", "Release Authorisation"): ["BP-460.20"],
    ("VS-230", "Staged Rollout & Pilot"): ["BP-80.40", "BP-460.30"],
    ("VS-230", "OTA Distribution"): ["BP-80.40", "BP-460.30"],
    ("VS-230", "Field Telemetry & Health"): ["BP-460.30", "BP-50.40"],
    ("VS-230", "Vulnerability & Incident Response"): ["BP-80.10", "BP-460.20"],
    ("VS-230", "Decommission & Sunset"): ["BP-460.30"],
    # ---------- VS-250 Flight-to-Settle (ATC)
    ("VS-250", "Flight Plan Filing"): ["BP-430.20"],
    ("VS-250", "Flight Operations"): ["BP-430.30"],
    ("VS-250", "Charge Determination"): ["BP-90.20"],
    ("VS-250", "Invoicing"): ["BP-90.20"],
    ("VS-250", "Collection"): ["BP-90.20", "BP-90.70"],
    ("VS-250", "Reconciliation & Reporting"): ["BP-90.30"],
    # ---------- VS-270 Greenlight-to-Premiere (Media)
    ("VS-270", "Concept & Pitch Intake"): ["BP-390.10"],
    ("VS-270", "Greenlight Decision"): ["BP-390.10"],
    ("VS-270", "Pre-Production"): ["BP-390.20"],
    ("VS-270", "Production"): ["BP-390.20"],
    ("VS-270", "Post-Production & Mastering"): ["BP-390.20"],
    ("VS-270", "Rights & Compliance Clearance"): ["BP-390.30", "BP-110.10"],
    ("VS-270", "Schedule & Catalogue Placement"): ["BP-390.40"],
    ("VS-270", "Distribution & Premiere"): ["BP-390.40"],
    ("VS-270", "Performance Feedback"): ["BP-390.60"],
    # ---------- VS-300 Insight-to-Reuse (Prof Services)
    ("VS-300", "Asset Identification"): ["BP-400.40"],
    ("VS-300", "Sanitisation & Redaction"): ["BP-400.40"],
    ("VS-300", "Curation & Versioning"): ["BP-400.40"],
    ("VS-300", "Cataloguing"): ["BP-400.40"],
    ("VS-300", "Distribution & Community"): ["BP-400.40"],
    ("VS-300", "Reuse & Analytics"): ["BP-400.40"],
    # ---------- VS-320 Lead-to-Event (Travel - MICE/events)
    ("VS-320", "Lead Qualification"): ["BP-380.30", "BP-380.10"],
    ("VS-320", "Proposal & Contract"): ["BP-380.30", "BP-30.50"],
    ("VS-320", "Block & Event Setup"): ["BP-380.10", "BP-380.60"],
    ("VS-320", "Event Execution"): ["BP-380.60", "BP-380.20"],
    ("VS-320", "Settlement"): ["BP-90.20", "BP-380.60"],
    ("VS-320", "Post-Event"): ["BP-380.20", "BP-380.60"],
    # ---------- VS-370 Network-Plan-to-Service (Transp & Log)
    ("VS-370", "Demand Forecast"): ["BP-40.10", "BP-410.10"],
    ("VS-370", "Network Design"): ["BP-410.10"],
    ("VS-370", "Capacity & Schedule Plan"): ["BP-410.10"],
    ("VS-370", "Service Publication"): ["BP-410.20"],
    ("VS-370", "Service Operations"): ["BP-410.20"],
    ("VS-370", "Performance Monitoring & Re-plan"): ["BP-410.10", "BP-50.40"],
    # ---------- VS-470 Refrigerant-to-Reclaim (HVAC)
    ("VS-470", "Procurement & Inventory"): ["BP-450.40", "BP-40.20"],
    ("VS-470", "Charge & Install"): ["BP-450.20", "BP-450.40"],
    ("VS-470", "Leak Detection & Repair"): ["BP-450.30", "BP-450.40"],
    ("VS-470", "Recovery & Reclaim"): ["BP-450.40"],
    ("VS-470", "Regulatory Reporting"): ["BP-450.40", "BP-110.30"],
    ("VS-470", "Phase-Out & Substitution"): ["BP-450.40", "BP-450.10"],
    ("VS-470", "End-of-Life Disposition"): ["BP-450.40", "BP-100.40"],
    # ---------- VS-520 Shop-to-Stay (Travel)
    ("VS-520", "Inspire & Discover"): ["BP-380.30", "BP-30.40"],
    ("VS-520", "Shop & Compare"): ["BP-380.30", "BP-380.50"],
    ("VS-520", "Book & Confirm"): ["BP-380.10", "BP-380.30"],
    ("VS-520", "Pre-Arrival"): ["BP-380.20"],
    ("VS-520", "Travel & Stay"): ["BP-380.20", "BP-380.60"],
    ("VS-520", "Settle & Recognise"): ["BP-90.20", "BP-380.60"],
    ("VS-520", "Post-Stay & Retain"): ["BP-380.40", "BP-380.20"],
    # ---------- VS-620 Trial-to-Renewal (Software & Tech)
    ("VS-620", "Trial Initiation"): ["BP-420.20"],
    ("VS-620", "Trial Activation"): ["BP-420.30", "BP-420.20"],
    ("VS-620", "Conversion to Paid"): ["BP-420.20"],
    ("VS-620", "Adoption"): ["BP-420.30"],
    ("VS-620", "Health & Risk Monitoring"): ["BP-420.40"],
    ("VS-620", "Renewal"): ["BP-420.40"],
    ("VS-620", "Expansion"): ["BP-420.40"],
    ("VS-620", "Churn or Wind-Down"): ["BP-420.20", "BP-420.40"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not (args.stream or args.all):
        ap.error("--stream <id> or --all")

    with open(PATH) as f: data = yaml.safe_load(f)
    target = ({sid for (sid, _) in MAPPING.keys()} if args.all else {args.stream})
    updated, skipped, seen = 0, 0, set()
    for stream in data["value_streams"]:
        if stream["id"] not in target: continue
        for stage in stream["stages"]:
            key = (stream["id"], stage["stage_name"])
            if key not in MAPPING: continue
            seen.add(key)
            if stage.get("process_ids"): skipped += 1; continue
            stage["process_ids"] = list(MAPPING[key])
            updated += 1
    unmapped = {k for k in MAPPING.keys() if k[0] in target} - seen
    if unmapped:
        for k in sorted(unmapped): print(f"⚠ unmapped: {k}")
        raise SystemExit(1)
    preamble = ("# Value Streams (orthogonal artefact, not part of the capability hierarchy).\n"
                "# Each stream has a stable VS-<n> id (sparse 10/20/30 numbering); each stage\n"
                "# has a stable VS-<n>.<m> id and links to L1 capabilities (`capability_ids`)\n"
                "# and to business processes (`process_ids`) that realize the work. The site\n"
                "# auto-expands an L1 to its descendants when filtering. Use 'notes' to capture\n"
                "# sub-scope detail.\n"
                "#\n"
                "# Each stream declares an `industries` array using the canonical L1 industry\n"
                "# vocabulary. `Cross-Industry`, when present, must stand alone.\n")
    body = yaml.safe_dump({"value_streams": data["value_streams"]}, sort_keys=False, width=10**9, allow_unicode=True)
    with open(PATH, "w", encoding="utf-8") as f: f.write(preamble + body)
    print(f"✔ Updated {updated} stage(s); skipped {skipped}.")


if __name__ == "__main__":
    main()
