#!/usr/bin/env python3
"""BP3 drill-down for industry-specific BP1s: Pharma (BP-190/200), Banking
(BP-130/140), Healthcare Provider (BP-170/180).

Re-emits each industry BP1 file with BP1 + BP2 + BP3 levels. APQC v8.0
version labels throughout.

Usage:
    python3 scripts/import_industry_bp3.py --bp1 BP-190
    python3 scripts/import_industry_bp3.py --industry pharma | banking | healthcare
"""
from __future__ import annotations

import argparse
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")
APQC_VERSION = "8.0"


def slugify(name):
    out, last = [], True
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch); last = False
        else:
            if not last:
                out.append("-"); last = True
    return "".join(out).strip("-")


# Industry BP1 trees: BP1 (id/apqc/name/desc/realizes/industry/children)
# Each BP2 child: (id, apqc, name, desc, realizes, [bp3 entries])
# Each BP3: (id, apqc, name, desc, realizes)
TREE: dict[str, dict] = {}

# ==========================================================================
# PHARMA — BP-190 + BP-200
# ==========================================================================
TREE["BP-190"] = {
    "id": "BP-190", "apqc": None,
    "name": "Discover and Develop Therapeutics",
    "industry": "Pharmaceuticals & Life Sciences",
    "description": "Conduct discovery, preclinical, and clinical development of therapeutic products through to regulatory submission readiness.",
    "framework_ref_label": "Life Sciences PCF v6.1/7.2 — Discovery and Development categories",
    "realizes": ["BC-810", "BC-820"],
    "children": [
        {
            "id": "BP-190.10", "apqc": None,
            "name": "Conduct Drug Discovery and Target Identification",
            "description": "Identify and validate biological targets; screen and optimise hit and lead compounds.",
            "realizes": ["BC-810"],
            "children": [
                ("BP-190.10.10", None, "Identify and Validate Biological Targets",
                 "Identify candidate disease targets and validate their relevance through genetic, biochemical, and disease-association studies.",
                 ["BC-810"]),
                ("BP-190.10.20", None, "Screen and Select Hit Compounds",
                 "Run high-throughput screening, fragment-based, and computational approaches to identify hit compounds against validated targets.",
                 ["BC-810"]),
                ("BP-190.10.30", None, "Optimise Lead Candidates",
                 "Refine hits into leads through medicinal-chemistry optimisation, ADME tuning, and selectivity profiling.",
                 ["BC-810"]),
            ],
        },
        {
            "id": "BP-190.20", "apqc": None,
            "name": "Conduct Preclinical Development",
            "description": "Conduct in vitro and in vivo preclinical studies; perform IND-enabling work.",
            "realizes": ["BC-810"],
            "children": [
                ("BP-190.20.10", None, "Conduct In Vitro Pharmacology and Safety",
                 "Run cell-based and biochemical assays for efficacy, selectivity, mechanism, and early safety.",
                 ["BC-810"]),
                ("BP-190.20.20", None, "Conduct In Vivo Toxicology and Pharmacokinetics",
                 "Run animal studies for pharmacokinetics, toxicology, and disease-model efficacy under GLP.",
                 ["BC-810", "BC-720"]),
                ("BP-190.20.30", None, "Prepare IND/CTA Submissions",
                 "Compile preclinical data and CMC into Investigational New Drug / Clinical Trial Application packages.",
                 ["BC-130", "BC-810"]),
            ],
        },
        {
            "id": "BP-190.30", "apqc": None,
            "name": "Conduct Clinical Trials",
            "description": "Plan and conduct clinical trials across Phase I, II, III, and IV under GCP.",
            "realizes": ["BC-810"],
            "children": [
                ("BP-190.30.10", None, "Conduct Phase I Clinical Trials",
                 "Run first-in-human safety, tolerability, and pharmacokinetic studies under GCP.",
                 ["BC-810"]),
                ("BP-190.30.20", None, "Conduct Phase II Clinical Trials",
                 "Run dose-finding and proof-of-concept efficacy trials in target patient populations.",
                 ["BC-810"]),
                ("BP-190.30.30", None, "Conduct Phase III Clinical Trials",
                 "Run pivotal efficacy and safety trials at scale to support marketing authorisation.",
                 ["BC-810"]),
                ("BP-190.30.40", None, "Conduct Phase IV / Post-Marketing Studies",
                 "Run post-approval studies for long-term safety, comparative effectiveness, and label expansion.",
                 ["BC-810", "BC-130"]),
            ],
        },
        {
            "id": "BP-190.40", "apqc": None,
            "name": "Manage Clinical Operations and Sites",
            "description": "Operate the clinical-trial machine: site selection, patient recruitment, monitoring, data management.",
            "realizes": ["BC-810", "BC-300"],
            "children": [
                ("BP-190.40.10", None, "Select and Onboard Clinical Sites",
                 "Identify, qualify, and onboard investigator sites with site-initiation activities.",
                 ["BC-810"]),
                ("BP-190.40.20", None, "Recruit and Enroll Patients",
                 "Recruit eligible patients through investigator sites, registries, and digital channels; manage informed consent.",
                 ["BC-810"]),
                ("BP-190.40.30", None, "Monitor Trial Conduct",
                 "Monitor sites for protocol adherence, data quality, and patient safety; manage site queries and source data verification.",
                 ["BC-810", "BC-720"]),
                ("BP-190.40.40", None, "Manage Clinical Trial Data",
                 "Capture, clean, and lock clinical-trial data; manage EDC systems and statistical analyses.",
                 ["BC-610", "BC-810"]),
            ],
        },
        {
            "id": "BP-190.50", "apqc": None,
            "name": "Prepare Regulatory Submissions",
            "description": "Prepare and file regulatory submissions (IND, NDA, BLA, MAA) and respond to agency queries.",
            "realizes": ["BC-130"],
            "children": [
                ("BP-190.50.10", None, "Prepare CMC and Module 3 Documentation",
                 "Author Chemistry, Manufacturing, and Controls documentation for regulatory submissions.",
                 ["BC-130", "BC-720"]),
                ("BP-190.50.20", None, "Prepare Clinical Module 5",
                 "Author clinical study reports and integrated summaries of efficacy and safety.",
                 ["BC-130", "BC-810"]),
                ("BP-190.50.30", None, "File and Respond to Regulatory Queries",
                 "File NDA/BLA/MAA submissions; respond to regulatory authority questions and information requests.",
                 ["BC-130"]),
            ],
        },
    ],
}

TREE["BP-200"] = {
    "id": "BP-200", "apqc": None,
    "name": "Manufacture, Supply, and Pharmacovigilance",
    "industry": "Pharmaceuticals & Life Sciences",
    "description": "Manufacture pharmaceutical and biologic products under GMP; manage commercial supply chain; run pharmacovigilance and post-market safety surveillance.",
    "framework_ref_label": "Life Sciences PCF v6.1/7.2 — Manufacturing and Pharmacovigilance categories",
    "realizes": ["BC-520", "BC-130"],
    "children": [
        {
            "id": "BP-200.10", "apqc": None,
            "name": "Manage GMP Manufacturing Operations",
            "description": "Run GMP-compliant manufacturing of APIs, drug products, and biologics.",
            "realizes": ["BC-520", "BC-720"],
            "children": [
                ("BP-200.10.10", None, "Plan GMP Production",
                 "Plan GMP production runs against demand and supply constraints; manage materials and capacity.",
                 ["BC-520"]),
                ("BP-200.10.20", None, "Execute GMP Manufacturing",
                 "Execute GMP manufacturing operations including API synthesis, drug-product formulation, and biologics fermentation/purification.",
                 ["BC-520", "BC-720"]),
                ("BP-200.10.30", None, "Manage Batch Records and Release",
                 "Maintain executed batch records; perform QA review and product release.",
                 ["BC-720"]),
            ],
        },
        {
            "id": "BP-200.20", "apqc": None,
            "name": "Manage Quality Assurance and Quality Control",
            "description": "Run QA/QC programs across the product lifecycle, including stability, release testing, and CAPA.",
            "realizes": ["BC-720"],
            "children": [
                ("BP-200.20.10", None, "Operate Quality Control Testing",
                 "Run incoming, in-process, and finished-product QC testing.",
                 ["BC-720"]),
                ("BP-200.20.20", None, "Manage Stability Studies",
                 "Plan and run ICH stability studies; manage shelf-life determination.",
                 ["BC-720"]),
                ("BP-200.20.30", None, "Manage CAPA and Deviations",
                 "Process deviations, OOS results, and corrective/preventive actions per ICH Q10.",
                 ["BC-720"]),
                ("BP-200.20.40", None, "Conduct Quality Audits",
                 "Conduct internal and supplier quality audits; manage findings and corrective actions.",
                 ["BC-720", "BC-140"]),
            ],
        },
        {
            "id": "BP-200.30", "apqc": None,
            "name": "Manage Cold-Chain and Pharmaceutical Supply Chain",
            "description": "Operate the pharmaceutical supply chain, including cold-chain logistics, serialisation, and distributor management.",
            "realizes": ["BC-520", "BC-530"],
            "children": [
                ("BP-200.30.10", None, "Manage Cold-Chain Logistics",
                 "Operate temperature-controlled storage and transport across the supply chain.",
                 ["BC-520"]),
                ("BP-200.30.20", None, "Manage Serialisation and Track-and-Trace",
                 "Apply unit-level serialisation and aggregate to comply with DSCSA / FMD track-and-trace requirements.",
                 ["BC-520", "BC-130"]),
                ("BP-200.30.30", None, "Manage Wholesaler and Pharmacy Distribution",
                 "Manage 3PL/wholesaler relationships; deliver to retail and hospital pharmacy channels.",
                 ["BC-510", "BC-520"]),
            ],
        },
        {
            "id": "BP-200.40", "apqc": None,
            "name": "Manage Pharmacovigilance and Adverse-Event Reporting",
            "description": "Capture, assess, and report adverse events and safety signals; maintain the safety database and PSUR cycle.",
            "realizes": ["BC-130", "BC-120"],
            "children": [
                ("BP-200.40.10", None, "Process Adverse-Event Cases",
                 "Receive, triage, and process individual case safety reports across markets.",
                 ["BC-130"]),
                ("BP-200.40.20", None, "Conduct Signal Detection and Risk Assessment",
                 "Detect safety signals; assess and document risk; update Risk Management Plans.",
                 ["BC-120", "BC-130"]),
                ("BP-200.40.30", None, "Maintain Safety Database",
                 "Maintain the global safety database with adequate data quality and traceability.",
                 ["BC-610", "BC-130"]),
                ("BP-200.40.40", None, "Submit PSUR / PADER and Regulatory Safety Reports",
                 "Prepare and submit Periodic Safety Update Reports and equivalent regulatory safety reports.",
                 ["BC-130"]),
            ],
        },
        {
            "id": "BP-200.50", "apqc": None,
            "name": "Manage Product Registration and Post-Market Compliance",
            "description": "Maintain product registrations across markets and run post-market regulatory commitments and inspections.",
            "realizes": ["BC-130"],
            "children": [
                ("BP-200.50.10", None, "Maintain Product Registrations",
                 "Maintain marketing authorisations across jurisdictions; manage registration databases.",
                 ["BC-130"]),
                ("BP-200.50.20", None, "Submit Variations and Renewals",
                 "Prepare and submit registration variations, line extensions, and periodic renewals.",
                 ["BC-130"]),
                ("BP-200.50.30", None, "Manage Inspection Readiness",
                 "Maintain inspection readiness for FDA / EMA / health-authority inspections; respond to findings.",
                 ["BC-130", "BC-720"]),
            ],
        },
    ],
}

# ==========================================================================
# BANKING — BP-130 + BP-140
# ==========================================================================
TREE["BP-130"] = {
    "id": "BP-130", "apqc": None,
    "name": "Operate Banking Products and Services",
    "industry": "Banking & Capital Markets",
    "description": "Run banking-specific product and service operations: deposit-taking, lending, cards, payments, trade finance, customer servicing, channels — distinct from cross-industry Order-to-Cash.",
    "framework_ref_label": "Banking Industry Architecture Network — service-domain reference",
    "framework": "BIAN",
    "realizes": ["BC-100"],
    "children": [
        {
            "id": "BP-130.10", "apqc": None, "name": "Manage Deposit Operations",
            "description": "Operate retail and commercial deposit accounts: account opening, transaction posting, interest calculation, and statement production.",
            "realizes": [],
            "children": [
                ("BP-130.10.10", None, "Open and Maintain Deposit Accounts",
                 "Onboard customers; open and amend deposit accounts including KYC and account-opening compliance.",
                 ["BC-130"]),
                ("BP-130.10.20", None, "Process Deposit Transactions",
                 "Post deposits, withdrawals, transfers; calculate and credit interest.",
                 []),
                ("BP-130.10.30", None, "Manage Statements and Disclosures",
                 "Produce and deliver account statements and regulatory disclosures.",
                 []),
            ],
        },
        {
            "id": "BP-130.20", "apqc": None, "name": "Manage Lending Operations",
            "description": "Originate, underwrite, service, and collect on loans across retail, mortgage, commercial, and syndicated facilities.",
            "realizes": [],
            "children": [
                ("BP-130.20.10", None, "Originate Loans",
                 "Capture loan applications across channels; perform initial validation and KYC.",
                 ["BC-130"]),
                ("BP-130.20.20", None, "Underwrite and Decision Loans",
                 "Underwrite credit applications; render approve/decline decisions; price and offer loans.",
                 []),
                ("BP-130.20.30", None, "Document, Disburse, and Service Loans",
                 "Execute loan documentation; disburse funds; service loans through their lifecycle.",
                 []),
                ("BP-130.20.40", None, "Manage Collections and Recoveries",
                 "Manage delinquent loans through collections, restructuring, and recovery actions.",
                 []),
            ],
        },
        {
            "id": "BP-130.30", "apqc": None, "name": "Manage Card Operations",
            "description": "Operate credit, debit, and prepaid card programs: issuance, authorisation, clearing, settlement, and disputes.",
            "realizes": [],
            "children": [
                ("BP-130.30.10", None, "Issue and Manage Cards",
                 "Onboard cardholders; issue, replace, and maintain physical and virtual cards.",
                 []),
                ("BP-130.30.20", None, "Authorise, Clear, and Settle Card Transactions",
                 "Operate card authorisation, clearing, and settlement across schemes.",
                 []),
                ("BP-130.30.30", None, "Manage Card Disputes and Chargebacks",
                 "Process cardholder disputes and chargebacks per scheme rules.",
                 ["BC-430"]),
            ],
        },
        {
            "id": "BP-130.40", "apqc": None, "name": "Manage Payment Operations",
            "description": "Process domestic and cross-border payments across rails (ACH, wire, RTGS, instant payments, SWIFT).",
            "realizes": [],
            "children": [
                ("BP-130.40.10", None, "Initiate and Validate Payments",
                 "Capture payment instructions across channels; perform validation, sanctions screening, and AML checks.",
                 ["BC-130"]),
                ("BP-130.40.20", None, "Route and Execute Payments",
                 "Route payments to appropriate rails (ACH, wire, RTGS, instant) and execute settlement.",
                 []),
                ("BP-130.40.30", None, "Reconcile and Investigate Payments",
                 "Reconcile payment flows and investigate exceptions, returns, and recalls.",
                 []),
            ],
        },
        {
            "id": "BP-130.50", "apqc": None, "name": "Manage Trade Finance Operations",
            "description": "Operate trade-finance products: letters of credit, documentary collections, supply-chain finance, guarantees.",
            "realizes": [],
            "children": [
                ("BP-130.50.10", None, "Issue Trade Finance Instruments",
                 "Issue letters of credit, guarantees, and bonds against approved facilities.",
                 []),
                ("BP-130.50.20", None, "Manage Trade Documents and Discrepancies",
                 "Examine trade documents under UCP 600; manage discrepancies and authorisations to pay.",
                 []),
                ("BP-130.50.30", None, "Operate Supply-Chain Finance and Receivables",
                 "Operate supplier-finance and receivables-finance programs.",
                 []),
            ],
        },
        {
            "id": "BP-130.60", "apqc": None, "name": "Manage Banking Customer Servicing",
            "description": "Service banking customers across channels: call centre, branch, digital, and dispute handling.",
            "realizes": ["BC-430", "BC-420"],
            "children": [
                ("BP-130.60.10", None, "Resolve Customer Inquiries and Servicing Requests",
                 "Receive and resolve customer inquiries and service requests across channels.",
                 ["BC-430"]),
                ("BP-130.60.20", None, "Manage Customer Complaints and Disputes",
                 "Process and resolve customer complaints and disputes; manage regulatory complaint reporting.",
                 ["BC-430"]),
                ("BP-130.60.30", None, "Manage Account Maintenance",
                 "Process account maintenance: contact updates, beneficiary changes, joint-account changes.",
                 ["BC-420"]),
            ],
        },
        {
            "id": "BP-130.70", "apqc": None, "name": "Manage Banking Channels and Distribution",
            "description": "Operate banking distribution channels: branch network, ATM estate, call centre, digital, partner introducers (BIAN Customer & Channel category).",
            "realizes": ["BC-410", "BC-420"],
            "children": [
                ("BP-130.70.10", None, "Operate Branch Network",
                 "Operate physical branch network and in-branch services.",
                 ["BC-700"]),
                ("BP-130.70.20", None, "Operate ATM and Self-Service Estate",
                 "Operate ATMs and self-service banking infrastructure.",
                 []),
                ("BP-130.70.30", None, "Operate Digital and Mobile Banking Channels",
                 "Operate digital and mobile banking channels including authentication and digital onboarding.",
                 ["BC-600", "BC-620"]),
            ],
        },
    ],
}

TREE["BP-140"] = {
    "id": "BP-140", "apqc": None,
    "name": "Operate Capital Markets and Treasury Services",
    "industry": "Banking & Capital Markets",
    "description": "Run capital-markets and treasury operations: trading execution, settlement and clearing, custody, asset servicing, and securities lending.",
    "framework_ref_label": "Capital Markets service-domain reference",
    "framework": "BIAN",
    "realizes": ["BC-210"],
    "children": [
        {
            "id": "BP-140.10", "apqc": None, "name": "Manage Trading Operations",
            "description": "Execute trades across asset classes: equities, fixed income, FX, commodities, derivatives.",
            "realizes": ["BC-210"],
            "children": [
                ("BP-140.10.10", None, "Capture and Validate Trade Orders",
                 "Receive trade orders across channels; validate against limits and pre-trade controls.",
                 ["BC-210", "BC-120"]),
                ("BP-140.10.20", None, "Execute Trades",
                 "Execute trades on exchanges, MTFs, and OTC counterparties across asset classes.",
                 ["BC-210"]),
                ("BP-140.10.30", None, "Manage Trade Allocation and Confirmation",
                 "Allocate executed trades to client accounts; confirm trades with counterparties.",
                 ["BC-210"]),
                ("BP-140.10.40", None, "Manage Position and Trading Risk",
                 "Manage intraday and end-of-day positions; monitor market and credit risk on trading book.",
                 ["BC-120"]),
            ],
        },
        {
            "id": "BP-140.20", "apqc": None, "name": "Manage Clearing and Settlement",
            "description": "Clear and settle trades through central counterparties and bilateral mechanisms.",
            "realizes": ["BC-210"],
            "children": [
                ("BP-140.20.10", None, "Clear Trades through CCPs",
                 "Submit trades to central counterparties; manage margin and default-fund contributions.",
                 ["BC-210"]),
                ("BP-140.20.20", None, "Settle Trades",
                 "Settle trades through CSDs and correspondent banks; manage delivery-vs-payment.",
                 ["BC-210"]),
                ("BP-140.20.30", None, "Manage Settlement Failures and Buy-Ins",
                 "Manage failed settlements and CSDR buy-in obligations.",
                 ["BC-210"]),
            ],
        },
        {
            "id": "BP-140.30", "apqc": None, "name": "Manage Custody Operations",
            "description": "Hold and safekeep client securities; process corporate actions and income.",
            "realizes": ["BC-210"],
            "children": [
                ("BP-140.30.10", None, "Hold Client Securities in Custody",
                 "Maintain client securities holdings in custody and sub-custody networks.",
                 ["BC-210"]),
                ("BP-140.30.20", None, "Process Corporate Actions",
                 "Process voluntary and mandatory corporate actions; communicate with clients.",
                 ["BC-210"]),
                ("BP-140.30.30", None, "Process Income and Tax",
                 "Collect and credit dividends, coupons, and other income; apply withholding tax and tax reclaims.",
                 ["BC-210", "BC-220"]),
            ],
        },
        {
            "id": "BP-140.40", "apqc": None, "name": "Manage Asset Servicing",
            "description": "Service investment products: corporate actions, dividend processing, proxy voting, tax reclaim.",
            "realizes": ["BC-210"],
            "children": [
                ("BP-140.40.10", None, "Manage Proxy Voting and Shareholder Communications",
                 "Receive and process proxy voting instructions; communicate shareholder events.",
                 ["BC-210"]),
                ("BP-140.40.20", None, "Manage Fund Accounting and NAV",
                 "Calculate and publish fund net-asset values; manage fund expenses and accruals.",
                 ["BC-200", "BC-210"]),
                ("BP-140.40.30", None, "Manage Investor Reporting",
                 "Produce and distribute investor reports; manage transparency disclosures.",
                 ["BC-240", "BC-210"]),
            ],
        },
        {
            "id": "BP-140.50", "apqc": None, "name": "Manage Securities Lending",
            "description": "Operate securities-lending programs and collateral management.",
            "realizes": ["BC-210"],
            "children": [
                ("BP-140.50.10", None, "Lend Securities and Manage Collateral",
                 "Lend securities to borrowers; receive and manage collateral.",
                 ["BC-210"]),
                ("BP-140.50.20", None, "Manage Recalls and Returns",
                 "Recall lent securities for corporate actions or sales; manage returns and substitutions.",
                 ["BC-210"]),
            ],
        },
    ],
}

# ==========================================================================
# HEALTHCARE PROVIDER — BP-170 + BP-180
# ==========================================================================
TREE["BP-170"] = {
    "id": "BP-170", "apqc": None,
    "name": "Deliver Patient Care",
    "industry": "Healthcare Providers",
    "description": "Run end-to-end patient care delivery in a hospital or care-network setting: from access through clinical encounters to discharge and post-discharge follow-up.",
    "framework_ref_label": "Healthcare Provider PCF v7.2 — Care delivery categories",
    "realizes": ["BC-100"],
    "children": [
        {
            "id": "BP-170.10", "apqc": None, "name": "Manage Patient Access and Registration",
            "description": "Receive, register, schedule, and admit patients across inpatient, outpatient, and emergency channels.",
            "realizes": [],
            "children": [
                ("BP-170.10.10", None, "Schedule Patient Appointments and Encounters",
                 "Schedule outpatient appointments and inpatient admissions across services.",
                 []),
                ("BP-170.10.20", None, "Register and Verify Patient Demographics",
                 "Register patients; verify demographics and coverage; perform authorisation checks.",
                 []),
                ("BP-170.10.30", None, "Admit and Transfer Patients",
                 "Admit patients to inpatient units; manage internal transfers and bed assignments.",
                 []),
            ],
        },
        {
            "id": "BP-170.20", "apqc": None, "name": "Perform Clinical Assessment and Triage",
            "description": "Triage and clinically assess patients on arrival, including history, examination, and acuity scoring.",
            "realizes": [],
            "children": [
                ("BP-170.20.10", None, "Perform ED Triage",
                 "Run emergency-department triage and acuity scoring (ESI, MTS).",
                 []),
                ("BP-170.20.20", None, "Conduct Initial History and Examination",
                 "Capture history, perform physical examination, document chief complaint.",
                 []),
                ("BP-170.20.30", None, "Develop Initial Care Plan",
                 "Formulate initial diagnosis and care plan; place initial orders.",
                 []),
            ],
        },
        {
            "id": "BP-170.30", "apqc": None, "name": "Deliver Clinical Care",
            "description": "Provide clinical care across inpatient, outpatient, surgical, and emergency settings.",
            "realizes": [],
            "children": [
                ("BP-170.30.10", None, "Administer Medications and Treatments",
                 "Administer medications, treatments, and procedures per orders; perform medication reconciliation.",
                 ["BC-720"]),
                ("BP-170.30.20", None, "Provide Nursing Care",
                 "Provide bedside nursing care across shifts; document care delivered.",
                 []),
                ("BP-170.30.30", None, "Conduct Multidisciplinary Rounds",
                 "Conduct multidisciplinary care rounds; update care plans collaboratively.",
                 []),
                ("BP-170.30.40", None, "Manage Critical Care and Emergency Response",
                 "Manage critical care and rapid-response events; escalate per protocols.",
                 ["BC-160"]),
            ],
        },
        {
            "id": "BP-170.40", "apqc": None, "name": "Manage Care Coordination and Transitions",
            "description": "Coordinate care across teams and settings; manage transitions between units, facilities, or to home.",
            "realizes": [],
            "children": [
                ("BP-170.40.10", None, "Coordinate Multidisciplinary Care",
                 "Coordinate care between physicians, nursing, ancillary services, and case management.",
                 []),
                ("BP-170.40.20", None, "Manage Inter-Facility Transfers",
                 "Coordinate transfers to higher acuity, post-acute, or rehabilitation facilities.",
                 []),
                ("BP-170.40.30", None, "Coordinate Social and Community Resources",
                 "Engage social work and community resources to support discharge planning.",
                 []),
            ],
        },
        {
            "id": "BP-170.50", "apqc": None, "name": "Discharge and Follow Up",
            "description": "Discharge patients with appropriate instructions, medication reconciliation, and follow-up scheduling.",
            "realizes": [],
            "children": [
                ("BP-170.50.10", None, "Conduct Discharge Planning",
                 "Plan discharge readiness, destination, and follow-up; complete discharge education.",
                 []),
                ("BP-170.50.20", None, "Reconcile Discharge Medications",
                 "Reconcile and reconcile-on-discharge medications; produce discharge prescriptions.",
                 ["BC-720"]),
                ("BP-170.50.30", None, "Schedule Post-Discharge Follow-Up",
                 "Schedule follow-up appointments and post-discharge community-care services.",
                 []),
            ],
        },
        {
            "id": "BP-170.60", "apqc": None, "name": "Manage Patient Experience",
            "description": "Monitor and manage the patient experience across the care journey, including grievance handling.",
            "realizes": ["BC-430"],
            "children": [
                ("BP-170.60.10", None, "Measure Patient Satisfaction and Experience",
                 "Run HCAHPS and equivalent patient-experience surveys; analyse results.",
                 ["BC-430"]),
                ("BP-170.60.20", None, "Manage Patient Complaints and Grievances",
                 "Process patient complaints and formal grievances per regulatory requirements.",
                 ["BC-430"]),
            ],
        },
    ],
}

TREE["BP-180"] = {
    "id": "BP-180", "apqc": None,
    "name": "Manage Clinical Operations and Health Information",
    "industry": "Healthcare Providers",
    "description": "Run the operational backbone of a healthcare provider: ancillary clinical services (pharmacy, laboratory, imaging, surgical), health information management, infection prevention, and credentialing.",
    "framework_ref_label": "Healthcare Provider PCF v7.2 — Clinical operations categories",
    "realizes": ["BC-100"],
    "children": [
        {
            "id": "BP-180.10", "apqc": None, "name": "Manage Pharmacy Operations",
            "description": "Operate inpatient and outpatient pharmacy services, including medication preparation, dispensing, and reconciliation.",
            "realizes": [],
            "children": [
                ("BP-180.10.10", None, "Procure and Manage Pharmacy Inventory",
                 "Procure pharmaceuticals; manage cold-chain and controlled-substance inventory.",
                 ["BC-500", "BC-530"]),
                ("BP-180.10.20", None, "Compound and Dispense Medications",
                 "Compound sterile and non-sterile preparations; dispense medications to inpatient and outpatient settings.",
                 []),
                ("BP-180.10.30", None, "Provide Clinical Pharmacy Services",
                 "Provide medication therapy management, clinical consultation, and antibiotic stewardship.",
                 ["BC-720"]),
            ],
        },
        {
            "id": "BP-180.20", "apqc": None, "name": "Manage Laboratory Operations",
            "description": "Operate clinical laboratory services across pre-analytical, analytical, and post-analytical phases.",
            "realizes": [],
            "children": [
                ("BP-180.20.10", None, "Collect and Receive Specimens",
                 "Collect specimens; receive and triage incoming specimens for testing.",
                 []),
                ("BP-180.20.20", None, "Perform Laboratory Testing",
                 "Perform clinical chemistry, haematology, microbiology, molecular, and pathology testing.",
                 ["BC-720"]),
                ("BP-180.20.30", None, "Verify and Report Results",
                 "Verify and authorise results; deliver to ordering clinicians.",
                 []),
            ],
        },
        {
            "id": "BP-180.30", "apqc": None, "name": "Manage Imaging and Diagnostics Operations",
            "description": "Operate radiology and imaging services, including modality scheduling, acquisition, and reporting.",
            "realizes": [],
            "children": [
                ("BP-180.30.10", None, "Schedule and Acquire Imaging Studies",
                 "Schedule modalities; acquire imaging studies (CT, MRI, ultrasound, X-ray, nuclear).",
                 []),
                ("BP-180.30.20", None, "Interpret and Report Imaging",
                 "Interpret studies; produce structured radiology reports.",
                 []),
                ("BP-180.30.30", None, "Manage Imaging Quality and Safety",
                 "Manage radiation dose, contrast safety, and imaging-modality quality control.",
                 ["BC-720", "BC-730"]),
            ],
        },
        {
            "id": "BP-180.40", "apqc": None, "name": "Manage Surgical and Procedural Services",
            "description": "Operate operating rooms and procedural suites, including scheduling, sterile processing, and theatre logistics.",
            "realizes": [],
            "children": [
                ("BP-180.40.10", None, "Schedule and Manage OR Cases",
                 "Schedule surgical cases; manage block time and case logistics.",
                 []),
                ("BP-180.40.20", None, "Provide Perioperative Care",
                 "Provide pre-, intra-, and post-operative care including anaesthesia.",
                 []),
                ("BP-180.40.30", None, "Manage Sterile Processing and Instruments",
                 "Operate sterile processing department; track and sterilise instruments.",
                 ["BC-720"]),
            ],
        },
        {
            "id": "BP-180.50", "apqc": None, "name": "Manage Health Information and Medical Records",
            "description": "Manage patient medical records, clinical documentation, coding, and information release.",
            "realizes": ["BC-610"],
            "children": [
                ("BP-180.50.10", None, "Maintain Electronic Medical Records",
                 "Operate the EMR/EHR; maintain documentation completeness and access controls.",
                 ["BC-610", "BC-600"]),
                ("BP-180.50.20", None, "Code Clinical Encounters",
                 "Assign ICD/CPT codes to encounters and procedures; review for accuracy.",
                 []),
                ("BP-180.50.30", None, "Release Information and Manage Privacy",
                 "Process information-release requests; manage privacy under HIPAA / GDPR.",
                 ["BC-130", "BC-610"]),
            ],
        },
        {
            "id": "BP-180.60", "apqc": None, "name": "Manage Infection Prevention and Control",
            "description": "Run infection-prevention surveillance, controls, and outbreak response across the care environment.",
            "realizes": ["BC-720", "BC-730"],
            "children": [
                ("BP-180.60.10", None, "Conduct Infection Surveillance",
                 "Surveil healthcare-associated infections; report to public-health authorities.",
                 ["BC-720"]),
                ("BP-180.60.20", None, "Manage Outbreak Response",
                 "Activate and run outbreak response, including isolation and contact tracing.",
                 ["BC-160", "BC-730"]),
            ],
        },
        {
            "id": "BP-180.70", "apqc": None, "name": "Manage Practitioner Credentialing and Privileging",
            "description": "Credential and privilege practising clinicians; manage ongoing competency and peer review.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-180.70.10", None, "Initial Credentialing and Privileging",
                 "Verify credentials; grant initial clinical privileges per medical-staff bylaws.",
                 ["BC-300"]),
                ("BP-180.70.20", None, "Manage Ongoing Competency and Peer Review",
                 "Conduct ongoing professional practice evaluation, focused review, and reappointment.",
                 ["BC-300"]),
            ],
        },
    ],
}


def _emit(bp1):
    framework = bp1.get("framework", "APQC-PCF")
    L = []
    L.append(f"id: {bp1['id']}")
    L.append(f"name: {bp1['name']}")
    L.append("level: 1")
    L.append(f"industry: {bp1['industry']}")
    L.append("description: >-")
    L.append(f"  {bp1['description']}")
    L.append("framework_refs:")
    L.append(f"  - framework: {framework}")
    L.append(f"    external_id: \"{bp1['framework_ref_label']}\"")
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
            for cid, capqc, cname, cdesc, crealizes in bp2["children"]:
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


def write_bp1(bp1):
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_emit(bp1))
    return path


INDUSTRY_BP1S = {
    "pharma": ["BP-190", "BP-200"],
    "banking": ["BP-130", "BP-140"],
    "healthcare": ["BP-170", "BP-180"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1")
    ap.add_argument("--industry", choices=list(INDUSTRY_BP1S.keys()))
    args = ap.parse_args()
    if not (args.bp1 or args.industry):
        ap.error("Pass --bp1 <id> or --industry pharma|banking|healthcare")
    targets = [args.bp1] if args.bp1 else INDUSTRY_BP1S[args.industry]
    for bp1_id in targets:
        if bp1_id not in TREE:
            raise SystemExit(f"Unknown {bp1_id}")
        bp1 = TREE[bp1_id]
        path = write_bp1(bp1)
        nb_bp2 = len(bp1["children"])
        nb_bp3 = sum(len(b.get("children") or []) for b in bp1["children"])
        print(f"✔ {bp1_id} → {os.path.relpath(path, REPO_ROOT)} ({nb_bp2} BP2, {nb_bp3} BP3)")


if __name__ == "__main__":
    main()
