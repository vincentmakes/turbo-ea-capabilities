#!/usr/bin/env python3
"""Industry-specific PCF generator (Phase 3): Retail, Automotive OEM,
Health Insurance Payor.

Three more industry BP1 imports to round out the immediately-mappable
industries from the existing BC catalogue. BP1 + BP2 only.

References (cross-checked May 2026, see business-capability-governance-model.md §11.7
addendum committed alongside this script):
  - Retail:   APQC Retail PCF v7.2.1 + ARTS / NRF data model
  - Automotive (OEM): APQC Automotive (OEM) PCF v7.2.2
  - Health Insurance Payor: APQC Health Insurance Payor PCF v7.2.1

Usage:
    python3 scripts/import_industry_pcfs_phase3.py --bp1 BP-280
    python3 scripts/import_industry_pcfs_phase3.py --all
"""
from __future__ import annotations

import argparse
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")


def slugify(name: str) -> str:
    out, last_dash = [], True
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch); last_dash = False
        else:
            if not last_dash:
                out.append("-"); last_dash = True
    return "".join(out).strip("-")


TREE: dict[str, dict] = {}

TREE["BP-280"] = {
    "id": "BP-280",
    "name": "Operate Retail Merchandising and Stores",
    "description": "Run retail-specific operations: merchandising and assortment, omni-channel commerce, store operations, loyalty, and supply for store and online fulfilment. Aligned to APQC Retail PCF's industry-specific categories (Develop and Manage Customer Experience, Market Products and Services, Merchandise Products and Services, Deliver Products).",
    "industry": "Retail & Consumer Goods",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Retail PCF v7.2.1 — Operating categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-280.10", "Manage Merchandising and Assortment Planning",
         "Plan assortments, allocate space and shelf, and manage category and brand lifecycles.",
         ["BC-820", "BC-400"]),
        ("BP-280.20", "Manage Pricing, Promotions, and Markdown",
         "Set everyday and promotional pricing; plan and execute markdown and clearance.",
         ["BC-440"]),
        ("BP-280.30", "Operate Omni-Channel Commerce",
         "Operate e-commerce, mobile, marketplace, and digital channels alongside physical store sales.",
         ["BC-420", "BC-410"]),
        ("BP-280.40", "Operate Store Operations",
         "Run store-level operations: opening procedures, labour scheduling, cash handling, loss prevention.",
         ["BC-700", "BC-300"]),
        ("BP-280.50", "Operate Customer Loyalty and CX Programs",
         "Run loyalty, member, and customer-experience programs across channels.",
         ["BC-420"]),
        ("BP-280.60", "Manage Store and Online Fulfilment",
         "Fulfil orders across BOPIS, kerbside, ship-from-store, and DC-to-customer; manage last-mile.",
         ["BC-520", "BC-530"]),
    ],
}

TREE["BP-290"] = {
    "id": "BP-290",
    "name": "Manage Vehicle Programs and Dealer Network",
    "description": "Run automotive-OEM-specific operations: vehicle program management (including type approval and homologation), dealer network management, vehicle distribution, recall management, and connected/aftermarket services. Aligned to APQC Automotive (OEM) PCF v7.2.2.",
    "industry": "Automotive & Mobility",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Automotive (OEM) PCF v7.2.2"},
    ],
    "realizes": ["BC-820"],
    "children": [
        ("BP-290.10", "Manage Vehicle Program Lifecycle",
         "Govern vehicle programs from concept gate through SOP and end-of-production, including homologation and type approval.",
         ["BC-820", "BC-810"]),
        ("BP-290.20", "Manage Dealer Network",
         "Recruit, onboard, contract, and manage performance of the dealer network across regions.",
         ["BC-410", "BC-510"]),
        ("BP-290.30", "Manage Vehicle Distribution and Logistics",
         "Allocate, ship, and deliver finished vehicles to dealers and customers; manage build slots and ATP.",
         ["BC-520"]),
        ("BP-290.40", "Manage Vehicle Recalls and Field Actions",
         "Identify, investigate, and execute safety recalls and field service actions; manage NHTSA / regulator reporting.",
         ["BC-720", "BC-130"]),
        ("BP-290.50", "Operate Aftermarket and Parts Distribution",
         "Operate the aftermarket parts business: sourcing, distribution, dealer parts ordering, and remanufacture.",
         ["BC-520", "BC-530"]),
        ("BP-290.60", "Manage Connected and Mobility Services",
         "Operate connected-vehicle services, telematics, charging networks, and adjacent mobility offers.",
         ["BC-600", "BC-820"]),
    ],
}

TREE["BP-300"] = {
    "id": "BP-300",
    "name": "Operate Health Insurance Payor",
    "description": "Run health insurance payor operations: member enrolment and eligibility, provider network management, medical claims adjudication, care management, member services, and regulatory operations distinct from P&C insurance. Aligned to APQC Health Insurance Payor PCF v7.2.1.",
    "industry": "Insurance",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Health Insurance Payor PCF v7.2.1"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-300.10", "Manage Member Enrolment and Eligibility",
         "Enrol and disenrol members across individual, group, Medicare, and Medicaid lines; maintain eligibility.",
         []),
        ("BP-300.20", "Manage Provider Network and Contracting",
         "Recruit, contract, credential, and manage performance of in-network providers; maintain provider directory.",
         ["BC-510"]),
        ("BP-300.30", "Adjudicate Medical Claims",
         "Receive, edit, adjudicate, and pay medical claims under benefit plans; manage appeals and grievances.",
         []),
        ("BP-300.40", "Manage Care and Utilization",
         "Run care-management and utilisation-management programs: prior authorisation, case management, disease management.",
         []),
        ("BP-300.50", "Manage Member Services",
         "Service members across channels for inquiries, ID cards, formularies, and benefits questions.",
         ["BC-430"]),
        ("BP-300.60", "Manage Health Plan Regulatory Operations",
         "Run regulatory operations specific to health plans: HEDIS, Star Ratings, MLR reporting, state DOI filings.",
         ["BC-130"]),
    ],
}


def _emit_yaml(bp1: dict) -> str:
    L = []
    L.append(f"id: {bp1['id']}")
    L.append(f"name: {bp1['name']}")
    L.append("level: 1")
    L.append(f"industry: {bp1['industry']}")
    L.append("description: >-")
    L.append(f"  {bp1['description']}")
    if bp1.get("framework_refs"):
        L.append("framework_refs:")
        for fr in bp1["framework_refs"]:
            L.append("  - framework: " + fr["framework"])
            L.append(f"    external_id: \"{fr['external_id']}\"")
    L.append("realizes_capability_ids:")
    for bc in bp1["realizes"]:
        L.append(f"  - {bc}")
    L.append("children:")
    for cid, cname, cdesc, crealizes in bp1["children"]:
        L.append(f"  - id: {cid}")
        L.append(f"    name: {cname}")
        L.append("    level: 2")
        L.append("    description: >-")
        L.append(f"      {cdesc}")
        if crealizes:
            L.append("    realizes_capability_ids:")
            for bc in crealizes:
                L.append(f"      - {bc}")
        else:
            L.append("    realizes_capability_ids: []")
        L.append("    children: []")
    return "\n".join(L) + "\n"


def write_bp1(bp1: dict) -> str:
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_emit_yaml(bp1))
    return path


def update_index(new_filename: str):
    idx_path = os.path.join(PROCESSES_DIR, "_index.yaml")
    with open(idx_path) as fh:
        lines = fh.readlines()
    files, header = [], []
    in_files = False
    for ln in lines:
        if ln.startswith("files:"):
            in_files = True
            header.append(ln)
            continue
        if in_files and ln.strip().startswith("- "):
            files.append(ln.strip().lstrip("- "))
        elif not in_files:
            header.append(ln)
    if new_filename not in files:
        files.append(new_filename)
    files = sorted(files)
    with open(idx_path, "w") as fh:
        for ln in header:
            fh.write(ln)
        for f in files:
            fh.write(f"  - {f}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1", help="Single BP1 to write (e.g. BP-280).")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not (args.bp1 or args.all):
        ap.error("Pass --bp1 <id> or --all")

    targets = list(TREE.keys()) if args.all else [args.bp1]
    for bp1_id in targets:
        if bp1_id not in TREE:
            raise SystemExit(f"Unknown {bp1_id}; defined: {list(TREE.keys())}")
        bp1 = TREE[bp1_id]
        path = write_bp1(bp1)
        update_index(os.path.basename(path))
        print(f"✔ {bp1_id} → {os.path.relpath(path, REPO_ROOT)} "
              f"(industry: {bp1['industry']}, {len(bp1['children'])} BP2)")


if __name__ == "__main__":
    main()
