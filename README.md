# turbo-ea-capabilities

An **open-source Business Capability Reference Catalogue**. It is intentionally tool-agnostic and can be used in any Enterprise Architecture management solution — well beyond [Turbo EA](https://www.turbo-ea.org). This site exists to help enterprise architects get started with the implementation of an EA function, by providing a curated, opinionated baseline that teams can adopt, adapt, and extend.

- **Browse online:** [`capabilities.turbo-ea.org`](https://capabilities.turbo-ea.org/) — searchable web catalogue.
- **Source of truth:** YAML files in [`catalogue/`](catalogue/).
- **Public site + JSON API:** [`capabilities.turbo-ea.org`](https://capabilities.turbo-ea.org/) (Cloudflare Pages).
- **Python package:** [`turbo-ea-capabilities`](https://pypi.org/project/turbo-ea-capabilities/) on PyPI — embeds the catalogue as bundled JSON for offline / airgapped consumers.
- **Blog & EA resources:** [`turbo-ea.org/blog`](https://www.turbo-ea.org/blog/).

The naming convention, decomposition rules, and identifier scheme are defined in [`business-capability-governance-model.md`](business-capability-governance-model.md). The operational PR/CI workflow is in [`governance.md`](governance.md).

## Layout

```
turbo-ea-capabilities/
├── catalogue/              # YAML source of truth (one file per L1)
│   ├── _index.yaml
│   └── L1-*.yaml
├── schema/                 # JSON Schema 2020-12 for the YAML shape
├── scripts/                # lint, build_api, build_pkg, cli helpers
├── packages/py/            # Python package (turbo_ea_capabilities)
├── site/                   # Astro static site for browse UI + JSON API
└── .github/workflows/      # lint on PRs, deploy on push, publish on tag
```

## Quick start

```bash
# Install JS deps
npm ci

# Lint the catalogue (runs on every PR)
npm run lint

# Build everything: dist/api/*.json, dist/site/, packages/py/.../data/*.json
npm run build

# Local Astro dev server (after build)
npm run dev

# Python package
cd packages/py
pip install -e ".[dev]"
pytest
python -c "from turbo_ea_capabilities import load_all, VERSION; print(VERSION, len(load_all()))"
```

## Editing the catalogue

Use the helper CLIs to keep diffs clean:

```bash
npm run cap:add       -- --parent BC-2.1 --name "Forecast Reconciliation"
npm run cap:mv        -- --id BC-3.1.2 --new-parent BC-2.1
npm run cap:deprecate -- --id BC-3.1.2 --successor BC-3.1.1 --reason "Merged into BC-3.1.1"
```

All editing rules — what's a capability, how to name it, when to deprecate — are in [`business-capability-governance-model.md`](business-capability-governance-model.md).

## Static API

After `npm run build`, the following endpoints are available under `dist/api/` (and at `capabilities.turbo-ea.org/api/`):

| Path | Returns |
| --- | --- |
| `GET /api/version.json` | `{catalogue_version, schema_version, generated_at, node_count}` |
| `GET /api/capabilities.json` | Flat array of every node, sorted by id |
| `GET /api/tree.json` | Nested tree (one entry per L1) |
| `GET /api/by-l1/<slug>.json` | Single L1 nested subtree |
| `GET /api/capability/<id>.json` | One node + its direct children |

All responses are static, immutable per build, and cacheable by Cloudflare's edge.

## Licence

[MIT](LICENSE).
