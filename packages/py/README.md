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
    load_macros,
    get_macros_for_capability,
    VERSION,
    SCHEMA_VERSION,
    GENERATED_AT,
)

print(f"Catalogue {VERSION} (schema v{SCHEMA_VERSION}), built {GENERATED_AT}")
print(f"{len(load_all())} capabilities, {len(load_macros())} macro capabilities")

root = get_subtree("BC-2")
for child in root.children:
    print(f"  {child.id}  {child.name}")

# Macro navigation overlay (optional — empty list on pre-macro snapshots)
for m in load_macros():
    print(f"  {m.id}  {m.name}  ({len(m.capability_ids)} L1s)")
print(get_macros_for_capability("BC-100"))  # → [MacroCapability(id='MC-10', ...)]
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
| `load_macros()` | `list[MacroCapability]` — executive navigation overlay above L1 (empty on snapshots without the layer) |
| `get_macro(mc_id)` | `MacroCapability \| None` |
| `get_macros_for_capability(bc_id)` | `list[MacroCapability]` — the ≤1 macro claiming the BC's L1 ancestor |
| `get_capabilities_in_macro(mc_id)` | `list[Capability]` — L1 capabilities grouped by the macro |

`Capability` (with new optional `macro_id` backlink), `MacroCapability`, `BusinessProcess`, `ValueStream` are all frozen Pydantic v2 models — see `_models.py`. The macro layer is purely additive: existing `Capability` fields are unchanged and `SCHEMA_VERSION` is not bumped when only macros are added or edited.

## Macro capabilities

When the L1 layer of the catalogue is too large for unaided executive consumption, the wheel ships an optional **Macro Capability** overlay that groups L1s into a small set of executive-level domains for navigation. The Cross-Industry baseline currently ships 9 macros covering all 41 Cross-Industry L1s; industry-specific L1s do not (yet) have a macro layer.

The overlay is:

- **Optional.** Older wheels without `data/macro-capabilities.json` keep working — `load_macros()` returns `[]`.
- **Additive.** No existing field on `Capability`/`BusinessProcess`/`ValueStream` was changed. `Capability` gains one new optional field, `macro_id: Optional[str]`, populated at build time on every L1 (and inherited via prefix lookup to descendants). `SCHEMA_VERSION` is unchanged.
- **Orthogonal.** Macros do not enter the BC tree, do not participate in value-stream stage links, and do not realize processes. They group L1s — that's all.

```python
from turbo_ea_capabilities import (
    load_macros,
    get_macro,
    get_macros_for_capability,
    get_capabilities_in_macro,
)

# 1. Render Cross-Industry as 9 executive cards
for macro in load_macros():
    if macro.industry == "Cross-Industry":
        print(f"{macro.id}  {macro.name}  ({len(macro.capability_ids)} L1s)")

# 2. Breadcrumb / category label on a capability detail page
m = get_macros_for_capability("BC-100.10.20")  # walks to L1 BC-100
# → [MacroCapability(id='MC-10', name='Enterprise Governance & Risk', ...)]

# 3. Drill into a macro
caps = get_capabilities_in_macro("MC-10")
# → [Capability(id='BC-100', ...), Capability(id='BC-110', ...), ...]

# 4. Translate the macro display name
fr = get_macro("MC-10").localized("fr")
print(fr.name)  # "Gouvernance d'Entreprise et Risque"
```

The model is documented in [Section 13 of the governance doc](https://github.com/vincentmakes/turbo-ea-capabilities/blob/main/business-capability-governance-model.md#13-macro-capability-layer).

## Versioning

Two version numbers travel together:

- `VERSION` — semver of the catalogue content.
- `SCHEMA_VERSION` — integer; bumps only on non-additive field/value changes.

Pin against `SCHEMA_VERSION` to detect breaking shape changes; pin against `VERSION` minor for additive content updates.

## Source

The catalogue YAML and build pipeline live at <https://github.com/vincentmakes/turbo-ea-capabilities>.
