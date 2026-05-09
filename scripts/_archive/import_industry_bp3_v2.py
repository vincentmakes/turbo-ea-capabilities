#!/usr/bin/env python3
"""BP3 drill-down for the highest-leverage industry BP1s without it.

Target: Public Sector (BP-340/350/360 — 9 wired streams), Real Estate
(BP-320/330 — 4 wired streams), Travel & Hospitality (BP-380 — 3 wired
streams).

Re-emits each BP1 file with BP1 + BP2 + BP3 levels.
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


# Schema: BP1 dict (id, name, industry, description, framework_label, realizes,
#                   children: [{id, name, description, realizes, children: [(id, name, desc, realizes)]}])
TREE: dict[str, dict] = {}

# ============ Public Sector (BP-340/350/360) ============

TREE["BP-340"] = {
    "id": "BP-340", "name": "Manage Public Service and Benefit Delivery",
    "industry": "Public Sector & Government",
    "description": "Run citizen-facing public service delivery: identity and records, benefit and entitlement programs, licensing, immigration, and civil registration.",
    "framework_label": "FEAF Business Reference Model — Service Delivery domain",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-340.10", "name": "Manage Citizen Identity and Records",
         "description": "Issue and maintain citizen identity, civil registration records, and verifiable credentials.",
         "realizes": ["BC-610"], "children": [
            ("BP-340.10.10", "Issue Citizen Identity Credentials",
             "Issue national IDs, e-IDs, and verifiable credentials.", ["BC-610"]),
            ("BP-340.10.20", "Maintain Citizen Identity Registry",
             "Maintain authoritative identity registry; update demographics; manage identity proofing.", ["BC-610"]),
            ("BP-340.10.30", "Authenticate and Federate Identity",
             "Operate citizen-authentication services and federation across government services.", ["BC-620", "BC-610"]),
        ]},
        {"id": "BP-340.20", "name": "Manage Benefit and Entitlement Programs",
         "description": "Administer benefit and entitlement programs: eligibility, application, decision, payment, ongoing review.",
         "realizes": [], "children": [
            ("BP-340.20.10", "Configure Benefit Programs",
             "Define and maintain benefit-program rules, eligibility criteria, and payment schedules.", []),
            ("BP-340.20.20", "Process Benefit Applications",
             "Receive and process applications for benefits; collect supporting evidence.", []),
            ("BP-340.20.30", "Determine Benefit Eligibility",
             "Apply rules and evidence to determine benefit eligibility and entitlement amount.", []),
            ("BP-340.20.40", "Disburse Benefit Payments",
             "Calculate and disburse benefit payments to recipients.", ["BC-200"]),
            ("BP-340.20.50", "Manage Continuing Eligibility and Reviews",
             "Conduct periodic eligibility reviews; adjust entitlements based on changes in circumstance.", []),
        ]},
        {"id": "BP-340.30", "name": "Manage Licensing and Permitting",
         "description": "Operate licensing and permitting regimes: application intake, evaluation, issuance, renewal, enforcement.",
         "realizes": [], "children": [
            ("BP-340.30.10", "Receive Licensing/Permit Applications",
             "Receive applications across channels; perform initial completeness checks.", []),
            ("BP-340.30.20", "Evaluate Applications and Render Decisions",
             "Evaluate applications against statutory criteria; render licensing decisions.", []),
            ("BP-340.30.30", "Issue Licences and Permits",
             "Issue physical or digital licences and permits to approved applicants.", []),
            ("BP-340.30.40", "Manage Renewals and Modifications",
             "Process licence renewals, modifications, and conditional updates.", []),
        ]},
        {"id": "BP-340.40", "name": "Manage Visa and Immigration",
         "description": "Operate visa, asylum, immigration, and border admission processes.",
         "realizes": [], "children": [
            ("BP-340.40.10", "Process Visa Applications",
             "Receive and process visa applications including biometric capture.", []),
            ("BP-340.40.20", "Conduct Pre-Travel Authorisation",
             "Operate pre-travel authorisation systems (e.g. ESTA, ETIAS).", []),
            ("BP-340.40.30", "Manage Border Admission",
             "Inspect arrivals at ports of entry; render admission decisions.", []),
            ("BP-340.40.40", "Manage Immigration Status and Removal",
             "Maintain immigration-status records; process removals and returns.", []),
        ]},
        {"id": "BP-340.50", "name": "Manage Vital and Statutory Records",
         "description": "Maintain civil/vital records: births, deaths, marriages, statutory filings.",
         "realizes": ["BC-610"], "children": [
            ("BP-340.50.10", "Register Vital Events",
             "Register births, deaths, marriages, and equivalent vital events.", ["BC-610"]),
            ("BP-340.50.20", "Issue Vital-Records Certificates",
             "Issue certified copies of vital records; manage authentication and apostille.", []),
            ("BP-340.50.30", "Maintain Statutory Public Registers",
             "Maintain public registers required by statute; manage controlled disclosure.", ["BC-610"]),
        ]},
    ],
}

TREE["BP-350"] = {
    "id": "BP-350", "name": "Manage Public Sector Revenue and Compliance",
    "industry": "Public Sector & Government",
    "description": "Operate public-sector revenue collection and regulatory compliance: tax filing and collection, customs and trade, regulatory enforcement, judicial / statutory filings.",
    "framework_label": "FEAF — Tax Administration / Regulatory & Compliance domains",
    "realizes": ["BC-220", "BC-130"],
    "children": [
        {"id": "BP-350.10", "name": "Manage Tax Filing and Collection",
         "description": "Receive tax returns, assess liabilities, collect tax, manage refunds and disputes.",
         "realizes": ["BC-220"], "children": [
            ("BP-350.10.10", "Register Taxpayers and Assign IDs",
             "Register taxpayers; assign tax identification numbers; manage taxpayer master.", ["BC-220"]),
            ("BP-350.10.20", "Process Tax Returns",
             "Receive, validate, and process tax returns across tax types.", ["BC-220"]),
            ("BP-350.10.30", "Assess and Collect Tax",
             "Assess tax liabilities; collect payments; manage refunds and credits.", ["BC-220", "BC-200"]),
            ("BP-350.10.40", "Manage Tax Disputes and Appeals",
             "Process taxpayer disputes, objections, and appeals.", ["BC-220", "BC-150"]),
        ]},
        {"id": "BP-350.20", "name": "Manage Customs and Trade Administration",
         "description": "Operate customs entry, duty assessment, trade-compliance, and border-control processes.",
         "realizes": ["BC-130"], "children": [
            ("BP-350.20.10", "Process Customs Declarations",
             "Receive and process customs declarations for import/export.", ["BC-130"]),
            ("BP-350.20.20", "Assess and Collect Duties and VAT",
             "Assess customs duties, excise, and VAT; collect at border.", ["BC-220", "BC-130"]),
            ("BP-350.20.30", "Manage Trade Compliance and Sanctions",
             "Manage export controls, sanctions screening, and trade-compliance enforcement.", ["BC-130"]),
        ]},
        {"id": "BP-350.30", "name": "Manage Regulatory Enforcement and Investigations",
         "description": "Conduct regulatory inspections and investigations; impose and recover penalties.",
         "realizes": ["BC-130", "BC-150"], "children": [
            ("BP-350.30.10", "Plan and Conduct Regulatory Inspections",
             "Plan inspection programs; conduct site or document inspections.", ["BC-130"]),
            ("BP-350.30.20", "Conduct Investigations and Cases",
             "Open and conduct regulatory investigations and cases.", ["BC-130", "BC-150"]),
            ("BP-350.30.30", "Impose and Collect Penalties",
             "Impose regulatory penalties; manage collection and enforcement.", ["BC-130", "BC-200"]),
        ]},
        {"id": "BP-350.40", "name": "Manage Court and Statutory Filings",
         "description": "Receive, docket, and process court filings and statutory submissions; manage case dispositions.",
         "realizes": ["BC-150"], "children": [
            ("BP-350.40.10", "Receive and Docket Court Filings",
             "Receive court filings; assign case numbers; docket events.", ["BC-150"]),
            ("BP-350.40.20", "Manage Court Hearings and Trials",
             "Schedule and manage court hearings, trials, and dispositions.", ["BC-150"]),
            ("BP-350.40.30", "Maintain Court and Public Records",
             "Maintain official court records; manage public access and sealing orders.", ["BC-610", "BC-150"]),
        ]},
    ],
}

TREE["BP-360"] = {
    "id": "BP-360", "name": "Manage Public Sector Programs and Funding",
    "industry": "Public Sector & Government",
    "description": "Operate public-sector procurement and program funding: government procurement under FAR / EU rules, program funding administration, grants and awards, public-sector reporting.",
    "framework_label": "FEAF — Mission Support / Resource Management; FAR / EU procurement",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-360.10", "name": "Manage Public-Sector Procurement",
         "description": "Plan, solicit, award, and administer government contracts under FAR / EU procurement rules.",
         "realizes": ["BC-500"], "children": [
            ("BP-360.10.10", "Plan Acquisitions and Conduct Market Research",
             "Conduct acquisition planning and market research per FAR Part 7 / EU equivalents.", ["BC-500"]),
            ("BP-360.10.20", "Publish Solicitations",
             "Draft and publish RFPs, RFQs, and IFBs.", ["BC-500"]),
            ("BP-360.10.30", "Evaluate Bids and Award Contracts",
             "Evaluate bids; conduct source selection; award contracts.", ["BC-500"]),
            ("BP-360.10.40", "Administer Public-Sector Contracts",
             "Administer contracts: modifications, deliverable acceptance, closeout.", ["BC-500", "BC-150"]),
        ]},
        {"id": "BP-360.20", "name": "Manage Program Funding and Appropriations",
         "description": "Administer appropriations, allotments, and obligations against authorised programs.",
         "realizes": ["BC-200", "BC-230"], "children": [
            ("BP-360.20.10", "Manage Appropriations and Allotments",
             "Receive and allocate appropriations to programs and budget lines.", ["BC-230"]),
            ("BP-360.20.20", "Manage Obligations and Outlays",
             "Record obligations against appropriations; track outlays.", ["BC-200"]),
            ("BP-360.20.30", "Manage Apportionment and Reprogramming",
             "Manage apportionment splits and reprogramming requests.", ["BC-230"]),
        ]},
        {"id": "BP-360.30", "name": "Manage Grants and Awards",
         "description": "Award and administer grants and cooperative agreements; manage grantee compliance and reporting.",
         "realizes": [], "children": [
            ("BP-360.30.10", "Develop Grant Programs and Notices",
             "Design grant programs and publish funding-opportunity announcements.", []),
            ("BP-360.30.20", "Process Grant Applications and Awards",
             "Receive grant applications; evaluate and award grants.", []),
            ("BP-360.30.30", "Monitor Grantee Performance and Audit",
             "Monitor grantee performance; conduct single-audit or equivalent oversight.", ["BC-140"]),
        ]},
        {"id": "BP-360.40", "name": "Manage Public-Sector Performance and Statistical Reporting",
         "description": "Produce statutory performance, statistical, and accountability reports per IPSAS / GFSM standards.",
         "realizes": ["BC-130"], "children": [
            ("BP-360.40.10", "Produce IPSAS Financial Statements",
             "Produce public-sector financial statements per IPSAS or equivalent.", ["BC-200"]),
            ("BP-360.40.20", "Produce GFSM Statistical Reports",
             "Produce IMF GFSM statistical reports and OECD equivalents.", ["BC-130"]),
            ("BP-360.40.30", "Produce Mission/Performance Accountability Reports",
             "Produce statutory mission and performance accountability reports.", ["BC-130"]),
        ]},
    ],
}

# ============ Real Estate (BP-320/330) ============

TREE["BP-320"] = {
    "id": "BP-320", "name": "Operate Real Estate Asset and Property Management",
    "industry": "Real Estate",
    "description": "Run real-estate-specific asset and property operations: portfolio management, tenant lease lifecycle, day-to-day property/facility management, capital projects, disposition.",
    "framework_label": "Real Estate asset and property reference (OSCRE IDM-aligned)",
    "realizes": ["BC-710"],
    "children": [
        {"id": "BP-320.10", "name": "Manage Real Estate Portfolio",
         "description": "Plan and govern the portfolio of properties: asset strategy, hold/sell decisions, performance reporting.",
         "realizes": ["BC-710"], "children": [
            ("BP-320.10.10", "Develop Portfolio Strategy",
             "Set the multi-year portfolio strategy: asset class mix, geographic mix, hold/sell criteria.", ["BC-710"]),
            ("BP-320.10.20", "Conduct Asset-Level Hold/Sell Reviews",
             "Periodically review each asset for hold, sell, refurbish, or repurpose decisions.", ["BC-710"]),
            ("BP-320.10.30", "Produce Portfolio Performance Reporting",
             "Produce portfolio performance reports for owners, partners, and lenders.", ["BC-230"]),
        ]},
        {"id": "BP-320.20", "name": "Manage Tenant Lease Lifecycle",
         "description": "Originate, abstract, administer, and renew tenant leases; manage lease accounting and CAM reconciliation.",
         "realizes": [], "children": [
            ("BP-320.20.10", "Originate and Negotiate Tenant Leases",
             "Source tenants; negotiate terms; execute new leases.", []),
            ("BP-320.20.20", "Abstract and Administer Leases",
             "Abstract lease terms; administer rent escalations, renewals, and options.", []),
            ("BP-320.20.30", "Reconcile CAM, Insurance, and Tax Pass-Throughs",
             "Reconcile common-area maintenance, insurance, and tax pass-throughs annually.", []),
            ("BP-320.20.40", "Manage Lease Renewals and Expirations",
             "Manage lease renewals, terminations, and tenant turnover.", []),
        ]},
        {"id": "BP-320.30", "name": "Operate Property Management and Facility Operations",
         "description": "Run day-to-day property operations: tenant services, on-site management, vendor coordination, common-area facility management.",
         "realizes": ["BC-700"], "children": [
            ("BP-320.30.10", "Operate On-Site Property Management",
             "Run on-site property management, including tenant relations and inspections.", ["BC-700"]),
            ("BP-320.30.20", "Coordinate Property Vendors and Service Contracts",
             "Source and manage property vendors (cleaning, security, landscaping, lift maintenance).", ["BC-510"]),
            ("BP-320.30.30", "Manage Tenant Service Requests",
             "Receive and resolve tenant service requests and maintenance tickets.", ["BC-430"]),
        ]},
        {"id": "BP-320.40", "name": "Manage Property Capital Projects",
         "description": "Plan and deliver capital projects on owned property: tenant improvements, repositioning, refurbishment.",
         "realizes": ["BC-700", "BC-900"], "children": [
            ("BP-320.40.10", "Plan and Approve Property Capital Projects",
             "Plan tenant improvements, repositioning, and major refurbishment projects.", ["BC-900"]),
            ("BP-320.40.20", "Execute Property Capital Projects",
             "Execute property capital projects across design, construction, and handover.", ["BC-700", "BC-900"]),
        ]},
        {"id": "BP-320.50", "name": "Manage Real Estate Disposition",
         "description": "Position, market, and dispose of property assets; manage sale and post-closing transition.",
         "realizes": ["BC-710"], "children": [
            ("BP-320.50.10", "Position and Market Properties for Sale",
             "Prepare properties for sale; develop sale offerings; engage brokers and investors.", ["BC-710", "BC-410"]),
            ("BP-320.50.20", "Negotiate and Close Property Sales",
             "Negotiate sale terms; execute closing and post-closing transition.", ["BC-710"]),
        ]},
    ],
}

TREE["BP-330"] = {
    "id": "BP-330", "name": "Operate Real Estate Brokerage and Capital Markets",
    "industry": "Real Estate",
    "description": "Run real estate brokerage, transaction management, and capital-markets operations: listing and brokerage, acquisition/disposition advisory, real estate fund management, valuation and appraisal.",
    "framework_label": "Real Estate brokerage / capital markets reference (RESO Data Dictionary, IPMS, RICS)",
    "realizes": ["BC-710"],
    "children": [
        {"id": "BP-330.10", "name": "Manage Real Estate Listing and Brokerage",
         "description": "Operate residential and commercial brokerage: listing agreements, MLS exposure, showings, offer negotiation.",
         "realizes": ["BC-410"], "children": [
            ("BP-330.10.10", "Win Listing Agreements",
             "Pursue and win listing agreements with property owners.", ["BC-410"]),
            ("BP-330.10.20", "Market Listings",
             "Set up and market listings across MLS, portals, and direct channels.", ["BC-410", "BC-400"]),
            ("BP-330.10.30", "Coordinate Showings and Offers",
             "Coordinate property showings; receive and present offers to seller.", []),
            ("BP-330.10.40", "Close Brokerage Transactions and Manage Commission",
             "Coordinate closing; manage commission settlement and disclosures.", ["BC-200"]),
        ]},
        {"id": "BP-330.20", "name": "Manage Real Estate Acquisition and Disposition Advisory",
         "description": "Advise clients on acquisitions and dispositions: target identification, underwriting, due diligence, deal closing.",
         "realizes": ["BC-710"], "children": [
            ("BP-330.20.10", "Source and Underwrite Deals",
             "Source acquisition opportunities; underwrite to investment criteria.", ["BC-710", "BC-230"]),
            ("BP-330.20.20", "Conduct Due Diligence",
             "Conduct legal, financial, environmental, and physical due diligence.", ["BC-710", "BC-150"]),
            ("BP-330.20.30", "Structure and Close Real Estate Transactions",
             "Structure deals; negotiate and close acquisition or disposition transactions.", ["BC-710"]),
        ]},
        {"id": "BP-330.30", "name": "Manage Real Estate Capital Markets and Fund Management",
         "description": "Operate real-estate fund and investment management: capital raising, fund administration, asset/portfolio reporting.",
         "realizes": ["BC-210"], "children": [
            ("BP-330.30.10", "Form and Capitalise Real Estate Vehicles",
             "Establish funds, joint ventures, and SPVs; manage capital commitments and calls.", ["BC-210"]),
            ("BP-330.30.20", "Manage Fund Accounting and NAV",
             "Calculate fund NAV; manage fund-level expenses and accruals.", ["BC-200", "BC-210"]),
            ("BP-330.30.30", "Produce LP Reporting and Distributions",
             "Produce limited-partner reports; manage distributions and waterfall calculations.", ["BC-240"]),
        ]},
        {"id": "BP-330.40", "name": "Manage Real Estate Valuation and Appraisal",
         "description": "Conduct property valuation and appraisal under IPMS / RICS / USPAP standards.",
         "realizes": [], "children": [
            ("BP-330.40.10", "Conduct Property Valuations",
             "Conduct property valuations using income, sales-comparison, and cost approaches.", []),
            ("BP-330.40.20", "Produce Appraisal Reports",
             "Produce appraisal reports per RICS / USPAP / IVS standards.", []),
        ]},
    ],
}

# ============ Travel & Hospitality (BP-380) ============

TREE["BP-380"] = {
    "id": "BP-380", "name": "Operate Hospitality Properties and Distribution",
    "industry": "Travel & Hospitality",
    "description": "Run hospitality-specific operations: reservations and inventory, guest experience, distribution and channel, loyalty, revenue management, property operations.",
    "framework_label": "AHLA USALI 11th Ed + HEDNA + OpenTravel + HTNG reference architecture",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-380.10", "name": "Manage Reservations and Inventory",
         "description": "Manage room, table, and event-space inventory; receive and confirm reservations across channels.",
         "realizes": [], "children": [
            ("BP-380.10.10", "Manage Inventory Allotments and Restrictions",
             "Manage room/table/event-space inventory, allotments, and stay restrictions.", []),
            ("BP-380.10.20", "Process Reservations and Modifications",
             "Receive reservations across channels; process changes, cancellations, and waitlist.", []),
            ("BP-380.10.30", "Manage Group Blocks and Allocations",
             "Manage group blocks for events, conferences, and tour operators.", []),
        ]},
        {"id": "BP-380.20", "name": "Manage Guest Experience and Stay",
         "description": "Operate the guest journey from arrival through stay to departure.",
         "realizes": ["BC-430"], "children": [
            ("BP-380.20.10", "Manage Pre-Arrival and Check-In",
             "Conduct pre-arrival communication; manage check-in, ID verification, and key issuance.", ["BC-430"]),
            ("BP-380.20.20", "Service In-Stay Requests",
             "Manage in-stay guest requests, housekeeping requests, and amenity orders.", ["BC-430"]),
            ("BP-380.20.30", "Manage Check-Out and Folio Settlement",
             "Manage check-out, folio review, and final charge settlement.", ["BC-430", "BC-200"]),
            ("BP-380.20.40", "Resolve Guest Complaints and Service Recovery",
             "Resolve guest complaints with service-recovery protocols.", ["BC-430"]),
        ]},
        {"id": "BP-380.30", "name": "Manage Distribution and Channel",
         "description": "Operate distribution across direct, OTA, GDS, and metasearch channels; manage rate parity and content.",
         "realizes": ["BC-410"], "children": [
            ("BP-380.30.10", "Connect and Manage Distribution Channels",
             "Connect to OTA, GDS, metasearch, and wholesaler channels via channel manager.", ["BC-410"]),
            ("BP-380.30.20", "Manage Rate Parity and Content Distribution",
             "Maintain rate parity across channels; distribute content (descriptions, photos, amenities).", ["BC-440"]),
            ("BP-380.30.30", "Manage Direct Booking Channels",
             "Operate brand.com, mobile app, and call-centre booking channels.", ["BC-410", "BC-600"]),
        ]},
        {"id": "BP-380.40", "name": "Manage Loyalty Programs",
         "description": "Operate guest loyalty programs across enrolment, accrual, redemption, and partner exchange.",
         "realizes": ["BC-420"], "children": [
            ("BP-380.40.10", "Enrol and Tier Loyalty Members",
             "Enrol guests; manage tier qualification and re-qualification.", ["BC-420"]),
            ("BP-380.40.20", "Process Loyalty Accruals and Redemptions",
             "Process points/nights accruals and redemptions across the program.", []),
            ("BP-380.40.30", "Manage Loyalty Partner Exchange",
             "Manage loyalty exchange with airline, credit-card, and other program partners.", ["BC-510"]),
        ]},
        {"id": "BP-380.50", "name": "Manage Revenue Management and Yield",
         "description": "Forecast demand and optimise pricing, length-of-stay controls, and channel mix.",
         "realizes": ["BC-440"], "children": [
            ("BP-380.50.10", "Forecast Demand and Set Rate Strategy",
             "Forecast demand by segment, channel, and date; set rate-management strategy.", ["BC-440"]),
            ("BP-380.50.20", "Operate Yield and Pricing Controls",
             "Operate dynamic pricing, length-of-stay controls, and channel-mix optimisation.", ["BC-440"]),
        ]},
        {"id": "BP-380.60", "name": "Operate Property Operations",
         "description": "Operate rooms, food & beverage, events, housekeeping, property maintenance.",
         "realizes": ["BC-700"], "children": [
            ("BP-380.60.10", "Operate Rooms Division",
             "Operate front office, housekeeping, and rooms division.", ["BC-700"]),
            ("BP-380.60.20", "Operate F&B and Banqueting",
             "Operate restaurants, bars, banqueting, and in-room dining services.", []),
            ("BP-380.60.30", "Operate Events and Group Services",
             "Operate group events: meeting setup, AV, banquet service, group dining.", []),
            ("BP-380.60.40", "Operate Property Engineering and Maintenance",
             "Operate property engineering, preventive and corrective maintenance.", ["BC-700"]),
        ]},
    ],
}


# Append additional BP3 trees (Insurance, Defense, Utilities, Education)
TREE["BP-150"] = {
    "id": "BP-150", "name": "Operate Insurance Underwriting, Policy, and Claims",
    "industry": "Insurance",
    "description": "Run insurance-specific operations: product filing, underwriting, policy administration, claims handling, reinsurance, actuarial reserving, distribution.",
    "framework_label": "BIAN Insurance reference + ACORD Process Model (Distribution / UW / Policy / Claims / Reinsurance)",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-150.10", "name": "Manage Product Filing and Approval", "description": "Develop, file, and obtain regulatory approval for insurance products and rate plans.", "realizes": [], "children": [
            ("BP-150.10.10", "Develop Insurance Product Concepts", "Develop insurance product concepts; conduct actuarial pricing analysis.", []),
            ("BP-150.10.20", "File Products with Regulators", "Prepare regulatory filings (rate, form, rule); manage filing process.", ["BC-130"]),
            ("BP-150.10.30", "Manage Product Approvals and Re-Filings", "Track filing decisions; manage re-filings and product changes.", ["BC-130"]),
        ]},
        {"id": "BP-150.20", "name": "Manage Underwriting Operations", "description": "Risk-assess and price insurance applications; bind cover.", "realizes": [], "children": [
            ("BP-150.20.10", "Receive and Triage Submissions", "Receive submissions from brokers and direct channels; triage for underwriter assignment.", []),
            ("BP-150.20.20", "Conduct Risk Assessment and Pricing", "Conduct risk assessment; apply rating engines; price the risk.", []),
            ("BP-150.20.30", "Render Underwriting Decisions", "Underwrite to bind authority limits; decline, refer, or quote.", []),
            ("BP-150.20.40", "Bind and Issue Quotes", "Issue quotes; bind cover when accepted.", []),
        ]},
        {"id": "BP-150.30", "name": "Manage Policy Administration", "description": "Administer policies across the lifecycle: issuance, endorsements, renewals, cancellations.", "realizes": [], "children": [
            ("BP-150.30.10", "Issue Policies and Documents", "Issue policy documents, schedules, and certificates.", []),
            ("BP-150.30.20", "Process Endorsements and Mid-Term Changes", "Process endorsements, mid-term changes, and notifications.", []),
            ("BP-150.30.30", "Manage Renewals and Cancellations", "Manage renewal cycles, non-renewals, and cancellations.", []),
            ("BP-150.30.40", "Manage Premium Billing and Collection", "Bill and collect premiums; manage premium financing.", ["BC-200"]),
        ]},
        {"id": "BP-150.40", "name": "Manage Claims Operations", "description": "Receive, investigate, adjudicate, and pay insurance claims, including fraud and recovery.", "realizes": [], "children": [
            ("BP-150.40.10", "Receive and Triage FNOL", "Receive first notice of loss; triage and assign claim.", []),
            ("BP-150.40.20", "Investigate and Adjust Claims", "Investigate claims; engage adjusters and experts; assess coverage and liability.", []),
            ("BP-150.40.30", "Estimate Reserves and Approve Settlement", "Estimate claim reserves; approve and pay settlement.", ["BC-200"]),
            ("BP-150.40.40", "Detect and Investigate Claims Fraud", "Apply fraud-detection analytics; investigate suspicious claims; refer to SIU.", ["BC-130"]),
            ("BP-150.40.50", "Manage Subrogation and Recoveries", "Pursue subrogation and salvage recoveries from third parties.", []),
        ]},
        {"id": "BP-150.50", "name": "Manage Reinsurance Operations", "description": "Cede risk to reinsurers; administer reinsurance treaties and recoveries.", "realizes": [], "children": [
            ("BP-150.50.10", "Negotiate and Place Reinsurance Treaties", "Place treaty and facultative reinsurance with reinsurers.", []),
            ("BP-150.50.20", "Cede Risk and Manage Bordereaux", "Cede underwritten risk per treaty terms; produce bordereaux to reinsurers.", []),
            ("BP-150.50.30", "Manage Reinsurance Claims Recoveries", "Submit and recover reinsurance claims from treaty reinsurers.", []),
        ]},
        {"id": "BP-150.60", "name": "Manage Actuarial Reserving and Capital", "description": "Calculate insurance reserves, capital requirements, and produce statutory actuarial reports.", "realizes": ["BC-200"], "children": [
            ("BP-150.60.10", "Calculate IBNR and Loss Reserves", "Calculate IBNR and loss reserves using actuarial methods.", ["BC-200"]),
            ("BP-150.60.20", "Calculate Capital Requirements", "Calculate Solvency II / NAIC RBC / IFRS 17 capital and reserves.", ["BC-200"]),
            ("BP-150.60.30", "Produce Statutory Actuarial Reports", "Produce statutory actuarial reports including ORSA / opinion / external SAO.", ["BC-200", "BC-130"]),
        ]},
        {"id": "BP-150.70", "name": "Manage Insurance Distribution and Producer Network", "description": "Manage broker, agent, MGA, and direct distribution channels.", "realizes": ["BC-410", "BC-510"], "children": [
            ("BP-150.70.10", "Onboard and License Producers", "Onboard agents, brokers, and MGAs; verify licensing.", ["BC-510"]),
            ("BP-150.70.20", "Manage Producer Commissions", "Calculate and pay producer commissions and bonuses.", ["BC-510", "BC-200"]),
            ("BP-150.70.30", "Monitor Producer Performance", "Monitor producer performance, loss ratios, and compliance.", ["BC-510"]),
        ]},
    ],
}

TREE["BP-230"] = {
    "id": "BP-230", "name": "Manage Aerospace and Defense Programs",
    "industry": "Defense & Aerospace",
    "description": "Run aerospace and defense programs across the acquisition lifecycle: capture, contract, develop, deliver, sustain, and dispose, including export-control and configuration management.",
    "framework_label": "Aerospace and Defense PCF v7.2 (IBM-donated) + AS9100 + DoD acquisition lifecycle",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-230.10", "name": "Manage Capture and Bid", "description": "Pursue defense and aerospace opportunities: bid/no-bid, capture planning, proposal development.", "realizes": ["BC-410"], "children": [
            ("BP-230.10.10", "Conduct Capture Planning", "Conduct customer intelligence and capture planning for major opportunities.", ["BC-410"]),
            ("BP-230.10.20", "Develop and Submit Proposals", "Develop technical, management, and cost proposals; submit to customer.", ["BC-410"]),
            ("BP-230.10.30", "Manage Teaming and Subcontracting", "Establish teaming agreements; manage subcontractor solicitation and selection.", ["BC-510"]),
        ]},
        {"id": "BP-230.20", "name": "Manage Program Contract and Earned Value", "description": "Manage the program contract through award, change, modifications, and earned-value reporting.", "realizes": ["BC-150", "BC-900"], "children": [
            ("BP-230.20.10", "Negotiate and Award Contract", "Negotiate contract terms; award and baseline.", ["BC-150"]),
            ("BP-230.20.20", "Operate Earned Value Management System", "Operate EVMS per ANSI/EIA-748; report EAC, CPI, SPI to customer.", ["BC-900"]),
            ("BP-230.20.30", "Manage Contract Modifications and Change", "Process contract modifications, REAs, and equitable adjustments.", ["BC-150"]),
        ]},
        {"id": "BP-230.30", "name": "Perform Mission Systems Engineering", "description": "Perform systems engineering for defense and aerospace mission systems, including verification and validation.", "realizes": ["BC-810"], "children": [
            ("BP-230.30.10", "Develop System Requirements", "Decompose customer requirements into system and subsystem requirements.", ["BC-810"]),
            ("BP-230.30.20", "Design and Integrate Mission Systems", "Design and integrate mission-system architectures across hardware and software.", ["BC-810"]),
            ("BP-230.30.30", "Verify and Validate Mission Systems", "Conduct V&V activities including DT&E and OT&E.", ["BC-810", "BC-720"]),
        ]},
        {"id": "BP-230.40", "name": "Manage Configuration and Technical Data Package", "description": "Maintain configuration of platforms and systems; manage the technical data package across the lifecycle.", "realizes": ["BC-820"], "children": [
            ("BP-230.40.10", "Establish Configuration Baselines", "Establish functional, allocated, and product baselines per MIL-HDBK-61.", ["BC-820"]),
            ("BP-230.40.20", "Manage Engineering Change Proposals", "Process ECPs; manage CCB review and incorporation.", ["BC-820", "BC-910"]),
            ("BP-230.40.30", "Maintain Technical Data Package", "Maintain TDP per ASME Y14.100; manage data rights and deliverables.", ["BC-820"]),
        ]},
        {"id": "BP-230.50", "name": "Manage Export Controls and Security", "description": "Manage ITAR / EAR / EU dual-use export controls and program security.", "realizes": ["BC-150", "BC-620"], "children": [
            ("BP-230.50.10", "Classify and License Exports", "Classify items per USML/CCL; obtain licences for exports/transfers.", ["BC-150"]),
            ("BP-230.50.20", "Manage Foreign Disclosure", "Manage foreign-disclosure decisions and Technology Control Plans.", ["BC-150", "BC-620"]),
            ("BP-230.50.30", "Operate Industrial Security and Classified Programs", "Operate industrial security per NISPOM; manage classified-program security.", ["BC-620"]),
        ]},
        {"id": "BP-230.60", "name": "Sustain Defense Systems", "description": "Sustain in-service defense and aerospace systems: depot maintenance, overhaul, modifications, obsolescence.", "realizes": ["BC-700"], "children": [
            ("BP-230.60.10", "Operate Depot and Field Maintenance", "Operate depot-level and field-level maintenance for in-service systems.", ["BC-700"]),
            ("BP-230.60.20", "Manage Spares and Repair Pool", "Manage spares pool; coordinate repair-and-return cycles.", ["BC-530"]),
            ("BP-230.60.30", "Manage Diminishing Manufacturing Sources", "Identify DMSMS risks; manage obsolescence and bridge buys.", ["BC-820"]),
        ]},
        {"id": "BP-230.70", "name": "Manage Disposal and Demilitarisation", "description": "Demilitarise and dispose of defense materiel at end-of-life under regulatory and security controls.", "realizes": ["BC-740"], "children": [
            ("BP-230.70.10", "Demilitarise End-of-Life Materiel", "Demilitarise platforms and weapons under DoD/MoD demil standards.", ["BC-740"]),
            ("BP-230.70.20", "Dispose of Hazardous and Classified Materiel", "Dispose of hazardous and classified materiel per regulations.", ["BC-730", "BC-620"]),
        ]},
    ],
}

TREE["BP-260"] = {
    "id": "BP-260", "name": "Operate Energy and Water Asset Operations",
    "industry": "Power & Water Utilities",
    "description": "Operate utility production and network assets: generation (electric), production and treatment (water), transmission, distribution, storage.",
    "framework_label": "APQC Utilities PCF v7.2 — Asset operations categories",
    "realizes": ["BC-700"],
    "children": [
        {"id": "BP-260.10", "name": "Operate Electricity Generation", "description": "Operate electricity generation assets across thermal, hydro, nuclear, renewable.", "realizes": ["BC-700", "BC-720"], "children": [
            ("BP-260.10.10", "Schedule and Dispatch Generation", "Schedule generation against day-ahead and intraday markets; dispatch to system operator instructions.", ["BC-700"]),
            ("BP-260.10.20", "Operate Generation Plant", "Operate thermal, hydro, nuclear, and renewable generation plants safely and efficiently.", ["BC-700", "BC-720"]),
            ("BP-260.10.30", "Manage Generation Performance and Outages", "Monitor performance; manage planned and forced outages.", ["BC-700", "BC-160"]),
        ]},
        {"id": "BP-260.20", "name": "Operate Water Production and Treatment", "description": "Operate water abstraction, treatment, and wastewater treatment assets.", "realizes": ["BC-700", "BC-720", "BC-730"], "children": [
            ("BP-260.20.10", "Abstract Raw Water", "Abstract raw water from sources per licence and environmental conditions.", ["BC-730"]),
            ("BP-260.20.20", "Treat Drinking Water", "Treat raw water to drinking-water quality standards.", ["BC-720"]),
            ("BP-260.20.30", "Treat Wastewater", "Operate wastewater treatment to effluent quality standards.", ["BC-730"]),
            ("BP-260.20.40", "Conduct Water Quality Assurance", "Sample and test water quality across the production chain; report to regulators.", ["BC-720"]),
        ]},
        {"id": "BP-260.30", "name": "Operate Transmission and Distribution Networks", "description": "Operate electricity T&D networks (or water mains and reticulation).", "realizes": ["BC-700"], "children": [
            ("BP-260.30.10", "Operate Transmission Networks", "Operate high-voltage transmission networks and substations.", ["BC-700"]),
            ("BP-260.30.20", "Operate Distribution Networks", "Operate distribution networks and feeders to customer connections.", ["BC-700"]),
            ("BP-260.30.30", "Balance and Dispatch the System", "Balance supply and demand in real time; dispatch system resources.", ["BC-700"]),
        ]},
        {"id": "BP-260.40", "name": "Manage Outages, Restoration, and Emergency Response", "description": "Detect and respond to outages and emergencies; coordinate restoration crews and customer comms.", "realizes": ["BC-160", "BC-700"], "children": [
            ("BP-260.40.10", "Detect and Localise Outages", "Detect outages via SCADA, AMI, and customer reports; localise faults.", ["BC-700"]),
            ("BP-260.40.20", "Dispatch and Restore", "Dispatch crews; restore service per operating procedures.", ["BC-700"]),
            ("BP-260.40.30", "Manage Emergency and Storm Response", "Activate emergency response for storms, ice, wildfire, and equivalent events.", ["BC-160"]),
        ]},
        {"id": "BP-260.50", "name": "Manage Energy Storage and Distributed Energy Resources", "description": "Operate energy storage and integrate DER and demand response.", "realizes": ["BC-700", "BC-600"], "children": [
            ("BP-260.50.10", "Operate Energy Storage", "Operate utility-scale and distributed energy-storage assets.", ["BC-700"]),
            ("BP-260.50.20", "Integrate Distributed Energy Resources", "Integrate DER (rooftop solar, EV chargers) into operations.", ["BC-700", "BC-600"]),
            ("BP-260.50.30", "Manage Demand Response Programs", "Manage demand-response programs across customer segments.", ["BC-700"]),
        ]},
        {"id": "BP-260.60", "name": "Manage Network Planning and Capital Investment", "description": "Plan utility-network capital investment under regulatory price-control and reliability frameworks.", "realizes": ["BC-230", "BC-130"], "children": [
            ("BP-260.60.10", "Develop Network Investment Plans", "Develop multi-year network investment plans; align to price-control submissions.", ["BC-230"]),
            ("BP-260.60.20", "Conduct Reliability and Resilience Planning", "Plan reliability and resilience investments; meet NERC/CIGRE/equivalent standards.", ["BC-160"]),
        ]},
    ],
}

TREE["BP-270"] = {
    "id": "BP-270", "name": "Manage Utility Customer and Regulatory Operations",
    "industry": "Power & Water Utilities",
    "description": "Run utility-specific customer operations (metering, billing, supply switching, hardship support) and regulatory operations (price control, code compliance, statutory reporting).",
    "framework_label": "APQC Utilities PCF v7.2 — Customer and regulatory categories",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-270.10", "name": "Manage Customer Metering and Meter Data", "description": "Operate the meter estate; collect, validate, estimate, edit meter data.", "realizes": ["BC-610"], "children": [
            ("BP-270.10.10", "Operate Meter Estate", "Operate smart and non-smart meter estate; manage meter exchange.", ["BC-610"]),
            ("BP-270.10.20", "Collect and Validate Meter Data", "Collect AMI/AMR readings; validate, estimate, and edit (VEE) meter data.", ["BC-610"]),
            ("BP-270.10.30", "Provide Meter Data to Market", "Provide meter data to retailers, settlement bodies, and customers.", ["BC-610"]),
        ]},
        {"id": "BP-270.20", "name": "Operate Utility Billing and Revenue Collection", "description": "Calculate utility bills, present bills, run dunning, and manage collections and disconnection.", "realizes": ["BC-200"], "children": [
            ("BP-270.20.10", "Calculate Utility Bills", "Calculate utility bills using tariffs, meter data, and prepayment top-up where applicable.", ["BC-200"]),
            ("BP-270.20.20", "Present Bills and Manage Inquiries", "Present bills across channels; resolve billing inquiries and disputes.", ["BC-430", "BC-200"]),
            ("BP-270.20.30", "Manage Collections and Disconnection", "Run dunning and collections; manage disconnection and reconnection per regulations.", ["BC-200"]),
        ]},
        {"id": "BP-270.30", "name": "Manage Supply Switching and Customer Onboarding", "description": "Manage supply-point onboarding, switching, and tariff changes per market codes.", "realizes": ["BC-420", "BC-430"], "children": [
            ("BP-270.30.10", "Manage Customer Switching", "Manage customer switching between retailers per market codes.", ["BC-420"]),
            ("BP-270.30.20", "Operate Supply-Point Onboarding", "Onboard new connections; manage move-in/move-out events.", ["BC-430"]),
        ]},
        {"id": "BP-270.40", "name": "Manage Vulnerable Customer and Hardship Programs", "description": "Identify and support vulnerable customers and customers in hardship per regulatory obligations.", "realizes": ["BC-430", "BC-130"], "children": [
            ("BP-270.40.10", "Identify and Register Vulnerable Customers", "Identify and register vulnerable customers per regulatory definitions.", ["BC-430", "BC-130"]),
            ("BP-270.40.20", "Operate Hardship Programs", "Operate payment plans, hardship grants, and energy-efficiency programs for hardship customers.", ["BC-430"]),
        ]},
        {"id": "BP-270.50", "name": "Manage Regulatory Reporting and Price-Control Submissions", "description": "Prepare regulatory rate filings, performance reports, and price-control submissions.", "realizes": ["BC-130", "BC-240"], "children": [
            ("BP-270.50.10", "Prepare Price-Control Submissions", "Prepare RIIO / equivalent price-control submissions to economic regulators.", ["BC-130", "BC-240"]),
            ("BP-270.50.20", "Produce Regulatory Performance Reports", "Produce regulatory performance reports against published targets.", ["BC-130"]),
            ("BP-270.50.30", "Manage Regulatory Inquiries and Audits", "Respond to regulatory inquiries and audits; manage remediation.", ["BC-130", "BC-140"]),
        ]},
    ],
}

TREE["BP-240"] = {
    "id": "BP-240", "name": "Manage Student Lifecycle",
    "industry": "Education",
    "description": "Run the end-to-end student lifecycle from prospective recruitment through admissions, enrolment, learning delivery, assessment, graduation, alumni engagement.",
    "framework_label": "Education PCF v7.2.1 — Student lifecycle categories",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-240.10", "name": "Recruit and Admit Students", "description": "Recruit prospective students and process admissions, including selection and offer-acceptance.", "realizes": [], "children": [
            ("BP-240.10.10", "Conduct Outreach and Recruitment", "Conduct outreach campaigns and recruitment events.", ["BC-400"]),
            ("BP-240.10.20", "Process Applications and Selection", "Receive applications; conduct selection and admissions decisions.", []),
            ("BP-240.10.30", "Issue Offers and Manage Acceptance", "Issue offers; manage acceptance, deferral, and rejection.", []),
        ]},
        {"id": "BP-240.20", "name": "Enrol and Register Students", "description": "Enrol admitted students and register them in courses and programmes for each academic period.", "realizes": [], "children": [
            ("BP-240.20.10", "Enrol Students into Programmes", "Enrol admitted students into academic programmes.", []),
            ("BP-240.20.20", "Register Students for Courses", "Register students for courses each academic period; manage waitlists.", []),
        ]},
        {"id": "BP-240.30", "name": "Deliver Teaching and Learning", "description": "Deliver teaching and learning experiences across modes (in-person, online, hybrid).", "realizes": [], "children": [
            ("BP-240.30.10", "Schedule Classes and Resources", "Schedule classes, instructors, and learning spaces.", []),
            ("BP-240.30.20", "Deliver Instruction Across Modes", "Deliver in-person, online, and hybrid instruction.", []),
            ("BP-240.30.30", "Manage Learning Management Systems", "Operate the LMS and digital learning environments.", ["BC-600"]),
        ]},
        {"id": "BP-240.40", "name": "Assess Students and Award Credentials", "description": "Assess student learning, manage examinations and assignments, and award qualifications.", "realizes": [], "children": [
            ("BP-240.40.10", "Conduct Assessments and Examinations", "Conduct course assessments, exams, and equivalent learning measures.", []),
            ("BP-240.40.20", "Manage Grading and Academic Standing", "Manage grading, GPA, and academic standing.", []),
            ("BP-240.40.30", "Verify Completion and Award Credentials", "Verify programme completion; award degrees, diplomas, certificates.", []),
        ]},
        {"id": "BP-240.50", "name": "Manage Student Support and Wellbeing", "description": "Provide academic, financial, mental-health, accessibility support to enrolled students.", "realizes": [], "children": [
            ("BP-240.50.10", "Provide Academic and Career Support", "Provide academic advising, tutoring, and career-services support.", []),
            ("BP-240.50.20", "Provide Financial Aid and Bursary Support", "Administer financial aid, bursaries, scholarships, and student loans.", ["BC-200"]),
            ("BP-240.50.30", "Provide Wellbeing and Accessibility Services", "Provide mental-health, counselling, and accessibility services.", []),
        ]},
        {"id": "BP-240.60", "name": "Manage Graduation and Alumni Relations", "description": "Process graduation and confer awards; engage alumni for lifelong relationships and giving.", "realizes": [], "children": [
            ("BP-240.60.10", "Process Graduation Ceremonies", "Process graduation ceremonies and conferral of awards.", []),
            ("BP-240.60.20", "Manage Alumni Engagement and Giving", "Engage alumni for ongoing relationships, advancement, and giving.", []),
        ]},
    ],
}

TREE["BP-250"] = {
    "id": "BP-250", "name": "Manage Curriculum, Programmes, and Research",
    "industry": "Education",
    "description": "Manage the academic backbone: curriculum and programme design, accreditation, research administration, and educational content management.",
    "framework_label": "Education PCF v7.2.1 — Curriculum and research categories",
    "realizes": ["BC-100"],
    "children": [
        {"id": "BP-250.10", "name": "Design and Maintain Curriculum and Programmes", "description": "Design, approve, and maintain curricula and academic programmes; manage course catalogues.", "realizes": [], "children": [
            ("BP-250.10.10", "Design New Programmes and Curricula", "Design new academic programmes and curricula; obtain internal approval.", []),
            ("BP-250.10.20", "Maintain Course Catalogue", "Maintain course catalogue; process course-change requests.", []),
            ("BP-250.10.30", "Map Learning Outcomes", "Map learning outcomes across curriculum; ensure alignment to programme outcomes.", []),
        ]},
        {"id": "BP-250.20", "name": "Manage Programme Accreditation and Quality Assurance", "description": "Manage programme accreditation cycles and academic quality-assurance processes.", "realizes": ["BC-720", "BC-130"], "children": [
            ("BP-250.20.10", "Prepare Accreditation Self-Studies", "Prepare programme accreditation self-studies for CHEA / ENQA / equivalent.", ["BC-130"]),
            ("BP-250.20.20", "Manage Accreditation Visits and Outcomes", "Manage accreditation visits; respond to findings; remediate.", ["BC-130"]),
            ("BP-250.20.30", "Conduct Periodic Programme Reviews", "Conduct periodic programme reviews and continuous improvement.", ["BC-720"]),
        ]},
        {"id": "BP-250.30", "name": "Administer Research and Scholarship", "description": "Administer research grants, ethics, integrity, and research outputs.", "realizes": ["BC-150", "BC-610"], "children": [
            ("BP-250.30.10", "Pursue and Manage Research Grants", "Pursue research opportunities; develop proposals; manage award setup and post-award administration.", []),
            ("BP-250.30.20", "Manage Research Ethics and Integrity", "Operate research-ethics committees; manage research-integrity oversight.", ["BC-150"]),
            ("BP-250.30.30", "Manage Research Data and Outputs", "Manage research data, publications, and dissemination.", ["BC-610", "BC-840"]),
            ("BP-250.30.40", "Measure Research Impact", "Measure research impact through bibliometrics and equivalent measures.", []),
        ]},
        {"id": "BP-250.40", "name": "Manage Educational Content and Learning Resources", "description": "Develop and curate teaching content, courseware, and learning resources, including digital platforms.", "realizes": ["BC-820"], "children": [
            ("BP-250.40.10", "Develop Courseware and Learning Resources", "Develop courseware, OER, and learning resources.", ["BC-820"]),
            ("BP-250.40.20", "Operate Digital Learning Platforms", "Operate digital learning platforms and content repositories.", ["BC-600"]),
        ]},
        {"id": "BP-250.50", "name": "Manage Educator Workforce", "description": "Plan and manage the academic workforce: recruitment, tenure tracks, peer review, professional development.", "realizes": ["BC-300"], "children": [
            ("BP-250.50.10", "Recruit and Onboard Educators", "Recruit and onboard academic staff per policies.", ["BC-300"]),
            ("BP-250.50.20", "Manage Tenure Track and Promotion", "Manage tenure tracks, peer review, and academic promotion.", ["BC-300"]),
            ("BP-250.50.30", "Provide Educator Professional Development", "Provide pedagogy and continuing professional development for educators.", ["BC-300"]),
        ]},
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
    for bp2 in bp1["children"]:
        L.append(f"  - id: {bp2['id']}")
        L.append(f"    name: {bp2['name']}")
        L.append("    level: 2")
        L.append("    description: >-")
        L.append(f"      {bp2['description']}")
        if bp2["realizes"]:
            L.append("    realizes_capability_ids:")
            for bc in bp2["realizes"]:
                L.append(f"      - {bc}")
        else:
            L.append("    realizes_capability_ids: []")
        if not bp2.get("children"):
            L.append("    children: []")
        else:
            L.append("    children:")
            for cid, cname, cdesc, crealizes in bp2["children"]:
                L.append(f"      - id: {cid}")
                L.append(f"        name: {cname}")
                L.append("        level: 3")
                L.append("        description: >-")
                L.append(f"          {cdesc}")
                if crealizes:
                    L.append("        realizes_capability_ids:")
                    for bc in crealizes:
                        L.append(f"          - {bc}")
                else:
                    L.append("        realizes_capability_ids: []")
                L.append("        children: []")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1", required=True)
    args = ap.parse_args()
    if args.bp1 not in TREE: raise SystemExit(f"Unknown {args.bp1}")
    bp1 = TREE[args.bp1]
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(emit(bp1))
    nb_bp2 = len(bp1["children"])
    nb_bp3 = sum(len(b.get("children") or []) for b in bp1["children"])
    print(f"✔ {bp1['id']} → BP1-{slug}.yaml ({nb_bp2} BP2, {nb_bp3} BP3)")


if __name__ == "__main__":
    main()
