# Business Capability Governance Model

> **Purpose:** Provide a TOGAF-aligned, industry-neutral definition, decomposition model, and naming convention for Business Capabilities, suitable for adoption in an enterprise architecture governance framework.
>
> **Scope:** Applies to all Business Capabilities recorded in the Enterprise Architecture repository, regardless of business domain, geography, or organisational unit.
>
> **Status:** Reference model — to be adapted and ratified by the Architecture Review Board.

---

## Table of Contents

1. [Definition](#1-definition)
2. [What a Business Capability Is Not](#2-what-a-business-capability-is-not)
3. [Capability Levels](#3-capability-levels)
4. [Decomposition Rules](#4-decomposition-rules)
5. [Naming Convention](#5-naming-convention)
6. [Identifier Convention](#6-identifier-convention)
7. [Mandatory Metadata](#7-mandatory-metadata)
8. [Worked Example](#8-worked-example)
9. [Governance Process](#9-governance-process)
10. [Glossary](#10-glossary)

---

## 1. Definition

A **Business Capability** is a stable, **outcome-oriented** expression of *what* the enterprise is able to do to deliver value — independent of *how* it does it (process), *who* does it (organisation), *when* it does it (value stream), or *with what* it does it (applications, technology, data).

Building on TOGAF — which defines a capability as "an ability that an organization, person, or system possesses" and frames Business Capabilities as a core building block of the Business Architecture in ADM Phase B and the Content Metamodel — a governance-grade definition adds the following constraints:

> A Business Capability is a **uniquely named, stable, mutually exclusive and collectively exhaustive (MECE)** unit of business ability, expressed as a **noun phrase**, that:
>
> - describes an **outcome the business must be able to deliver**, not an activity it performs;
> - is **decoupled** from organisational structure, value streams, processes, applications, and technology;
> - has a **single accountable business owner** at the enterprise level;
> - can be **assessed** along defined dimensions (maturity, performance, strategic importance, investment, health);
> - exists at a **defined level** in the capability hierarchy, with parent/child relationships that are strictly compositional ("is-part-of"), never sequential or causal.

A Business Capability answers the question **"What must the enterprise be able to do?"** — never "How is it done?", "Who does it?", "When?", or "Where?".

---

## 2. What a Business Capability Is Not

| It is not… | Because… | Belongs in… |
|---|---|---|
| A **process** | Capabilities are stable; processes describe *how* and change frequently | Process model |
| A **value stream** or **business context** (e.g. Order-to-Cash, Procure-to-Pay, Hire-to-Retire) | These describe an end-to-end *flow* that exercises multiple capabilities in sequence | Value stream / business context model |
| A **function** or **department** | Capabilities cut across the org chart; one capability may be exercised by many functions and vice versa | Organisation model |
| An **application** or **service** | Applications *enable* capabilities; one capability may be supported by many applications | Application architecture |
| A **project** or **initiative** | Initiatives *change* capabilities — they are not capabilities themselves | Portfolio / roadmap |
| A **KPI** | KPIs *measure* capability performance; they are attributes, not capabilities | Performance model |
| A **role** or **skill** | Roles and skills are *resources* a capability draws on | Workforce / competency model |

> **Note on Business Context.** Names such as *Order-to-Cash*, *Procure-to-Pay*, *Idea-to-Market*, *Hire-to-Retire* are **business contexts** (end-to-end value streams). They are not Business Capabilities and must not appear in the capability hierarchy. They are modelled in a separate, orthogonal artefact and *linked* to the capabilities they exercise.

---

## 3. Capability Levels

Every node in the hierarchy is a **Business Capability**. There are no separate concepts such as "Domain", "Area", or "Group" above the capability layer — those are categorisation conveniences, not capabilities, and introduce naming ambiguity.

Levels are simply **decomposition depths** of a single concept.

| Level | Type | Purpose | Typical count | Owner profile | Primary governance use |
|---|---|---|---|---|---|
| **L1** | Business Capability | Top-level enterprise capability — broadest ability the enterprise must possess | 10–20 | Executive (C-level / SVP) | Strategic narrative, board-level capability heatmap |
| **L2** | Business Capability | First decomposition — meaningful, owned, assessable unit | 50–150 | Business VP / Function Head | Investment portfolio, strategic themes, roadmap anchoring |
| **L3** | Business Capability | Detailed decomposition — the **core working level** of EA governance, used for application mapping, sourcing decisions, and rationalisation | 200–600 | Director / Head of (delegated SME) | Application-to-capability mapping, build/buy/partner decisions |
| **L4** *(optional)* | Business Capability | Operational granularity — used sparingly, only where L3 is too coarse for a specific decision (e.g. regulated processes, deeply technical operations) | Sparse, on-demand | Subject Matter Expert | Vendor selection, specific solution architecture |

### 3.1 Type vs. Level

- The **type** is always *Business Capability* — at every level.
- The **level** (L1, L2, L3, L4) indicates decomposition depth, not a different kind of object.
- This keeps the model homogeneous, simplifies metadata schemas, and prevents the re-introduction of artificial layers.

---

## 4. Decomposition Rules

The following rules are governance-enforced and apply at every level of the hierarchy.

1. **MECE within a parent.** Children of any node must be Mutually Exclusive and Collectively Exhaustive *relative to that parent*.
2. **Strictly compositional.** A child is *part of* the parent. It is never a step, a phase, a variant, or a use case of the parent.
3. **Single parent.** A capability has exactly one parent. If multi-use is needed, model it as a *shared service* relationship, not a multi-parent edge in the hierarchy.
4. **Stop decomposing** when further breakdown would:
   - start describing *how* (process, activity, procedure);
   - duplicate another branch;
   - no longer add governance value (no distinct owner, no distinct application footprint, no distinct decision to be made).
5. **Symmetry is not required.** One branch may go four levels deep while another stops at L2. Do not force balance.
6. **Maximum depth = L4.** If L5 feels necessary, the model has slipped into process territory — push it to the process layer instead.

---

## 5. Naming Convention

### 5.1 Core rule

**Names are noun phrases. Always. At every level.**

A noun phrase names a *thing* — an ability, a discipline, an outcome. It does not describe an action.

### 5.2 Linguistic rules

| Rule | Specification | Example |
|---|---|---|
| **Part of speech** | Noun or noun phrase only. **No verbs. No verbal phrases.** | ✅ *Customer Order Management* &nbsp;&nbsp; ❌ *Manage Customer Orders* |
| **Verb-derived nouns** | Nominalised forms (*Management*, *Planning*, *Acquisition*, *Inspection*) are nouns and are acceptable | ✅ *Production Planning*, *Capacity Planning* |
| **Bare gerunds** | Acceptable **only** when the gerund has become an established discipline noun (e.g. *Marketing*, *Engineering*, *Accounting*, *Manufacturing*). Gerunds taking an object are forbidden | ✅ *Marketing Management* &nbsp;&nbsp; ❌ *Producing Spare Parts* |
| **Default form for top-level capabilities** | Prefer *X Management* or *X Operations* to remove ambiguity | ✅ *Production Management* &nbsp;&nbsp; ⚠️ *Production* (ambiguous) |
| **Length** | 2–5 words. Short and unambiguous | ✅ *Spare Parts Pricing* &nbsp;&nbsp; ❌ *Pricing of Spare Parts and Aftermarket Components for Service Contracts* |
| **Casing** | Title Case | *Demand Forecasting* |
| **Articles** | No definite or indefinite articles ("the", "a", "an") | ❌ *The Demand Forecasting* |
| **Acronyms** | Spell out unless universally understood (e.g. *HR*, *IT*) | *Enterprise Resource Planning Operations*, not *ERP Ops* |
| **Vendor / product names** | Forbidden | ❌ *SAP Master Data* &nbsp;&nbsp; ✅ *Master Data Management* |
| **Organisation / location names** | Forbidden | ❌ *EMEA Sales Planning* &nbsp;&nbsp; ✅ *Sales Planning* |
| **Value stream / business context names** | Forbidden — these are not capabilities | ❌ *Order-to-Cash* &nbsp;&nbsp; ✅ *Customer Order Management* |
| **Plurals** | Singular for the capability itself; plural only when the noun is inherently plural | *Order Management* (not *Orders Management*); *Human Resources* is acceptable |
| **Language** | One canonical language (typically English) for the model; localised labels stored as attributes |  |
| **Uniqueness** | Name must be unique within the parent; the full path (L1 > L2 > L3 …) must be globally unique |  |

### 5.3 Anti-patterns to reject in review

- Names containing verbs (*Manage*, *Process*, *Handle*, *Perform*, *Execute*, *Deliver*).
- Verbal phrases or gerunds with objects (*Producing Spare Parts*, *Selling to Customers*).
- Names referencing a tool, vendor, system, or technology.
- Names referencing an organisational unit, geography, or business unit.
- Names that read as a process step (*Initial …*, *Final …*, *Step 1 — …*).
- Names representing value streams or end-to-end flows (*Order-to-Cash*, *Procure-to-Pay*).
- Names duplicating another branch (sign of poor MECE).
- Names longer than 5 words (sign of compound concepts that should be split).

### 5.4 Test for compliance

Apply these three tests before accepting a name:

1. **Noun test.** Insert the name into the sentence: *"The enterprise has \_\_\_."* If it reads naturally as a thing the enterprise possesses, it is a noun phrase. If it implies an action, it fails.
2. **Independence test.** Could a different organisation, using different processes, different applications, and different vendors, also have this capability? If not, the name is contaminated by *how*, *who*, or *with what*.
3. **Stability test.** Will this name still make sense in five years if the organisation reorganises and replaces its application landscape? If not, it is too coupled to the current state.

---

## 6. Identifier Convention

Use a **stable numeric identifier** alongside the name. Names may be refined over time; identifiers are immutable once published.

### 6.1 Format

```
BC-<L1>.<L2>[.<L3>][.<L4>]
```

### 6.2 Examples

| Identifier | Level | Name |
|---|---|---|
| `BC-3` | L1 | Customer Management |
| `BC-3.2` | L2 | Customer Order Management |
| `BC-3.2.4` | L3 | Order Capture |
| `BC-3.2.4.1` | L4 | Standard Order Capture |

### 6.3 Numbering rules

- Numbering is **sparse and non-sequential**. Leave gaps (10, 20, 30, …) so future insertions do not force renumbering.
- Once retired, an identifier is **never reused**.
- Identifiers are independent of display order; sorting is by ID, but presentation may follow business logic.

---

## 7. Mandatory Metadata

For a capability to be considered *governed* and accepted into the EA repository, each **L2 capability** must carry the following attributes. **L1** capabilities require the same metadata at a higher level of abstraction. **L3** and **L4** capabilities inherit ownership from their L2 parent unless otherwise specified.

### 7.1 Identification

- **Identifier** (immutable)
- **Name**
- **Level** (L1 – L4)
- **Parent identifier**

### 7.2 Description

- **Definition** — 1 to 3 sentences, outcome-oriented, business language.
- **In-scope examples** — short list of concrete outcomes covered.
- **Out-of-scope examples** — short list of concrete outcomes *not* covered (clarifies MECE boundaries).

### 7.3 Ownership

- **Capability Owner** — named role (not a person), with current incumbent recorded separately.
- **Delegated SME** *(optional)* — for L3 / L4.

### 7.4 Assessment

- **Strategic Importance** — Core / Differentiating / Commodity (or equivalent scale).
- **Maturity** — CMMI 1–5, or a four-level custom scale (e.g. Initial / Repeatable / Defined / Optimised).
- **Health / Performance** — RAG status, with linked KPIs.

### 7.5 Lifecycle

- **Status** — Proposed / Active / Deprecated / Retired.
- **Effective date** — when the current version became active.
- **Last reviewed date**.
- **Next review date**.

### 7.6 Relationships

- **Linked business contexts / value streams** (e.g. which contexts exercise this capability).
- **Linked applications** (via the EA repository).
- **Linked information objects** *(optional)*.
- **Linked organisational units** *(optional, advisory only — does not drive structure)*.

### 7.7 Industry classification

Each capability carries an **Industry** tag indicating where the capability applies. The tag follows three patterns:

- **`Cross-Industry`** — reserved for capabilities universal to virtually all enterprises (e.g. Financial Management, HR Management, Procurement Management). Use this *only* for genuinely universal capabilities.
- **`<Single Industry>`** — for capabilities specific to one industry (e.g. `Banking & Capital Markets` for AML Transaction Monitoring; `Pharmaceuticals & Life Sciences` for Pharmacovigilance).
- **`<Industry 1>; <Industry 2>; ...`** — semicolon-separated for capabilities genuinely shared by 2 or more specific industries but *not* universal. Example: `Manufacturing & Industrial; Engineering Services` for engineering disciplines used in both contexts.

Rules:
- A multi-industry tag is appropriate only when the **same capability scope** is used in each named industry. If the scope differs (e.g. generic Quality Management vs pharma's GMP-specific Pharmaceutical Quality Management), keep them as separate capabilities under their respective industry blocks.
- An L2 capability inherits its parent L1's industry tag unless explicitly overridden. If the L2 has different applicability than its L1, document the override in the description.
- Cross-Industry is **not** an alternative to multi-industry tagging. Cross-Industry means *all*; multi-industry means *some specific subset*. Use multi-industry tagging when only a defined subset of industries shares the capability.
- Tools that filter on Industry must treat the field as a list (split on `;`). The browse UI and the static JSON API both do this; consumers building their own filters should match the same way.

---

## 8. Worked Example

The example below illustrates the conventions applied to a manufacturing-oriented branch. The same rules apply across business domains.

```
BC-2  Production Management                              (L1 Business Capability)
├── BC-2.1  Production Planning                          (L2 Business Capability)
│   ├── BC-2.1.1  Demand-Driven Planning                 (L3 Business Capability)
│   ├── BC-2.1.2  Capacity Planning                      (L3 Business Capability)
│   └── BC-2.1.3  Material Requirements Planning         (L3 Business Capability)
├── BC-2.2  Shop Floor Operations                        (L2 Business Capability)
│   ├── BC-2.2.1  Work Order Management                  (L3 Business Capability)
│   ├── BC-2.2.2  Machine Data Acquisition               (L3 Business Capability)
│   └── BC-2.2.3  Operator Guidance                      (L3 Business Capability)
└── BC-2.3  Quality Management                           (L2 Business Capability)
    ├── BC-2.3.1  Incoming Inspection                    (L3 Business Capability)
    ├── BC-2.3.2  In-Process Quality Control             (L3 Business Capability)
    └── BC-2.3.3  Non-Conformance Management             (L3 Business Capability)
```

**Why this example is conformant:**

- Every node is a noun phrase; no verbs or verbal phrases.
- No vendor, system, or organisational references.
- No business contexts or value stream names (no *Order-to-Cash*, no *Procure-to-Pay*).
- Decomposition is strictly compositional — children are *parts of* parents, not steps in a flow.
- Decomposition stops where the next breakdown would describe *how*.
- Branches are not symmetric — and do not need to be.
- Every node is the same type (*Business Capability*); only the level differs.

---

## 9. Governance Process

### 9.1 Roles

| Role | Responsibility |
|---|---|
| **Chief Enterprise Architect** | Owns the capability *model* (structure, conventions, integrity). |
| **Capability Owner** | Owns an individual capability — its definition, scope, performance. |
| **Architecture Review Board (ARB)** | Approves changes to the capability model. |
| **EA Repository Steward** | Maintains the capability model in the tool of record. |

### 9.2 Change control

Adding, renaming, splitting, merging, or retiring a capability follows a lightweight RFC process:

1. **Proposal** — submitted by any architect or capability owner, including rationale, impact on existing artefacts (applications, projects, KPIs), and proposed effective date.
2. **Review** — Architecture Review Board reviews against this governance model.
3. **Decision** — Approve / Reject / Defer, with documented rationale.
4. **Implementation** — EA Repository Steward applies the change as a YAML pull request against this repository; affected owners are notified.
5. **Communication** — material changes are published in the EA change log.

> **Source of truth.** The catalogue is the YAML under `catalogue/`. Approved changes land as PRs that pass `scripts/lint.ts` (which enforces the schema in `schema/capability.schema.json` and every rule in §3-§7). Spreadsheets, exported CSVs, and direct edits to generated JSON artefacts are *not* a governance channel — they cannot be reviewed, diffed, or rolled back. See [`governance.md`](governance.md) for the operational PR workflow.

### 9.3 Versioning

The capability model is versioned using semantic versioning: `MAJOR.MINOR.PATCH`.

- **MAJOR** — structural changes (L1 reshuffle, level definition changes).
- **MINOR** — additions of new capabilities.
- **PATCH** — renames, definition refinements, metadata updates.

### 9.4 Review cadence

- Each **L2 capability** is reviewed at least **annually** by its owner.
- The **full model** is reviewed every **2 to 3 years** to avoid drift.
- Reviews are tracked via the *Last reviewed* and *Next review* metadata fields.

### 9.5 Reference frameworks

Where an industry reference framework exists, anchor the upper levels (L1 / L2) to it, and diverge below that — where the enterprise's differentiation lives. The catalogue in this repository was built using the references below.

**Cross-industry — process and management**

- **APQC Process Classification Framework** — cross-industry process taxonomy.
- **TOGAF** — enterprise architecture method and content metamodel.
- **DAMA-DMBOK** — data management body of knowledge.
- **ITIL** — IT service management.
- **TBM** — Technology Business Management for IT financial transparency.
- **PRINCE2 / PMI PMBOK** — project and programme management.
- **ADKAR / Prosci** — organisational change management.
- **Three Horizons / stage-gate** — innovation portfolio governance.
- **TRL (Technology Readiness Levels)** — R&D maturation.

**Cross-industry — risk, security, quality, sustainability**

- **NIST Cybersecurity Framework, ISO 27001** — cybersecurity management.
- **ISO 9001** — quality management.
- **ISO 14001 / ISO 45001** — environmental and occupational H&S management.
- **ISO 22301** — business continuity.
- **ISO 55000** — asset management.
- **GHG Protocol, TCFD, ESRS / CSRD, IFRS S1-S2, GRI** — sustainability and climate disclosure.
- **OECD Transfer Pricing Guidelines, BEPS** — tax.
- **IFRS 16 / ASC 842** — lease accounting.
- **FCPA, UK Bribery Act** — anti-bribery and corruption.
- **GDPR** and equivalents — privacy and data protection.

**Manufacturing & engineering services**

- **ISA-95** — manufacturing operations and OT/IT integration.
- **RCM, FMEA, FTA** — reliability and maintenance engineering.
- **Lean / Six Sigma / Kaizen** — continuous improvement.
- **AACE International cost estimation classes** — engineering cost estimation.
- **ISO 19650** — BIM information management.
- **IEC 61511** — safety instrumented systems.
- **HAZOP / HAZID** — process hazard reviews.

**Air Traffic Control**

- **ICAO Annexes 3, 10, 11, 12, 13, 15, 19** — meteorology, aeronautical telecoms, ATS, SAR, accident investigation, AIM, safety management.
- **EUROCONTROL ATFCM, AIRAC, SES/PRB performance scheme** — flow management, AIM cycle, performance.
- **PBN (RNAV/RNP), SWIM, AIXM** — performance-based navigation, system-wide information management, AIM data.
- **COSPAS-SARSAT** — emergency beacon coordination.

**Banking & capital markets**

- **BIAN service domains** — banking capability anchor.
- **Basel III** — capital, LCR, NSFR, IRRBB, FRTB.
- **IFRS 9** — expected credit loss.
- **SR 11-7 / TRIM** — model risk management.
- **ISO 20022, SWIFT GPI** — payment messaging.
- **UCP 600, ISP98, URC 522** — trade finance rules.
- **MiFID II / MiFIR, EMIR, CSDR, SFTR** — market structure, derivatives, settlement, securities financing.
- **FATF recommendations** — AML/CFT.

**Pharmaceuticals & life sciences**

- **ICH guidelines** — E2 (PV), E6 (GCP), E8/E9 (clinical), Q1-Q12 (CMC and quality).
- **ICH eCTD** — regulatory submissions.
- **EU GVP modules, FDA REMS** — pharmacovigilance and risk management.
- **GLP, GCP, GMP, GDP** — non-clinical, clinical, manufacturing, distribution practice.
- **EU GMP Annex 1 (sterile), Annex 16 (QP release)** — sterile manufacturing and batch release.
- **GAMP 5, 21 CFR Part 11** — computerised system validation and electronic records.
- **CDISC SDTM / ADaM** — clinical data standards.
- **DSCSA, EU FMD** — pharmaceutical serialisation and verification.
- **Sunshine Act, EFPIA Disclosure Code** — HCP transparency.
- **GPP3, ICMJE** — publication practice.
- **HTA bodies (NICE, IQWiG, HAS, CADTH)** — health technology assessment.

**Defense & aerospace**

- **DoD 5000 series** — defense acquisition lifecycle.
- **EIA-748** — earned value management systems.
- **FAR / DFARS / CAS** — federal acquisition, defense supplement, cost accounting standards.
- **DoDAF / MoDAF / NAF** — defense architecture frameworks.
- **MIL-HDBK-61** — configuration management.
- **MIL-HDBK-502** — logistic support analysis.
- **S1000D** — technical publication standard.
- **DMSMS** — diminishing manufacturing sources management.
- **ITAR (22 CFR 120-130), EAR (15 CFR 730-774)** — export control of defense and dual-use items.
- **NISPOM (32 CFR 117), CMMC** — industrial security and supply-chain cybersecurity.
- **EKMS / KMI** — cryptographic key management.
- **E.O. 13587, ICD 203** — insider threat and analytic tradecraft standards.
- **Shipley capture management** — bid/proposal practice.

**Other industry anchors not yet exercised in the catalogue but recommended for adoption**

- **eTOM** — telecommunications.
- **ACORD** — insurance.

These references describe *what* organisations in a given industry typically do — useful as a starting point, but they must still be adapted to the enterprise's own context and re-expressed in conformant noun-phrase form where necessary. Citing a framework does not exempt a node from §5 (naming) or §4 (decomposition) — frameworks inform the *shape* of the model, not the *form* of its names.

---

## 10. Glossary

| Term | Definition |
|---|---|
| **ADM** | Architecture Development Method (TOGAF). |
| **ARB** | Architecture Review Board. |
| **Business Capability** | See [Section 1](#1-definition). |
| **Business Context** | An end-to-end flow (value stream, scenario, journey) such as Order-to-Cash or Procure-to-Pay that exercises multiple capabilities in sequence. *Not* a capability. |
| **Capability Map** | A structured representation of capabilities, typically rendered as a hierarchical or tiled diagram. |
| **MECE** | Mutually Exclusive, Collectively Exhaustive. |
| **Noun Phrase** | A grammatical unit whose head is a noun (e.g. *Customer Order Management*). Names a thing; does not describe an action. |
| **TOGAF** | The Open Group Architecture Framework. |
| **Value Stream** | An end-to-end set of activities delivering value to a stakeholder; orthogonal to capabilities. A type of Business Context. |

---

*This document is a reference governance model. It is intended to be adopted, adapted, and ratified by an enterprise's Architecture Review Board to fit local context and tooling.*
