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



# ============ Media (BP-390) ============
TREE.append(("BP-390", "Develop, Produce, and Distribute Content",
    "Media, Entertainment & Telecom Content",
    "Run media-industry operations: content development and greenlight, production, rights and IP, distribution and syndication, advertising/subscription, audience measurement.",
    "Broadcasting/Media PCF v7.2.x + MovieLabs Common Workflow + SMPTE/EBU/DPP",
    ["BC-100"],
    [
        ("BP-390.10", "Develop and Greenlight Content", "Source, evaluate, and greenlight content concepts; manage development slate.", ["BC-800"], [
            ("BP-390.10.10", "Source and Evaluate Content Ideas", "Source content ideas; conduct creative development.", ["BC-800"]),
            ("BP-390.10.20", "Greenlight Content for Production", "Conduct greenlight reviews; commit to production.", ["BC-800"]),
        ]),
        ("BP-390.20", "Produce Content", "Plan, execute, post-produce content (film, TV, audio, news).", [], [
            ("BP-390.20.10", "Plan Pre-Production", "Plan pre-production: scripts, casting, location, scheduling.", []),
            ("BP-390.20.20", "Execute Principal Production", "Execute principal photography or recording.", []),
            ("BP-390.20.30", "Conduct Post-Production and Mastering", "Conduct editing, VFX, sound, color, and mastering.", []),
        ]),
        ("BP-390.30", "Manage Rights and IP", "Acquire, register, and administer content rights; manage chain of title.", ["BC-840"], [
            ("BP-390.30.10", "Acquire and Register Rights", "Acquire and register content rights and chain of title.", ["BC-840"]),
            ("BP-390.30.20", "License Rights to/from Third Parties", "License rights inbound and outbound.", ["BC-840"]),
        ]),
        ("BP-390.40", "Distribute and Syndicate Content", "Distribute content across linear, OTT, theatrical, home-entertainment, syndication channels.", ["BC-520"], [
            ("BP-390.40.10", "Schedule and Place Content", "Schedule content; place in catalogue.", []),
            ("BP-390.40.20", "Distribute via Linear and OTT", "Distribute via linear broadcast, OTT, and streaming.", ["BC-520"]),
            ("BP-390.40.30", "Manage Theatrical and Home-Entertainment Releases", "Manage theatrical, home-entertainment, and syndication windows.", []),
        ]),
        ("BP-390.50", "Operate Advertising Sales and Subscription", "Sell advertising inventory and operate subscription services.", ["BC-410", "BC-420"], [
            ("BP-390.50.10", "Sell Advertising Inventory", "Sell advertising inventory across linear and digital.", ["BC-410"]),
            ("BP-390.50.20", "Operate Ad Trafficking and Delivery", "Traffic creative; deliver and verify ad impressions.", []),
            ("BP-390.50.30", "Operate Subscription Services", "Operate subscription billing and member servicing.", ["BC-420"]),
        ]),
        ("BP-390.60", "Manage Audience Measurement and Analytics", "Capture and analyse audience data for monetisation and programming decisions.", ["BC-610"], [
            ("BP-390.60.10", "Capture Audience Telemetry", "Capture viewing telemetry across linear, OTT, and ad delivery.", ["BC-610"]),
            ("BP-390.60.20", "Analyse Audience and Performance", "Analyse audience metrics and content performance.", ["BC-610"]),
        ]),
    ],
))

# ============ Professional Services (BP-400) ============
TREE.append(("BP-400", "Operate Professional Services Engagements",
    "Professional Services",
    "Run professional-services engagements end-to-end: opportunity, engagement planning, delivery, billing/realisation, knowledge reuse, talent management.",
    "Consulting/Professional Services PCF v7.2.x + CMMI-SVC v2.0 + SPI",
    ["BC-100"],
    [
        ("BP-400.10", "Manage Engagement Lifecycle", "Run engagement lifecycle: opportunity, proposal, planning, delivery, change, closeout.", ["BC-410", "BC-900"], [
            ("BP-400.10.10", "Pursue Opportunities and Submit Proposals", "Pursue opportunities; develop and submit proposals.", ["BC-410"]),
            ("BP-400.10.20", "Plan and Mobilise Engagements", "Plan engagements; mobilise teams and resources.", ["BC-900"]),
            ("BP-400.10.30", "Deliver and Manage Engagement Change", "Deliver engagements; manage scope changes.", ["BC-900"]),
            ("BP-400.10.40", "Close Out Engagements", "Close out engagements with deliverables and lessons learned.", []),
        ]),
        ("BP-400.20", "Manage Resource and Talent", "Plan, allocate, and develop the professional workforce.", ["BC-300"], [
            ("BP-400.20.10", "Plan and Allocate Resources", "Plan resource demand; allocate consultants to engagements.", ["BC-300"]),
            ("BP-400.20.20", "Develop Skills and Capabilities", "Develop staff skills, certifications, and capabilities.", ["BC-300"]),
        ]),
        ("BP-400.30", "Manage Client Relationships and Accounts", "Run account management for client portfolios.", ["BC-420", "BC-410"], [
            ("BP-400.30.10", "Manage Key Accounts", "Manage strategic and key accounts.", ["BC-420"]),
            ("BP-400.30.20", "Manage Cross-Sell and Renewal", "Drive cross-sell and renewal in client accounts.", ["BC-410"]),
        ]),
        ("BP-400.40", "Manage Knowledge Reuse and Methodology", "Capture engagement knowledge; develop methodologies and reusable assets.", ["BC-830"], [
            ("BP-400.40.10", "Capture and Curate Engagement Knowledge", "Capture engagement assets; sanitise and curate.", ["BC-830"]),
            ("BP-400.40.20", "Develop Methodologies and IP", "Develop firm methodologies and IP for reuse.", ["BC-830", "BC-840"]),
        ]),
        ("BP-400.50", "Manage Engagement Quality and Risk", "Run engagement-level QA, peer review, risk management; manage independence and conflict checks.", ["BC-720", "BC-120"], [
            ("BP-400.50.10", "Conduct Independence and Conflict Checks", "Conduct independence, conflict, and ethics checks at engagement acceptance.", ["BC-150", "BC-130"]),
            ("BP-400.50.20", "Conduct Engagement Peer Review and QA", "Conduct engagement-level peer review and QA.", ["BC-720"]),
        ]),
    ],
))

# ============ Software & Technology (BP-420) ============
TREE.append(("BP-420", "Operate Software-as-a-Service Lifecycle",
    "Software & Technology",
    "Run SaaS-specific operations: product lifecycle, subscription/trial lifecycle, customer onboarding, customer success and renewal, cloud and tenant operations.",
    "TSIA frameworks + ITIL 4 + DORA capability model + DevOps/SRE practices",
    ["BC-820", "BC-600"],
    [
        ("BP-420.10", "Manage SaaS Product Lifecycle", "Operate SaaS product lifecycle: roadmap, feature flags, beta/GA cycles, deprecation, EOL.", ["BC-820"], [
            ("BP-420.10.10", "Manage SaaS Roadmap and Release Trains", "Manage product roadmap and release trains.", ["BC-820"]),
            ("BP-420.10.20", "Operate Feature Flags and Experimentation", "Operate feature flags, A/B testing, and progressive rollouts.", ["BC-820"]),
        ]),
        ("BP-420.20", "Manage Subscription and Trial Lifecycle", "Operate trial, conversion, subscription, expansion, contraction, cancellation.", ["BC-410", "BC-440"], [
            ("BP-420.20.10", "Manage Trials and Conversion", "Run free/paid trial programs; convert to paid.", ["BC-410"]),
            ("BP-420.20.20", "Manage Subscription Lifecycle Events", "Process subscription start, change, pause, cancel.", ["BC-440"]),
        ]),
        ("BP-420.30", "Manage Customer Onboarding and Adoption", "Onboard customers; drive adoption and time-to-value.", ["BC-430", "BC-420"], [
            ("BP-420.30.10", "Onboard Customers", "Onboard new customers through implementation milestones.", ["BC-430"]),
            ("BP-420.30.20", "Drive Adoption and Time-to-Value", "Drive feature adoption, milestones, and time-to-value.", ["BC-420"]),
        ]),
        ("BP-420.40", "Manage Customer Success and Renewal", "Run customer-success programs; manage health scores, expansion, renewals.", ["BC-420", "BC-410"], [
            ("BP-420.40.10", "Monitor Customer Health Signals", "Monitor health scores; identify risk and expansion opportunities.", ["BC-420"]),
            ("BP-420.40.20", "Drive Expansion and Renewal", "Drive expansion (upsell/cross-sell) and renewal.", ["BC-410"]),
        ]),
        ("BP-420.50", "Operate Cloud and Tenant Operations", "Operate multi-tenant SaaS infrastructure: provisioning, capacity, observability, SRE.", ["BC-600", "BC-620"], [
            ("BP-420.50.10", "Provision and Isolate Tenants", "Provision tenants; manage tenant isolation and quotas.", ["BC-600"]),
            ("BP-420.50.20", "Operate SRE and Incident Response", "Operate SRE practices and incident response.", ["BC-600", "BC-160"]),
            ("BP-420.50.30", "Operate Observability and Capacity", "Operate observability, telemetry, and capacity management.", ["BC-600"]),
        ]),
    ],
))

# ============ Air Traffic Control (BP-430) ============
TREE.append(("BP-430", "Operate Air Traffic Management",
    "Air Traffic Control",
    "Run air-navigation-service-provider operations: airspace management, flight data, ATC services, CNS, aeronautical information, safety.",
    "ICAO Doc 4444 + ICAO Doc 9750 + EUROCONTROL ATM Master Plan + FAA Order 7110.65 + CANSO",
    ["BC-100"],
    [
        ("BP-430.10", "Manage Airspace and Air Traffic Flow", "Plan and manage airspace structure, sectors, and traffic flow.", [], [
            ("BP-430.10.10", "Manage Airspace Structure", "Maintain airspace structure, sectors, and routes.", []),
            ("BP-430.10.20", "Manage Air Traffic Flow", "Plan and execute air traffic flow management.", []),
        ]),
        ("BP-430.20", "Manage Flight Data and Plan", "Receive, validate, distribute, and update flight plans.", [], [
            ("BP-430.20.10", "Receive and Validate Flight Plans", "Receive and validate ICAO/national flight plans.", []),
            ("BP-430.20.20", "Distribute Flight Data", "Distribute flight data to controllers and adjacent ANSPs.", []),
        ]),
        ("BP-430.30", "Provide Air Traffic Control Services", "Provide tower, approach, and en-route ATC services.", [], [
            ("BP-430.30.10", "Provide Tower Control", "Provide aerodrome / tower ATC services.", []),
            ("BP-430.30.20", "Provide Approach and En-Route Control", "Provide approach and en-route ATC services.", []),
            ("BP-430.30.30", "Manage Separation and Conflict Resolution", "Maintain separation; resolve conflicts.", []),
        ]),
        ("BP-430.40", "Manage CNS Infrastructure", "Operate CNS infrastructure supporting ATC services.", ["BC-700", "BC-600"], [
            ("BP-430.40.10", "Operate Communications and Surveillance", "Operate VHF/data link/radar/ADS-B systems.", ["BC-700", "BC-600"]),
            ("BP-430.40.20", "Operate Navigation Aids", "Operate ground-based and satellite navigation aids.", ["BC-700"]),
        ]),
        ("BP-430.50", "Manage Aeronautical Information", "Capture, validate, and publish aeronautical information.", ["BC-610"], [
            ("BP-430.50.10", "Maintain AIP and Charts", "Maintain Aeronautical Information Publication and charts.", ["BC-610"]),
            ("BP-430.50.20", "Issue NOTAMs and Updates", "Issue NOTAMs and updates to airspace users.", ["BC-610"]),
        ]),
        ("BP-430.60", "Manage Aviation Safety and Investigation", "Run ATM safety-management activities including occurrence reporting.", ["BC-720", "BC-160"], [
            ("BP-430.60.10", "Operate Safety Management System", "Operate ATM SMS per ICAO Annex 19 / CANSO standards.", ["BC-720"]),
            ("BP-430.60.20", "Investigate Safety Occurrences", "Investigate safety occurrences; produce just-culture findings.", ["BC-160"]),
        ]),
    ],
))

# ============ Engineering Services (BP-440) ============
TREE.append(("BP-440", "Deliver Engineering and Construction Services",
    "Engineering Services",
    "Run engineering-services-firm operations: tendering and estimation, engineering design, construction execution, commissioning and handover.",
    "ISO 19650 BIM + AIA Phases / RIBA Plan of Work + PMI Construction Extension to PMBOK",
    ["BC-700", "BC-810"],
    [
        ("BP-440.10", "Manage Engineering Tendering and Estimation", "Pursue engineering opportunities; develop tenders, cost estimates, schedules.", ["BC-410"], [
            ("BP-440.10.10", "Pursue Engineering Opportunities", "Pursue engineering opportunities; pre-qualify.", ["BC-410"]),
            ("BP-440.10.20", "Develop Cost Estimates and Tenders", "Develop cost estimates and tenders.", ["BC-230"]),
        ]),
        ("BP-440.20", "Deliver Engineering Design", "Perform engineering design across disciplines; manage design coordination via BIM/CDE.", ["BC-810"], [
            ("BP-440.20.10", "Perform Multi-Discipline Engineering Design", "Perform engineering design across disciplines.", ["BC-810"]),
            ("BP-440.20.20", "Coordinate Design via BIM and CDE", "Coordinate design through BIM and CDE per ISO 19650.", ["BC-810"]),
        ]),
        ("BP-440.30", "Deliver Construction Execution", "Execute construction work to design and schedule; manage subcontractors, materials, HSE.", ["BC-700", "BC-900"], [
            ("BP-440.30.10", "Manage Construction Subcontractors", "Manage subcontractor packages and execution.", ["BC-510"]),
            ("BP-440.30.20", "Execute Construction Work", "Execute construction to design and schedule.", ["BC-700", "BC-900"]),
            ("BP-440.30.30", "Manage Construction HSE", "Manage construction HSE per industry standards.", ["BC-730"]),
        ]),
        ("BP-440.40", "Manage Commissioning and Handover", "Commission and validate engineered assets; manage handover with as-built documentation.", ["BC-720", "BC-700"], [
            ("BP-440.40.10", "Commission Assets", "Commission and validate engineered assets.", ["BC-720"]),
            ("BP-440.40.20", "Hand Over to Operations", "Hand over to operations with as-built documentation.", ["BC-700"]),
        ]),
        ("BP-440.50", "Manage Engineering Document and Configuration", "Maintain engineering documents, drawings, configuration baselines.", ["BC-820", "BC-610"], [
            ("BP-440.50.10", "Manage Engineering Documents", "Manage engineering documents across project lifecycle.", ["BC-820", "BC-610"]),
            ("BP-440.50.20", "Manage Engineering Configuration", "Manage engineering configuration baselines and changes.", ["BC-820", "BC-910"]),
        ]),
    ],
))

# ============ HVAC & BAS (BP-450) ============
TREE.append(("BP-450", "Operate HVAC and Building Automation Lifecycle",
    "HVAC & Building Automation Systems",
    "Run HVAC and building-automation operations: product development, installation/commissioning, operations, refrigerant-lifecycle management.",
    "ASHRAE + BACnet/KNX + AHRI + EU F-Gas / EPA 608",
    ["BC-820"],
    [
        ("BP-450.10", "Develop HVAC and BAS Products", "Develop HVAC equipment and BAS solutions; obtain certifications.", ["BC-810", "BC-820"], [
            ("BP-450.10.10", "Engineer HVAC Equipment", "Engineer HVAC equipment to ASHRAE standards.", ["BC-810"]),
            ("BP-450.10.20", "Develop BAS Solutions", "Develop BAS solutions per BACnet/KNX standards.", ["BC-820"]),
            ("BP-450.10.30", "Obtain AHRI and Energy Certifications", "Obtain AHRI certification and energy ratings.", ["BC-720"]),
        ]),
        ("BP-450.20", "Manage HVAC Installation and Commissioning", "Install HVAC and BAS; commission per ASHRAE Guideline 0/1.1/1.2.", ["BC-700", "BC-720"], [
            ("BP-450.20.10", "Install HVAC and BAS Equipment", "Install HVAC and BAS equipment per design.", ["BC-700"]),
            ("BP-450.20.20", "Commission per ASHRAE Guideline", "Commission per ASHRAE Guideline 0/1.1/1.2.", ["BC-720"]),
        ]),
        ("BP-450.30", "Operate Building Automation", "Operate BAS for HVAC, lighting, and other building systems.", ["BC-700"], [
            ("BP-450.30.10", "Manage BAS Setpoints and Schedules", "Manage BAS setpoints, schedules, and control sequences.", ["BC-700"]),
            ("BP-450.30.20", "Monitor and Optimise Energy Performance", "Monitor and optimise building energy performance.", ["BC-700", "BC-740"]),
        ]),
        ("BP-450.40", "Manage Refrigerant Lifecycle", "Capture, recover, and reclaim refrigerants per F-Gas / EPA 608.", ["BC-740", "BC-130"], [
            ("BP-450.40.10", "Manage Refrigerant Inventory and Quotas", "Manage refrigerant inventory and EU F-Gas quotas.", ["BC-130", "BC-530"]),
            ("BP-450.40.20", "Recover and Reclaim Refrigerants", "Recover and reclaim refrigerants per regulations.", ["BC-740"]),
            ("BP-450.40.30", "Manage Phase-Down Substitution", "Manage phase-down substitution to lower-GWP refrigerants.", ["BC-740"]),
        ]),
    ],
))

# ============ Electrical Components (BP-460) ============
TREE.append(("BP-460", "Develop and Operate Electrical Equipment",
    "Electrical Components & Equipment",
    "Run electrical-equipment-industry operations: electrical/electronic product development, type approval and certification, component lifecycle, distributor and broker network.",
    "IEC + IPC + UL + IATF 16949",
    ["BC-820"],
    [
        ("BP-460.10", "Develop Electrical and Electronic Products", "Design and develop electrical/electronic products; manage HW-SW co-design and EMC.", ["BC-810", "BC-820"], [
            ("BP-460.10.10", "Develop Hardware Designs", "Develop hardware designs for electrical/electronic products.", ["BC-810"]),
            ("BP-460.10.20", "Develop Embedded Software and Firmware", "Develop embedded software and firmware.", ["BC-810", "BC-600"]),
            ("BP-460.10.30", "Manage EMC and Functional Safety", "Manage EMC and functional safety per IEC 61508.", ["BC-720"]),
        ]),
        ("BP-460.20", "Manage Type Approval and Certification", "Obtain product certifications; manage compliance throughout lifecycle.", ["BC-720", "BC-130"], [
            ("BP-460.20.10", "Obtain Product Certifications", "Obtain UL, CE, IEC certifications and agency marks.", ["BC-720", "BC-130"]),
            ("BP-460.20.20", "Maintain Certification Compliance", "Maintain certification compliance through lifecycle.", ["BC-130"]),
        ]),
        ("BP-460.30", "Manage Component Lifecycle and Obsolescence", "Manage PCN, EOL, last-time-buy windows, replacement migration.", ["BC-820"], [
            ("BP-460.30.10", "Issue Product Change Notifications", "Issue PCNs to customers and channel.", ["BC-820"]),
            ("BP-460.30.20", "Manage End-of-Life and Last-Time Buy", "Manage EOL and last-time-buy windows.", ["BC-820", "BC-530"]),
        ]),
        ("BP-460.40", "Manage Distributor and Broker Network", "Onboard and manage authorised distributors and brokers; manage counterfeit risk.", ["BC-510", "BC-410"], [
            ("BP-460.40.10", "Onboard Authorised Distributors", "Onboard and qualify authorised distributors.", ["BC-510"]),
            ("BP-460.40.20", "Manage Counterfeit and Grey-Market Risk", "Manage counterfeit and grey-market component risk.", ["BC-720", "BC-120"]),
        ]),
    ],
))

# ============ Manufacturing & Industrial (BP-470) ============
TREE.append(("BP-470", "Operate Manufacturing and Industrial Operations",
    "Manufacturing & Industrial",
    "Run manufacturing-specific specialisations: discrete and process manufacturing, manufacturing maintenance (TPM), industrial automation / OT.",
    "ISA-95 (IEC 62264) MOM + APQC Cross-Industry PCF + TPM/OEE + MESA MOM Model + IEC 62443",
    ["BC-520"],
    [
        ("BP-470.10", "Operate Discrete Manufacturing", "Run discrete manufacturing per ISA-95 Level 3 MOM.", ["BC-520", "BC-720"], [
            ("BP-470.10.10", "Schedule and Dispatch Production", "Schedule and dispatch production orders to shop floor.", ["BC-520"]),
            ("BP-470.10.20", "Execute Discrete Production", "Execute assembly, machining, fabrication operations.", ["BC-520"]),
            ("BP-470.10.30", "Manage Quality and Traceability", "Manage in-process quality and lot/serial traceability.", ["BC-720", "BC-610"]),
        ]),
        ("BP-470.20", "Operate Process Manufacturing", "Run process manufacturing (continuous, batch).", ["BC-520", "BC-720"], [
            ("BP-470.20.10", "Manage Recipes and Batch Records", "Manage recipes and batch records per S88.", ["BC-820"]),
            ("BP-470.20.20", "Execute Process Manufacturing", "Execute continuous and batch process operations.", ["BC-520"]),
        ]),
        ("BP-470.30", "Manage Manufacturing Maintenance", "Run TPM and maintenance programs across plant assets; track OEE and reliability.", ["BC-700", "BC-720"], [
            ("BP-470.30.10", "Operate Preventive and Corrective Maintenance", "Operate planned, preventive, and corrective maintenance.", ["BC-700"]),
            ("BP-470.30.20", "Track OEE and Reliability", "Track OEE; drive reliability improvements.", ["BC-700", "BC-720"]),
        ]),
        ("BP-470.40", "Operate Industrial Automation and OT", "Operate industrial automation systems and OT cybersecurity per IEC 62443.", ["BC-600", "BC-620"], [
            ("BP-470.40.10", "Operate SCADA / MES / HMI", "Operate SCADA, MES, and HMI systems on plant floor.", ["BC-600"]),
            ("BP-470.40.20", "Manage OT Cybersecurity", "Manage OT cybersecurity per IEC 62443.", ["BC-620", "BC-600"]),
        ]),
    ],
))

# ============ Agriculture & Food Production (BP-480) ============
TREE.append(("BP-480", "Operate Agriculture and Food Production",
    "Agriculture & Food Production",
    "Run agriculture and food-production operations: crop and livestock production, food processing and manufacturing, farm-to-market supply chain, food-safety.",
    "Food & Beverage PCF v7.2.x + GLOBALG.A.P. + FSMA / EU 178/2002 + ISO 22000",
    ["BC-520"],
    [
        ("BP-480.10", "Manage Crop Production", "Run crop production: planning, planting, crop protection, irrigation, harvest.", [], [
            ("BP-480.10.10", "Plan and Plant Crops", "Plan crop rotations; plant per agronomic plan.", []),
            ("BP-480.10.20", "Manage Crop Protection and Irrigation", "Apply crop-protection products; manage irrigation.", []),
            ("BP-480.10.30", "Conduct Harvest", "Conduct harvest; manage yield and quality.", []),
        ]),
        ("BP-480.20", "Manage Livestock Production", "Run livestock production: breeding, husbandry, animal health, welfare.", [], [
            ("BP-480.20.10", "Manage Breeding and Genetics", "Manage breeding programs and genetics.", []),
            ("BP-480.20.20", "Manage Animal Health and Welfare", "Manage animal health, vaccination, and welfare.", ["BC-730"]),
        ]),
        ("BP-480.30", "Operate Food Processing and Manufacturing", "Run food processing under HACCP / FSSC 22000.", ["BC-520", "BC-720"], [
            ("BP-480.30.10", "Operate HACCP and Food-Safety Programs", "Operate HACCP plans and food-safety programs.", ["BC-720"]),
            ("BP-480.30.20", "Execute Food Manufacturing", "Execute food manufacturing operations.", ["BC-520"]),
            ("BP-480.30.30", "Manage Allergen and Hygiene Controls", "Manage allergen segregation and hygienic operations.", ["BC-720", "BC-730"]),
        ]),
        ("BP-480.40", "Manage Farm-to-Market Supply Chain and Traceability", "Operate farm-to-market supply chains; maintain traceability for recall and food-safety.", ["BC-520", "BC-130"], [
            ("BP-480.40.10", "Operate Farm-to-Market Logistics", "Operate cold-chain and bulk-commodity logistics.", ["BC-520"]),
            ("BP-480.40.20", "Maintain End-to-End Traceability", "Maintain product traceability for recalls and food-safety reporting.", ["BC-610", "BC-130"]),
        ]),
    ],
))

# ============ Chemicals (BP-490) ============
TREE.append(("BP-490", "Operate Chemical Manufacturing and Compliance",
    "Chemicals",
    "Run chemical-industry operations: chemical product development, chemical manufacturing, hazardous-materials and REACH compliance, process safety, distribution.",
    "REACH + GHS + ACC Responsible Care + OSHA PSM + EU Seveso III + ISO 9001/14001",
    ["BC-520", "BC-130"],
    [
        ("BP-490.10", "Develop Chemical Products and Formulations", "Develop chemical products and formulations.", ["BC-810", "BC-820"], [
            ("BP-490.10.10", "Conduct Chemical R&D and Synthesis Routes", "Conduct chemical R&D and develop synthesis routes.", ["BC-810"]),
            ("BP-490.10.20", "Develop Specialty Formulations", "Develop specialty chemical formulations.", ["BC-810", "BC-820"]),
            ("BP-490.10.30", "Manage Product Stewardship", "Manage product stewardship from R&D through end-of-life.", ["BC-820", "BC-740"]),
        ]),
        ("BP-490.20", "Operate Chemical Manufacturing", "Run continuous and batch chemical manufacturing.", ["BC-520", "BC-720"], [
            ("BP-490.20.10", "Operate Continuous Chemical Manufacturing", "Operate continuous chemical manufacturing.", ["BC-520"]),
            ("BP-490.20.20", "Operate Batch Chemical Manufacturing", "Operate batch chemical manufacturing.", ["BC-520"]),
            ("BP-490.20.30", "Manage Chemical Quality", "Manage chemical product quality and specifications.", ["BC-720"]),
        ]),
        ("BP-490.30", "Manage Hazardous Materials and REACH Compliance", "Maintain REACH and equivalent registrations; manage SDS, GHS labelling.", ["BC-130"], [
            ("BP-490.30.10", "Maintain REACH Registrations", "Maintain REACH registrations and authorisations.", ["BC-130"]),
            ("BP-490.30.20", "Manage SDS and GHS Labelling", "Maintain SDS and GHS labels per jurisdiction.", ["BC-130"]),
        ]),
        ("BP-490.40", "Manage Process Safety and Major-Hazard Operations", "Operate PSM per OSHA / Seveso III; manage major-accident hazards.", ["BC-730", "BC-160"], [
            ("BP-490.40.10", "Operate Process Safety Management", "Operate PSM per OSHA / Seveso III.", ["BC-730"]),
            ("BP-490.40.20", "Manage Major-Accident Hazard Programs", "Manage major-accident hazard programs.", ["BC-160", "BC-730"]),
        ]),
        ("BP-490.50", "Manage Chemical Distribution and Logistics", "Operate hazmat-compliant chemical distribution.", ["BC-520"], [
            ("BP-490.50.10", "Manage Hazmat Compliant Logistics", "Operate hazmat-compliant logistics per ADR/RID/IMDG.", ["BC-520", "BC-130"]),
            ("BP-490.50.20", "Manage Chemical Distributor Network", "Manage chemical distributor and tolling network.", ["BC-510"]),
        ]),
    ],
))

# ============ Transportation & Logistics (BP-410) ============
TREE.append(("BP-410", "Operate Transportation and Logistics Services",
    "Transportation & Logistics",
    "Operate transportation and logistics services across modes: network planning, freight movement, last-mile delivery, returns/reverse logistics, freight forwarding and customs.",
    "SCOR v14.0 + GS1 Global Logistics + UN/CEFACT MMT + IATA/IMO/AAR",
    ["BC-520"],
    [
        ("BP-410.10", "Plan Transport Network and Capacity", "Design transport network, asset, and capacity plans.", ["BC-520"], [
            ("BP-410.10.10", "Plan Network and Routing", "Plan transport network and routing.", ["BC-520"]),
            ("BP-410.10.20", "Plan Capacity and Asset Utilisation", "Plan asset capacity and utilisation.", ["BC-520"]),
        ]),
        ("BP-410.20", "Operate Freight and Passenger Movement", "Execute movement across modes; manage dispatch, tracking, exceptions.", ["BC-520"], [
            ("BP-410.20.10", "Dispatch and Track Movements", "Dispatch shipments; track in transit.", ["BC-520"]),
            ("BP-410.20.20", "Operate Multi-Modal Carriage", "Execute carriage across road/rail/air/marine modes.", ["BC-520"]),
            ("BP-410.20.30", "Manage Exceptions and Service Recovery", "Manage exceptions and service recovery.", ["BC-430", "BC-520"]),
        ]),
        ("BP-410.30", "Manage Last-Mile and Customer Delivery", "Plan and execute last-mile delivery.", ["BC-430", "BC-520"], [
            ("BP-410.30.10", "Plan Last-Mile Routes", "Plan last-mile routes and delivery slots.", ["BC-520"]),
            ("BP-410.30.20", "Execute Last-Mile Delivery", "Execute last-mile delivery to consignees.", ["BC-430", "BC-520"]),
        ]),
        ("BP-410.40", "Manage Freight Forwarding and Customs", "Operate freight forwarding, multi-modal coordination, customs/trade-compliance.", ["BC-130"], [
            ("BP-410.40.10", "Coordinate Multi-Modal Forwarding", "Coordinate multi-modal forwarding for cross-border movements.", ["BC-520"]),
            ("BP-410.40.20", "Manage Customs and Trade Compliance", "Manage customs entries and trade-compliance.", ["BC-130"]),
        ]),
        ("BP-410.50", "Manage Returns and Reverse Logistics", "Operate returns and reverse-logistics flows.", ["BC-520"], [
            ("BP-410.50.10", "Process Returns Authorisations", "Process returns authorisations from customers.", ["BC-430", "BC-520"]),
            ("BP-410.50.20", "Operate Reverse-Logistics Flows", "Operate reverse-logistics for repairs, recalls, disposal.", ["BC-520"]),
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
