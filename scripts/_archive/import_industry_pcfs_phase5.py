#!/usr/bin/env python3
"""Phase 5 generator: 12 BP1 files filling the remaining industry gap.
Travel & Hospitality, Media, Professional Services, Transportation & Logistics,
Software & Technology, Air Traffic Control, Engineering Services, HVAC & BAS,
Electrical Components, Manufacturing & Industrial, Agriculture, Chemicals.

Anchored on industry frameworks documented in business-capability-governance-model.md §11.7.
"""
from __future__ import annotations
import argparse, os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")


def slugify(name):
    out, last = [], True
    for ch in name.lower():
        if ch.isalnum(): out.append(ch); last = False
        elif not last: out.append("-"); last = True
    return "".join(out).strip("-")


# Schema: BP1 dict {id, name, industry, description, framework_label,
#                   realizes, children: [(id, name, desc, [realizes])]}
TREE: dict[str, dict] = {}

TREE["BP-380"] = {
    "id": "BP-380",
    "name": "Operate Hospitality Properties and Distribution",
    "industry": "Travel & Hospitality",
    "description": "Run hospitality-specific operations: reservations and inventory, guest experience, distribution and channel, loyalty, revenue management, and property operations (rooms, F&B, events).",
    "framework_label": "AHLA USALI 11th Ed + HEDNA + OpenTravel + HTNG reference architecture",
    "realizes": ["BC-100"],
    "children": [
        ("BP-380.10", "Manage Reservations and Inventory",
         "Manage room, table, and event-space inventory; receive and confirm reservations across channels.",
         []),
        ("BP-380.20", "Manage Guest Experience and Stay",
         "Operate the guest journey from arrival through stay to departure, including check-in, in-stay servicing, and check-out.",
         ["BC-430"]),
        ("BP-380.30", "Manage Distribution and Channel",
         "Operate distribution across direct, OTA, GDS, and metasearch channels; manage rate parity and content.",
         ["BC-410"]),
        ("BP-380.40", "Manage Loyalty Programs",
         "Operate guest loyalty programs across enrolment, accrual, redemption, and partner exchange.",
         ["BC-420"]),
        ("BP-380.50", "Manage Revenue Management and Yield",
         "Forecast demand and optimise pricing, length-of-stay controls, and channel mix.",
         ["BC-440"]),
        ("BP-380.60", "Operate Property Operations",
         "Operate rooms, food & beverage, events, housekeeping, and property maintenance.",
         ["BC-700"]),
    ],
}

TREE["BP-390"] = {
    "id": "BP-390",
    "name": "Develop, Produce, and Distribute Content",
    "industry": "Media, Entertainment & Telecom Content",
    "description": "Run media-industry operations: content development and greenlight, production, rights and IP, distribution and syndication, advertising/subscription monetisation, audience measurement.",
    "framework_label": "APQC Broadcasting/Media PCF v7.2.x + MovieLabs Common Workflow + SMPTE/EBU/DPP standards",
    "realizes": ["BC-100"],
    "children": [
        ("BP-390.10", "Develop and Greenlight Content",
         "Source, evaluate, and greenlight content concepts; manage development slate.",
         ["BC-800"]),
        ("BP-390.20", "Produce Content",
         "Plan, execute, and post-produce content (film, TV, audio, news), including pre-production, principal photography/recording, and post.",
         []),
        ("BP-390.30", "Manage Rights and Intellectual Property",
         "Acquire, register, and administer content rights; manage chain of title; license rights to and from third parties.",
         ["BC-840"]),
        ("BP-390.40", "Distribute and Syndicate Content",
         "Distribute content across linear, OTT, theatrical, home-entertainment, syndication, and licensee channels.",
         ["BC-520"]),
        ("BP-390.50", "Operate Advertising Sales and Subscription",
         "Sell advertising inventory and operate subscription services; manage ad operations, viewership-based billing.",
         ["BC-410", "BC-420"]),
        ("BP-390.60", "Manage Audience Measurement and Analytics",
         "Capture and analyse audience data (linear ratings, streaming telemetry, ad delivery) for monetisation and programming decisions.",
         ["BC-610"]),
    ],
}

TREE["BP-400"] = {
    "id": "BP-400",
    "name": "Operate Professional Services Engagements",
    "industry": "Professional Services",
    "description": "Run professional-services engagements end-to-end: opportunity, engagement planning, delivery, billing/realisation, knowledge reuse, talent management.",
    "framework_label": "APQC Consulting/Professional Services PCF v7.2.x + CMMI-SVC v2.0 + SPI benchmarks",
    "realizes": ["BC-100"],
    "children": [
        ("BP-400.10", "Manage Engagement Lifecycle",
         "Run engagement lifecycle: opportunity, proposal, engagement letter, planning, delivery, change control, closeout.",
         ["BC-410", "BC-900"]),
        ("BP-400.20", "Manage Resource and Talent",
         "Plan, allocate, and develop the professional workforce; manage utilisation, leverage, and skills development.",
         ["BC-300"]),
        ("BP-400.30", "Manage Client Relationships and Accounts",
         "Run account management for client portfolios; manage cross-sell and renewal.",
         ["BC-420", "BC-410"]),
        ("BP-400.40", "Manage Knowledge Reuse and Methodology",
         "Capture engagement knowledge, develop methodologies, and curate reusable assets for future engagements.",
         ["BC-830"]),
        ("BP-400.50", "Manage Engagement Quality and Risk",
         "Run engagement-level quality assurance, peer review, and risk management; manage independence and conflict checks.",
         ["BC-720", "BC-120"]),
    ],
}

TREE["BP-410"] = {
    "id": "BP-410",
    "name": "Operate Transportation and Logistics Services",
    "industry": "Transportation & Logistics",
    "description": "Operate transportation and logistics services across modes: network planning, capacity management, freight movement, last-mile delivery, returns/reverse logistics, freight forwarding and customs.",
    "framework_label": "SCOR v14.0 + GS1 Global Logistics + UN/CEFACT MMT + IATA/IMO/AAR operating standards",
    "realizes": ["BC-520"],
    "children": [
        ("BP-410.10", "Plan Transport Network and Capacity",
         "Design transport network, asset, and capacity plans; align with demand forecasts and service-level commitments.",
         ["BC-520"]),
        ("BP-410.20", "Operate Freight and Passenger Movement",
         "Execute movement across modes (road, rail, air, marine, intermodal); manage dispatch, tracking, and exception handling.",
         ["BC-520"]),
        ("BP-410.30", "Manage Last-Mile and Customer Delivery",
         "Plan and execute last-mile delivery; manage delivery exceptions and customer-facing communication.",
         ["BC-430", "BC-520"]),
        ("BP-410.40", "Manage Freight Forwarding and Customs",
         "Operate freight forwarding, multi-modal coordination, and customs/trade-compliance for cross-border movements.",
         ["BC-130"]),
        ("BP-410.50", "Manage Returns and Reverse Logistics",
         "Operate returns and reverse-logistics flows for repairs, recalls, and disposal.",
         ["BC-520"]),
    ],
}

TREE["BP-420"] = {
    "id": "BP-420",
    "name": "Operate Software-as-a-Service Lifecycle",
    "industry": "Software & Technology",
    "description": "Run SaaS-specific operations: product lifecycle, subscription/trial lifecycle, customer onboarding, customer success and renewal, cloud and tenant operations.",
    "framework_label": "TSIA frameworks + ITIL 4 + DORA capability model + DevOps/SRE practices",
    "realizes": ["BC-820", "BC-600"],
    "children": [
        ("BP-420.10", "Manage SaaS Product Lifecycle",
         "Operate SaaS product lifecycle: roadmap, feature flags, beta/GA cycles, deprecation, and EOL.",
         ["BC-820"]),
        ("BP-420.20", "Manage Subscription and Trial Lifecycle",
         "Operate trial, conversion, subscription, expansion, contraction, and cancellation events.",
         ["BC-410", "BC-440"]),
        ("BP-420.30", "Manage Customer Onboarding and Adoption",
         "Onboard customers; drive adoption of features and time-to-value; manage activation milestones.",
         ["BC-430", "BC-420"]),
        ("BP-420.40", "Manage Customer Success and Renewal",
         "Run customer-success programs; manage health scores, expansion, and renewals.",
         ["BC-420", "BC-410"]),
        ("BP-420.50", "Operate Cloud and Tenant Operations",
         "Operate multi-tenant SaaS infrastructure: provisioning, isolation, capacity, observability, SRE/incident response.",
         ["BC-600", "BC-620"]),
    ],
}

TREE["BP-430"] = {
    "id": "BP-430",
    "name": "Operate Air Traffic Management",
    "industry": "Air Traffic Control",
    "description": "Run air-navigation-service-provider operations: airspace management, flight data and plan management, ATC services (tower/approach/en-route), CNS infrastructure, aeronautical information.",
    "framework_label": "ICAO Doc 4444 (PANS-ATM) + ICAO Doc 9750 (ASBU) + EUROCONTROL ATM Master Plan + FAA Order 7110.65 + CANSO Standard of Excellence",
    "realizes": ["BC-100"],
    "children": [
        ("BP-430.10", "Manage Airspace and Air Traffic Flow",
         "Plan and manage airspace structure, sectors, and traffic flow; coordinate with adjacent ANSPs.",
         []),
        ("BP-430.20", "Manage Flight Data and Plan",
         "Receive, validate, distribute, and update flight plans; coordinate flight-data exchange with operators and other ANSPs.",
         []),
        ("BP-430.30", "Provide Air Traffic Control Services",
         "Provide tower, approach, and en-route ATC services to airspace users; manage separation and conflict resolution.",
         []),
        ("BP-430.40", "Manage CNS Infrastructure",
         "Operate communications, navigation, and surveillance (CNS) infrastructure supporting ATC services.",
         ["BC-700", "BC-600"]),
        ("BP-430.50", "Manage Aeronautical Information",
         "Capture, validate, and publish aeronautical information (AIP, NOTAM, charts) to airspace users.",
         ["BC-610"]),
        ("BP-430.60", "Manage Aviation Safety and Investigation",
         "Run ATM safety-management activities including occurrence reporting, safety case management, just-culture investigation.",
         ["BC-720", "BC-160"]),
    ],
}

TREE["BP-440"] = {
    "id": "BP-440",
    "name": "Deliver Engineering and Construction Services",
    "industry": "Engineering Services",
    "description": "Run engineering-services-firm operations: tendering and estimation, engineering design, construction execution, commissioning and handover.",
    "framework_label": "ISO 19650 BIM + AIA Phases / RIBA Plan of Work + PMI Construction Extension to PMBOK",
    "realizes": ["BC-700", "BC-810"],
    "children": [
        ("BP-440.10", "Manage Engineering Tendering and Estimation",
         "Pursue engineering opportunities; develop tenders, cost estimates, and schedules.",
         ["BC-410"]),
        ("BP-440.20", "Deliver Engineering Design",
         "Perform engineering design across disciplines; manage design coordination via BIM/CDE.",
         ["BC-810"]),
        ("BP-440.30", "Deliver Construction Execution",
         "Execute construction work to design and schedule; manage subcontractors, materials, and HSE.",
         ["BC-700", "BC-900"]),
        ("BP-440.40", "Manage Commissioning and Handover",
         "Commission and validate engineered assets; manage handover to operations with as-built documentation.",
         ["BC-720", "BC-700"]),
        ("BP-440.50", "Manage Engineering Document and Configuration",
         "Maintain engineering documents, drawings, and configuration baselines through the project lifecycle.",
         ["BC-820", "BC-610"]),
    ],
}

TREE["BP-450"] = {
    "id": "BP-450",
    "name": "Operate HVAC and Building Automation Lifecycle",
    "industry": "HVAC & Building Automation Systems",
    "description": "Run HVAC and building-automation operations: product development, installation/commissioning, operations, refrigerant-lifecycle management.",
    "framework_label": "ASHRAE 62.1/90.1/15/211 + BACnet (ASHRAE 135) + KNX (ISO/IEC 14543-3) + AHRI certification + EU F-Gas / US EPA 608",
    "realizes": ["BC-820"],
    "children": [
        ("BP-450.10", "Develop HVAC and BAS Products",
         "Develop HVAC equipment and BAS solutions; obtain AHRI certification and energy-efficiency ratings.",
         ["BC-810", "BC-820"]),
        ("BP-450.20", "Manage HVAC Installation and Commissioning",
         "Install HVAC equipment and BAS; commission per ASHRAE Guideline 0 / 1.1 / 1.2 standards.",
         ["BC-700", "BC-720"]),
        ("BP-450.30", "Operate Building Automation",
         "Operate BAS for HVAC, lighting, and other building systems; manage tenant comfort and energy performance.",
         ["BC-700"]),
        ("BP-450.40", "Manage Refrigerant Lifecycle",
         "Capture, recover, and reclaim refrigerants per EU F-Gas / EPA Section 608; manage quotas and phase-down.",
         ["BC-740", "BC-130"]),
    ],
}

TREE["BP-460"] = {
    "id": "BP-460",
    "name": "Develop and Operate Electrical Equipment",
    "industry": "Electrical Components & Equipment",
    "description": "Run electrical-equipment-industry operations: electrical/electronic product development, type approval and certification, component lifecycle (PCN/EOL), distributor and broker network.",
    "framework_label": "IEC 60204/61439/61010/61508/62443 + IPC-A-600/610 + UL listings + IATF 16949 (where automotive-supply)",
    "realizes": ["BC-820"],
    "children": [
        ("BP-460.10", "Develop Electrical and Electronic Products",
         "Design and develop electrical/electronic products; manage hardware-software co-design and EMC.",
         ["BC-810", "BC-820"]),
        ("BP-460.20", "Manage Type Approval and Certification",
         "Obtain product certifications (UL, CE, IEC, agency marks); manage compliance throughout lifecycle.",
         ["BC-720", "BC-130"]),
        ("BP-460.30", "Manage Component Lifecycle and Obsolescence",
         "Manage product change notifications (PCN), end-of-life (EOL), last-time-buy windows, and replacement migration.",
         ["BC-820"]),
        ("BP-460.40", "Manage Distributor and Broker Network",
         "Onboard and manage authorised distributors and brokers; manage grey-market and counterfeit-component risk.",
         ["BC-510", "BC-410"]),
    ],
}

TREE["BP-470"] = {
    "id": "BP-470",
    "name": "Operate Manufacturing and Industrial Operations",
    "industry": "Manufacturing & Industrial",
    "description": "Run manufacturing-specific operational specialisations: discrete and process manufacturing operations, manufacturing maintenance (TPM), and industrial automation / OT (ISA-95-aligned MOM).",
    "framework_label": "ISA-95 (IEC 62264) MOM + APQC Cross-Industry PCF + TPM/OEE + MESA MOM Model + IEC 62443 (OT cybersecurity)",
    "realizes": ["BC-520"],
    "children": [
        ("BP-470.10", "Operate Discrete Manufacturing",
         "Run discrete manufacturing (assembly, machining, fabrication) per ISA-95 Level 3 MOM.",
         ["BC-520", "BC-720"]),
        ("BP-470.20", "Operate Process Manufacturing",
         "Run process manufacturing (continuous, batch) per ISA-95 Level 3 MOM.",
         ["BC-520", "BC-720"]),
        ("BP-470.30", "Manage Manufacturing Maintenance",
         "Run TPM and maintenance programs across plant assets; track OEE and reliability metrics.",
         ["BC-700", "BC-720"]),
        ("BP-470.40", "Operate Industrial Automation and OT",
         "Operate industrial automation systems (SCADA, MES, HMI) and OT cybersecurity per IEC 62443.",
         ["BC-600", "BC-620"]),
    ],
}

TREE["BP-480"] = {
    "id": "BP-480",
    "name": "Operate Agriculture and Food Production",
    "industry": "Agriculture & Food Production",
    "description": "Run agriculture and food-production operations: crop and livestock production, food processing and manufacturing, farm-to-market supply chain, food-safety and traceability.",
    "framework_label": "APQC Food & Beverage PCF v7.2.x + GLOBALG.A.P. + FSMA / EU 178/2002 + ISO 22000/FSSC 22000 + AgGateway + ISO 11783 (ISOBUS)",
    "realizes": ["BC-520"],
    "children": [
        ("BP-480.10", "Manage Crop Production",
         "Run crop production: planning, planting, crop protection, irrigation, and harvest under GLOBALG.A.P. or equivalent.",
         []),
        ("BP-480.20", "Manage Livestock Production",
         "Run livestock production: breeding, husbandry, animal health, and welfare per industry standards.",
         []),
        ("BP-480.30", "Operate Food Processing and Manufacturing",
         "Run food processing and manufacturing under HACCP / FSSC 22000; manage hygienic operations and allergen controls.",
         ["BC-520", "BC-720"]),
        ("BP-480.40", "Manage Farm-to-Market Supply Chain and Traceability",
         "Operate farm-to-market supply chains; maintain end-to-end traceability for food-safety and recall purposes.",
         ["BC-520", "BC-130"]),
    ],
}

TREE["BP-490"] = {
    "id": "BP-490",
    "name": "Operate Chemical Manufacturing and Compliance",
    "industry": "Chemicals",
    "description": "Run chemical-industry operations: chemical product development and formulation, chemical manufacturing, hazardous-materials and REACH compliance, chemical distribution and process safety.",
    "framework_label": "REACH (EU 1907/2006) + GHS + ACC Responsible Care + OSHA PSM + EU Seveso III 2012/18/EU + ISO 9001/14001",
    "realizes": ["BC-520", "BC-130"],
    "children": [
        ("BP-490.10", "Develop Chemical Products and Formulations",
         "Develop chemical products and formulations; manage product stewardship from R&D onward.",
         ["BC-810", "BC-820"]),
        ("BP-490.20", "Operate Chemical Manufacturing",
         "Run continuous and batch chemical manufacturing; manage process control, kinetics, and yield.",
         ["BC-520", "BC-720"]),
        ("BP-490.30", "Manage Hazardous Materials and REACH Compliance",
         "Maintain REACH and equivalent registrations; manage SDS, GHS labelling, exposure scenarios, and authorisations.",
         ["BC-130"]),
        ("BP-490.40", "Manage Process Safety and Major-Hazard Operations",
         "Operate process-safety management per OSHA PSM / Seveso III; manage major-accident hazards.",
         ["BC-730", "BC-160"]),
        ("BP-490.50", "Manage Chemical Distribution and Logistics",
         "Operate hazmat-compliant chemical distribution: bulk and packed shipments, ADR/RID/IMDG transport regulations.",
         ["BC-520"]),
    ],
}


def emit(bp1):
    L = []
    L.append(f"id: {bp1['id']}")
    L.append(f"name: {bp1['name']}")
    L.append("level: 1")
    L.append(f"industry: {bp1['industry']}")
    L.append("description: >-")
    L.append(f"  {bp1['description']}")
    L.append("framework_refs:")
    L.append("  - framework: APQC-PCF")
    L.append(f"    external_id: \"{bp1['framework_label']}\"")
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


def write_bp1(bp1):
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(emit(bp1))
    return path


def update_index(new_filename):
    idx_path = os.path.join(PROCESSES_DIR, "_index.yaml")
    with open(idx_path) as fh: lines = fh.readlines()
    files, header, in_files = [], [], False
    for ln in lines:
        if ln.startswith("files:"):
            in_files = True; header.append(ln); continue
        if in_files and ln.strip().startswith("- "):
            files.append(ln.strip().lstrip("- "))
        elif not in_files:
            header.append(ln)
    if new_filename not in files: files.append(new_filename)
    files = sorted(files)
    with open(idx_path, "w") as fh:
        for ln in header: fh.write(ln)
        for f in files: fh.write(f"  - {f}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not (args.bp1 or args.all):
        ap.error("Pass --bp1 <id> or --all")
    targets = list(TREE.keys()) if args.all else [args.bp1]
    for bp1_id in targets:
        if bp1_id not in TREE: raise SystemExit(f"Unknown {bp1_id}")
        bp1 = TREE[bp1_id]
        path = write_bp1(bp1)
        update_index(os.path.basename(path))
        print(f"✔ {bp1_id} → {os.path.relpath(path, REPO_ROOT)} (industry: {bp1['industry']}, {len(bp1['children'])} BP2)")


if __name__ == "__main__":
    main()
