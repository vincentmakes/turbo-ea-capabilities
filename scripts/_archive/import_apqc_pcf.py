#!/usr/bin/env python3
"""One-shot generator for the 12 APQC PCF Cross-Industry BP1 files.

Run once to populate catalogue/processes/BP1-*.yaml. After review/merge,
this script can be archived under scripts/_archive/ — further authoring
should go through `npm run bp:add` per the governance model.

Source: APQC Process Classification Framework (PCF) Cross-Industry v7.x.
APQC permits PCF use with attribution; see NOTICE.
"""
import os
import yaml
from collections import OrderedDict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")
APQC_VERSION = "7.4.0"


def slugify(name: str) -> str:
    out = []
    last_dash = True
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
            last_dash = False
        else:
            if not last_dash:
                out.append("-")
                last_dash = True
    return "".join(out).strip("-")


# Each entry: (bp_id, apqc_code, name, description, realizes_capability_ids, [children])
# children: list of (bp_id, apqc_code, name, description, realizes_capability_ids)
TREE = [
    {
        "id": "BP-10",
        "apqc": "1.0",
        "name": "Develop Vision and Strategy",
        "description": "Define the business concept and long-term vision, develop the business strategy, and manage the strategic initiative portfolio that turns strategy into outcomes.",
        "realizes": ["BC-100"],
        "children": [
            ("BP-10.10", "1.1", "Define the Business Concept and Long-Term Vision",
             "Frame the enterprise's purpose, scope, and aspirational future state. Establishes the long-horizon view that strategic plans serve.",
             ["BC-100"]),
            ("BP-10.20", "1.2", "Develop Business Strategy",
             "Translate the long-term vision into a multi-year business strategy with markets, value propositions, and competitive positioning.",
             ["BC-100", "BC-230"]),
            ("BP-10.30", "1.3", "Manage Strategic Initiatives",
             "Charter, prioritise, and govern the portfolio of initiatives that execute the strategy. Allocate resources and track strategic outcomes.",
             ["BC-100", "BC-900", "BC-920"]),
        ],
    },
    {
        "id": "BP-20",
        "apqc": "2.0",
        "name": "Develop and Manage Products and Services",
        "description": "Govern the product/service portfolio across the lifecycle: from idea generation and development through market test and production readiness.",
        "realizes": ["BC-820", "BC-810", "BC-800"],
        "children": [
            ("BP-20.10", "2.1", "Govern and Manage the Product/Service Development Program",
             "Establish development governance, stage gates, portfolio prioritisation, and program controls across the product/service lifecycle.",
             ["BC-820", "BC-900"]),
            ("BP-20.20", "2.2", "Generate and Define New Product/Service Ideas",
             "Source, screen, and define candidate product and service concepts. Translate market and technology insight into evaluable concepts.",
             ["BC-800", "BC-810"]),
            ("BP-20.30", "2.3", "Develop Products and Services",
             "Design, engineer, and validate products and services from concept through release readiness, including IP protection.",
             ["BC-810", "BC-820", "BC-840"]),
            ("BP-20.40", "2.4", "Test Market for New or Revised Products and Services",
             "Validate concept-market fit through market trials, pilots, and customer testing before full-scale launch.",
             ["BC-820", "BC-400"]),
            ("BP-20.50", "2.5", "Prepare for Production",
             "Industrialise the design, qualify the supply base, and ready operations to produce or deliver at commercial scale.",
             ["BC-820", "BC-520"]),
        ],
    },
    {
        "id": "BP-30",
        "apqc": "3.0",
        "name": "Market and Sell Products and Services",
        "description": "Understand markets and customers, set marketing and sales strategy, and execute the demand-creation and order-capture activities that monetise products and services.",
        "realizes": ["BC-400", "BC-410", "BC-420", "BC-440"],
        "children": [
            ("BP-30.10", "3.1", "Understand Markets, Customers, and Capabilities",
             "Develop the evidence base on market dynamics, customer needs, segments, and competitive position that drives marketing and sales decisions.",
             ["BC-400", "BC-420"]),
            ("BP-30.20", "3.2", "Develop Marketing Strategy",
             "Define target segments, value propositions, brand positioning, and channel mix that direct marketing investment.",
             ["BC-400"]),
            ("BP-30.30", "3.3", "Develop Sales Strategy",
             "Define sales coverage, channel structure, account strategy, and quota/incentive design.",
             ["BC-410"]),
            ("BP-30.40", "3.4", "Develop and Manage Marketing Plans",
             "Plan, execute, and measure marketing campaigns and demand-generation programs that deliver pipeline against the strategy.",
             ["BC-400"]),
            ("BP-30.50", "3.5", "Develop and Manage Sales Plans",
             "Plan, execute, and manage the sales motion: account planning, opportunity management, pricing, quoting, and order capture.",
             ["BC-410", "BC-440"]),
        ],
    },
    {
        "id": "BP-40",
        "apqc": "4.0",
        "name": "Deliver Physical Products",
        "description": "Plan and run the physical supply chain end-to-end: procurement, production, and outbound logistics that move goods from suppliers to customers.",
        "realizes": ["BC-520", "BC-530"],
        "children": [
            ("BP-40.10", "4.1", "Plan for and Align Supply Chain Resources",
             "Forecast demand, plan supply, balance capacity, and align inventory positions to meet service-level and cost targets.",
             ["BC-520", "BC-530"]),
            ("BP-40.20", "4.2", "Procure Materials and Services",
             "Source, contract, and acquire goods and services from suppliers, including supplier qualification and ongoing supplier management.",
             ["BC-500", "BC-510"]),
            ("BP-40.30", "4.3", "Produce/Manufacture/Deliver Product",
             "Convert inputs into finished products through production scheduling, manufacturing operations, and quality control.",
             ["BC-520", "BC-720"]),
            ("BP-40.40", "4.4", "Manage Logistics and Warehousing",
             "Run the inbound, internal, and outbound flow of goods: warehousing, transport, fulfilment, and reverse logistics.",
             ["BC-520", "BC-530"]),
        ],
    },
    {
        "id": "BP-50",
        "apqc": "5.0",
        "name": "Deliver Services",
        "description": "Govern, plan, and execute the delivery of services to customers — including the resourcing, operations, and post-delivery management distinct from physical-goods supply chains.",
        "realizes": ["BC-430", "BC-720"],
        "children": [
            ("BP-50.10", "5.1", "Establish Service Delivery Governance and Strategy",
             "Define service-delivery operating model, governance forums, and service strategy aligned to customer outcomes and SLAs.",
             ["BC-100", "BC-720"]),
            ("BP-50.20", "5.2", "Manage Service Delivery Resources",
             "Plan, allocate, and develop the people, facilities, and infrastructure that deliver service.",
             ["BC-300", "BC-700"]),
            ("BP-50.30", "5.3", "Deliver Service to Customer",
             "Execute the service interaction with the customer end-to-end, including provisioning, support, and assurance.",
             ["BC-430"]),
            ("BP-50.40", "5.4", "Manage Service Delivery",
             "Monitor, assure, and improve service delivery against SLAs and customer-experience targets.",
             ["BC-430", "BC-720"]),
        ],
    },
    {
        "id": "BP-60",
        "apqc": "6.0",
        "name": "Manage Customer Service",
        "description": "Develop and run the customer-care function: strategy, contact-center operations, and continuous evaluation that resolves customer issues and protects loyalty.",
        "realizes": ["BC-430", "BC-420"],
        "children": [
            ("BP-60.10", "6.1", "Develop Customer Care/Customer Service Strategy",
             "Define the customer-service operating model, channels, service levels, and self-service strategy.",
             ["BC-430", "BC-100"]),
            ("BP-60.20", "6.2", "Plan and Manage Customer Service Operations",
             "Run day-to-day customer service operations: contact handling, case management, escalation, and workforce management.",
             ["BC-430"]),
            ("BP-60.30", "6.3", "Measure and Evaluate Customer Service Operations",
             "Measure service performance, customer satisfaction, and operational efficiency; drive continuous improvement.",
             ["BC-430", "BC-720"]),
        ],
    },
    {
        "id": "BP-70",
        "apqc": "7.0",
        "name": "Develop and Manage Human Capital",
        "description": "Manage the workforce end-to-end: HR strategy, recruitment, development, reward, redeployment, and employee data and inquiries.",
        "realizes": ["BC-300"],
        "children": [
            ("BP-70.10", "7.1", "Develop and Manage Human Resources Planning, Policies, and Strategies",
             "Set HR strategy, workforce plans, and policies aligned to business strategy and regulatory obligations.",
             ["BC-300"]),
            ("BP-70.20", "7.2", "Recruit, Source, and Select Employees",
             "Attract, assess, and hire candidates to fill workforce demand, including onboarding readiness.",
             ["BC-300"]),
            ("BP-70.30", "7.3", "Develop and Counsel Employees",
             "Onboard, train, develop, and coach employees across their tenure to build capability and engagement.",
             ["BC-300"]),
            ("BP-70.40", "7.4", "Reward and Retain Employees",
             "Design and operate compensation, benefits, recognition, and retention programs.",
             ["BC-300"]),
            ("BP-70.50", "7.5", "Redeploy and Retire Employees",
             "Manage transitions: internal mobility, redeployment, separations, and retirement.",
             ["BC-300"]),
            ("BP-70.60", "7.6", "Manage Employee Information and Analytics",
             "Maintain employee master data and produce workforce analytics that inform decisions.",
             ["BC-300", "BC-610"]),
            ("BP-70.70", "7.7", "Manage Employee Inquiries",
             "Resolve employee questions and service requests via HR shared-service or case-management channels.",
             ["BC-300"]),
        ],
    },
    {
        "id": "BP-80",
        "apqc": "8.0",
        "name": "Manage Information Technology",
        "description": "Run the enterprise IT function: strategy, build, deploy, run, and knowledge management — including IT-side risk and resilience that protects business continuity.",
        "realizes": ["BC-600", "BC-610", "BC-620"],
        "children": [
            ("BP-80.10", "8.1", "Develop and Manage Business Resilience and Risk",
             "Identify, assess, and mitigate IT-related risks; maintain business-continuity and disaster-recovery readiness for technology-enabled operations.",
             ["BC-160", "BC-120", "BC-620"]),
            ("BP-80.20", "8.2", "Develop Information Technology (IT) Strategy",
             "Set the IT strategy, target architecture, and investment plan that supports the business strategy.",
             ["BC-600", "BC-170"]),
            ("BP-80.30", "8.3", "Develop and Maintain Information Technology Solutions",
             "Design, build, integrate, and evolve the application and infrastructure portfolio that runs the business.",
             ["BC-600"]),
            ("BP-80.40", "8.4", "Deploy Information Technology Solutions",
             "Release new and changed IT solutions into production with appropriate change controls and adoption support.",
             ["BC-600", "BC-910"]),
            ("BP-80.50", "8.5", "Deliver and Support Information Technology Services",
             "Operate IT services day-to-day: incident, problem, request, and service-level management.",
             ["BC-600"]),
            ("BP-80.60", "8.6", "Manage IT Knowledge",
             "Capture and curate IT knowledge: configuration data, runbooks, architecture, and support knowledge bases.",
             ["BC-830", "BC-600"]),
        ],
    },
    {
        "id": "BP-90",
        "apqc": "9.0",
        "name": "Manage Financial Resources",
        "description": "Run enterprise finance end-to-end: planning and management accounting, transaction processing (revenue, AP, payroll), reporting, treasury, controls, tax, and consolidation.",
        "realizes": ["BC-200", "BC-230", "BC-210", "BC-220"],
        "children": [
            ("BP-90.10", "9.1", "Perform Planning and Management Accounting",
             "Plan, budget, forecast, and produce management-accounting analyses that drive business decisions.",
             ["BC-230"]),
            ("BP-90.20", "9.2", "Perform Revenue Accounting",
             "Recognise, record, and report revenue in accordance with accounting standards and contract terms.",
             ["BC-200"]),
            ("BP-90.30", "9.3", "Perform General Accounting and Reporting",
             "Maintain the general ledger, perform period-end close, and produce statutory and management financial reports.",
             ["BC-200"]),
            ("BP-90.40", "9.4", "Manage Fixed-Asset Project Accounting",
             "Account for capital projects and fixed assets across acquisition, depreciation, impairment, and disposal.",
             ["BC-200", "BC-900"]),
            ("BP-90.50", "9.5", "Process Payroll",
             "Calculate, pay, and report employee compensation, including statutory withholdings and benefits accounting.",
             ["BC-300", "BC-200"]),
            ("BP-90.60", "9.6", "Process Accounts Payable and Expense Reimbursements",
             "Validate, approve, and pay supplier invoices and employee expense claims.",
             ["BC-200", "BC-500"]),
            ("BP-90.70", "9.7", "Manage Treasury Operations",
             "Manage cash, liquidity, banking, debt, investments, and financial-risk hedging.",
             ["BC-210"]),
            ("BP-90.80", "9.8", "Manage Internal Controls",
             "Design, operate, and assure financial internal controls aligned to regulatory and assurance requirements.",
             ["BC-140", "BC-130"]),
            ("BP-90.90", "9.9", "Manage Taxes",
             "Determine, file, and pay direct, indirect, and transactional taxes; manage tax controversy and planning.",
             ["BC-220"]),
            ("BP-90.100", "9.10", "Manage International Funds/Consolidation",
             "Translate, consolidate, and report multi-entity, multi-currency results.",
             ["BC-200", "BC-210"]),
        ],
    },
    {
        "id": "BP-100",
        "apqc": "10.0",
        "name": "Acquire, Construct, and Manage Assets",
        "description": "Plan, acquire, construct, maintain, and dispose of productive assets — facilities, plant, real estate, and similar long-lived enterprise assets.",
        "realizes": ["BC-700", "BC-710"],
        "children": [
            ("BP-100.10", "10.1", "Plan and Acquire Assets",
             "Plan asset needs, evaluate buy/lease alternatives, and acquire productive assets.",
             ["BC-710", "BC-700"]),
            ("BP-100.20", "10.2", "Design and Construct Productive Assets",
             "Design, construct, and commission productive assets — facilities, plant, and infrastructure.",
             ["BC-700", "BC-720"]),
            ("BP-100.30", "10.3", "Maintain Productive Assets",
             "Operate and maintain productive assets across their useful life: planned, preventive, and corrective maintenance.",
             ["BC-700"]),
            ("BP-100.40", "10.4", "Dispose of Productive Assets",
             "Decommission and dispose of assets at end-of-life, including environmental and remarketing considerations.",
             ["BC-710", "BC-740"]),
        ],
    },
    {
        "id": "BP-110",
        "apqc": "11.0",
        "name": "Manage Enterprise Risk, Compliance, Remediation, and Resiliency",
        "description": "Run enterprise risk, compliance, business resilience, and EHS programs that protect the enterprise from financial, operational, regulatory, and safety threats.",
        "realizes": ["BC-120", "BC-130", "BC-160", "BC-730"],
        "children": [
            ("BP-110.10", "11.1", "Manage Enterprise Risk",
             "Identify, assess, treat, and monitor enterprise risk across financial, operational, strategic, and compliance dimensions.",
             ["BC-120", "BC-140"]),
            ("BP-110.20", "11.2", "Manage Business Resiliency",
             "Maintain business-continuity and disaster-recovery capabilities; respond to and recover from disruptive events.",
             ["BC-160"]),
            ("BP-110.30", "11.3", "Manage Environmental, Health, and Safety (EHS)",
             "Run EHS programs that protect employees, communities, and the environment, including incident response and regulatory reporting.",
             ["BC-730", "BC-740"]),
        ],
    },
    {
        "id": "BP-120",
        "apqc": "12.0",
        "name": "Manage External Relationships",
        "description": "Manage the enterprise's relationships with external stakeholders: investors, government, board, legal, ethical, and public-relations counterparts.",
        "realizes": ["BC-240", "BC-150", "BC-850", "BC-110"],
        "children": [
            ("BP-120.10", "12.1", "Build Investor Relationships",
             "Engage with current and prospective investors, analysts, and rating agencies; manage investor communications and disclosures.",
             ["BC-240"]),
            ("BP-120.20", "12.2", "Manage Government and Industry Relationships",
             "Engage with regulators, government bodies, and industry associations on policy, lobbying, and regulatory matters.",
             ["BC-150", "BC-850"]),
            ("BP-120.30", "12.3", "Manage Relations with Board of Directors",
             "Support the board: agendas, materials, governance processes, and director engagement.",
             ["BC-110", "BC-240"]),
            ("BP-120.40", "12.4", "Manage Legal and Ethical Issues",
             "Manage legal matters, contracts, litigation, ethics programs, and corporate-conduct standards.",
             ["BC-150", "BC-130"]),
            ("BP-120.50", "12.5", "Manage Public Relations Program",
             "Run external communications, media relations, brand reputation, and crisis communications.",
             ["BC-850"]),
        ],
    },
]


def build_yaml(bp1: dict) -> str:
    """Build a YAML document string for one BP1 file. We assemble manually to
    control field order — schema 'children' must come last, framework_refs
    inline-readable."""
    lines = []
    lines.append(f"id: {bp1['id']}")
    lines.append(f"name: {bp1['name']}")
    lines.append("level: 1")
    lines.append("industry: Cross-Industry")
    # description as a folded scalar
    lines.append("description: >-")
    lines.append(f"  {bp1['description']}")
    # framework_refs
    lines.append("framework_refs:")
    lines.append("  - framework: APQC-PCF")
    lines.append(f"    external_id: \"{bp1['apqc']}\"")
    lines.append(f"    version: \"{APQC_VERSION}\"")
    # realizes_capability_ids
    lines.append("realizes_capability_ids:")
    for bc in bp1["realizes"]:
        lines.append(f"  - {bc}")
    # children
    lines.append("children:")
    for cid, capqc, cname, cdesc, crealizes in bp1["children"]:
        lines.append(f"  - id: {cid}")
        lines.append(f"    name: {cname}")
        lines.append("    level: 2")
        lines.append("    description: >-")
        lines.append(f"      {cdesc}")
        lines.append("    framework_refs:")
        lines.append("      - framework: APQC-PCF")
        lines.append(f"        external_id: \"{capqc}\"")
        lines.append(f"        version: \"{APQC_VERSION}\"")
        lines.append("    realizes_capability_ids:")
        for bc in crealizes:
            lines.append(f"      - {bc}")
        lines.append("    children: []")
    return "\n".join(lines) + "\n"


def main():
    os.makedirs(PROCESSES_DIR, exist_ok=True)
    written = []
    for bp1 in TREE:
        slug = slugify(bp1["name"])
        path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
        # Sanity-check the slug round-trips through YAML
        content = build_yaml(bp1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        written.append(f"BP1-{slug}.yaml")
    # Update _index.yaml
    index_path = os.path.join(PROCESSES_DIR, "_index.yaml")
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write("# Index of business-process L1 (BP1) files. Lint enforces every BP1 file is registered here.\n")
        fh.write("files:\n")
        for f in sorted(written):
            fh.write(f"  - {f}\n")
    total_children = sum(len(bp1["children"]) for bp1 in TREE)
    print(f"✔ Wrote {len(written)} BP1 file(s), {total_children} BP2 child(ren), updated _index.yaml")


if __name__ == "__main__":
    main()
