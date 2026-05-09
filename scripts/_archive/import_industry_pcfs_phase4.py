#!/usr/bin/env python3
"""Industry-specific PCF generator (Phase 4): Mining & Metals, Real Estate,
Public Sector & Government.

6 net-new BP1 files capturing operational processes outside the cross-
industry baseline. Anchored on:
  - Mining & Metals: ICMM Mining Principles + CRIRSCO/JORC reserve standards
                     + GISTM tailings standard
  - Real Estate:     OSCRE IDM + RESO Data Dictionary + IPMS measurement
  - Public Sector:   FEAF + TOGAF Government Reference Model + IPSAS

Usage:
    python3 scripts/import_industry_pcfs_phase4.py --bp1 BP-310
    python3 scripts/import_industry_pcfs_phase4.py --all
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

# ------------------------------------------------------------ Mining & Metals
TREE["BP-310"] = {
    "id": "BP-310",
    "name": "Operate Mining and Metals Lifecycle",
    "description": "Run the end-to-end mining and metals lifecycle: exploration and resource definition, mine planning, extraction, mineral processing, tailings management, and mine closure and rehabilitation.",
    "industry": "Mining & Metals",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Mining lifecycle reference (no published APQC Mining PCF; structure aligned to ICMM Mining Principles and CRIRSCO reserve standards)"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-310.10", "Manage Mineral Exploration and Resource Definition",
         "Conduct mineral exploration; estimate and classify resources/reserves under JORC/SAMREC/NI 43-101.",
         []),
        ("BP-310.20", "Manage Mine Planning and Development",
         "Plan and design mine layouts; develop mine projects through feasibility study, construction, and commissioning.",
         ["BC-700", "BC-900"]),
        ("BP-310.30", "Operate Mining Extraction",
         "Operate underground or surface mining: drilling, blasting, hauling, and grade control.",
         []),
        ("BP-310.40", "Operate Mineral Processing and Beneficiation",
         "Process ore through crushing, grinding, flotation, leaching, smelting, refining, and product blending.",
         ["BC-720"]),
        ("BP-310.50", "Manage Tailings and Mining Waste",
         "Manage tailings storage facilities and mining waste under GISTM and ICMM tailings governance standards.",
         ["BC-730", "BC-740"]),
        ("BP-310.60", "Manage Mine Closure and Rehabilitation",
         "Plan and execute integrated mine closure: progressive rehabilitation, decommissioning, and post-closure monitoring per ICMM Integrated Mine Closure guidance.",
         ["BC-740", "BC-730"]),
    ],
}

# ------------------------------------------------------------ Real Estate
TREE["BP-320"] = {
    "id": "BP-320",
    "name": "Operate Real Estate Asset and Property Management",
    "description": "Run real-estate-specific asset and property operations: portfolio management, tenant lease lifecycle, day-to-day property/facility management, capital projects, and disposition.",
    "industry": "Real Estate",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Real Estate asset and property reference (OSCRE IDM-aligned)"},
    ],
    "realizes": ["BC-710"],
    "children": [
        ("BP-320.10", "Manage Real Estate Portfolio",
         "Plan and govern the portfolio of properties: asset strategy, hold/sell decisions, performance reporting.",
         ["BC-710"]),
        ("BP-320.20", "Manage Tenant Lease Lifecycle",
         "Originate, abstract, administer, and renew tenant leases; manage lease accounting and CAM reconciliation.",
         []),
        ("BP-320.30", "Operate Property Management and Facility Operations",
         "Run day-to-day property operations: tenant services, on-site management, vendor coordination, common-area facility management.",
         ["BC-700"]),
        ("BP-320.40", "Manage Property Capital Projects",
         "Plan and deliver capital projects on owned property: tenant improvements, repositioning, refurbishment.",
         ["BC-700", "BC-900"]),
        ("BP-320.50", "Manage Real Estate Disposition",
         "Position, market, and dispose of property assets; manage sale and post-closing transition.",
         ["BC-710"]),
    ],
}

TREE["BP-330"] = {
    "id": "BP-330",
    "name": "Operate Real Estate Brokerage and Capital Markets",
    "description": "Run real estate brokerage, transaction management, and capital-markets operations: listing and brokerage, acquisition/disposition advisory, real estate fund management, valuation and appraisal.",
    "industry": "Real Estate",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Real Estate brokerage / capital markets reference (RESO Data Dictionary, IPMS, RICS)"},
    ],
    "realizes": ["BC-710"],
    "children": [
        ("BP-330.10", "Manage Real Estate Listing and Brokerage",
         "Operate residential and commercial brokerage: listing agreements, MLS exposure, showings, and offer negotiation.",
         ["BC-410"]),
        ("BP-330.20", "Manage Real Estate Acquisition and Disposition Advisory",
         "Advise clients on acquisitions and dispositions: target identification, underwriting, due diligence, and deal closing.",
         ["BC-710"]),
        ("BP-330.30", "Manage Real Estate Capital Markets and Fund Management",
         "Operate real-estate fund and investment management: capital raising, fund administration, asset/portfolio reporting.",
         ["BC-210"]),
        ("BP-330.40", "Manage Real Estate Valuation and Appraisal",
         "Conduct property valuation and appraisal under IPMS / RICS / USPAP standards.",
         []),
    ],
}

# ------------------------------------------------------------ Public Sector & Government
TREE["BP-340"] = {
    "id": "BP-340",
    "name": "Manage Public Service and Benefit Delivery",
    "description": "Run citizen-facing public service delivery: identity and records, benefit and entitlement programs, licensing, immigration, and civil registration.",
    "industry": "Public Sector & Government",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "FEAF Business Reference Model — Service Delivery domain"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-340.10", "Manage Citizen Identity and Records",
         "Issue and maintain citizen identity, civil registration records, and verifiable credentials.",
         ["BC-610"]),
        ("BP-340.20", "Manage Benefit and Entitlement Programs",
         "Administer benefit and entitlement programs: eligibility, application, decision, payment, and ongoing review.",
         []),
        ("BP-340.30", "Manage Licensing and Permitting",
         "Operate licensing and permitting regimes: application intake, evaluation, issuance, renewal, and enforcement.",
         []),
        ("BP-340.40", "Manage Visa and Immigration",
         "Operate visa, asylum, immigration, and border admission processes.",
         []),
        ("BP-340.50", "Manage Vital and Statutory Records",
         "Maintain civil/vital records: births, deaths, marriages, statutory filings.",
         ["BC-610"]),
    ],
}

TREE["BP-350"] = {
    "id": "BP-350",
    "name": "Manage Public Sector Revenue and Compliance",
    "description": "Operate public-sector revenue collection and regulatory compliance: tax filing and collection, customs and trade, regulatory enforcement, and judicial / statutory filings.",
    "industry": "Public Sector & Government",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "FEAF — Tax Administration / Regulatory & Compliance domains"},
    ],
    "realizes": ["BC-220", "BC-130"],
    "children": [
        ("BP-350.10", "Manage Tax Filing and Collection",
         "Receive tax returns, assess liabilities, collect tax, and manage refunds and disputes.",
         ["BC-220"]),
        ("BP-350.20", "Manage Customs and Trade Administration",
         "Operate customs entry, duty assessment, trade-compliance, and border-control processes.",
         ["BC-130"]),
        ("BP-350.30", "Manage Regulatory Enforcement and Investigations",
         "Conduct regulatory inspections and investigations; impose and recover penalties.",
         ["BC-130", "BC-150"]),
        ("BP-350.40", "Manage Court and Statutory Filings",
         "Receive, docket, and process court filings and statutory submissions; manage case dispositions.",
         ["BC-150"]),
    ],
}

TREE["BP-360"] = {
    "id": "BP-360",
    "name": "Manage Public Sector Programs and Funding",
    "description": "Operate public-sector procurement and program funding: government procurement under FAR / EU rules, program funding administration, grants and awards, public-sector reporting.",
    "industry": "Public Sector & Government",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "FEAF — Mission Support / Resource Management domains; FAR / EU procurement"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-360.10", "Manage Public-Sector Procurement",
         "Plan, solicit, award, and administer government contracts under FAR / EU procurement rules.",
         ["BC-500"]),
        ("BP-360.20", "Manage Program Funding and Appropriations",
         "Administer appropriations, allotments, and obligations against authorised programs.",
         ["BC-200", "BC-230"]),
        ("BP-360.30", "Manage Grants and Awards",
         "Award and administer grants and cooperative agreements; manage grantee compliance and reporting.",
         []),
        ("BP-360.40", "Manage Public-Sector Performance and Statistical Reporting",
         "Produce statutory performance, statistical, and accountability reports per IPSAS / GFSM standards.",
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
    ap.add_argument("--bp1", help="Single BP1 to write (e.g. BP-310).")
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
