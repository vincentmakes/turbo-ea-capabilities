# turbo-ea-capabilities

Reference Business Capability catalogue for [Turbo EA](https://turbo-ea.org), bundled as a Python package.

All catalogue data ships inside the wheel — no network access required at runtime. Designed for offline / airgapped Turbo EA deployments.

## Install

```bash
pip install turbo-ea-capabilities
```

## Usage

```python
from turbo_ea_capabilities import (
    load_all,
    load_tree,
    get_by_id,
    get_children,
    get_subtree,
    get_ancestors,
    VERSION,
    SCHEMA_VERSION,
    GENERATED_AT,
)

print(f"Catalogue {VERSION} (schema v{SCHEMA_VERSION}), built {GENERATED_AT}")
print(f"{len(load_all())} capabilities")

root = get_subtree("BC-2")
for child in root.children:
    print(f"  {child.id}  {child.name}")
```

## API

| Function | Returns |
| --- | --- |
| `load_all()` | `list[Capability]` — flat, every node, sorted by id |
| `load_tree()` | `list[Capability]` — nested, one entry per L1 |
| `get_by_id(id)` | `Capability \| None` |
| `get_children(id)` | `list[Capability]` — direct children only |
| `get_subtree(id)` | `Capability \| None` — node with `.children` populated recursively |
| `get_ancestors(id)` | `list[Capability]` — root → parent (excludes the node itself) |

`Capability` is a frozen Pydantic v2 model — see `_models.py`.

## Versioning

Two version numbers travel together:

- `VERSION` — semver of the catalogue content.
- `SCHEMA_VERSION` — integer; bumps only on non-additive field/value changes.

Pin against `SCHEMA_VERSION` to detect breaking shape changes; pin against `VERSION` minor for additive content updates.

## Source

The catalogue YAML and build pipeline live at <https://github.com/vincentmakes/turbo-ea-capabilities>.
