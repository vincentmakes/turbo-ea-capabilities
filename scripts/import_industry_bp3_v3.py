#!/usr/bin/env python3
"""BP3 drill-down for the remaining 18 industry BP1s without it.

Re-emits each BP1 file with BP1 + BP2 + BP3 levels. Compact data structure.
"""
from __future__ import annotations
import argparse, os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")


def slug(n):
    o, l = [], True
    for c in n.lower():
        if c.isalnum(): o.append(c); l = False
        elif not l: o.append("-"); l = True
    return "".join(o).strip("-")


# Compact: BP1 = (id, name, industry, framework_label, [bc_realizes],
#                 [(bp2_id, bp2_name, [bc_realizes],
#                   [(bp3_id, bp3_name, bp3_desc, [bc_realizes])])])
TREE = []

# ============ Telecom (BP-160) ============
TREE.append(("BP-160", "Operate Communications Networks and Services",
    "Telecommunications",
    "Run telecom-specific operations: network lifecycle, service provisioning and assurance, performance management, and spectrum and interconnect management.",
    "TM Forum Frameworx eTOM Operations and Strategy domains",
    ["BC-100", "BC-600"],
    [
        ("BP-160.10", "Manage Network Lifecycle", "Plan, design, build, and decommission network infrastructure across the lifecycle.", ["BC-700", "BC-600"], [
            ("BP-160.10.10", "Plan and Design Network Capacity", "Plan and design network capacity, topology, and target architecture.", ["BC-700", "BC-600"]),
            ("BP-160.10.20", "Build and Deploy Network Elements", "Build, install, and deploy network elements and infrastructure.", ["BC-700"]),
            ("BP-160.10.30", "Decommission Network Elements", "Decommission and dispose of obsolete network elements.", ["BC-700"]),
        ]),
        ("BP-160.20", "Manage Network Operations and Service Assurance", "Operate the network and assure services: fault, performance, configuration, and capacity management.", ["BC-600", "BC-720"], [
            ("BP-160.20.10", "Manage Network Faults", "Detect, isolate, and resolve network faults.", ["BC-600"]),
            ("BP-160.20.20", "Manage Network Performance", "Monitor and tune network performance against KPIs.", ["BC-600", "BC-720"]),
            ("BP-160.20.30", "Manage Network Configuration", "Maintain network configuration baselines; manage CMDB.", ["BC-600", "BC-610"]),
            ("BP-160.20.40", "Manage Network Capacity", "Forecast and plan network capacity headroom.", ["BC-600"]),
        ]),
        ("BP-160.30", "Manage Service Provisioning and Activation", "Provision and activate customer services across access, core, and OSS systems.", ["BC-430", "BC-600"], [
            ("BP-160.30.10", "Validate Service Feasibility", "Check feasibility of customer service requests against network resources.", ["BC-600"]),
            ("BP-160.30.20", "Provision and Activate Customer Services", "Provision and activate services on the network.", ["BC-430", "BC-600"]),
            ("BP-160.30.30", "Conduct Service Acceptance Testing", "Run acceptance tests; hand over to customer.", ["BC-720"]),
        ]),
        ("BP-160.40", "Manage Service Quality and Performance", "Manage service quality and performance against SLAs across the customer base.", ["BC-720", "BC-430"], [
            ("BP-160.40.10", "Monitor Service Quality and SLAs", "Monitor service quality against SLAs; report breaches.", ["BC-720"]),
            ("BP-160.40.20", "Manage Service Quality Improvements", "Drive service quality improvements based on root-cause analysis.", ["BC-720"]),
        ]),
        ("BP-160.50", "Manage Spectrum and Interconnect", "Manage radio spectrum holdings and interconnect arrangements with peer operators.", ["BC-150", "BC-510"], [
            ("BP-160.50.10", "Acquire and Manage Spectrum Licences", "Acquire spectrum licences; manage spectrum holdings and renewals.", ["BC-150"]),
            ("BP-160.50.20", "Manage Inter-Operator Agreements", "Negotiate and operate interconnect, roaming, and wholesale agreements.", ["BC-510"]),
            ("BP-160.50.30", "Manage Inter-Operator Settlement", "Settle inter-operator usage; manage disputes.", ["BC-510", "BC-200"]),
        ]),
    ],
))

# ============ Oil & Gas (BP-210, BP-220) ============
TREE.append(("BP-210", "Acquire, Explore, and Develop Hydrocarbon Assets",
    "Oil & Gas",
    "Run upstream petroleum operations from licence acquisition and exploration through field appraisal and development to first hydrocarbons.",
    "Upstream Petroleum PCF v7.2 — Categories 2.0 'Acquire, Explore, and Appraise Hydrocarbon Assets' and 3.0 'Develop and Deplete Hydrocarbon Assets'",
    ["BC-100"],
    [
        ("BP-210.10", "Acquire Hydrocarbon Licences and Acreage", "Acquire exploration and production rights through licence rounds, farm-ins, asset acquisitions.", ["BC-150"], [
            ("BP-210.10.10", "Pursue Licence Rounds", "Bid in licence rounds; manage commitments.", ["BC-150"]),
            ("BP-210.10.20", "Negotiate Farm-Ins and Acquisitions", "Negotiate farm-in agreements and asset acquisitions.", ["BC-150"]),
        ]),
        ("BP-210.20", "Explore for Hydrocarbon Resources", "Conduct geological and geophysical exploration: seismic acquisition, processing, prospect generation.", [], [
            ("BP-210.20.10", "Acquire Seismic Data", "Acquire 2D/3D seismic data over licence acreage.", []),
            ("BP-210.20.20", "Process and Interpret Seismic", "Process seismic data; interpret structure and stratigraphy.", []),
            ("BP-210.20.30", "Generate and Mature Prospects", "Generate prospects and lead inventories; mature for drill decision.", []),
        ]),
        ("BP-210.30", "Appraise and Evaluate Discoveries", "Drill appraisal wells; evaluate discoveries to estimate resources and commercial viability.", [], [
            ("BP-210.30.10", "Drill Appraisal Wells", "Drill appraisal wells to delineate discoveries.", []),
            ("BP-210.30.20", "Evaluate Resources and Reserves", "Estimate resources and reserves per SPE-PRMS / equivalent.", []),
        ]),
        ("BP-210.40", "Develop Hydrocarbon Assets", "Plan, design, execute field-development projects, including drilling and facilities construction.", ["BC-700", "BC-900"], [
            ("BP-210.40.10", "Concept Select and Sanction Field Development", "Conduct concept select; reach FID and sanction field development.", ["BC-900"]),
            ("BP-210.40.20", "Drill Development Wells", "Drill development wells per the field-development plan.", []),
            ("BP-210.40.30", "Construct and Commission Production Facilities", "Construct and commission production facilities.", ["BC-700", "BC-900"]),
        ]),
        ("BP-210.50", "Manage Subsurface and Reservoir Engineering", "Manage subsurface modelling, reservoir engineering, recovery optimisation across the asset life.", [], [
            ("BP-210.50.10", "Maintain Subsurface Models", "Maintain subsurface and reservoir models; update with production data.", []),
            ("BP-210.50.20", "Optimise Reservoir Recovery", "Plan and execute interventions to optimise hydrocarbon recovery.", []),
        ]),
    ],
))

TREE.append(("BP-220", "Produce and Trade Petroleum",
    "Oil & Gas",
    "Run production operations through to product trading and downstream refining, blending, distribution, and retail fuel marketing.",
    "Upstream PCF v7.2 (production) + Downstream Petroleum PCF v7.2 (refining, marketing)",
    ["BC-520"],
    [
        ("BP-220.10", "Operate Hydrocarbon Production", "Operate producing wells, surface facilities, gathering systems; optimise production rates.", [], [
            ("BP-220.10.10", "Operate Producing Wells", "Operate producing wells; manage well work and interventions.", []),
            ("BP-220.10.20", "Operate Surface Facilities", "Operate surface separation, treatment, and gathering facilities.", ["BC-700"]),
            ("BP-220.10.30", "Manage Production Allocation", "Allocate production to wells, leases, and partners.", ["BC-200"]),
        ]),
        ("BP-220.20", "Operate Refining and Processing", "Run refining and gas processing: crude distillation, conversion, treatment, blending.", ["BC-520", "BC-720"], [
            ("BP-220.20.10", "Plan Refinery Operations", "Plan refinery operations: crude slate, unit utilisation, product yields.", ["BC-520"]),
            ("BP-220.20.20", "Operate Refinery Units", "Operate distillation, conversion, treatment, and blending units.", ["BC-520", "BC-720"]),
            ("BP-220.20.30", "Manage Product Quality and Blending", "Blend products to specification; manage quality assurance.", ["BC-720"]),
        ]),
        ("BP-220.30", "Manage Petroleum Trading and Optimisation", "Trade crude, products, and energy; optimise the value chain through commercial decisions.", ["BC-210"], [
            ("BP-220.30.10", "Operate ETRM and Trade Capture", "Capture trades into ETRM; manage positions and exposures.", ["BC-210"]),
            ("BP-220.30.20", "Optimise Hydrocarbon Value Chain", "Optimise crude/product flows across the value chain.", ["BC-210", "BC-520"]),
        ]),
        ("BP-220.40", "Manage Bulk Distribution and Logistics", "Move bulk hydrocarbons through pipelines, marine, rail, truck; manage terminals and storage.", ["BC-520"], [
            ("BP-220.40.10", "Operate Pipelines and Terminals", "Operate pipelines, marine terminals, and storage tanks.", ["BC-700", "BC-520"]),
            ("BP-220.40.20", "Manage Marine and Rail Movements", "Manage marine and rail bulk hydrocarbon movements.", ["BC-520"]),
        ]),
        ("BP-220.50", "Operate Retail Fuel Marketing", "Operate retail fuels and convenience networks, including pricing, supply, station operations.", ["BC-440"], [
            ("BP-220.50.10", "Operate Service Stations and Convenience Retail", "Operate service stations and convenience retail.", []),
            ("BP-220.50.20", "Manage Retail Pricing and Supply", "Manage retail pricing and station supply.", ["BC-440", "BC-520"]),
        ]),
        ("BP-220.60", "Manage Hydrocarbon Asset Decommissioning", "Plan and execute decommissioning of upstream and downstream assets at end-of-life.", ["BC-740", "BC-730"], [
            ("BP-220.60.10", "Plan Asset Decommissioning", "Plan decommissioning programs; manage liabilities and stakeholders.", ["BC-740"]),
            ("BP-220.60.20", "Execute Decommissioning and Restoration", "Execute decommissioning and site restoration.", ["BC-740", "BC-730"]),
        ]),
    ],
))

# ============ Health Insurance Payor (BP-300) ============
TREE.append(("BP-300", "Operate Health Insurance Payor",
    "Insurance",
    "Run health insurance payor operations: member enrolment and eligibility, provider network management, medical claims adjudication, care management, member services, and regulatory operations distinct from P&C insurance.",
    "Health Insurance Payor PCF v7.2.1",
    ["BC-100"],
    [
        ("BP-300.10", "Manage Member Enrolment and Eligibility", "Enrol and disenrol members across individual, group, Medicare, Medicaid lines.", [], [
            ("BP-300.10.10", "Process Member Enrolments", "Process member enrolments and disenrolments.", []),
            ("BP-300.10.20", "Maintain Member Eligibility", "Maintain eligibility records; manage qualifying-event changes.", []),
            ("BP-300.10.30", "Issue Member ID Cards and Materials", "Issue ID cards and welcome materials.", ["BC-430"]),
        ]),
        ("BP-300.20", "Manage Provider Network and Contracting", "Recruit, contract, credential, manage performance of in-network providers.", ["BC-510"], [
            ("BP-300.20.10", "Recruit and Contract Providers", "Recruit and contract in-network providers and facilities.", ["BC-510"]),
            ("BP-300.20.20", "Credential Providers", "Credential providers per CMS / NCQA standards.", ["BC-510"]),
            ("BP-300.20.30", "Maintain Provider Directory", "Maintain provider directory; comply with No Surprises Act and equivalents.", ["BC-610"]),
        ]),
        ("BP-300.30", "Adjudicate Medical Claims", "Receive, edit, adjudicate, pay medical claims under benefit plans.", [], [
            ("BP-300.30.10", "Receive and Edit Claims", "Receive 837 claims; apply edits and validations.", []),
            ("BP-300.30.20", "Adjudicate Claims", "Adjudicate claims against benefits, eligibility, and provider contracts.", []),
            ("BP-300.30.30", "Pay Claims and Issue 835", "Pay claims; issue 835 remittance advice.", ["BC-200"]),
            ("BP-300.30.40", "Manage Appeals and Grievances", "Process member and provider appeals and grievances.", []),
        ]),
        ("BP-300.40", "Manage Care and Utilization", "Run care-management and utilisation-management programs.", [], [
            ("BP-300.40.10", "Conduct Prior Authorisation", "Process prior-authorisation requests for services.", []),
            ("BP-300.40.20", "Run Case and Disease Management", "Run case-management and disease-management programs.", []),
            ("BP-300.40.30", "Conduct Concurrent and Retrospective Review", "Conduct concurrent and retrospective utilisation review.", []),
        ]),
        ("BP-300.50", "Manage Member Services", "Service members across channels for inquiries, ID cards, formularies, benefits questions.", ["BC-430"], [
            ("BP-300.50.10", "Resolve Member Inquiries", "Resolve member inquiries across channels.", ["BC-430"]),
            ("BP-300.50.20", "Manage Member Engagement", "Run member-engagement programs and digital tools.", ["BC-420"]),
        ]),
        ("BP-300.60", "Manage Health Plan Regulatory Operations", "Run regulatory operations specific to health plans: HEDIS, Star Ratings, MLR, state DOI filings.", ["BC-130"], [
            ("BP-300.60.10", "Produce HEDIS Quality Measures", "Calculate and submit HEDIS quality measures.", ["BC-130", "BC-720"]),
            ("BP-300.60.20", "Produce Star Ratings and CMS Reports", "Produce CMS Star Ratings reports and equivalent regulator submissions.", ["BC-130"]),
            ("BP-300.60.30", "Calculate and Report MLR", "Calculate Medical Loss Ratio; submit to regulators.", ["BC-200", "BC-130"]),
        ]),
    ],
))

# ============ Retail (BP-280) ============
TREE.append(("BP-280", "Operate Retail Merchandising and Stores",
    "Retail & Consumer Goods",
    "Run retail-specific operations: merchandising and assortment, omni-channel commerce, store operations, loyalty, and supply for store and online fulfilment.",
    "Retail PCF v7.2.1 — Operating categories",
    ["BC-100"],
    [
        ("BP-280.10", "Manage Merchandising and Assortment Planning", "Plan assortments, allocate space and shelf, manage category and brand lifecycles.", ["BC-820", "BC-400"], [
            ("BP-280.10.10", "Plan Assortments by Category", "Plan assortments by category and store cluster.", ["BC-820"]),
            ("BP-280.10.20", "Manage Space and Planogram", "Allocate space and develop planograms.", []),
            ("BP-280.10.30", "Manage Category Lifecycle", "Manage category lifecycle: introductions, refreshes, exits.", ["BC-820"]),
        ]),
        ("BP-280.20", "Manage Pricing, Promotions, and Markdown", "Set everyday and promotional pricing; plan and execute markdown and clearance.", ["BC-440"], [
            ("BP-280.20.10", "Set Everyday Pricing", "Set everyday-low / regular pricing across categories.", ["BC-440"]),
            ("BP-280.20.20", "Plan and Execute Promotions", "Plan and execute promotional events.", ["BC-440", "BC-400"]),
            ("BP-280.20.30", "Plan and Execute Markdowns", "Plan markdown cadences; execute clearance.", ["BC-440"]),
        ]),
        ("BP-280.30", "Operate Omni-Channel Commerce", "Operate e-commerce, mobile, marketplace, and digital channels alongside physical store sales.", ["BC-420", "BC-410"], [
            ("BP-280.30.10", "Operate Brand E-Commerce", "Operate brand.com, mobile app, and direct digital sales.", ["BC-410"]),
            ("BP-280.30.20", "Manage Marketplaces and Resellers", "Manage marketplace and reseller channels.", ["BC-410", "BC-510"]),
        ]),
        ("BP-280.40", "Operate Store Operations", "Run store-level operations: opening procedures, labour scheduling, cash handling, loss prevention.", ["BC-700", "BC-300"], [
            ("BP-280.40.10", "Manage Store Workforce and Scheduling", "Schedule and manage store labour.", ["BC-300"]),
            ("BP-280.40.20", "Operate Store Daily Operations", "Run store opening, closing, and shift operations.", ["BC-700"]),
            ("BP-280.40.30", "Manage Loss Prevention", "Run loss-prevention programs.", ["BC-120"]),
        ]),
        ("BP-280.50", "Operate Customer Loyalty and CX Programs", "Run loyalty, member, and customer-experience programs across channels.", ["BC-420"], [
            ("BP-280.50.10", "Run Loyalty Program", "Operate loyalty enrolment, accruals, redemptions.", ["BC-420"]),
            ("BP-280.50.20", "Manage Customer Experience Programs", "Run CX measurement and improvement programs.", ["BC-420", "BC-430"]),
        ]),
        ("BP-280.60", "Manage Store and Online Fulfilment", "Fulfil orders across BOPIS, kerbside, ship-from-store, DC-to-customer; manage last-mile.", ["BC-520", "BC-530"], [
            ("BP-280.60.10", "Operate BOPIS and Kerbside", "Operate buy-online-pick-up-in-store and kerbside pickup.", ["BC-520"]),
            ("BP-280.60.20", "Operate Ship-from-Store", "Operate ship-from-store fulfilment.", ["BC-520", "BC-530"]),
            ("BP-280.60.30", "Manage Last-Mile and Returns", "Manage last-mile delivery and customer returns.", ["BC-520"]),
        ]),
    ],
))

# ============ Automotive OEM (BP-290) ============
TREE.append(("BP-290", "Manage Vehicle Programs and Dealer Network",
    "Automotive & Mobility",
    "Run automotive-OEM-specific operations: vehicle program management, dealer network management, vehicle distribution, recall management, connected/aftermarket services.",
    "Automotive (OEM) PCF v7.2.2",
    ["BC-820"],
    [
        ("BP-290.10", "Manage Vehicle Program Lifecycle", "Govern vehicle programs from concept gate through SOP and end-of-production.", ["BC-820", "BC-810"], [
            ("BP-290.10.10", "Develop Vehicle Concepts", "Develop vehicle concepts; conduct concept gates.", ["BC-820"]),
            ("BP-290.10.20", "Engineer and Validate Vehicles", "Engineer, integrate, and validate vehicle programs.", ["BC-810"]),
            ("BP-290.10.30", "Obtain Type Approval and Homologation", "Obtain type approval and homologation in target markets.", ["BC-720", "BC-130"]),
            ("BP-290.10.40", "Launch Vehicle Programs", "Manage vehicle program launch including SOP and ramp.", ["BC-820"]),
        ]),
        ("BP-290.20", "Manage Dealer Network", "Recruit, onboard, contract, and manage performance of the dealer network.", ["BC-410", "BC-510"], [
            ("BP-290.20.10", "Recruit and Onboard Dealers", "Recruit and onboard new dealers; verify standards.", ["BC-410", "BC-510"]),
            ("BP-290.20.20", "Manage Dealer Agreements", "Manage dealer agreements, modifications, and terminations.", ["BC-150", "BC-510"]),
            ("BP-290.20.30", "Monitor Dealer Performance", "Monitor dealer performance against standards and KPIs.", ["BC-410"]),
        ]),
        ("BP-290.30", "Manage Vehicle Distribution and Logistics", "Allocate, ship, and deliver finished vehicles to dealers and customers.", ["BC-520"], [
            ("BP-290.30.10", "Allocate Vehicles to Dealers", "Allocate vehicles to dealers per ATP and demand.", ["BC-520"]),
            ("BP-290.30.20", "Ship and Deliver Vehicles", "Ship and deliver vehicles to dealers/customers.", ["BC-520"]),
        ]),
        ("BP-290.40", "Manage Vehicle Recalls and Field Actions", "Identify, investigate, and execute safety recalls and field service actions.", ["BC-720", "BC-130"], [
            ("BP-290.40.10", "Investigate Field Issues", "Investigate field-quality issues; determine recall need.", ["BC-720"]),
            ("BP-290.40.20", "Execute Recalls", "Execute recalls; manage NHTSA / regulator reporting.", ["BC-130", "BC-720"]),
        ]),
        ("BP-290.50", "Operate Aftermarket and Parts Distribution", "Operate the aftermarket parts business: sourcing, distribution, dealer parts ordering, remanufacture.", ["BC-520", "BC-530"], [
            ("BP-290.50.10", "Manage Aftermarket Parts Catalogue", "Manage aftermarket parts catalogue and superseding.", ["BC-820", "BC-530"]),
            ("BP-290.50.20", "Distribute Aftermarket Parts", "Distribute parts to dealers and customers.", ["BC-520"]),
        ]),
        ("BP-290.60", "Manage Connected and Mobility Services", "Operate connected-vehicle services, telematics, charging networks, adjacent mobility offers.", ["BC-600", "BC-820"], [
            ("BP-290.60.10", "Operate Connected-Vehicle Platform", "Operate connected-vehicle platform and OTA updates.", ["BC-600", "BC-820"]),
            ("BP-290.60.20", "Manage Mobility Services", "Manage charging networks, ride-share, and adjacent mobility services.", ["BC-820", "BC-410"]),
        ]),
    ],
))

# ============ Mining (BP-310) ============
TREE.append(("BP-310", "Operate Mining and Metals Lifecycle",
    "Mining & Metals",
    "Run end-to-end mining and metals lifecycle: exploration and resource definition, mine planning, extraction, mineral processing, tailings management, closure and rehabilitation.",
    "Mining lifecycle reference (no published APQC Mining PCF; aligned to ICMM Mining Principles, CRIRSCO, GISTM)",
    ["BC-100"],
    [
        ("BP-310.10", "Manage Mineral Exploration and Resource Definition", "Conduct mineral exploration; estimate and classify resources/reserves under JORC/SAMREC/NI 43-101.", [], [
            ("BP-310.10.10", "Conduct Mineral Exploration", "Conduct geological mapping, geophysical and geochemical surveys; drill exploration holes.", []),
            ("BP-310.10.20", "Estimate Resources and Reserves", "Estimate resources and reserves under JORC/SAMREC/NI 43-101.", []),
        ]),
        ("BP-310.20", "Manage Mine Planning and Development", "Plan and design mine layouts; develop mine projects through feasibility, construction, commissioning.", ["BC-700", "BC-900"], [
            ("BP-310.20.10", "Conduct Feasibility Studies", "Conduct PFS and DFS for mine development.", ["BC-900"]),
            ("BP-310.20.20", "Design Mine Layouts and Schedules", "Design mine layouts; schedule production and development.", []),
            ("BP-310.20.30", "Construct and Commission Mines", "Construct and commission mining projects.", ["BC-700", "BC-900"]),
        ]),
        ("BP-310.30", "Operate Mining Extraction", "Operate underground or surface mining: drilling, blasting, hauling, grade control.", [], [
            ("BP-310.30.10", "Operate Drill and Blast", "Operate drill-and-blast operations.", []),
            ("BP-310.30.20", "Operate Loading and Hauling", "Operate loading and hauling operations.", []),
            ("BP-310.30.30", "Manage Grade Control", "Manage grade control and ore-waste delineation.", []),
        ]),
        ("BP-310.40", "Operate Mineral Processing and Beneficiation", "Process ore through crushing, grinding, flotation, leaching, smelting, refining, blending.", ["BC-720"], [
            ("BP-310.40.10", "Operate Crushing and Grinding", "Operate crushing and grinding circuits.", []),
            ("BP-310.40.20", "Operate Concentration and Refining", "Operate flotation, leaching, smelting, refining.", ["BC-720"]),
            ("BP-310.40.30", "Manage Product Blending and Quality", "Blend mineral products to specification.", ["BC-720"]),
        ]),
        ("BP-310.50", "Manage Tailings and Mining Waste", "Manage tailings storage facilities and mining waste under GISTM and ICMM standards.", ["BC-730", "BC-740"], [
            ("BP-310.50.10", "Operate Tailings Storage Facilities", "Operate tailings storage facilities under GISTM governance.", ["BC-730"]),
            ("BP-310.50.20", "Manage Mine Waste and Water", "Manage waste rock and mine water across the operation.", ["BC-730", "BC-740"]),
        ]),
        ("BP-310.60", "Manage Mine Closure and Rehabilitation", "Plan and execute integrated mine closure: rehabilitation, decommissioning, post-closure monitoring.", ["BC-740", "BC-730"], [
            ("BP-310.60.10", "Plan Mine Closure", "Plan integrated mine closure per ICMM IMC guidance.", ["BC-740"]),
            ("BP-310.60.20", "Execute Rehabilitation and Closure", "Execute rehabilitation and closure works.", ["BC-740", "BC-730"]),
            ("BP-310.60.30", "Conduct Post-Closure Monitoring", "Conduct post-closure environmental monitoring.", ["BC-730"]),
        ]),
    ],
))


def emit(t):
    bp1_id, name, ind, desc, fwlabel, realizes, children = t
    L = []
    L.append(f"id: {bp1_id}")
    L.append(f"name: {name}")
    L.append("level: 1")
    L.append(f"industry: {ind}")
    L.append("description: >-")
    L.append(f"  {desc}")
    L.append("framework_refs:")
    L.append("  - framework: APQC-PCF")
    L.append(f"    external_id: \"{fwlabel}\"")
    L.append("realizes_capability_ids:")
    for bc in realizes: L.append(f"  - {bc}")
    L.append("children:")
    for bp2_id, bp2_name, bp2_desc, bp2_realizes, bp3s in children:
        L.append(f"  - id: {bp2_id}")
        L.append(f"    name: {bp2_name}")
        L.append("    level: 2")
        L.append("    description: >-")
        L.append(f"      {bp2_desc}")
        if bp2_realizes:
            L.append("    realizes_capability_ids:")
            for bc in bp2_realizes: L.append(f"      - {bc}")
        else:
            L.append("    realizes_capability_ids: []")
        L.append("    children:")
        for cid, cname, cdesc, crealizes in bp3s:
            L.append(f"      - id: {cid}")
            L.append(f"        name: {cname}")
            L.append("        level: 3")
            L.append("        description: >-")
            L.append(f"          {cdesc}")
            if crealizes:
                L.append("        realizes_capability_ids:")
                for bc in crealizes: L.append(f"          - {bc}")
            else:
                L.append("        realizes_capability_ids: []")
            L.append("        children: []")
    return "\n".join(L) + "\n"


def write(t):
    bp1_id, name = t[0], t[1]
    s = slug(name)
    path = os.path.join(PROCESSES_DIR, f"BP1-{s}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(emit(t))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1", required=True)
    args = ap.parse_args()
    target = next((t for t in TREE if t[0] == args.bp1), None)
    if not target: raise SystemExit(f"Unknown {args.bp1}; defined: {[t[0] for t in TREE]}")
    path = write(target)
    nb_bp2 = len(target[6])
    nb_bp3 = sum(len(c[3]) for c in target[6])
    print(f"✔ {target[0]} → {os.path.relpath(path, REPO_ROOT)} ({nb_bp2} BP2, {nb_bp3} BP3)")


if __name__ == "__main__":
    main()
