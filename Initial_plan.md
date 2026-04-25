# Business Capability Reference Catalogue — Implementation Plan

## Context

You currently maintain a Business Capability reference catalogue as a spreadsheet plus a written naming-convention/governance model. The goals are:

1. **Systemize the source of data** — replace the spreadsheet with a structured, versioned, lint-checked source of truth.
2. **Expose it publicly** — `business-capabilities.turbo-ea.org` (Cloudflare Pages) with a browsing UI (filter, tree view), CSV/JSON export based on filters, and a read-only JSON API.
3. **Native consumption in Turbo EA** — admins browse the catalogue inside Turbo EA and **selectively import** capability branches (a node + its subtree) as `BusinessCapability` cards. Not a continuous sync — explicit, branch-scoped imports only.

**Constraints**
- Site must be hostable on Cloudflare Pages (static-first).
- Offline / airgapped Turbo EA deployments must work → catalogue ships as a Python package (PyPI) embedded in `backend/pyproject.toml`.
- Governance must remain PR-driven (your existing model preserved).

**Outcome**
- Separate public repo (`turbo-ea-capabilities`) holding YAML source, build pipeline, Python package, and Astro site.
- CF Pages serves the site + a static JSON API (`/api/*.json`) generated from the YAML at build time.
- Turbo EA gains a "Browse & Import Capabilities" admin screen that reads from the bundled Python package and creates `BusinessCapability` cards for a chosen subtree.

---

## Architecture overview

```
┌──────────────────────── turbo-ea-capabilities (separate repo) ────────────────────────┐
│                                                                                       │
│  catalogue/L1-*.yaml  ──┐                                                             │
│       (source of truth) │                                                             │
│                         ▼                                                             │
│                   scripts/build.ts ──┬──► dist/api/*.json   (CF Pages → static API)   │
│                                      ├──► dist/site/        (CF Pages → browse UI)   │
│                                      └──► packages/py/.../data/*.json                │
│                                                          │                            │
│                                                          ▼                            │
│                                              python -m build → wheel → PyPI           │
└───────────────────────────────────────────────────────────┬───────────────────────────┘
                                                            │
                                          pip install turbo-ea-capabilities
                                                            │
                                                            ▼
┌──────────────────────────── turbo-ea (this repo) ─────────────────────────────────────┐
│  backend/pyproject.toml: turbo-ea-capabilities>=X.Y                                    │
│                                                                                        │
│  Admin → Browse & Import Capabilities                                                  │
│   ├─ GET /api/v1/capability-catalogue/tree    (reads bundled package)                  │
│   ├─ POST /api/v1/capability-catalogue/import-branch                                   │
│   │     {root_id, include_descendants, parent_card_id?}                                │
│   │     → creates BusinessCapability cards, wired via parent_id                        │
│   └─ Stores `catalogueId` in card.attributes for idempotency                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key data flow rules**
- YAML is the only place humans edit. JSON is always generated.
- The Python package is a **build artifact** — `data/*.json` is gitignored and produced by CI before `python -m build`.
- Turbo EA never reads YAML and never calls the public API at runtime. It reads the bundled JSON via `importlib.resources`.
- `attributes["catalogueId"]` on each imported card is the single idempotency key.

---

## Phases (each ships independently)

| Phase | Output | Unblocks |
|------|--------|----------|
| 1 | Catalogue repo bootstrap: YAML schema, file layout, lint | Phases 2–4 |
| 2 | Build pipeline: YAML → JSON API artifacts | Phases 3–5 |
| 3 | Python package (`turbo-ea-capabilities`) on PyPI | Phase 5 |
| 4 | CF Pages site (browse UI + static JSON API) | Public consumption |
| 5 | Turbo EA "Browse & Import Branch" admin feature | Internal consumption |

---

## Phase 1 — Catalogue repo bootstrap

### Repo layout

```
turbo-ea-capabilities/
├── README.md
├── LICENSE                           # decide: MIT / CC-BY-SA / proprietary
├── governance.md                     # codify your existing naming convention
├── CODEOWNERS                        # one team per L1 file
├── .github/
│   └── workflows/
│       ├── lint.yml                  # runs on every PR
│       ├── deploy-site.yml           # CF Pages on push to main
│       └── publish-package.yml       # PyPI on tag v*
├── catalogue/                        # YAML source of truth
│   ├── L1-customer.yaml
│   ├── L1-finance.yaml
│   └── ...
├── schema/
│   └── capability.schema.json        # JSON Schema 2020-12
├── scripts/
│   ├── lint.ts                       # schema + naming + parent-exists + sort
│   ├── build_api.ts                  # YAML → dist/api/*.json
│   ├── build_pkg.ts                  # YAML → packages/py/.../data/*.json
│   └── cli/                          # `capabilities add`, `capabilities mv`
├── site/                             # Astro static site (Phase 4)
├── packages/py/                      # Python package (Phase 3)
└── package.json                      # root: TS toolchain, dev deps
```

### YAML schema (per-L1 file)

One file per top-level capability, full subtree nested inline. Children sorted by `id` (lint-enforced) so reordering produces no diff noise.

```yaml
# catalogue/L1-customer.yaml
id: CUS
name: Customer Management
level: 1
owner: customer-architecture-guild
description: |
  Capabilities related to managing the customer lifecycle, from
  acquisition through retention.
tags: [public, core]
references:
  - https://internal.wiki/capabilities/customer
children:
  - id: CUS-001
    name: Customer Acquisition
    level: 2
    description: |
      Activities and processes used to attract new customers.
    aliases: [customer-attraction]
    children:
      - id: CUS-001-001
        name: Lead Capture
        level: 3
        children: []
      - id: CUS-001-002
        name: Lead Qualification
        level: 3
        deprecated: true
        deprecation_reason: |
          Merged into CUS-001-001 in v1.4. Use CUS-001-001.
        successor_id: CUS-001-001
        children: []
```

### Field set (the shape `lint.ts` and the package both validate against)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Stable. Regex enforced (your naming convention — placeholder pattern below). |
| `name` | string | yes | Display name. |
| `level` | int (1–5) | yes | Must equal depth in tree. Lint enforces. |
| `parent_id` | string \| null | (computed) | Filled by build, not authored. |
| `description` | string | no | Multi-line block scalar (`|`). |
| `aliases` | string[] | no | Searchable alt names. |
| `owner` | string | no | Inherited from L1 if absent. |
| `tags` | string[] | no | Free-form taxonomy. |
| `references` | string[] | no | URLs. |
| `deprecated` | bool | no | Default false. |
| `deprecation_reason` | string | no | Required when `deprecated: true`. |
| `successor_id` | string | no | Must reference an existing id. |
| `metadata` | object | no | Escape hatch for governance fields not yet promoted to first-class. |
| `children` | array | yes | Empty array `[]` for leaves. |

### `schema/capability.schema.json`

JSON Schema 2020-12, recursive via `$ref`. Validates the parsed YAML object. Used by both `lint.ts` (CI) and the Python package's Pydantic model (so the schema lives in one canonical place — the package's `_models.py` is the Python mirror).

### `scripts/lint.ts` checks

1. Each file parses as YAML 1.2 strict.
2. Validates against `schema/capability.schema.json`.
3. **ID convention regex** — replace placeholder with your real pattern. Suggested starting point: `^[A-Z]{2,4}(-\d{3})*$` (e.g., `CUS`, `CUS-001`, `CUS-001-002`).
4. **Levels match depth** — `level: 1` only at root; children always `parent.level + 1`.
5. **Children sorted by `id`** ascending.
6. **No duplicate IDs** across all files (build a global map, fail on collision).
7. **`successor_id` exists** somewhere in the catalogue.
8. **`deprecation_reason` required** if `deprecated: true`.
9. **Quoted strings** for any value that would coerce (booleans, numbers, dates) — defensive against YAML 1.1 footguns.
10. **No orphan files** — every file is registered in `catalogue/_index.yaml` (optional but useful for build determinism).

### `governance.md`

Carry over your existing written governance verbatim. Add a "How to propose a change" section explaining the PR flow:
1. Branch off `main`.
2. Edit the relevant `L1-*.yaml` (or use `npm run cap:add`).
3. Open PR — CI lint runs.
4. CODEOWNERS for that L1 file is auto-requested for review.
5. On merge, site redeploys; on tag, package publishes.

### `CODEOWNERS`

```
catalogue/L1-customer.yaml   @yourorg/customer-architects
catalogue/L1-finance.yaml    @yourorg/finance-architects
governance.md                @yourorg/ea-leads
schema/                      @yourorg/ea-leads
```

### Tiny CLI (`scripts/cli/`)

To avoid hand-editing 500-line YAMLs:

```bash
npm run cap:add -- --parent CUS-002 --name "Customer Onboarding Workflow"
npm run cap:mv  -- --id CUS-001-002 --new-parent FIN-003
npm run cap:deprecate -- --id CUS-001-002 --successor CUS-001-001 --reason "..."
```

~150 lines of TypeScript using `yaml` (eemeli/yaml — preserves comments + ordering on round-trip). Pays for itself in week one.

---

## Phase 2 — Build pipeline (YAML → JSON artifacts)

A single deterministic build run produces three things from the same source:

```
catalogue/L1-*.yaml
        │
        ▼
   scripts/build_api.ts          scripts/build_pkg.ts
        │                                │
        ▼                                ▼
   dist/site/                     packages/py/src/turbo_ea_capabilities/data/
   dist/api/                          ├── capabilities.json
   ├── capabilities.json              ├── tree.json
   ├── tree.json                      └── version.json
   ├── version.json
   ├── by-l1/
   │   ├── customer.json
   │   └── ...
   └── capability/
       ├── CUS.json
       ├── CUS-001.json
       └── CUS-001-002.json
```

### Output specs

**`capabilities.json`** — flat array, every node, with computed `parent_id`:
```json
[
  {"id": "CUS", "name": "Customer Management", "level": 1, "parent_id": null, "description": "...", "deprecated": false, ...},
  {"id": "CUS-001", "name": "Customer Acquisition", "level": 2, "parent_id": "CUS", ...},
  {"id": "CUS-001-001", "name": "Lead Capture", "level": 3, "parent_id": "CUS-001", ...}
]
```

**`tree.json`** — same data, nested via `children` arrays. Used by the site for the tree view and by Turbo EA for the import browser.

**`by-l1/{slug}.json`** — per-L1 nested subtree. Cheap to fetch when only one domain is needed.

**`capability/{id}.json`** — single node + its direct children IDs. Powers detail pages.

**`version.json`** — `{ "catalogue_version": "1.4.2", "schema_version": "1", "generated_at": "2026-04-25T12:00:00Z", "node_count": 1234 }`.

### Build invariants (assert in `build_api.ts`, fail loudly)

- All nodes have unique `id`.
- All `successor_id` references resolve.
- All non-root nodes have a `parent_id` produced from tree position.
- Output JSON is sorted deterministically (so build outputs diff cleanly across runs).
- `version.json.catalogue_version` matches the git tag (CI enforces on tagged builds; on `main` builds, uses `<last-tag>+<sha>`).

### Versioning rules

- **`catalogue_version`** — semver tag on `main`. Bump per release: minor for additions, patch for description tweaks/typo fixes, major for renames or ID-scheme changes that break consumers.
- **`schema_version`** — separate integer that bumps **only** when the field set or value semantics change in a non-additive way. Pinned in the Python package as `SCHEMA_VERSION`.
- The two are independent: catalogue v1.4.2 and v1.5.0 can both have `schema_version: 1`. Consumers pin schema, not catalogue version.

### CI workflows

**`.github/workflows/lint.yml`** — runs on every PR:
```yaml
- npm ci
- npm run lint            # scripts/lint.ts
- npm run build:api       # asserts build invariants
- npm run build:pkg       # asserts package builds
- (cd packages/py && pip install -e ".[dev]" && pytest)
```

**`.github/workflows/deploy-site.yml`** — runs on push to `main`:
```yaml
- npm ci
- npm run build           # produces dist/site/ + dist/api/
- cloudflare/pages-action@v1 (uploads dist/)
```

**`.github/workflows/publish-package.yml`** — runs on tag `v*`:
```yaml
- npm ci
- npm run build:pkg
- cd packages/py
- python -m build --wheel --sdist
- twine upload dist/*
```

---

## Phase 3 — Python package (`turbo-ea-capabilities`)

### Package layout

```
packages/py/
├── pyproject.toml
├── README.md
├── src/turbo_ea_capabilities/
│   ├── __init__.py             # re-exports public API
│   ├── _models.py              # Pydantic Capability model
│   ├── _loader.py              # importlib.resources reader
│   ├── data/                   # gitignored — populated by build_pkg.ts
│   │   ├── .gitkeep
│   │   ├── capabilities.json
│   │   ├── tree.json
│   │   └── version.json
│   └── py.typed                # marker file → mypy/pyright pick up types
└── tests/
    ├── test_loader.py
    ├── test_models.py
    └── fixtures/
        └── small_catalogue.json
```

### `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "turbo-ea-capabilities"
dynamic = ["version"]            # read from data/version.json at build time
description = "Reference Business Capability catalogue for Turbo EA"
requires-python = ">=3.11"
dependencies = ["pydantic>=2.0"]
authors = [{ name = "Turbo EA Maintainers" }]
license = { text = "MIT" }       # match repo LICENSE choice

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov"]

[tool.hatch.version]
source = "code"
path = "scripts/_version.py"     # reads data/version.json

[tool.hatch.build.targets.wheel]
packages = ["src/turbo_ea_capabilities"]
include = ["src/turbo_ea_capabilities/data/*.json"]

[tool.hatch.build.targets.wheel.force-include]
"src/turbo_ea_capabilities/data" = "turbo_ea_capabilities/data"
```

### Public API (`src/turbo_ea_capabilities/__init__.py`)

```python
"""Reference Business Capability catalogue.

All data is bundled. No network access required.
"""
from ._loader import (
    load_all,
    load_tree,
    get_by_id,
    get_children,
    get_subtree,        # NEW — returns a node + all descendants (used by Turbo EA branch import)
    get_ancestors,      # NEW — root → node path (used by Turbo EA to reproduce hierarchy)
)
from ._models import Capability
from ._loader import VERSION, SCHEMA_VERSION, GENERATED_AT

__all__ = [
    "Capability",
    "load_all",
    "load_tree",
    "get_by_id",
    "get_children",
    "get_subtree",
    "get_ancestors",
    "VERSION",
    "SCHEMA_VERSION",
    "GENERATED_AT",
]
```

### `_models.py` (Pydantic v2 — matches Turbo EA stack)

```python
from pydantic import BaseModel, Field
from typing import Optional

class Capability(BaseModel):
    model_config = {"frozen": True}     # immutable post-load

    id: str
    name: str
    level: int = Field(ge=1, le=5)
    parent_id: Optional[str] = None
    description: Optional[str] = None
    aliases: list[str] = []
    owner: Optional[str] = None
    tags: list[str] = []
    references: list[str] = []
    deprecated: bool = False
    deprecation_reason: Optional[str] = None
    successor_id: Optional[str] = None
    metadata: dict = {}
    children: list["Capability"] = []   # populated only by load_tree() / get_subtree()
```

### `_loader.py` (sketch)

```python
import json
from functools import lru_cache
from importlib.resources import files
from ._models import Capability

_DATA = files("turbo_ea_capabilities") / "data"

@lru_cache(maxsize=1)
def _flat() -> list[Capability]:
    raw = json.loads((_DATA / "capabilities.json").read_text(encoding="utf-8"))
    return [Capability(**r) for r in raw]

@lru_cache(maxsize=1)
def _tree() -> list[Capability]:
    raw = json.loads((_DATA / "tree.json").read_text(encoding="utf-8"))
    return [Capability(**r) for r in raw]

@lru_cache(maxsize=1)
def _version_meta() -> dict:
    return json.loads((_DATA / "version.json").read_text(encoding="utf-8"))

VERSION: str = _version_meta()["catalogue_version"]
SCHEMA_VERSION: str = str(_version_meta()["schema_version"])
GENERATED_AT: str = _version_meta()["generated_at"]

def load_all() -> list[Capability]: ...
def load_tree() -> list[Capability]: ...
def get_by_id(id: str) -> Capability | None: ...
def get_children(id: str) -> list[Capability]: ...
def get_subtree(id: str) -> Capability | None: ...        # node + nested descendants
def get_ancestors(id: str) -> list[Capability]: ...       # root → node (excludes node itself)
```

`importlib.resources.files()` works correctly with wheels, editable installs, zipapps, PyInstaller, and Docker layers. No `__file__` hacks.

### Tests

- Round-trip: load every node, every node has a resolvable parent (or is root).
- `get_subtree("CUS-001")` returns the expected number of descendants.
- `Capability` model rejects `level: 6`, missing `name`, etc.
- Version constants are non-empty strings.

---

## Phase 4 — CF Pages site + JSON API

### Stack choice

**Astro** for the site. Reasons:
- Static-first, no SSR runtime needed → trivial CF Pages deploy.
- Islands architecture lets the filter UI be a single React/Preact island while the rest is plain HTML.
- Built-in support for emitting raw JSON files alongside HTML pages → the static API and the site come out of one build.
- Mature ecosystem, fast incremental builds.

Reject Next.js (overkill, SSR complications) and plain HTML (no routing/component reuse).

### Site layout

```
site/
├── astro.config.mjs            # site URL, base, integrations
├── package.json
├── public/                     # favicon, robots.txt, openapi.json (optional)
├── src/
│   ├── data/
│   │   └── load.ts             # imports ../../dist/api/*.json at build time
│   ├── components/
│   │   ├── CapabilityTree.tsx  # React island — collapsible tree
│   │   ├── FilterPanel.tsx     # React island — level/owner/tag/deprecated filters
│   │   ├── ExportButton.tsx    # React island — CSV/JSON export of filtered set
│   │   └── CapabilityCard.astro
│   ├── layouts/
│   │   └── Base.astro
│   ├── pages/
│   │   ├── index.astro                  # full tree + filters
│   │   ├── l1/[slug].astro              # per-L1 view (one file per L1, dynamic route)
│   │   ├── capability/[id].astro        # per-capability detail
│   │   ├── search.astro                 # full-text search
│   │   ├── about.astro                  # links to governance, schema, repo
│   │   └── api/                         # static JSON endpoints
│   │       ├── capabilities.json.ts
│   │       ├── tree.json.ts
│   │       ├── version.json.ts
│   │       ├── by-l1/[slug].json.ts
│   │       └── capability/[id].json.ts
│   └── styles/global.css
└── tsconfig.json
```

Astro's file-based routing turns `pages/api/capabilities.json.ts` into `https://business-capabilities.turbo-ea.org/api/capabilities.json` — a static file, served from CF's edge cache, free.

### Browse UI features

- **Tree view** (default): collapsible, full hierarchy, lazy-rendered for L4+.
- **Table view** toggle: AG-Grid-Community-style flat table (use `@tanstack/react-table` — lighter than AG Grid for static use).
- **Filter panel**:
  - Level checkbox group (1–5)
  - Owner multiselect
  - Tag multiselect
  - "Show deprecated" toggle (default off)
  - Free-text search across `name`, `aliases`, `description`
- **Export**:
  - "Export filtered as CSV" — client-side CSV from the current filter result
  - "Export filtered as JSON" — same data, JSON shape matching `capabilities.json`
- **Detail page** per capability:
  - Breadcrumb (root → ... → this node)
  - Children list
  - Aliases, owner, tags, references
  - Deprecation banner if applicable
  - "Permalink" + "Raw JSON" + "Copy ID" buttons
  - "View on GitHub" link to the source line in the YAML file

### API surface (read-only, public, cacheable)

| URL | Returns |
|-----|---------|
| `GET /api/version.json` | `{catalogue_version, schema_version, generated_at, node_count}` |
| `GET /api/capabilities.json` | flat array, all nodes |
| `GET /api/tree.json` | nested tree |
| `GET /api/by-l1/{slug}.json` | single-L1 nested subtree |
| `GET /api/capability/{id}.json` | single node + direct children IDs |

All responses static, immutable per build, served with `Cache-Control: public, max-age=300, s-maxage=86400`. CF Pages handles edge caching.

**OpenAPI** — optionally publish `public/openapi.json` documenting the four endpoints, so consumers can codegen clients.

### Cloudflare Pages config

- **Build command**: `npm run build` (orchestrates `lint` → `build_api` → `build_pkg` → `astro build`)
- **Output dir**: `dist/` (Astro emits `site/` content here; `dist/api/*.json` already lives here from `build_api.ts`)
- **Custom domain**: `business-capabilities.turbo-ea.org` (CNAME on your DNS to the Pages project)
- **Environment**: none required for build (no secrets in repo)
- **Branch deploys**: enabled — every PR gets a preview URL, reviewers can browse the catalogue change before merge

### Search implementation

Build-time index using **Pagefind** (zero-config static search). It crawls the rendered Astro pages and emits a static index served from `/pagefind/`. Runs as part of the Astro build. No server, no API keys.

### Optional polish (not v1)

- RSS feed of catalogue changes (`/api/changes.rss`) — nice for stakeholder awareness.
- `application/ld+json` structured data on detail pages for SEO.
- Diff view between two catalogue versions (compare two `version.json`s).

---

## Phase 5 — Turbo EA: Browse & Import Branch (selective, not sync)

### Behaviour summary

**Not** a continuous sync. The admin:
1. Opens **Admin → Capability Catalogue Browser** (new page).
2. Browses the catalogue tree (loaded from the bundled Python package — no network).
3. Picks a node (any level) — that node and optionally its descendants form the "branch".
4. Optionally chooses an **existing** `BusinessCapability` card to graft the imported branch under (otherwise the branch becomes a new top-level subtree).
5. Reviews a preview: which catalogue nodes are new, which already exist locally (matched by `catalogueId`), what the resulting card hierarchy will look like.
6. Confirms → backend creates `BusinessCapability` cards for the new nodes, wires `parent_id` to reproduce the catalogue hierarchy, and skips already-imported nodes (idempotent).

There is **no** orphan tracking, **no** auto-update of previously-imported cards, **no** background job. Every import is an explicit, scoped admin action.

### Idempotency key

Each imported card stores its catalogue ID:
```python
card.attributes["catalogueId"] = "CUS-001-002"
card.attributes["catalogueVersion"] = "1.4.2"   # version at import time, informational
card.attributes["catalogueImportedAt"] = "2026-04-25T..."
```

Match strategy on re-import: query
```sql
SELECT id FROM cards
WHERE type = 'BusinessCapability'
  AND attributes ->> 'catalogueId' = :catalogue_id
```
A node already in the cards table is **not** re-created; its existing card is reused as a parent for any new descendants in the branch.

### Files to add

**`backend/app/services/capability_catalogue_service.py`** (new) — pure business logic, no FastAPI imports:

```python
"""Browse the bundled capability catalogue and import branches as cards."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from turbo_ea_capabilities import (
    Capability,
    VERSION as CATALOGUE_VERSION,
    SCHEMA_VERSION,
    get_subtree,
    load_tree,
)
from app.models import Card, User
from app.services.event_bus import publish

@dataclass
class ImportPreview:
    root_id: str
    nodes_new: list[str]            # catalogueIds that will be created
    nodes_existing: list[str]       # catalogueIds already in cards table
    parent_card_id: str | None      # graft point (if any)
    catalogue_version: str
    schema_version: str

@dataclass
class ImportResult:
    created_card_ids: list[str]
    skipped_catalogue_ids: list[str]
    catalogue_version: str

async def get_catalogue_tree() -> list[Capability]:
    """Read-only: returns the full bundled tree."""
    return load_tree()

async def preview_branch_import(
    db: AsyncSession,
    *,
    root_id: str,
    include_descendants: bool,
    parent_card_id: str | None,
) -> ImportPreview:
    subtree = get_subtree(root_id)
    if subtree is None:
        raise ValueError(f"Unknown catalogue id: {root_id}")
    nodes = _walk(subtree, include_descendants)
    existing_ids = await _existing_catalogue_ids(db, [n.id for n in nodes])
    return ImportPreview(
        root_id=root_id,
        nodes_new=[n.id for n in nodes if n.id not in existing_ids],
        nodes_existing=sorted(existing_ids),
        parent_card_id=parent_card_id,
        catalogue_version=CATALOGUE_VERSION,
        schema_version=SCHEMA_VERSION,
    )

async def import_branch(
    db: AsyncSession,
    *,
    user: User,
    root_id: str,
    include_descendants: bool,
    parent_card_id: str | None,
) -> ImportResult:
    subtree = get_subtree(root_id)
    if subtree is None:
        raise ValueError(f"Unknown catalogue id: {root_id}")
    nodes = _walk(subtree, include_descendants)

    # Resolve already-imported nodes once
    existing = await _existing_catalogue_id_to_card_id(db, [n.id for n in nodes])

    # BFS: create cards in parent-before-child order; wire parent_id from
    # either an already-imported card or a card we just created.
    created: list[str] = []
    skipped: list[str] = []
    id_to_card_id: dict[str, str] = dict(existing)
    now = datetime.now(timezone.utc).isoformat()

    for node in nodes:                                 # nodes is BFS-ordered
        if node.id in existing:
            skipped.append(node.id)
            continue

        # Determine the parent card for this node.
        if node.parent_id and node.parent_id in id_to_card_id:
            local_parent_id = id_to_card_id[node.parent_id]
        elif node.id == root_id:
            local_parent_id = parent_card_id            # admin's chosen graft point
        else:
            # Should be impossible after BFS — defensive
            local_parent_id = None

        card = Card(
            type="BusinessCapability",
            name=node.name,
            description=node.description,
            parent_id=local_parent_id,
            attributes={
                "catalogueId": node.id,
                "catalogueVersion": CATALOGUE_VERSION,
                "catalogueImportedAt": now,
                "capabilityLevel": f"L{node.level}",
                # extras the catalogue carries that fit BusinessCapability:
                **({"aliases": node.aliases} if node.aliases else {}),
                **({"tags": node.tags} if node.tags else {}),
                **({"deprecated": True} if node.deprecated else {}),
            },
        )
        db.add(card)
        await db.flush()                                # need card.id for children
        id_to_card_id[node.id] = str(card.id)
        created.append(str(card.id))
        await publish("card.created", {"id": str(card.id), "type": "BusinessCapability"})

    await db.commit()
    return ImportResult(
        created_card_ids=created,
        skipped_catalogue_ids=skipped,
        catalogue_version=CATALOGUE_VERSION,
    )

# --- helpers (omitted in detail for brevity) ---
def _walk(root: Capability, include_descendants: bool) -> list[Capability]: ...
async def _existing_catalogue_ids(db, ids: list[str]) -> set[str]: ...
async def _existing_catalogue_id_to_card_id(db, ids) -> dict[str, str]: ...
```

Mirrors the bulk-card pattern from `backend/app/services/seed_demo.py:5688–5730` (db.add per row, single commit).

**`backend/app/api/v1/capability_catalogue.py`** (new) — three routes:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user, require_permission
from app.models import User
from app.services import capability_catalogue_service as svc

router = APIRouter(prefix="/capability-catalogue", tags=["capability-catalogue"])


class ImportBranchIn(BaseModel):
    root_id: str
    include_descendants: bool = True
    parent_card_id: str | None = None


@router.get(
    "/tree",
    dependencies=[Depends(require_permission("admin.metamodel"))],
)
async def get_tree(user: User = Depends(get_current_user)):
    """Returns the bundled catalogue tree. No network access."""
    tree = await svc.get_catalogue_tree()
    from turbo_ea_capabilities import VERSION, SCHEMA_VERSION
    return {
        "catalogue_version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "tree": [t.model_dump() for t in tree],
    }


@router.post(
    "/import-branch/preview",
    dependencies=[Depends(require_permission("admin.metamodel"))],
)
async def preview(
    payload: ImportBranchIn,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await svc.preview_branch_import(
            db,
            root_id=payload.root_id,
            include_descendants=payload.include_descendants,
            parent_card_id=payload.parent_card_id,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.post(
    "/import-branch",
    dependencies=[Depends(require_permission("admin.metamodel"))],
)
async def import_branch(
    payload: ImportBranchIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return await svc.import_branch(
            db,
            user=user,
            root_id=payload.root_id,
            include_descendants=payload.include_descendants,
            parent_card_id=payload.parent_card_id,
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
```

Permission check follows the convention in `backend/app/api/v1/servicenow.py:715–775` — uses `Depends(require_permission(...))`. `admin.metamodel` is reused since BusinessCapability cards are metamodel-adjacent reference data; no new permission key is required for v1.

### Files to edit

**`backend/pyproject.toml`** — add to `dependencies`:
```toml
"turbo-ea-capabilities>=1.0,<2.0",
```
(Constrain on the **minor** so `SCHEMA_VERSION` major bumps require an explicit Turbo EA pin update.)

**`backend/app/api/v1/router.py`** — register the new router (one line, mirrors the other 34 routers).

**`backend/app/services/__init__.py`** — export `capability_catalogue_service` if the existing convention does that. (Skim before editing.)

**(Optional) `backend/app/core/permissions.py`** — only if you decide the import deserves its own permission key (e.g., `capabilities.import`). Recommendation: skip for v1, reuse `admin.metamodel`. Add a dedicated key only if the audit story demands it.

No new SQLAlchemy model, no Alembic migration — the data fits in `card.attributes` JSONB.

### Frontend (Turbo EA)

**New file: `frontend/src/features/admin/CapabilityCatalogueBrowser.tsx`** — full-page admin route at `/admin/capability-catalogue`.

UI components:
- Tree view of the catalogue (left pane) — uses MUI `TreeView` or a small custom collapsible.
- Detail pane (right) — selected node's metadata, plus an "Import this branch" button.
- Import dialog:
  - Radio: "This node only" / "This node + all descendants" (default: descendants).
  - Autocomplete: "Graft under existing capability card" — searches existing `BusinessCapability` cards. Optional. If empty, the branch root becomes a top-level card.
  - Calls `POST /capability-catalogue/import-branch/preview` → shows preview ("12 new, 3 already imported").
  - Confirm → `POST /capability-catalogue/import-branch` → toast with created-count + link to inventory filtered to BusinessCapability.

Routing: add a lazy `import()` line in `App.tsx` next to the other admin routes.

Translation keys: add to `frontend/src/i18n/locales/{locale}/admin.json` for **all 8 locales** (mandatory per CLAUDE.md i18n checklist):
- `admin.capabilityCatalogue.title`
- `admin.capabilityCatalogue.importButton`
- `admin.capabilityCatalogue.importPreview.summary` (with `{{new}}` and `{{existing}}` interpolation)
- `admin.capabilityCatalogue.importMode.nodeOnly`
- `admin.capabilityCatalogue.importMode.withDescendants`
- `admin.capabilityCatalogue.graftUnder.label`
- `admin.capabilityCatalogue.graftUnder.placeholder`
- `admin.capabilityCatalogue.deprecatedBadge`
- `admin.capabilityCatalogue.success` (with `{{count}}` interpolation, plural _one/_other)

### Documentation (per CLAUDE.md docs checklist)

- New page: `docs/admin/capability-catalogue.md` (+ all 7 locale variants).
- Add to `nav:` in `mkdocs.yml` with translated labels.
- Add screenshot entry to `scripts/screenshots/pages.ts` (sequential id, e.g., `27_admin_capability_catalogue`) AND reference the image in the doc page in all 8 locales.
- Glossary: add "Capability Catalogue" entry.

### CHANGELOG + version bump

- Bump `/VERSION` minor (new feature).
- Add `## [X.Y.0] - YYYY-MM-DD` heading to `CHANGELOG.md` with an `### Added` line.

### Tests

**Backend** (`backend/tests/services/test_capability_catalogue_service.py`):
- `preview_branch_import` returns correct new/existing split when some nodes already imported.
- `import_branch` creates the right number of cards, in correct parent-child order.
- Re-running `import_branch` on the same root is idempotent (zero new cards on second run).
- `parent_card_id` is honoured: graft point becomes parent of the branch root.
- Unknown `root_id` raises (→ 404 in route).

Use the savepoint-rollback factory pattern (`create_user`, etc.) per `backend/tests/conftest.py`.

The package itself is a runtime dependency in tests — install via `pip install -e ".[dev]"` in the test env. Pin a known catalogue version in tests (override via a fixture that monkeypatches `turbo_ea_capabilities.VERSION` and the JSON fixtures).

**Frontend** (`frontend/src/features/admin/CapabilityCatalogueBrowser.test.tsx`):
- Renders tree from mocked `GET /capability-catalogue/tree`.
- Calls preview before final import.
- Disables "Import" button while preview is loading.

---

## Critical files (reference)

### In the new `turbo-ea-capabilities` repo (to create)

| Path | Purpose |
|------|---------|
| `catalogue/L1-*.yaml` | Source of truth |
| `schema/capability.schema.json` | JSON Schema for lint |
| `scripts/lint.ts` | All lint rules |
| `scripts/build_api.ts` | YAML → `dist/api/*.json` |
| `scripts/build_pkg.ts` | YAML → `packages/py/.../data/*.json` |
| `packages/py/pyproject.toml` | Python package config |
| `packages/py/src/turbo_ea_capabilities/__init__.py` | Public Python API |
| `packages/py/src/turbo_ea_capabilities/_models.py` | Pydantic Capability |
| `packages/py/src/turbo_ea_capabilities/_loader.py` | importlib.resources reader |
| `site/src/pages/index.astro` | Browse home |
| `site/src/pages/api/*.ts` | Static JSON endpoints |
| `.github/workflows/lint.yml` | PR lint |
| `.github/workflows/deploy-site.yml` | CF Pages deploy |
| `.github/workflows/publish-package.yml` | PyPI publish on tag |
| `governance.md` | Codified naming convention |
| `CODEOWNERS` | Per-L1 ownership |

### In `turbo-ea` (to add/edit)

| Path | Action | Reference / pattern |
|------|--------|---------------------|
| `backend/pyproject.toml` | Edit — add `turbo-ea-capabilities` dep | `backend/pyproject.toml:6–24` |
| `backend/app/services/capability_catalogue_service.py` | New | Mirrors bulk-create pattern at `backend/app/services/seed_demo.py:5688–5730` |
| `backend/app/api/v1/capability_catalogue.py` | New | Route style from `backend/app/api/v1/servicenow.py:715–775` |
| `backend/app/api/v1/router.py` | Edit — register router | Existing pattern in same file |
| `backend/tests/services/test_capability_catalogue_service.py` | New | Conftest factories at `backend/tests/conftest.py` |
| `frontend/src/features/admin/CapabilityCatalogueBrowser.tsx` | New | Layout + i18n style from `frontend/src/features/admin/MetamodelAdmin.tsx` |
| `frontend/src/App.tsx` | Edit — add lazy route | Existing lazy admin imports |
| `frontend/src/i18n/locales/{8 locales}/admin.json` | Edit — add keys | Per CLAUDE.md i18n checklist |
| `docs/admin/capability-catalogue.md` (+ 7 locale variants) | New | Per CLAUDE.md docs checklist |
| `mkdocs.yml` | Edit — nav + locale labels | Existing nav structure |
| `scripts/screenshots/pages.ts` | Edit — new entry | Per CLAUDE.md screenshot rules |
| `VERSION` | Edit — minor bump | Single source of truth |
| `CHANGELOG.md` | Edit — new heading + entry | Keep a Changelog format |

### Existing utilities to reuse (do not reinvent)

- `PermissionService.require_permission` — `backend/app/services/permission_service.py`
- `require_permission(...)` FastAPI dependency — `backend/app/api/deps.py`
- `event_bus.publish` — `backend/app/services/event_bus.py` (emit `card.created` for SSE)
- `Card` ORM model — `backend/app/models/card.py`
- Card factory in tests — `backend/tests/conftest.py` (`create_card`, `create_user`, `create_card_type`)
- `useResolveLabel` / `useResolveMetaLabel` — `frontend/src/hooks/useResolveLabel.ts` (for any displayed metamodel label)

---

## Verification

### Catalogue repo (Phase 1–4)

```bash
# In the new repo
npm ci
npm run lint                           # must pass on a hand-authored sample
npm run build                          # produces dist/api/*.json + dist/site/
npm run preview                        # local Astro server, click around the UI

# Python package
cd packages/py
pip install -e ".[dev]"
pytest                                 # loader + model tests
python -c "from turbo_ea_capabilities import load_all, VERSION; \
           print(VERSION, len(load_all()))"

# Static API smoke test (after build)
cat dist/api/version.json | jq .
cat dist/api/capabilities.json | jq 'length'
cat dist/api/by-l1/customer.json | jq '.children | length'
```

PR preview deploys via CF Pages — open the preview URL and verify:
- Tree renders, filters work, export downloads a CSV with the filtered subset.
- `/api/capabilities.json` returns the full catalogue.
- Detail page for a known ID renders with breadcrumb + children.

### Turbo EA integration (Phase 5)

```bash
# Backend
cd backend
ruff format . && ruff check .          # mandatory pre-commit per CLAUDE.md
pip install -e ".[dev]"                # picks up turbo-ea-capabilities from PyPI
python -m pytest tests/services/test_capability_catalogue_service.py -q
./scripts/test.sh                      # full suite, ephemeral postgres

# Frontend
cd frontend
npm run lint
npm run test:run
npm run build

# Manual end-to-end
docker compose up --build -d
# 1. Log in as admin → /admin/capability-catalogue
# 2. Tree loads (no network call to public site — confirm via DevTools)
# 3. Pick a leaf → "Import this node only" → preview shows 1 new, 0 existing
# 4. Confirm → toast "1 capability imported"
# 5. Pick the same leaf again → preview shows 0 new, 1 existing → no duplicates
# 6. Pick a parent → "Import with descendants" → preview correct
# 7. Check inventory: BusinessCapability cards appear with the expected hierarchy
# 8. Open a card → attributes include catalogueId, catalogueVersion, catalogueImportedAt
```

### Versioning sanity

```bash
# In Turbo EA, after import:
docker compose exec backend python -c \
  "from turbo_ea_capabilities import VERSION, SCHEMA_VERSION; \
   print(f'catalogue={VERSION} schema={SCHEMA_VERSION}')"
```

---

## Open decisions (worth confirming before/during execution)

1. **Repo + package visibility** — public GitHub + public PyPI (simplest, free, indexable) vs private GitHub + private package index (GitHub Packages or a private PyPI). Drives CI auth setup. Plan defaults to **public** but works either way.

2. **Catalogue licence** — MIT? CC-BY-SA? Proprietary "internal-only"? Affects the `LICENSE` file and the `license` field in `pyproject.toml`. Default in plan: MIT.

3. **ID convention regex** — your existing governance doc has the pattern. Drop it into `scripts/lint.ts`. The plan uses `^[A-Z]{2,4}(-\d{3})*$` as a placeholder.

4. **Permission key** — reuse `admin.metamodel` (recommended for v1) vs add `capabilities.import` to `core/permissions.py`. The latter buys you a finer audit / role split if you later want non-admin EA leads to import. Plan defaults to **reuse**.

5. **What catalogue fields to mirror onto the imported card** — the plan stores `catalogueId`, `catalogueVersion`, `catalogueImportedAt`, `capabilityLevel` (already a BusinessCapability field), plus `aliases`/`tags`/`deprecated` if present. Confirm that's the right slice; anything else (e.g., `owner`) you want surfaced needs a corresponding field in the BusinessCapability `fields_schema`.

6. **Which existing card to graft under** — the plan supports an optional `parent_card_id`. Confirm this is desired vs always importing as new top-level capabilities.

7. **Descendant-only mode** — plan supports "node only" and "node + descendants". Worth confirming that's enough; we could also offer "all ancestors up to root" but it's rarely useful in practice.

8. **Re-import behaviour for the same node** — plan = idempotent skip (existing card untouched). Alternative: warn + offer "Update name/description from catalogue" toggle. Out of scope for v1; revisit after first usage.

9. **Astro vs other static framework** — plan picks Astro. If you have an existing strong preference (Next static export, plain Eleventy, etc.), substitute — the YAML → JSON pipeline is framework-agnostic.

10. **Catalogue v0.x bootstrap content** — initial seed: do you import the spreadsheet wholesale, or hand-curate L1+L2 first and iterate? Plan assumes a `scripts/import_spreadsheet.ts` one-shot tool to generate the initial YAML files from your existing CSV/XLSX, then humans take over via PRs.
