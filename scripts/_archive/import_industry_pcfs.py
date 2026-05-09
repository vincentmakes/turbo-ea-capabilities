#!/usr/bin/env python3
"""Industry-specific PCF / framework imports as new BP1 files.

Each industry adds BP1 categories that supplement the cross-industry baseline
with industry-specific operational processes. Anchored on the corresponding
industry framework: APQC industry-specific PCFs primarily, with BIAN/eTOM/
ACORD cited via framework_refs where applicable.

Scope of this PR:
- Banking & Capital Markets (BIAN service-domain inspired)
- Insurance (ACORD-aligned)
- Telecommunications (TM Forum eTOM-aligned)

Each industry adds 1 BP1 file at BP1 + BP2 depth. BP3 drill is deferred to
follow-up PRs once the industry PCF reference is verified, since BP3 codes
in industry-specific PCFs are less standardised across published references.

Usage:
    python3 scripts/import_industry_pcfs.py --bp1 BP-130
    python3 scripts/import_industry_pcfs.py --all
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


# Each entry is BP1 + BP2 only. BP3 deferred.
TREE: dict[str, dict] = {}

TREE["BP-130"] = {
    "id": "BP-130",
    "name": "Operate Banking Products and Services",
    "description": "Run banking-specific product and service operations: deposit-taking, lending, cards, payments, trade finance, and customer servicing — distinct from the cross-industry Order-to-Cash flow.",
    "industry": "Banking & Capital Markets",
    "framework_refs": [
        {"framework": "BIAN", "external_id": "Banking Industry Architecture Network — service-domain reference"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-130.10", "Manage Deposit Operations",
         "Operate retail and commercial deposit accounts: account opening, transaction posting, interest calculation, and statement production.",
         []),
        ("BP-130.20", "Manage Lending Operations",
         "Originate, underwrite, service, and collect on loans: retail, mortgage, commercial, and syndicated facilities.",
         []),
        ("BP-130.30", "Manage Card Operations",
         "Operate credit, debit, and prepaid card programs: issuance, authorisation, clearing, settlement, and disputes.",
         []),
        ("BP-130.40", "Manage Payment Operations",
         "Process domestic and cross-border payments across rails (ACH, wire, RTGS, instant payments, SWIFT).",
         []),
        ("BP-130.50", "Manage Trade Finance Operations",
         "Operate trade-finance products: letters of credit, documentary collections, supply-chain finance, guarantees.",
         []),
        ("BP-130.60", "Manage Banking Customer Servicing",
         "Service banking customers across channels: call centre, branch, digital, and dispute handling.",
         ["BC-430", "BC-420"]),
    ],
}

TREE["BP-140"] = {
    "id": "BP-140",
    "name": "Operate Capital Markets and Treasury Services",
    "description": "Run capital-markets and treasury operations: trading execution, settlement and clearing, custody, asset servicing, and securities lending.",
    "industry": "Banking & Capital Markets",
    "framework_refs": [
        {"framework": "BIAN", "external_id": "Capital Markets service-domain reference"},
    ],
    "realizes": ["BC-210"],
    "children": [
        ("BP-140.10", "Manage Trading Operations",
         "Execute trades across asset classes: equities, fixed income, FX, commodities, derivatives.",
         ["BC-210"]),
        ("BP-140.20", "Manage Clearing and Settlement",
         "Clear and settle trades through central counterparties and bilateral mechanisms.",
         ["BC-210"]),
        ("BP-140.30", "Manage Custody Operations",
         "Hold and safekeep client securities; process corporate actions and income.",
         ["BC-210"]),
        ("BP-140.40", "Manage Asset Servicing",
         "Service investment products: corporate actions, dividend processing, proxy voting, tax reclaim.",
         ["BC-210"]),
        ("BP-140.50", "Manage Securities Lending",
         "Operate securities-lending programs and collateral management.",
         ["BC-210"]),
    ],
}

TREE["BP-150"] = {
    "id": "BP-150",
    "name": "Operate Insurance Underwriting, Policy, and Claims",
    "description": "Run insurance-specific operations: product filing, underwriting, policy administration, claims handling, reinsurance, and actuarial reserving.",
    "industry": "Insurance",
    "framework_refs": [
        {"framework": "BIAN", "external_id": "Insurance reference (where applicable)"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-150.10", "Manage Product Filing and Approval",
         "Develop, file, and obtain regulatory approval for insurance products and rate plans.",
         []),
        ("BP-150.20", "Manage Underwriting Operations",
         "Risk-assess and price insurance applications; bind cover.",
         []),
        ("BP-150.30", "Manage Policy Administration",
         "Administer policies across the lifecycle: issuance, endorsements, renewals, cancellations.",
         []),
        ("BP-150.40", "Manage Claims Operations",
         "Receive, investigate, adjudicate, and pay insurance claims, including fraud and recovery.",
         []),
        ("BP-150.50", "Manage Reinsurance Operations",
         "Cede risk to reinsurers; administer reinsurance treaties and recoveries.",
         []),
        ("BP-150.60", "Manage Actuarial Reserving and Capital",
         "Calculate insurance reserves, capital requirements, and produce statutory actuarial reports.",
         ["BC-200"]),
    ],
}

TREE["BP-160"] = {
    "id": "BP-160",
    "name": "Operate Communications Networks and Services",
    "description": "Run telecom-specific operations: network lifecycle, service provisioning and assurance, performance management, and spectrum and interconnect management.",
    "industry": "Telecommunications",
    "framework_refs": [
        {"framework": "eTOM", "external_id": "TM Forum Frameworx eTOM Operations and Strategy domains"},
    ],
    "realizes": ["BC-100", "BC-600"],
    "children": [
        ("BP-160.10", "Manage Network Lifecycle",
         "Plan, design, build, and decommission network infrastructure across the lifecycle.",
         ["BC-700", "BC-600"]),
        ("BP-160.20", "Manage Network Operations and Service Assurance",
         "Operate the network and assure services: fault, performance, configuration, and capacity management.",
         ["BC-600", "BC-720"]),
        ("BP-160.30", "Manage Service Provisioning and Activation",
         "Provision and activate customer services across access, core, and OSS systems.",
         ["BC-430", "BC-600"]),
        ("BP-160.40", "Manage Service Quality and Performance",
         "Manage service quality and performance against SLAs across the customer base.",
         ["BC-720", "BC-430"]),
        ("BP-160.50", "Manage Spectrum and Interconnect",
         "Manage radio spectrum holdings and interconnect arrangements with peer operators.",
         ["BC-150", "BC-510"]),
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
        L.append("    realizes_capability_ids:")
        if crealizes:
            for bc in crealizes:
                L.append(f"      - {bc}")
        else:
            # Empty array required by schema (minItems on capability_ids? No,
            # realizes_capability_ids is uniqueItems but no min — empty list ok).
            L[-1] = "    realizes_capability_ids: []"
        L.append("    children: []")
    return "\n".join(L) + "\n"


def write_bp1(bp1: dict) -> str:
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_emit_yaml(bp1))
    return path


def update_index(new_filename: str):
    """Add a BP1 filename to catalogue/processes/_index.yaml if not present."""
    idx_path = os.path.join(PROCESSES_DIR, "_index.yaml")
    with open(idx_path) as fh:
        lines = fh.readlines()
    files = []
    header = []
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
    ap.add_argument("--bp1", help="Single BP1 to write (e.g. BP-130).")
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
