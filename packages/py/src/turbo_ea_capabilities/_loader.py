"""Load the bundled JSON catalogue via importlib.resources.

`importlib.resources.files()` works correctly with wheels, editable installs,
zipapps, PyInstaller, and Docker layers - no `__file__` hacks.
"""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import as_file, files
from typing import Iterable, Optional

from ._models import Capability, LocalizedFields

_PACKAGE = "turbo_ea_capabilities"


def _read_json(name: str) -> object:
    res = files(_PACKAGE) / "data" / name
    with as_file(res) as path:
        return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(name: str) -> Optional[object]:
    """Read a bundled JSON file or return None if absent.

    Used for optional artefacts (locales.json, i18n/<lang>.json) so older
    builds without translation data still load cleanly.
    """
    res = files(_PACKAGE) / "data" / name
    try:
        with as_file(res) as path:
            if not path.is_file():
                return None
            return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ModuleNotFoundError):
        return None


@lru_cache(maxsize=1)
def _flat_records() -> tuple[Capability, ...]:
    raw = _read_json("capabilities.json")
    if not isinstance(raw, list):
        raise RuntimeError("capabilities.json must be a list")
    return tuple(Capability.model_validate(r) for r in raw)


@lru_cache(maxsize=1)
def _tree_records() -> tuple[Capability, ...]:
    raw = _read_json("tree.json")
    if not isinstance(raw, list):
        raise RuntimeError("tree.json must be a list")
    return tuple(Capability.model_validate(r) for r in raw)


@lru_cache(maxsize=1)
def _by_id() -> dict[str, Capability]:
    out: dict[str, Capability] = {}
    for c in _flat_records():
        out[c.id] = c
    return out


@lru_cache(maxsize=1)
def _children_index() -> dict[str, tuple[Capability, ...]]:
    """Map parent_id -> tuple of direct children, sorted by id."""
    parent_to_children: dict[str, list[Capability]] = {}
    for c in _flat_records():
        if c.parent_id is None:
            continue
        parent_to_children.setdefault(c.parent_id, []).append(c)
    return {
        pid: tuple(sorted(kids, key=_compare_key))
        for pid, kids in parent_to_children.items()
    }


def _compare_key(c: Capability) -> tuple[int, ...]:
    return tuple(int(s) for s in c.id.removeprefix("BC-").split("."))


@lru_cache(maxsize=1)
def _version_meta() -> dict:
    raw = _read_json("version.json")
    if not isinstance(raw, dict):
        raise RuntimeError("version.json must be an object")
    return raw


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def load_all() -> list[Capability]:
    """Flat list of every capability, sorted by id."""
    return list(_flat_records())


def load_tree() -> list[Capability]:
    """Nested tree (one entry per L1), each with `.children` populated."""
    return list(_tree_records())


def get_by_id(capability_id: str) -> Optional[Capability]:
    return _by_id().get(capability_id)


def get_children(capability_id: str) -> list[Capability]:
    return list(_children_index().get(capability_id, ()))


def get_subtree(capability_id: str) -> Optional[Capability]:
    """Return the node with `.children` populated recursively."""
    flat = _by_id().get(capability_id)
    if flat is None:
        return None
    return _hydrate(flat)


def _hydrate(node: Capability) -> Capability:
    kids = _children_index().get(node.id, ())
    if not kids:
        return node
    hydrated = tuple(_hydrate(k) for k in kids)
    return node.model_copy(update={"children": hydrated})


def get_ancestors(capability_id: str) -> list[Capability]:
    """Root → parent path (excludes the node itself).

    Returns an empty list for the root or for an unknown id.
    """
    by_id = _by_id()
    node = by_id.get(capability_id)
    if node is None:
        return []
    chain: list[Capability] = []
    cursor = node
    while cursor.parent_id is not None:
        parent = by_id.get(cursor.parent_id)
        if parent is None:
            break
        chain.append(parent)
        cursor = parent
    chain.reverse()
    return chain


def iter_subtree(capability_id: str) -> Iterable[Capability]:
    """BFS-order iterator over a node and its descendants (parent before child)."""
    root = _by_id().get(capability_id)
    if root is None:
        return
    queue: list[Capability] = [root]
    children_index = _children_index()
    while queue:
        cur = queue.pop(0)
        yield cur
        queue.extend(children_index.get(cur.id, ()))


# ---------------------------------------------------------------------------
# Localization
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _locales_manifest() -> dict:
    """Read locales.json or synthesize an English-only manifest."""
    raw = _read_optional_json("locales.json")
    if isinstance(raw, dict):
        return raw
    return {"default": "en", "locales": ["en"], "coverage": {}}


@lru_cache(maxsize=8)
def _locale_table(lang: str) -> dict[str, LocalizedFields]:
    """Map id -> LocalizedFields for `lang`. Empty dict if locale not bundled.

    `data/i18n/<lang>.json` is a flat object: {"BC-...": {name, description, ...}}.
    """
    if lang == "en":
        return {}
    raw = _read_optional_json(f"i18n/{lang}.json")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, LocalizedFields] = {}
    for cap_id, fields in raw.items():
        if not isinstance(fields, dict):
            continue
        out[cap_id] = LocalizedFields.model_validate(fields)
    return out


def available_locales() -> tuple[str, ...]:
    """All bundled locales including 'en'. Sorted, en first.

    Use this to feature-detect which languages this wheel ships, e.g.::

        if user_lang in available_locales():
            cap = cap.localized(user_lang)
    """
    locales = list(_locales_manifest().get("locales", ["en"]))
    if "en" not in locales:
        locales.insert(0, "en")
    rest = sorted(loc for loc in locales if loc != "en")
    return ("en", *rest)


def locale_coverage(lang: str) -> Optional[dict]:
    """Return coverage stats for `lang` (total, translated, l1_files), or None.

    Convenience for CI / observability - call sites don't need this for
    runtime translation.
    """
    cov = _locales_manifest().get("coverage", {})
    if not isinstance(cov, dict):
        return None
    entry = cov.get(lang)
    return entry if isinstance(entry, dict) else None


def _localize(node: Capability, lang: str, fallback: str = "en") -> Capability:
    """Return a copy of `node` with translatable fields swapped to `lang`.

    Recurses into `children`. Missing per-field translations fall back to
    the source (English) value. `lang == "en"` is a no-op.
    """
    if lang == "en":
        return node
    table = _locale_table(lang)
    fields = table.get(node.id)
    update: dict[str, object] = {}
    if fields is not None:
        if fields.name is not None:
            update["name"] = fields.name
        if fields.description is not None:
            update["description"] = fields.description
        if fields.aliases:
            update["aliases"] = fields.aliases
        if fields.in_scope:
            update["in_scope"] = fields.in_scope
        if fields.out_of_scope:
            update["out_of_scope"] = fields.out_of_scope
    if node.children:
        update["children"] = tuple(_localize(c, lang, fallback) for c in node.children)
    return node.model_copy(update=update) if update else node


# Module-level constants
_meta = _version_meta()
VERSION: str = str(_meta.get("catalogue_version", "0.0.0"))
SCHEMA_VERSION: str = str(_meta.get("schema_version", "0"))
GENERATED_AT: str = str(_meta.get("generated_at", ""))
NODE_COUNT: int = int(_meta.get("node_count", 0))
