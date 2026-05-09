#!/usr/bin/env python3
"""Industry-specific PCF generator (Phase 2): Healthcare, Life Sciences,
Petroleum (Upstream + Downstream), Aerospace & Defense, Education, Utilities.

Each industry adds 1-2 net-new BP1 files capturing operational processes
genuinely outside the cross-industry PCF baseline. Anchored on:
  - Healthcare Provider:    APQC Healthcare Provider PCF v7.2 + HL7
  - Life Sciences:          APQC Life Sciences PCF v6.1/7.2 + ICH
  - Petroleum:              APQC Upstream/Downstream Petroleum PCF v7.2
  - Aerospace & Defense:    APQC A&D PCF v7.2 + AS9100
  - Education:              APQC Education PCF v7.2
  - Utilities:              APQC Utilities PCF v7.2

References cross-checked via web search (May 2026) — APQC public site is
gated, so structure is anchored on best-available public summaries plus the
cross-industry pattern. Reviewers with verified APQC PDFs should sanity-
check BP2 names before merge.

Usage:
    python3 scripts/import_industry_pcfs_phase2.py --bp1 BP-170
    python3 scripts/import_industry_pcfs_phase2.py --all
"""
from __future__ import annotations

import argparse
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")


def slugify(name: str) -> str:
    out, last_dash = [], True
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch); last_dash = False
        else:
            if not last_dash:
                out.append("-"); last_dash = True
    return "".join(out).strip("-")


# Each entry: BP1 + BP2 only. BP3 deferred to follow-up PRs.
TREE: dict[str, dict] = {}

# ------------------------------------------------------------ Healthcare Provider
TREE["BP-170"] = {
    "id": "BP-170",
    "name": "Deliver Patient Care",
    "description": "Run end-to-end patient care delivery in a hospital or care-network setting: from access through clinical encounters to discharge and post-discharge follow-up.",
    "industry": "Healthcare Providers",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Healthcare Provider PCF v7.2 — Care delivery categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-170.10", "Manage Patient Access and Registration",
         "Receive, register, schedule, and admit patients across inpatient, outpatient, and emergency channels.",
         []),
        ("BP-170.20", "Perform Clinical Assessment and Triage",
         "Triage and clinically assess patients on arrival, including history, examination, and acuity scoring.",
         []),
        ("BP-170.30", "Deliver Clinical Care",
         "Provide clinical care across inpatient, outpatient, surgical, and emergency settings.",
         []),
        ("BP-170.40", "Manage Care Coordination and Transitions",
         "Coordinate care across teams and settings; manage transitions between units, facilities, or to home.",
         []),
        ("BP-170.50", "Discharge and Follow Up",
         "Discharge patients with appropriate instructions, medication reconciliation, and follow-up scheduling.",
         []),
        ("BP-170.60", "Manage Patient Experience",
         "Monitor and manage the patient experience across the care journey, including grievance handling.",
         ["BC-430"]),
    ],
}

TREE["BP-180"] = {
    "id": "BP-180",
    "name": "Manage Clinical Operations and Health Information",
    "description": "Run the operational backbone of a healthcare provider: ancillary clinical services (pharmacy, laboratory, imaging, surgical), health information management, infection prevention, and credentialing.",
    "industry": "Healthcare Providers",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Healthcare Provider PCF v7.2 — Clinical operations categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-180.10", "Manage Pharmacy Operations",
         "Operate inpatient and outpatient pharmacy services, including medication preparation, dispensing, and reconciliation.",
         []),
        ("BP-180.20", "Manage Laboratory Operations",
         "Operate clinical laboratory services across pre-analytical, analytical, and post-analytical phases.",
         []),
        ("BP-180.30", "Manage Imaging and Diagnostics Operations",
         "Operate radiology and imaging services, including modality scheduling, acquisition, and reporting.",
         []),
        ("BP-180.40", "Manage Surgical and Procedural Services",
         "Operate operating rooms and procedural suites, including scheduling, sterile processing, and theatre logistics.",
         []),
        ("BP-180.50", "Manage Health Information and Medical Records",
         "Manage patient medical records, clinical documentation, coding, and information release.",
         ["BC-610"]),
        ("BP-180.60", "Manage Infection Prevention and Control",
         "Run infection-prevention surveillance, controls, and outbreak response across the care environment.",
         ["BC-720", "BC-730"]),
        ("BP-180.70", "Manage Practitioner Credentialing and Privileging",
         "Credential and privilege practising clinicians; manage ongoing competency and peer review.",
         ["BC-300"]),
    ],
}

# ------------------------------------------------------------ Life Sciences
TREE["BP-190"] = {
    "id": "BP-190",
    "name": "Discover and Develop Therapeutics",
    "description": "Conduct discovery, preclinical, and clinical development of therapeutic products through to regulatory submission readiness.",
    "industry": "Pharmaceuticals & Life Sciences",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Life Sciences PCF v6.1/7.2 — Discovery and Development categories"},
    ],
    "realizes": ["BC-810", "BC-820"],
    "children": [
        ("BP-190.10", "Conduct Drug Discovery and Target Identification",
         "Identify and validate biological targets; screen and optimise hit and lead compounds.",
         ["BC-810"]),
        ("BP-190.20", "Conduct Preclinical Development",
         "Conduct in vitro and in vivo preclinical studies; perform IND-enabling work.",
         ["BC-810"]),
        ("BP-190.30", "Conduct Clinical Trials",
         "Plan and conduct clinical trials across Phase I, II, III, and IV under GCP.",
         ["BC-810"]),
        ("BP-190.40", "Manage Clinical Operations and Sites",
         "Operate the clinical-trial machine: site selection, patient recruitment, monitoring, data management.",
         ["BC-810", "BC-300"]),
        ("BP-190.50", "Prepare Regulatory Submissions",
         "Prepare and file regulatory submissions (IND, NDA, BLA, MAA) and respond to agency queries.",
         ["BC-130"]),
    ],
}

TREE["BP-200"] = {
    "id": "BP-200",
    "name": "Manufacture, Supply, and Pharmacovigilance",
    "description": "Manufacture pharmaceutical and biologic products under GMP; manage commercial supply chain; run pharmacovigilance and post-market safety surveillance.",
    "industry": "Pharmaceuticals & Life Sciences",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Life Sciences PCF v6.1/7.2 — Manufacturing and Pharmacovigilance categories"},
    ],
    "realizes": ["BC-520", "BC-130"],
    "children": [
        ("BP-200.10", "Manage GMP Manufacturing Operations",
         "Run GMP-compliant manufacturing of APIs, drug products, and biologics.",
         ["BC-520", "BC-720"]),
        ("BP-200.20", "Manage Quality Assurance and Quality Control",
         "Run QA/QC programs across the product lifecycle, including stability, release testing, and CAPA.",
         ["BC-720"]),
        ("BP-200.30", "Manage Cold-Chain and Pharmaceutical Supply Chain",
         "Operate the pharmaceutical supply chain, including cold-chain logistics, serialisation, and distributor management.",
         ["BC-520", "BC-530"]),
        ("BP-200.40", "Manage Pharmacovigilance and Adverse-Event Reporting",
         "Capture, assess, and report adverse events and safety signals; maintain the safety database and PSUR cycle.",
         ["BC-130", "BC-120"]),
        ("BP-200.50", "Manage Product Registration and Post-Market Compliance",
         "Maintain product registrations across markets and run post-market regulatory commitments and inspections.",
         ["BC-130"]),
    ],
}

# ------------------------------------------------------------ Petroleum
TREE["BP-210"] = {
    "id": "BP-210",
    "name": "Acquire, Explore, and Develop Hydrocarbon Assets",
    "description": "Run upstream petroleum operations from licence acquisition and exploration through field appraisal and development to first hydrocarbons.",
    "industry": "Oil & Gas",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Upstream Petroleum PCF v7.2 — Categories 2.0 'Acquire, Explore, and Appraise Hydrocarbon Assets' and 3.0 'Develop and Deplete Hydrocarbon Assets'"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-210.10", "Acquire Hydrocarbon Licences and Acreage",
         "Acquire exploration and production rights through licence rounds, farm-ins, and asset acquisitions.",
         ["BC-150"]),
        ("BP-210.20", "Explore for Hydrocarbon Resources",
         "Conduct geological and geophysical exploration: seismic acquisition, processing, and prospect generation.",
         []),
        ("BP-210.30", "Appraise and Evaluate Discoveries",
         "Drill appraisal wells and evaluate discoveries to estimate resources and commercial viability.",
         []),
        ("BP-210.40", "Develop Hydrocarbon Assets",
         "Plan, design, and execute field-development projects, including drilling and facilities construction.",
         ["BC-700", "BC-900"]),
        ("BP-210.50", "Manage Subsurface and Reservoir Engineering",
         "Manage subsurface modelling, reservoir engineering, and recovery optimisation across the asset life.",
         []),
    ],
}

TREE["BP-220"] = {
    "id": "BP-220",
    "name": "Produce and Trade Petroleum",
    "description": "Run production operations through to product trading and downstream refining, blending, distribution, and retail fuel marketing.",
    "industry": "Oil & Gas",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Upstream PCF v7.2 (production) + Downstream Petroleum PCF v7.2 (refining, marketing)"},
    ],
    "realizes": ["BC-520"],
    "children": [
        ("BP-220.10", "Operate Hydrocarbon Production",
         "Operate producing wells, surface facilities, and gathering systems; optimise production rates.",
         []),
        ("BP-220.20", "Operate Refining and Processing",
         "Run refining and gas processing: crude distillation, conversion, treatment, and blending.",
         ["BC-520", "BC-720"]),
        ("BP-220.30", "Manage Petroleum Trading and Optimisation",
         "Trade crude, products, and energy; optimise the value chain through commercial decisions.",
         ["BC-210"]),
        ("BP-220.40", "Manage Bulk Distribution and Logistics",
         "Move bulk hydrocarbons through pipelines, marine, rail, and truck; manage terminals and storage.",
         ["BC-520"]),
        ("BP-220.50", "Operate Retail Fuel Marketing",
         "Operate retail fuels and convenience networks, including pricing, supply, and station operations.",
         ["BC-440"]),
        ("BP-220.60", "Manage Hydrocarbon Asset Decommissioning",
         "Plan and execute decommissioning of upstream and downstream assets at end-of-life.",
         ["BC-740", "BC-730"]),
    ],
}

# ------------------------------------------------------------ Aerospace & Defense
TREE["BP-230"] = {
    "id": "BP-230",
    "name": "Manage Aerospace and Defense Programs",
    "description": "Run aerospace and defense programs across the acquisition lifecycle: capture, contract, develop, deliver, sustain, and dispose, including export-control and configuration management.",
    "industry": "Defense & Aerospace",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Aerospace and Defense PCF v7.2 — A&D-specific operating categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-230.10", "Manage Capture and Bid",
         "Pursue defense and aerospace opportunities: bid/no-bid, capture planning, proposal development.",
         ["BC-410"]),
        ("BP-230.20", "Manage Program Contract and Earned Value",
         "Manage the program contract through award, change, modifications, and earned-value reporting.",
         ["BC-150", "BC-900"]),
        ("BP-230.30", "Perform Mission Systems Engineering",
         "Perform systems engineering for defense and aerospace mission systems, including verification and validation.",
         ["BC-810"]),
        ("BP-230.40", "Manage Configuration and Technical Data Package",
         "Maintain configuration of platforms and systems; manage the technical data package across the lifecycle.",
         ["BC-820"]),
        ("BP-230.50", "Manage Export Controls and Security",
         "Manage ITAR / EAR / EU dual-use export controls and program security (industrial security, classified data).",
         ["BC-150", "BC-620"]),
        ("BP-230.60", "Sustain Defense Systems",
         "Sustain in-service defense and aerospace systems: depot maintenance, overhaul, modifications, obsolescence.",
         ["BC-700"]),
        ("BP-230.70", "Manage Disposal and Demilitarisation",
         "Demilitarise and dispose of defense materiel at end-of-life under regulatory and security controls.",
         ["BC-740"]),
    ],
}

# ------------------------------------------------------------ Education
TREE["BP-240"] = {
    "id": "BP-240",
    "name": "Manage Student Lifecycle",
    "description": "Run the end-to-end student lifecycle from prospective recruitment through admissions, enrolment, learning delivery, assessment, graduation, and alumni engagement.",
    "industry": "Education",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Education PCF v7.2 — Student lifecycle categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-240.10", "Recruit and Admit Students",
         "Recruit prospective students and process admissions, including selection and offer-acceptance.",
         []),
        ("BP-240.20", "Enrol and Register Students",
         "Enrol admitted students and register them in courses and programmes for each academic period.",
         []),
        ("BP-240.30", "Deliver Teaching and Learning",
         "Deliver teaching and learning experiences across modes (in-person, online, hybrid).",
         []),
        ("BP-240.40", "Assess Students and Award Credentials",
         "Assess student learning, manage examinations and assignments, and award qualifications.",
         []),
        ("BP-240.50", "Manage Student Support and Wellbeing",
         "Provide academic, financial, mental-health, and accessibility support to enrolled students.",
         []),
        ("BP-240.60", "Manage Graduation and Alumni Relations",
         "Process graduation and confer awards; engage alumni for lifelong relationships and giving.",
         []),
    ],
}

TREE["BP-250"] = {
    "id": "BP-250",
    "name": "Manage Curriculum, Programmes, and Research",
    "description": "Manage the academic backbone: curriculum and programme design, accreditation, research administration, and educational content management.",
    "industry": "Education",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Education PCF v7.2 — Curriculum and research categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-250.10", "Design and Maintain Curriculum and Programmes",
         "Design, approve, and maintain curricula and academic programmes; manage course catalogues.",
         []),
        ("BP-250.20", "Manage Programme Accreditation and Quality Assurance",
         "Manage programme accreditation cycles and academic quality-assurance processes.",
         ["BC-720", "BC-130"]),
        ("BP-250.30", "Administer Research and Scholarship",
         "Administer research grants, ethics, integrity, and research outputs; manage research-data governance.",
         ["BC-150", "BC-610"]),
        ("BP-250.40", "Manage Educational Content and Learning Resources",
         "Develop and curate teaching content, courseware, and learning resources, including digital platforms.",
         ["BC-820"]),
        ("BP-250.50", "Manage Educator Workforce",
         "Plan and manage the academic workforce: recruitment, tenure tracks, peer review, professional development.",
         ["BC-300"]),
    ],
}

# ------------------------------------------------------------ Utilities
TREE["BP-260"] = {
    "id": "BP-260",
    "name": "Operate Energy and Water Asset Operations",
    "description": "Operate utility production and network assets: generation (electric), production and treatment (water), transmission, distribution, and storage.",
    "industry": "Power & Water Utilities",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Utilities PCF v7.2 — Asset operations categories"},
    ],
    "realizes": ["BC-700"],
    "children": [
        ("BP-260.10", "Operate Electricity Generation",
         "Operate electricity generation assets across thermal, hydro, nuclear, and renewable plants.",
         ["BC-700", "BC-720"]),
        ("BP-260.20", "Operate Water Production and Treatment",
         "Operate water abstraction, treatment, and wastewater treatment assets to meet quality standards.",
         ["BC-700", "BC-720", "BC-730"]),
        ("BP-260.30", "Operate Transmission and Distribution Networks",
         "Operate electricity transmission and distribution networks (or water mains and reticulation).",
         ["BC-700"]),
        ("BP-260.40", "Manage Outages, Restoration, and Emergency Response",
         "Detect and respond to outages and emergencies; coordinate restoration crews and customer comms.",
         ["BC-160", "BC-700"]),
        ("BP-260.50", "Manage Energy Storage and Distributed Energy Resources",
         "Operate energy storage and integrate distributed energy resources (DER) and demand response.",
         ["BC-700", "BC-600"]),
        ("BP-260.60", "Manage Network Planning and Capital Investment",
         "Plan utility-network capital investment under regulatory price-control and reliability frameworks.",
         ["BC-230", "BC-130"]),
    ],
}

TREE["BP-270"] = {
    "id": "BP-270",
    "name": "Manage Utility Customer and Regulatory Operations",
    "description": "Run utility-specific customer operations (metering, billing, supply switching, hardship support) and regulatory operations (price control, code compliance, statutory reporting).",
    "industry": "Power & Water Utilities",
    "framework_refs": [
        {"framework": "APQC-PCF", "external_id": "Utilities PCF v7.2 — Customer and regulatory categories"},
    ],
    "realizes": ["BC-100"],
    "children": [
        ("BP-270.10", "Manage Customer Metering and Meter Data",
         "Operate the meter estate (smart and non-smart); collect, validate, estimate, and edit meter data.",
         ["BC-610"]),
        ("BP-270.20", "Operate Utility Billing and Revenue Collection",
         "Calculate utility bills, present bills, run dunning, and manage collections and disconnection.",
         ["BC-200"]),
        ("BP-270.30", "Manage Supply Switching and Customer Onboarding",
         "Manage supply-point onboarding, switching, and tariff changes per market codes.",
         ["BC-420", "BC-430"]),
        ("BP-270.40", "Manage Vulnerable Customer and Hardship Programs",
         "Identify and support vulnerable customers and customers in hardship per regulatory obligations.",
         ["BC-430", "BC-130"]),
        ("BP-270.50", "Manage Regulatory Reporting and Price-Control Submissions",
         "Prepare regulatory rate filings, performance reports, and price-control submissions.",
         ["BC-130", "BC-240"]),
    ],
}


def _emit_yaml(bp1: dict) -> str:
    L = []
    L.append(f"id: {bp1['id']}")
    L.append(f"name: {bp1['name']}")
    L.append("level: 1")
    L.append(f"industry: {bp1['industry']}")
    L.append("description: >-")
    L.append(f"  {bp1['description']}")
    if bp1.get("framework_refs"):
        L.append("framework_refs:")
        for fr in bp1["framework_refs"]:
            L.append("  - framework: " + fr["framework"])
            L.append(f"    external_id: \"{fr['external_id']}\"")
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


def write_bp1(bp1: dict) -> str:
    slug = slugify(bp1["name"])
    path = os.path.join(PROCESSES_DIR, f"BP1-{slug}.yaml")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_emit_yaml(bp1))
    return path


def update_index(new_filename: str):
    idx_path = os.path.join(PROCESSES_DIR, "_index.yaml")
    with open(idx_path) as fh:
        lines = fh.readlines()
    files, header = [], []
    in_files = False
    for ln in lines:
        if ln.startswith("files:"):
            in_files = True
            header.append(ln)
            continue
        if in_files and ln.strip().startswith("- "):
            files.append(ln.strip().lstrip("- "))
        elif not in_files:
            header.append(ln)
    if new_filename not in files:
        files.append(new_filename)
    files = sorted(files)
    with open(idx_path, "w") as fh:
        for ln in header:
            fh.write(ln)
        for f in files:
            fh.write(f"  - {f}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp1", help="Single BP1 to write (e.g. BP-170).")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not (args.bp1 or args.all):
        ap.error("Pass --bp1 <id> or --all")

    targets = list(TREE.keys()) if args.all else [args.bp1]
    for bp1_id in targets:
        if bp1_id not in TREE:
            raise SystemExit(f"Unknown {bp1_id}; defined: {list(TREE.keys())}")
        bp1 = TREE[bp1_id]
        path = write_bp1(bp1)
        update_index(os.path.basename(path))
        print(f"✔ {bp1_id} → {os.path.relpath(path, REPO_ROOT)} "
              f"(industry: {bp1['industry']}, {len(bp1['children'])} BP2)")


if __name__ == "__main__":
    main()
