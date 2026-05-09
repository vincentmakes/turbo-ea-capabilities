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

TREE["BP-90"] = {
    "id": "BP-90",
    "apqc": "9.0",
    "name": "Manage Financial Resources",
    "description": "Run enterprise finance end-to-end: planning and management accounting, transaction processing (revenue, AP, payroll), reporting, treasury, controls, tax, and consolidation.",
    "realizes": ["BC-200", "BC-230", "BC-210", "BC-220"],
    "children": [
        {
            "id": "BP-90.10", "apqc": "9.1",
            "name": "Perform Planning and Management Accounting",
            "description": "Plan, budget, forecast, and produce management-accounting analyses that drive business decisions.",
            "realizes": ["BC-230"],
            "children": [
                ("BP-90.10.10", "9.1.1", "Perform Planning/Budgeting/Forecasting",
                 "Run planning, budgeting, and forecasting cycles across the enterprise.",
                 ["BC-230"]),
                ("BP-90.10.20", "9.1.2", "Perform Cost Accounting and Control",
                 "Operate cost-accounting structures and controls.",
                 ["BC-230", "BC-200"]),
                ("BP-90.10.30", "9.1.3", "Perform Cost Management",
                 "Analyse and manage cost across products, services, and units.",
                 ["BC-230"]),
                ("BP-90.10.40", "9.1.4", "Evaluate and Manage Financial Performance",
                 "Evaluate financial performance and drive corrective actions.",
                 ["BC-230"]),
            ],
        },
        {
            "id": "BP-90.20", "apqc": "9.2",
            "name": "Perform Revenue Accounting",
            "description": "Recognise, record, and report revenue in accordance with accounting standards and contract terms.",
            "realizes": ["BC-200"],
            "children": [
                ("BP-90.20.10", "9.2.1", "Process Customer Credit",
                 "Manage customer credit limits and credit decisions.",
                 ["BC-200", "BC-420"]),
                ("BP-90.20.20", "9.2.2", "Invoice Customers",
                 "Generate and issue customer invoices.",
                 ["BC-200"]),
                ("BP-90.20.30", "9.2.3", "Process Accounts Receivable (AR)",
                 "Maintain the AR sub-ledger and apply customer payments.",
                 ["BC-200"]),
                ("BP-90.20.40", "9.2.4", "Manage and Process Collections",
                 "Run collections activities for past-due receivables.",
                 ["BC-200"]),
                ("BP-90.20.50", "9.2.5", "Manage and Process Adjustments/Deductions",
                 "Process AR adjustments, deductions, and write-offs.",
                 ["BC-200"]),
            ],
        },
        {
            "id": "BP-90.30", "apqc": "9.3",
            "name": "Perform General Accounting and Reporting",
            "description": "Maintain the general ledger, perform period-end close, and produce statutory and management financial reports.",
            "realizes": ["BC-200"],
            "children": [
                ("BP-90.30.10", "9.3.1", "Manage Policies and Procedures",
                 "Maintain accounting policies, procedures, and the chart of accounts.",
                 ["BC-200"]),
                ("BP-90.30.20", "9.3.2", "Perform General Accounting",
                 "Operate the GL through journal entry, reconciliation, and period-end close.",
                 ["BC-200"]),
                ("BP-90.30.30", "9.3.3", "Perform Fixed-Asset Accounting",
                 "Account for fixed assets across acquisition, depreciation, and disposal.",
                 ["BC-200"]),
                ("BP-90.30.40", "9.3.4", "Perform Financial Reporting",
                 "Produce statutory, management, and regulatory financial reports.",
                 ["BC-200", "BC-230"]),
            ],
        },
        {
            "id": "BP-90.40", "apqc": "9.4",
            "name": "Manage Fixed-Asset Project Accounting",
            "description": "Account for capital projects and fixed assets across acquisition, depreciation, impairment, and disposal.",
            "realizes": ["BC-200", "BC-900"],
            "children": [
                ("BP-90.40.10", "9.4.1", "Perform Capital Planning and Project Approval",
                 "Plan capital investment and approve capital projects.",
                 ["BC-230", "BC-900"]),
                ("BP-90.40.20", "9.4.2", "Perform Capital Project Accounting",
                 "Account for capital projects across the construction-in-progress lifecycle.",
                 ["BC-200", "BC-900"]),
                ("BP-90.40.30", "9.4.3", "Perform Asset Valuation and Tracking",
                 "Value, track, and reconcile the fixed-asset register.",
                 ["BC-200"]),
                ("BP-90.40.40", "9.4.4", "Manage Decommissioning, Disposals, Write-offs",
                 "Account for asset retirements, disposals, and write-offs.",
                 ["BC-200", "BC-740"]),
            ],
        },
        {
            "id": "BP-90.50", "apqc": "9.5",
            "name": "Process Payroll",
            "description": "Calculate, pay, and report employee compensation, including statutory withholdings and benefits accounting.",
            "realizes": ["BC-300", "BC-200"],
            "children": [
                ("BP-90.50.10", "9.5.1", "Report Time",
                 "Capture and approve employee time and attendance.",
                 ["BC-300"]),
                ("BP-90.50.20", "9.5.2", "Manage Pay",
                 "Calculate pay and execute payroll runs.",
                 ["BC-300", "BC-200"]),
                ("BP-90.50.30", "9.5.3", "Process Payroll Taxes",
                 "Calculate, withhold, and remit payroll taxes.",
                 ["BC-220", "BC-300"]),
                ("BP-90.50.40", "9.5.4", "Manage Time-Tracking and Labour-Cost Recovery",
                 "Track labour cost to projects, customers, or activities for cost recovery.",
                 ["BC-200", "BC-230"]),
            ],
        },
        {
            "id": "BP-90.60", "apqc": "9.6",
            "name": "Process Accounts Payable and Expense Reimbursements",
            "description": "Validate, approve, and pay supplier invoices and employee expense claims.",
            "realizes": ["BC-200", "BC-500"],
            "children": [
                ("BP-90.60.10", "9.6.1", "Process Accounts Payable (AP)",
                 "Process supplier invoices through 3-way match, approval, and payment.",
                 ["BC-200", "BC-500"]),
                ("BP-90.60.20", "9.6.2", "Process Expense Reimbursements",
                 "Process employee expense claims through approval and payment.",
                 ["BC-200", "BC-300"]),
            ],
        },
        {
            "id": "BP-90.70", "apqc": "9.7",
            "name": "Manage Treasury Operations",
            "description": "Manage cash, liquidity, banking, debt, investments, and financial-risk hedging.",
            "realizes": ["BC-210"],
            "children": [
                ("BP-90.70.10", "9.7.1", "Manage Treasury Policies and Procedures",
                 "Maintain treasury policies, controls, and authority matrices.",
                 ["BC-210"]),
                ("BP-90.70.20", "9.7.2", "Manage Cash",
                 "Manage cash positions, forecasts, and liquidity.",
                 ["BC-210"]),
                ("BP-90.70.30", "9.7.3", "Manage In-House Bank Accounts",
                 "Operate in-house bank structures and intercompany funding.",
                 ["BC-210"]),
                ("BP-90.70.40", "9.7.4", "Manage Debt and Investments",
                 "Manage corporate debt portfolios and investments.",
                 ["BC-210"]),
                ("BP-90.70.50", "9.7.5", "Monitor and Execute Risk and Hedging Transactions",
                 "Execute hedging programs and monitor financial-market risk exposures.",
                 ["BC-210", "BC-120"]),
                ("BP-90.70.60", "9.7.6", "Manage Financial Risk",
                 "Manage financial risks: FX, interest-rate, commodity, credit.",
                 ["BC-210", "BC-120"]),
            ],
        },
        {
            "id": "BP-90.80", "apqc": "9.8",
            "name": "Manage Internal Controls",
            "description": "Design, operate, and assure financial internal controls aligned to regulatory and assurance requirements.",
            "realizes": ["BC-140", "BC-130"],
            "children": [
                ("BP-90.80.10", "9.8.1", "Establish Internal Controls, Policies, and Procedures",
                 "Design and document the internal-control framework.",
                 ["BC-140", "BC-130"]),
                ("BP-90.80.20", "9.8.2", "Operate Controls and Monitor Compliance",
                 "Operate the control environment and monitor compliance with policy.",
                 ["BC-140", "BC-130"]),
                ("BP-90.80.30", "9.8.3", "Report on Internal Controls Compliance",
                 "Report on control effectiveness to audit and regulators.",
                 ["BC-140"]),
            ],
        },
        {
            "id": "BP-90.90", "apqc": "9.9",
            "name": "Manage Taxes",
            "description": "Determine, file, and pay direct, indirect, and transactional taxes; manage tax controversy and planning.",
            "realizes": ["BC-220"],
            "children": [
                ("BP-90.90.10", "9.9.1", "Develop Tax Strategy and Plan",
                 "Set tax strategy and planning across jurisdictions.",
                 ["BC-220"]),
                ("BP-90.90.20", "9.9.2", "Process Taxes",
                 "Calculate, file, and pay tax obligations.",
                 ["BC-220"]),
                ("BP-90.90.30", "9.9.3", "Perform Tax-Planning Calculations and Consultation",
                 "Perform tax-planning calculations and advise the business.",
                 ["BC-220"]),
                ("BP-90.90.40", "9.9.4", "Account for Taxes",
                 "Account for current and deferred taxes in financial statements.",
                 ["BC-220", "BC-200"]),
                ("BP-90.90.50", "9.9.5", "Monitor Tax Compliance",
                 "Monitor tax compliance and manage tax controversy.",
                 ["BC-220", "BC-130"]),
            ],
        },
        {
            "id": "BP-90.100", "apqc": "9.10",
            "name": "Manage International Funds/Consolidation",
            "description": "Translate, consolidate, and report multi-entity, multi-currency results.",
            "realizes": ["BC-200", "BC-210"],
            "children": [
                ("BP-90.100.10", "9.10.1", "Monitor International Rates",
                 "Monitor exchange rates and rate-related events relevant to consolidation.",
                 ["BC-210"]),
                ("BP-90.100.20", "9.10.2", "Manage International Transactions",
                 "Manage cross-border transactions and intercompany flows.",
                 ["BC-210", "BC-200"]),
                ("BP-90.100.30", "9.10.3", "Monitor Currency Exposures",
                 "Monitor and report currency exposures across the group.",
                 ["BC-210", "BC-120"]),
                ("BP-90.100.40", "9.10.4", "Report on Movement of Intercompany Funds",
                 "Report on intercompany flows and consolidation adjustments.",
                 ["BC-200", "BC-210"]),
            ],
        },
    ],
}

TREE["BP-80"] = {
    "id": "BP-80",
    "apqc": "8.0",
    "name": "Manage Information Technology",
    "description": "Run the enterprise IT function: strategy, build, deploy, run, and knowledge management — including IT-side risk and resilience that protects business continuity.",
    "realizes": ["BC-600", "BC-610", "BC-620"],
    "children": [
        {
            "id": "BP-80.10", "apqc": "8.1",
            "name": "Develop and Manage Business Resilience and Risk",
            "description": "Identify, assess, and mitigate IT-related risks; maintain business-continuity and disaster-recovery readiness for technology-enabled operations.",
            "realizes": ["BC-160", "BC-120", "BC-620"],
            "children": [
                ("BP-80.10.10", "8.1.1", "Manage IT Business Continuity",
                 "Plan and exercise IT business-continuity capabilities for critical services.",
                 ["BC-160", "BC-600"]),
                ("BP-80.10.20", "8.1.2", "Manage IT Disaster Recovery",
                 "Plan and exercise IT disaster-recovery capabilities for critical systems and data.",
                 ["BC-160", "BC-600"]),
                ("BP-80.10.30", "8.1.3", "Manage IT Risk",
                 "Identify and treat IT risks across availability, confidentiality, integrity, and compliance.",
                 ["BC-120", "BC-620"]),
                ("BP-80.10.40", "8.1.4", "Manage IT Compliance",
                 "Run IT compliance against policy, regulatory, and contractual obligations.",
                 ["BC-130", "BC-620"]),
            ],
        },
        {
            "id": "BP-80.20", "apqc": "8.2",
            "name": "Develop Information Technology (IT) Strategy",
            "description": "Set the IT strategy, target architecture, and investment plan that supports the business strategy.",
            "realizes": ["BC-600", "BC-170"],
            "children": [
                ("BP-80.20.10", "8.2.1", "Define Enterprise Architecture",
                 "Establish the enterprise architecture (business, application, data, technology) that aligns IT with strategy.",
                 ["BC-170", "BC-600"]),
                ("BP-80.20.20", "8.2.2", "Define IT Strategic Plan",
                 "Develop the IT strategy and multi-year plan that supports the business strategy.",
                 ["BC-600", "BC-100"]),
                ("BP-80.20.30", "8.2.3", "Manage IT Investment Portfolio",
                 "Govern the portfolio of IT investments across run, grow, and transform.",
                 ["BC-600", "BC-900"]),
                ("BP-80.20.40", "8.2.4", "Plan Business Solutions",
                 "Translate business demand into solution roadmaps and demand plans.",
                 ["BC-600", "BC-170"]),
            ],
        },
        {
            "id": "BP-80.30", "apqc": "8.3",
            "name": "Develop and Maintain Information Technology Solutions",
            "description": "Design, build, integrate, and evolve the application and infrastructure portfolio that runs the business.",
            "realizes": ["BC-600"],
            "children": [
                ("BP-80.30.10", "8.3.1", "Manage IT Development Resources",
                 "Plan and manage IT development resources, partners, and capacity.",
                 ["BC-600", "BC-300"]),
                ("BP-80.30.20", "8.3.2", "Develop and Maintain IT Solutions",
                 "Design, build, and evolve IT solutions across applications and infrastructure.",
                 ["BC-600"]),
                ("BP-80.30.30", "8.3.3", "Manage IT Solution Lifecycle",
                 "Manage the IT solution lifecycle from inception through retirement.",
                 ["BC-600", "BC-820"]),
            ],
        },
        {
            "id": "BP-80.40", "apqc": "8.4",
            "name": "Deploy Information Technology Solutions",
            "description": "Release new and changed IT solutions into production with appropriate change controls and adoption support.",
            "realizes": ["BC-600", "BC-910"],
            "children": [
                ("BP-80.40.10", "8.4.1", "Plan IT Service Release",
                 "Plan and schedule IT service releases, including dependencies and change windows.",
                 ["BC-600", "BC-910"]),
                ("BP-80.40.20", "8.4.2", "Deploy IT Solutions",
                 "Execute IT deployments through environments to production.",
                 ["BC-600"]),
                ("BP-80.40.30", "8.4.3", "Manage IT Operational Changes",
                 "Manage operational changes per change-management policy and CAB review.",
                 ["BC-910", "BC-600"]),
            ],
        },
        {
            "id": "BP-80.50", "apqc": "8.5",
            "name": "Deliver and Support Information Technology Services",
            "description": "Operate IT services day-to-day: incident, problem, request, and service-level management.",
            "realizes": ["BC-600"],
            "children": [
                ("BP-80.50.10", "8.5.1", "Manage IT Operations",
                 "Run day-to-day IT operations across production systems.",
                 ["BC-600"]),
                ("BP-80.50.20", "8.5.2", "Manage IT Service Requests",
                 "Receive, route, and fulfil IT service requests.",
                 ["BC-600"]),
                ("BP-80.50.30", "8.5.3", "Manage IT Incidents and Problems",
                 "Detect, triage, and resolve IT incidents and underlying problems.",
                 ["BC-600", "BC-160"]),
                ("BP-80.50.40", "8.5.4", "Manage IT Service Levels",
                 "Monitor IT services against agreed SLAs and report performance.",
                 ["BC-600", "BC-720"]),
            ],
        },
        {
            "id": "BP-80.60", "apqc": "8.6",
            "name": "Manage IT Knowledge",
            "description": "Capture and curate IT knowledge: configuration data, runbooks, architecture, and support knowledge bases.",
            "realizes": ["BC-830", "BC-600"],
            "children": [
                ("BP-80.60.10", "8.6.1", "Manage IT Configuration Data",
                 "Maintain CMDB and configuration data underpinning operations and change.",
                 ["BC-600", "BC-610"]),
                ("BP-80.60.20", "8.6.2", "Manage IT Documentation and Knowledge",
                 "Capture and curate IT runbooks, architectures, and support knowledge bases.",
                 ["BC-830", "BC-600"]),
            ],
        },
    ],
}

TREE["BP-70"] = {
    "id": "BP-70",
    "apqc": "7.0",
    "name": "Develop and Manage Human Capital",
    "description": "Manage the workforce end-to-end: HR strategy, recruitment, development, reward, redeployment, and employee data and inquiries.",
    "realizes": ["BC-300"],
    "children": [
        {
            "id": "BP-70.10", "apqc": "7.1",
            "name": "Develop and Manage Human Resources Planning, Policies, and Strategies",
            "description": "Set HR strategy, workforce plans, and policies aligned to business strategy and regulatory obligations.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-70.10.10", "7.1.1", "Develop Human Resources Strategy",
                 "Define HR strategy aligned to enterprise strategy and workforce ambition.",
                 ["BC-300", "BC-100"]),
                ("BP-70.10.20", "7.1.2", "Develop and Implement Human Resources Plans",
                 "Translate HR strategy into actionable workforce plans across functions and geographies.",
                 ["BC-300"]),
                ("BP-70.10.30", "7.1.3", "Monitor and Update Plans",
                 "Track and refresh HR plans as business and labour-market conditions change.",
                 ["BC-300"]),
            ],
        },
        {
            "id": "BP-70.20", "apqc": "7.2",
            "name": "Recruit, Source, and Select Employees",
            "description": "Attract, assess, and hire candidates to fill workforce demand, including onboarding readiness.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-70.20.10", "7.2.1", "Manage Employee Requisitions",
                 "Receive, validate, and approve employee requisitions from hiring managers.",
                 ["BC-300"]),
                ("BP-70.20.20", "7.2.2", "Recruit and Source Candidates",
                 "Source candidates through internal, external, and referral channels.",
                 ["BC-300"]),
                ("BP-70.20.30", "7.2.3", "Screen and Select Candidates",
                 "Assess and select candidates against requisition criteria.",
                 ["BC-300"]),
                ("BP-70.20.40", "7.2.4", "Manage New Hire/Re-hire",
                 "Process the new-hire/re-hire administrative onboarding.",
                 ["BC-300"]),
            ],
        },
        {
            "id": "BP-70.30", "apqc": "7.3",
            "name": "Develop and Counsel Employees",
            "description": "Onboard, train, develop, and coach employees across their tenure to build capability and engagement.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-70.30.10", "7.3.1", "Manage Employee Orientation and Deployment",
                 "Run orientation and initial deployment of new employees into their roles.",
                 ["BC-300"]),
                ("BP-70.30.20", "7.3.2", "Manage Employee Performance",
                 "Run goal-setting, performance reviews, and feedback cycles.",
                 ["BC-300"]),
                ("BP-70.30.30", "7.3.3", "Manage Employee Development",
                 "Plan and support employee development across careers.",
                 ["BC-300"]),
                ("BP-70.30.40", "7.3.4", "Develop and Train Employees",
                 "Design and deliver training programs that build employee capability.",
                 ["BC-300"]),
            ],
        },
        {
            "id": "BP-70.40", "apqc": "7.4",
            "name": "Reward and Retain Employees",
            "description": "Design and operate compensation, benefits, recognition, and retention programs.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-70.40.10", "7.4.1", "Develop and Manage Reward, Recognition, and Motivation Programs",
                 "Design and run reward and recognition programs that drive engagement and retention.",
                 ["BC-300"]),
                ("BP-70.40.20", "7.4.2", "Manage and Administer Benefits",
                 "Administer health, retirement, and other benefits programs.",
                 ["BC-300"]),
                ("BP-70.40.30", "7.4.3", "Manage Employee Assistance and Retention",
                 "Run employee-assistance programs and retention interventions for at-risk employees.",
                 ["BC-300"]),
                ("BP-70.40.40", "7.4.4", "Payroll Administration",
                 "Coordinate the HR-side of payroll administration: data, time, leaves, and approvals.",
                 ["BC-300", "BC-200"]),
            ],
        },
        {
            "id": "BP-70.50", "apqc": "7.5",
            "name": "Redeploy and Retire Employees",
            "description": "Manage transitions: internal mobility, redeployment, separations, and retirement.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-70.50.10", "7.5.1", "Manage Promotion and Demotion Processes",
                 "Run promotion and demotion decisions and the associated changes to comp/role.",
                 ["BC-300"]),
                ("BP-70.50.20", "7.5.2", "Manage Separation",
                 "Run voluntary and involuntary separations, including notice and severance.",
                 ["BC-300", "BC-150"]),
                ("BP-70.50.30", "7.5.3", "Manage Retirement",
                 "Process employee retirements, including pension and benefits transitions.",
                 ["BC-300"]),
                ("BP-70.50.40", "7.5.4", "Manage Leave of Absence",
                 "Manage paid and unpaid leave types, including statutory and parental leaves.",
                 ["BC-300"]),
            ],
        },
        {
            "id": "BP-70.60", "apqc": "7.6",
            "name": "Manage Employee Information and Analytics",
            "description": "Maintain employee master data and produce workforce analytics that inform decisions.",
            "realizes": ["BC-300", "BC-610"],
            "children": [
                ("BP-70.60.10", "7.6.1", "Manage Reporting Processes",
                 "Run statutory, regulatory, and management HR reporting cycles.",
                 ["BC-300"]),
                ("BP-70.60.20", "7.6.2", "Manage Employee Data",
                 "Maintain employee master data with the appropriate access and privacy controls.",
                 ["BC-300", "BC-610"]),
                ("BP-70.60.30", "7.6.3", "Manage HR Information Systems",
                 "Operate the HRIS and related systems supporting HR processes.",
                 ["BC-300", "BC-600"]),
                ("BP-70.60.40", "7.6.4", "Develop and Manage Employee Metrics",
                 "Define and produce workforce analytics and KPIs.",
                 ["BC-300", "BC-230"]),
            ],
        },
        {
            "id": "BP-70.70", "apqc": "7.7",
            "name": "Manage Employee Inquiries",
            "description": "Resolve employee questions and service requests via HR shared-service or case-management channels.",
            "realizes": ["BC-300"],
            "children": [
                ("BP-70.70.10", "7.7.1", "Receive and Respond to Employee Inquiries",
                 "Receive, route, and resolve employee inquiries on policy, benefits, and pay.",
                 ["BC-300"]),
                ("BP-70.70.20", "7.7.2", "Manage Employee Work Assignment Inquiries",
                 "Handle inquiries about role, schedule, location, and assignment changes.",
                 ["BC-300"]),
                ("BP-70.70.30", "7.7.3", "Manage Employee Grievances",
                 "Handle formal employee grievances and works-council interactions.",
                 ["BC-300", "BC-150"]),
            ],
        },
    ],
}

TREE["BP-60"] = {
    "id": "BP-60",
    "apqc": "6.0",
    "name": "Manage Customer Service",
    "description": "Develop and run the customer-care function: strategy, contact-center operations, and continuous evaluation that resolves customer issues and protects loyalty.",
    "realizes": ["BC-430", "BC-420"],
    "children": [
        {
            "id": "BP-60.10", "apqc": "6.1",
            "name": "Develop Customer Care/Customer Service Strategy",
            "description": "Define the customer-service operating model, channels, service levels, and self-service strategy.",
            "realizes": ["BC-430", "BC-100"],
            "children": [
                ("BP-60.10.10", "6.1.1", "Develop Customer Service Segmentation/Prioritisation",
                 "Define customer-service segments and prioritisation rules tied to value and risk.",
                 ["BC-430", "BC-420"]),
                ("BP-60.10.20", "6.1.2", "Define Customer Service Policies and Procedures",
                 "Establish customer-service policies, procedures, and decision-rights frameworks.",
                 ["BC-430"]),
                ("BP-60.10.30", "6.1.3", "Establish Service Levels for Customers",
                 "Define the SLAs and response-time targets that customer service must achieve.",
                 ["BC-430", "BC-720"]),
            ],
        },
        {
            "id": "BP-60.20", "apqc": "6.2",
            "name": "Plan and Manage Customer Service Operations",
            "description": "Run day-to-day customer service operations: contact handling, case management, escalation, and workforce management.",
            "realizes": ["BC-430"],
            "children": [
                ("BP-60.20.10", "6.2.1", "Plan and Manage Customer Service Workforce",
                 "Plan, schedule, and develop the customer-service workforce.",
                 ["BC-430", "BC-300"]),
                ("BP-60.20.20", "6.2.2", "Manage Customer Service Requests/Inquiries",
                 "Receive, route, and resolve customer service requests and inquiries.",
                 ["BC-430"]),
                ("BP-60.20.30", "6.2.3", "Manage Customer Complaints",
                 "Capture, route, and resolve customer complaints, including escalation handling.",
                 ["BC-430", "BC-720"]),
            ],
        },
        {
            "id": "BP-60.30", "apqc": "6.3",
            "name": "Measure and Evaluate Customer Service Operations",
            "description": "Measure service performance, customer satisfaction, and operational efficiency; drive continuous improvement.",
            "realizes": ["BC-430", "BC-720"],
            "children": [
                ("BP-60.30.10", "6.3.1", "Measure Customer Satisfaction with Customer Requests/Inquiries Handling",
                 "Run customer-satisfaction surveys and analytics for inquiry handling.",
                 ["BC-430"]),
                ("BP-60.30.20", "6.3.2", "Measure Customer Satisfaction with Complaint Handling",
                 "Run customer-satisfaction surveys and analytics for complaint resolution.",
                 ["BC-430"]),
                ("BP-60.30.30", "6.3.3", "Measure Customer Satisfaction with Products and Services",
                 "Measure overall customer satisfaction with products, services, and the brand.",
                 ["BC-430", "BC-820"]),
            ],
        },
    ],
}

TREE["BP-50"] = {
    "id": "BP-50",
    "apqc": "5.0",
    "name": "Deliver Services",
    "description": "Govern, plan, and execute the delivery of services to customers — including the resourcing, operations, and post-delivery management distinct from physical-goods supply chains.",
    "realizes": ["BC-430", "BC-720"],
    "children": [
        {
            "id": "BP-50.10", "apqc": "5.1",
            "name": "Establish Service Delivery Governance and Strategy",
            "description": "Define service-delivery operating model, governance forums, and service strategy aligned to customer outcomes and SLAs.",
            "realizes": ["BC-100", "BC-720"],
            "children": [
                ("BP-50.10.10", "5.1.1", "Establish Service Delivery Governance",
                 "Establish governance forums, decision rights, and operating-model controls for service delivery.",
                 ["BC-110", "BC-100"]),
                ("BP-50.10.20", "5.1.2", "Define Service Delivery Strategy",
                 "Define multi-year service-delivery strategy: portfolio, channels, sourcing, target service levels.",
                 ["BC-100"]),
                ("BP-50.10.30", "5.1.3", "Define Service Standards",
                 "Establish the service-quality standards and SLAs that delivery must achieve.",
                 ["BC-720", "BC-430"]),
            ],
        },
        {
            "id": "BP-50.20", "apqc": "5.2",
            "name": "Manage Service Delivery Resources",
            "description": "Plan, allocate, and develop the people, facilities, and infrastructure that deliver service.",
            "realizes": ["BC-300", "BC-700"],
            "children": [
                ("BP-50.20.10", "5.2.1", "Manage Service Delivery Workforce",
                 "Plan and manage the staffing, skills, and scheduling of the service-delivery workforce.",
                 ["BC-300"]),
                ("BP-50.20.20", "5.2.2", "Manage Service Delivery Resources and Assets",
                 "Manage the facilities, equipment, and assets used in service delivery.",
                 ["BC-700"]),
                ("BP-50.20.30", "5.2.3", "Manage Service Delivery Suppliers",
                 "Manage third-party service providers and supplier relationships supporting delivery.",
                 ["BC-510", "BC-500"]),
            ],
        },
        {
            "id": "BP-50.30", "apqc": "5.3",
            "name": "Deliver Service to Customer",
            "description": "Execute the service interaction with the customer end-to-end, including provisioning, support, and assurance.",
            "realizes": ["BC-430"],
            "children": [
                ("BP-50.30.10", "5.3.1", "Initiate Service Delivery",
                 "Onboard, provision, and start service for the customer.",
                 ["BC-430"]),
                ("BP-50.30.20", "5.3.2", "Execute Service Delivery",
                 "Perform the service interactions with the customer.",
                 ["BC-430"]),
                ("BP-50.30.30", "5.3.3", "Complete Service Delivery",
                 "Close out service engagements, capture deliverables, and confirm customer acceptance.",
                 ["BC-430"]),
            ],
        },
        {
            "id": "BP-50.40", "apqc": "5.4",
            "name": "Manage Service Delivery",
            "description": "Monitor, assure, and improve service delivery against SLAs and customer-experience targets.",
            "realizes": ["BC-430", "BC-720"],
            "children": [
                ("BP-50.40.10", "5.4.1", "Monitor Service Delivery Performance",
                 "Measure service-delivery performance against SLAs and KPIs.",
                 ["BC-430", "BC-720"]),
                ("BP-50.40.20", "5.4.2", "Assure Service Delivery Quality",
                 "Run quality assurance over the delivered service, including audits and customer feedback loops.",
                 ["BC-720", "BC-430"]),
                ("BP-50.40.30", "5.4.3", "Improve Service Delivery",
                 "Drive continuous improvement based on performance data and customer feedback.",
                 ["BC-720", "BC-430"]),
            ],
        },
    ],
}

TREE["BP-40"] = {
    "id": "BP-40",
    "apqc": "4.0",
    "name": "Deliver Physical Products",
    "description": "Plan and run the physical supply chain end-to-end: procurement, production, and outbound logistics that move goods from suppliers to customers.",
    "realizes": ["BC-520", "BC-530"],
    "children": [
        {
            "id": "BP-40.10", "apqc": "4.1",
            "name": "Plan for and Align Supply Chain Resources",
            "description": "Forecast demand, plan supply, balance capacity, and align inventory positions to meet service-level and cost targets.",
            "realizes": ["BC-520", "BC-530"],
            "children": [
                ("BP-40.10.10", "4.1.1", "Develop Production and Materials Strategies",
                 "Set the multi-period production and materials strategy to match the business plan.",
                 ["BC-520", "BC-530"]),
                ("BP-40.10.20", "4.1.2", "Manage Demand for Products and Services",
                 "Forecast and shape demand for products and services across channels and segments.",
                 ["BC-520", "BC-400"]),
                ("BP-40.10.30", "4.1.3", "Create Materials Plan",
                 "Translate the demand plan into a materials and components plan.",
                 ["BC-520", "BC-530"]),
                ("BP-40.10.40", "4.1.4", "Create and Manage Master Production Schedule",
                 "Build and maintain the master production schedule that drives execution.",
                 ["BC-520"]),
            ],
        },
        {
            "id": "BP-40.20", "apqc": "4.2",
            "name": "Procure Materials and Services",
            "description": "Source, contract, and acquire goods and services from suppliers, including supplier qualification and ongoing supplier management.",
            "realizes": ["BC-500", "BC-510"],
            "children": [
                ("BP-40.20.10", "4.2.1", "Develop Sourcing Strategies",
                 "Set category and item-level sourcing strategies aligned to the business plan.",
                 ["BC-500", "BC-510"]),
                ("BP-40.20.20", "4.2.2", "Select Suppliers and Develop/Maintain Contracts",
                 "Run RFx, qualify suppliers, and manage contracts across the lifecycle.",
                 ["BC-500", "BC-510"]),
                ("BP-40.20.30", "4.2.3", "Order Materials and Services",
                 "Issue purchase orders and receive goods and services against contracts.",
                 ["BC-500"]),
                ("BP-40.20.40", "4.2.4", "Appraise and Develop Suppliers",
                 "Monitor supplier performance, develop strategic suppliers, and remediate underperformers.",
                 ["BC-510"]),
            ],
        },
        {
            "id": "BP-40.30", "apqc": "4.3",
            "name": "Produce/Manufacture/Deliver Product",
            "description": "Convert inputs into finished products through production scheduling, manufacturing operations, and quality control.",
            "realizes": ["BC-520", "BC-720"],
            "children": [
                ("BP-40.30.10", "4.3.1", "Schedule Production",
                 "Convert the master schedule into shop-floor production schedules and orders.",
                 ["BC-520"]),
                ("BP-40.30.20", "4.3.2", "Produce/Assemble Product",
                 "Execute production and assembly to plan.",
                 ["BC-520"]),
                ("BP-40.30.30", "4.3.3", "Perform Quality Testing",
                 "Inspect and test products against quality specifications during and after production.",
                 ["BC-720"]),
                ("BP-40.30.40", "4.3.4", "Maintain Production Records and Manage Lot Traceability",
                 "Capture production records and maintain lot/serial traceability for compliance and recall.",
                 ["BC-520", "BC-610"]),
                ("BP-40.30.50", "4.3.5", "Perform Manufacturing Maintenance",
                 "Maintain production equipment to keep capacity available and quality assured.",
                 ["BC-700", "BC-720"]),
            ],
        },
        {
            "id": "BP-40.40", "apqc": "4.4",
            "name": "Manage Logistics and Warehousing",
            "description": "Run the inbound, internal, and outbound flow of goods: warehousing, transport, fulfilment, and reverse logistics.",
            "realizes": ["BC-520", "BC-530"],
            "children": [
                ("BP-40.40.10", "4.4.1", "Define Logistics Strategy",
                 "Set the logistics-network strategy: footprint, modes, partners, service levels.",
                 ["BC-520"]),
                ("BP-40.40.20", "4.4.2", "Plan and Manage Inbound Material Flow",
                 "Plan and execute the inbound flow of materials from suppliers to facilities.",
                 ["BC-520", "BC-510"]),
                ("BP-40.40.30", "4.4.3", "Operate Warehousing",
                 "Run warehousing operations: receiving, putaway, picking, and shipping.",
                 ["BC-530"]),
                ("BP-40.40.40", "4.4.4", "Operate Outbound Transportation",
                 "Plan and execute outbound transportation to customers and channels.",
                 ["BC-520"]),
                ("BP-40.40.50", "4.4.5", "Manage Returns; Manage Reverse Logistics",
                 "Run returns processing and the reverse-logistics flow for repairs, recalls, and disposal.",
                 ["BC-520", "BC-430"]),
            ],
        },
    ],
}

TREE["BP-30"] = {
    "id": "BP-30",
    "apqc": "3.0",
    "name": "Market and Sell Products and Services",
    "description": "Understand markets and customers, set marketing and sales strategy, and execute the demand-creation and order-capture activities that monetise products and services.",
    "realizes": ["BC-400", "BC-410", "BC-420", "BC-440"],
    "children": [
        {
            "id": "BP-30.10", "apqc": "3.1",
            "name": "Understand Markets, Customers, and Capabilities",
            "description": "Develop the evidence base on market dynamics, customer needs, segments, and competitive position that drives marketing and sales decisions.",
            "realizes": ["BC-400", "BC-420"],
            "children": [
                ("BP-30.10.10", "3.1.1", "Perform Customer and Market Intelligence Analysis",
                 "Gather and analyse customer, market, and competitor data to inform marketing and sales decisions.",
                 ["BC-400", "BC-420"]),
                ("BP-30.10.20", "3.1.2", "Evaluate and Prioritise Market Opportunities",
                 "Score and prioritise candidate markets and segments by attractiveness and fit.",
                 ["BC-400", "BC-100"]),
            ],
        },
        {
            "id": "BP-30.20", "apqc": "3.2",
            "name": "Develop Marketing Strategy",
            "description": "Define target segments, value propositions, brand positioning, and channel mix that direct marketing investment.",
            "realizes": ["BC-400"],
            "children": [
                ("BP-30.20.10", "3.2.1", "Define Offering and Customer Value Proposition",
                 "Articulate the offer-by-segment value proposition and positioning.",
                 ["BC-400", "BC-820"]),
                ("BP-30.20.20", "3.2.2", "Define Pricing Strategy",
                 "Set pricing strategy, structure, and policies aligned to the value proposition.",
                 ["BC-440"]),
                ("BP-30.20.30", "3.2.3", "Define Marketing Budgets",
                 "Set the overall marketing investment envelope and allocation across channels and programs.",
                 ["BC-400", "BC-230"]),
            ],
        },
        {
            "id": "BP-30.30", "apqc": "3.3",
            "name": "Develop Sales Strategy",
            "description": "Define sales coverage, channel structure, account strategy, and quota/incentive design.",
            "realizes": ["BC-410"],
            "children": [
                ("BP-30.30.10", "3.3.1", "Develop Sales Forecast",
                 "Develop the multi-period sales forecast by segment, channel, and product.",
                 ["BC-410", "BC-230"]),
                ("BP-30.30.20", "3.3.2", "Develop Sales Partner/Alliance Relationships",
                 "Establish and govern partner and alliance channels supporting sales.",
                 ["BC-410", "BC-510"]),
                ("BP-30.30.30", "3.3.3", "Establish Overall Sales Budgets",
                 "Set sales-function operating budgets and territory/account allocations.",
                 ["BC-410", "BC-230"]),
                ("BP-30.30.40", "3.3.4", "Establish Sales Goals and Measures",
                 "Set sales goals, quotas, and the performance measures used to manage the sales force.",
                 ["BC-410"]),
                ("BP-30.30.50", "3.3.5", "Establish Customer Management Measures",
                 "Define the customer-relationship measures used to track health and lifetime value.",
                 ["BC-420", "BC-410"]),
            ],
        },
        {
            "id": "BP-30.40", "apqc": "3.4",
            "name": "Develop and Manage Marketing Plans",
            "description": "Plan, execute, and measure marketing campaigns and demand-generation programs that deliver pipeline against the strategy.",
            "realizes": ["BC-400"],
            "children": [
                ("BP-30.40.10", "3.4.1", "Establish Goals, Objectives, and Metrics for Products/Services",
                 "Set per-product and per-channel marketing goals and KPIs.",
                 ["BC-400"]),
                ("BP-30.40.20", "3.4.2", "Establish Marketing Budgets",
                 "Allocate marketing investment across products, channels, and campaigns.",
                 ["BC-400", "BC-230"]),
                ("BP-30.40.30", "3.4.3", "Develop and Manage Media",
                 "Plan and run paid and owned media programs.",
                 ["BC-400"]),
                ("BP-30.40.40", "3.4.4", "Develop and Manage Pricing",
                 "Operate pricing across promotions, discounts, and lifecycle pricing decisions.",
                 ["BC-440"]),
                ("BP-30.40.50", "3.4.5", "Develop and Manage Promotional Activities",
                 "Plan and execute promotions, campaigns, and demand-generation programs.",
                 ["BC-400"]),
                ("BP-30.40.60", "3.4.6", "Track Customer Management Measures",
                 "Monitor customer health, retention, and engagement metrics.",
                 ["BC-420", "BC-400"]),
                ("BP-30.40.70", "3.4.7", "Develop and Manage Packaging Strategy",
                 "Manage product packaging and presentation in market.",
                 ["BC-820", "BC-400"]),
                ("BP-30.40.80", "3.4.8", "Manage Product and Brand",
                 "Run brand-management and product-management activities in market.",
                 ["BC-400", "BC-820"]),
            ],
        },
        {
            "id": "BP-30.50", "apqc": "3.5",
            "name": "Develop and Manage Sales Plans",
            "description": "Plan, execute, and manage the sales motion: account planning, opportunity management, pricing, quoting, and order capture.",
            "realizes": ["BC-410", "BC-440"],
            "children": [
                ("BP-30.50.10", "3.5.1", "Generate Leads",
                 "Source and qualify leads to feed the sales pipeline.",
                 ["BC-410", "BC-400"]),
                ("BP-30.50.20", "3.5.2", "Manage Customers and Accounts",
                 "Run account management for customers across renewal, upsell, and retention.",
                 ["BC-420", "BC-410"]),
                ("BP-30.50.30", "3.5.3", "Manage Customer Sales",
                 "Manage opportunities through pipeline stages from qualification to close.",
                 ["BC-410"]),
                ("BP-30.50.40", "3.5.4", "Manage Sales Orders",
                 "Capture, validate, and progress sales orders into fulfilment.",
                 ["BC-410"]),
                ("BP-30.50.50", "3.5.5", "Manage Sales Partners and Alliances",
                 "Operate partner and alliance sales channels.",
                 ["BC-410", "BC-510"]),
            ],
        },
    ],
}

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
