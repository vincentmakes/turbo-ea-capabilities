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
