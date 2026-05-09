#!/usr/bin/env python3
"""BP3 (Process-level) drill-down generator for APQC PCF Cross-Industry v7.4.0.

Re-emits a BP1 YAML file from the data dict in this script, including BP1 +
BP2 + BP3 levels. Idempotent — re-running with the same data produces an
identical file.

Usage:
    python3 scripts/import_apqc_pcf_bp3.py --bp1 BP-10
    python3 scripts/import_apqc_pcf_bp3.py --all

After the cross-industry drill is complete, archive this script alongside
the BP1+BP2 generator under scripts/_archive/.
"""
from __future__ import annotations

import argparse
import os
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")
APQC_VERSION = "7.4.0"


def slugify(name: str) -> str:
    out, last_dash = [], True
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch); last_dash = False
        else:
            if not last_dash:
                out.append("-"); last_dash = True
    return "".join(out).strip("-")


# ---------------------------------------------------------------------------
# Data structure:
#
# BP1 dict per category. Each BP2 child carries a 'children' list of BP3
# entries. BP3 entries are 5-tuples: (id, apqc_code, name, description,
# realizes_capability_ids).
#
# realizes_capability_ids resolve against the BC L1 catalogue. Cross-industry
# L1s only — industry-specific BCs land via industry-specific PCFs in a
# separate phase.
# ---------------------------------------------------------------------------

TREE: dict[str, dict] = {}

TREE["BP-10"] = {
    "id": "BP-10",
    "apqc": "1.0",
    "name": "Develop Vision and Strategy",
    "description": "Define the business concept and long-term vision, develop the business strategy, and manage the strategic initiative portfolio that turns strategy into outcomes.",
    "realizes": ["BC-100"],
    "children": [
        {
            "id": "BP-10.10", "apqc": "1.1",
            "name": "Define the Business Concept and Long-Term Vision",
            "description": "Frame the enterprise's purpose, scope, and aspirational future state. Establishes the long-horizon view that strategic plans serve.",
            "realizes": ["BC-100"],
            "children": [
                ("BP-10.10.10", "1.1.1", "Assess the External Environment",
                 "Scan macro, industry, regulatory, and competitive forces shaping the enterprise's future operating context.",
                 ["BC-100"]),
                ("BP-10.10.20", "1.1.2", "Survey Markets and Determine Customer Needs and Wants",
                 "Identify served and underserved customer segments and their unmet needs to inform vision and strategy.",
                 ["BC-100", "BC-400"]),
                ("BP-10.10.30", "1.1.3", "Perform Internal Analysis",
                 "Assess current capabilities, performance, financial position, and organisational health as input to strategy.",
                 ["BC-100", "BC-170"]),
                ("BP-10.10.40", "1.1.4", "Establish Strategic Vision",
                 "Articulate the long-term aspiration and strategic direction that orients the enterprise.",
                 ["BC-100"]),
                ("BP-10.10.50", "1.1.5", "Conduct Organisation Restructuring Opportunities",
                 "Identify potential organisational, portfolio, or operating-model shifts implied by the vision.",
                 ["BC-100", "BC-920"]),
            ],
        },
        {
            "id": "BP-10.20", "apqc": "1.2",
            "name": "Develop Business Strategy",
            "description": "Translate the long-term vision into a multi-year business strategy with markets, value propositions, and competitive positioning.",
            "realizes": ["BC-100", "BC-230"],
            "children": [
                ("BP-10.20.10", "1.2.1", "Develop Overall Mission Statement",
                 "Codify the enterprise mission expressing its purpose and reason for being.",
                 ["BC-100"]),
                ("BP-10.20.20", "1.2.2", "Define and Evaluate Strategic Options to Achieve the Objectives",
                 "Generate and assess alternative strategic paths against the objectives, constraints, and risk appetite.",
                 ["BC-100", "BC-230"]),
                ("BP-10.20.30", "1.2.3", "Select Long-Term Business Strategy",
                 "Choose the multi-year strategy that best balances opportunity, capability, and risk.",
                 ["BC-100"]),
                ("BP-10.20.40", "1.2.4", "Coordinate and Align Functional and Process Strategies",
                 "Cascade the chosen strategy into functional and process strategies that deliver it.",
                 ["BC-100", "BC-170", "BC-930"]),
                ("BP-10.20.50", "1.2.5", "Create Organisational Design",
                 "Define the structure, governance, decision rights, and reporting that execute the strategy.",
                 ["BC-100", "BC-110"]),
                ("BP-10.20.60", "1.2.6", "Develop and Set Organisational Goals",
                 "Translate the strategy into measurable enterprise, business-unit, and functional goals.",
                 ["BC-100", "BC-230"]),
                ("BP-10.20.70", "1.2.7", "Formulate Business Unit Strategies",
                 "Develop unit-level strategies aligned to the overall enterprise strategy.",
                 ["BC-100"]),
                ("BP-10.20.80", "1.2.8", "Communicate Strategies Internally and Externally",
                 "Communicate the strategy to internal stakeholders and (where appropriate) external audiences.",
                 ["BC-100", "BC-850", "BC-240"]),
            ],
        },
        {
            "id": "BP-10.30", "apqc": "1.3",
            "name": "Manage Strategic Initiatives",
            "description": "Charter, prioritise, and govern the portfolio of initiatives that execute the strategy. Allocate resources and track strategic outcomes.",
            "realizes": ["BC-100", "BC-900", "BC-920"],
            "children": [
                ("BP-10.30.10", "1.3.1", "Develop Strategic Initiatives",
                 "Charter initiatives required to deliver the strategy with scope, owners, and benefits.",
                 ["BC-100", "BC-900"]),
                ("BP-10.30.20", "1.3.2", "Evaluate Strategic Initiatives",
                 "Evaluate proposed initiatives against strategic fit, value, feasibility, and risk.",
                 ["BC-100", "BC-900"]),
                ("BP-10.30.30", "1.3.3", "Select Strategic Initiatives",
                 "Approve the portfolio of initiatives to fund and execute, with allocation decisions.",
                 ["BC-100", "BC-900"]),
                ("BP-10.30.40", "1.3.4", "Establish High-Level Measures",
                 "Define the strategic KPIs and outcome measures used to monitor execution.",
                 ["BC-100", "BC-230"]),
            ],
        },
    ],
}


# Other BP1s appended progressively below as we drill them. ----------------

TREE["BP-20"] = {
    "id": "BP-20",
    "apqc": "2.0",
    "name": "Develop and Manage Products and Services",
    "description": "Govern the product/service portfolio across the lifecycle: from idea generation and development through market test and production readiness.",
    "realizes": ["BC-820", "BC-810", "BC-800"],
    "children": [
        {
            "id": "BP-20.10", "apqc": "2.1",
            "name": "Govern and Manage the Product/Service Development Program",
            "description": "Establish development governance, stage gates, portfolio prioritisation, and program controls across the product/service lifecycle.",
            "realizes": ["BC-820", "BC-900"],
            "children": [
                ("BP-20.10.10", "2.1.1", "Manage Product and Service Portfolio",
                 "Govern the active and pipeline portfolio of products and services, balancing investment across categories and stages.",
                 ["BC-820", "BC-900"]),
                ("BP-20.10.20", "2.1.2", "Manage Product and Service Master Data",
                 "Maintain the authoritative product/service master record across systems and channels.",
                 ["BC-820", "BC-610"]),
                ("BP-20.10.30", "2.1.3", "Manage Product and Service Development Life Cycle",
                 "Operate stage gates, decision rights, and program controls across the product/service lifecycle.",
                 ["BC-820", "BC-900"]),
            ],
        },
        {
            "id": "BP-20.20", "apqc": "2.2",
            "name": "Generate and Define New Product/Service Ideas",
            "description": "Source, screen, and define candidate product and service concepts. Translate market and technology insight into evaluable concepts.",
            "realizes": ["BC-800", "BC-810"],
            "children": [
                ("BP-20.20.10", "2.2.1", "Perform Discovery Research",
                 "Run primary and secondary research to surface unmet needs and emerging technologies relevant to the portfolio.",
                 ["BC-800", "BC-810", "BC-400"]),
                ("BP-20.20.20", "2.2.2", "Generate New Product/Service Ideas",
                 "Systematically generate candidate product and service ideas through ideation, scouting, and open innovation channels.",
                 ["BC-800"]),
                ("BP-20.20.30", "2.2.3", "Define New Product/Service Ideas",
                 "Articulate idea concepts with target customer, value proposition, scope, and high-level feasibility.",
                 ["BC-800", "BC-820"]),
                ("BP-20.20.40", "2.2.4", "Develop Business Case for Product/Service",
                 "Develop the business case quantifying value, cost, risk, and strategic fit for go/no-go decisions.",
                 ["BC-800", "BC-820", "BC-230"]),
                ("BP-20.20.50", "2.2.5", "Validate New Product/Service Ideas",
                 "Validate concepts through customer research, technical feasibility, and economic screening before committing to development.",
                 ["BC-800", "BC-820"]),
            ],
        },
        {
            "id": "BP-20.30", "apqc": "2.3",
            "name": "Develop Products and Services",
            "description": "Design, engineer, and validate products and services from concept through release readiness, including IP protection.",
            "realizes": ["BC-810", "BC-820", "BC-840"],
            "children": [
                ("BP-20.30.10", "2.3.1", "Design and Prototype Products and Services",
                 "Translate validated concepts into detailed designs and prototypes that prove the offer.",
                 ["BC-810", "BC-820"]),
                ("BP-20.30.20", "2.3.2", "Build Products and Services Capabilities",
                 "Build the product/service deliverable to specification, including engineering and configuration.",
                 ["BC-810", "BC-820"]),
                ("BP-20.30.30", "2.3.3", "Test Product/Service",
                 "Validate the product/service against requirements through test, pilot, and pre-production trials.",
                 ["BC-820", "BC-720"]),
                ("BP-20.30.40", "2.3.4", "Manage Intellectual Property Created During Development",
                 "Identify, protect, and manage IP arising from product and service development.",
                 ["BC-840"]),
                ("BP-20.30.50", "2.3.5", "Refine Existing Products/Services",
                 "Improve existing offers based on field feedback, defects, or shifting requirements.",
                 ["BC-820"]),
            ],
        },
        {
            "id": "BP-20.40", "apqc": "2.4",
            "name": "Test Market for New or Revised Products and Services",
            "description": "Validate concept-market fit through market trials, pilots, and customer testing before full-scale launch.",
            "realizes": ["BC-820", "BC-400"],
            "children": [
                ("BP-20.40.10", "2.4.1", "Develop Market Test Plan",
                 "Define market-test scope, segments, channels, and success criteria.",
                 ["BC-820", "BC-400"]),
                ("BP-20.40.20", "2.4.2", "Conduct Market Test",
                 "Execute the market test in target segments and channels.",
                 ["BC-820", "BC-400"]),
                ("BP-20.40.30", "2.4.3", "Evaluate Market Test Results",
                 "Analyse market-test results against success criteria; recommend launch, iterate, or kill.",
                 ["BC-820", "BC-400"]),
            ],
        },
        {
            "id": "BP-20.50", "apqc": "2.5",
            "name": "Prepare for Production",
            "description": "Industrialise the design, qualify the supply base, and ready operations to produce or deliver at commercial scale.",
            "realizes": ["BC-820", "BC-520"],
            "children": [
                ("BP-20.50.10", "2.5.1", "Develop and Test Prototype Production and/or Service Delivery Process",
                 "Pilot the production or service-delivery process at limited scale and validate readiness.",
                 ["BC-820", "BC-520"]),
                ("BP-20.50.20", "2.5.2", "Design and Obtain Necessary Materials and Equipment",
                 "Source and qualify the materials, equipment, and tooling required for at-scale production.",
                 ["BC-500", "BC-510", "BC-520"]),
                ("BP-20.50.30", "2.5.3", "Install and Validate Production Process",
                 "Stand up the production or service-delivery process, validate quality, and hand off to operations.",
                 ["BC-820", "BC-520", "BC-720"]),
            ],
        },
    ],
}


def _emit_yaml(bp1: dict) -> str:
    """Emit a clean YAML string for a single BP1 file (BP1 + BP2 + BP3)."""
    L = []
    L.append(f"id: {bp1['id']}")
    L.append(f"name: {bp1['name']}")
    L.append("level: 1")
    L.append("industry: Cross-Industry")
    L.append("description: >-")
    L.append(f"  {bp1['description']}")
    L.append("framework_refs:")
    L.append("  - framework: APQC-PCF")
    L.append(f"    external_id: \"{bp1['apqc']}\"")
    L.append(f"    version: \"{APQC_VERSION}\"")
    L.append("realizes_capability_ids:")
    for bc in bp1["realizes"]:
        L.append(f"  - {bc}")
    L.append("children:")
    for bp2 in bp1["children"]:
        L.append(f"  - id: {bp2['id']}")
        L.append(f"    name: {bp2['name']}")
        L.append("    level: 2")
        L.append("    description: >-")
        L.append(f"      {bp2['description']}")
        L.append("    framework_refs:")
        L.append("      - framework: APQC-PCF")
        L.append(f"        external_id: \"{bp2['apqc']}\"")
        L.append(f"        version: \"{APQC_VERSION}\"")
        L.append("    realizes_capability_ids:")
        for bc in bp2["realizes"]:
            L.append(f"      - {bc}")
        L.append("    children:")
        if not bp2.get("children"):
            # Empty array — but YAML 'children:' followed by nothing fails
            # the schema's "children: array" requirement. Use [] inline.
            L[-1] = "    children: []"
        else:
            for cid, capqc, cname, cdesc, crealizes in bp2["children"]:
                L.append(f"      - id: {cid}")
                L.append(f"        name: {cname}")
                L.append("        level: 3")
                L.append("        description: >-")
                L.append(f"          {cdesc}")
                L.append("        framework_refs:")
                L.append("          - framework: APQC-PCF")
                L.append(f"            external_id: \"{capqc}\"")
                L.append(f"            version: \"{APQC_VERSION}\"")
                L.append("        realizes_capability_ids:")
                for bc in crealizes:
                    L.append(f"          - {bc}")
                L.append("        children: []")
    return "\n".join(L) + "\n"


def write_bp1(bp1: dict) -> str:
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_emit_yaml(bp1))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1", help="Generate one BP1 file (e.g. BP-10). Omit to process all in TREE.")
    args = ap.parse_args()

    targets = list(TREE.keys()) if not args.bp1 else [args.bp1]
    for bp1_id in targets:
        if bp1_id not in TREE:
            raise SystemExit(f"BP1 {bp1_id} not defined in TREE.")
        bp1 = TREE[bp1_id]
        path = write_bp1(bp1)
        bp3_count = sum(len(bp2.get("children") or []) for bp2 in bp1["children"])
        print(f"✔ {bp1_id} → {os.path.relpath(path, REPO_ROOT)} "
              f"({len(bp1['children'])} BP2, {bp3_count} BP3)")


if __name__ == "__main__":
    main()
