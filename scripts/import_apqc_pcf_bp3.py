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
