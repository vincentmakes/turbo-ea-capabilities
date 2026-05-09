"""Load the bundled JSON catalogue via importlib.resources.

`importlib.resources.files()` works correctly with wheels, editable installs,
zipapps, PyInstaller, and Docker layers - no `__file__` hacks.

Three artefact types are exposed: capabilities (BC), business processes (BP),
value streams (VS). All three are bundled inside the wheel; downstream
consumers never need to fetch anything at runtime.
"""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import as_file, files
from typing import Iterable, Optional

from ._models import (
    BusinessProcess,
    Capability,
    LocalizedFields,
    ValueStream,
)

_PACKAGE = "turbo_ea_capabilities"


def _read_json(name: str) -> object:
    res = files(_PACKAGE) / "data" / name
    with as_file(res) as path:
        return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(name: str) -> Optional[object]:
    """Read a bundled JSON file or return None if absent.

    Used for optional artefacts (locales.json, i18n/<lang>.json,
    business-processes.json on builds before schema_version 2) so older
    builds without those files still load cleanly.
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
        pid: tuple(sorted(kids, key=_compare_key_bc))
        for pid, kids in parent_to_children.items()
    }


def _compare_key_bc(c: Capability) -> tuple[int, ...]:
    return tuple(int(s) for s in c.id.removeprefix("BC-").split("."))


def _compare_key_bp(b: BusinessProcess) -> tuple[int, ...]:
    return tuple(int(s) for s in b.id.removeprefix("BP-").split("."))


# ---------------------------------------------------------------------------
# Business processes
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _bp_flat_records() -> tuple[BusinessProcess, ...]:
    raw = _read_optional_json("business-processes.json")
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise RuntimeError("business-processes.json must be a list")
    return tuple(BusinessProcess.model_validate(r) for r in raw)


@lru_cache(maxsize=1)
def _bp_tree_records() -> tuple[BusinessProcess, ...]:
    raw = _read_optional_json("bp-tree.json")
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise RuntimeError("bp-tree.json must be a list")
    return tuple(BusinessProcess.model_validate(r) for r in raw)


@lru_cache(maxsize=1)
def _bp_by_id() -> dict[str, BusinessProcess]:
    out: dict[str, BusinessProcess] = {}
    for b in _bp_flat_records():
        out[b.id] = b
    return out


@lru_cache(maxsize=1)
def _bp_children_index() -> dict[str, tuple[BusinessProcess, ...]]:
    parent_to_children: dict[str, list[BusinessProcess]] = {}
    for b in _bp_flat_records():
        if b.parent_id is None:
            continue
        parent_to_children.setdefault(b.parent_id, []).append(b)
    return {
        pid: tuple(sorted(kids, key=_compare_key_bp))
        for pid, kids in parent_to_children.items()
    }


# ---------------------------------------------------------------------------
# Value streams
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _vs_records() -> tuple[ValueStream, ...]:
    raw = _read_optional_json("value-streams.json")
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise RuntimeError("value-streams.json must be a list")
    return tuple(ValueStream.model_validate(r) for r in raw)


@lru_cache(maxsize=1)
def _vs_by_id() -> dict[str, ValueStream]:
    return {v.id: v for v in _vs_records()}


@lru_cache(maxsize=1)
def _version_meta() -> dict:
    raw = _read_json("version.json")
    if not isinstance(raw, dict):
        raise RuntimeError("version.json must be an object")
    return raw


# ---------------------------------------------------------------------------
# Public API: capabilities (existing surface preserved verbatim)
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
    return _hydrate_capability(flat)


def _hydrate_capability(node: Capability) -> Capability:
    kids = _children_index().get(node.id, ())
    if not kids:
        return node
    hydrated = tuple(_hydrate_capability(k) for k in kids)
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
# Public API: business processes
# ---------------------------------------------------------------------------
def load_business_processes() -> list[BusinessProcess]:
    """Flat list of every business process, sorted by id. Empty list if the
    bundled wheel pre-dates schema_version 2 or no BP1 files were imported.
    """
    return list(_bp_flat_records())


def load_process_tree() -> list[BusinessProcess]:
    """Nested tree (one entry per BP1), each with `.children` populated."""
    return list(_bp_tree_records())


def get_business_process(bp_id: str) -> Optional[BusinessProcess]:
    return _bp_by_id().get(bp_id)


def get_bp_children(bp_id: str) -> list[BusinessProcess]:
    return list(_bp_children_index().get(bp_id, ()))


def get_bp_subtree(bp_id: str) -> Optional[BusinessProcess]:
    flat = _bp_by_id().get(bp_id)
    if flat is None:
        return None
    return _hydrate_business_process(flat)


def _hydrate_business_process(node: BusinessProcess) -> BusinessProcess:
    kids = _bp_children_index().get(node.id, ())
    if not kids:
        return node
    hydrated = tuple(_hydrate_business_process(k) for k in kids)
    return node.model_copy(update={"children": hydrated})


def get_processes_for_capability(capability_id: str) -> list[BusinessProcess]:
    """Business processes whose `realizes_capability_ids` include the given
    BC id or any of its ancestors. Returns the full BP nodes (not ids)."""
    cap = _by_id().get(capability_id)
    if cap is None:
        return []
    # Walk the cap's value_stream_stages and the inverse (precomputed at build
    # time): cap.realizes_processes is the direct list.
    out: list[BusinessProcess] = []
    bp_by_id = _bp_by_id()
    for bp_id in cap.realizes_processes:
        bp = bp_by_id.get(bp_id)
        if bp is not None:
            out.append(bp)
    return out


# ---------------------------------------------------------------------------
# Public API: value streams
# ---------------------------------------------------------------------------
def load_value_streams() -> list[ValueStream]:
    """All value streams, sorted by name (insertion order from the YAML)."""
    return list(_vs_records())


def get_value_stream(vs_id: str) -> Optional[ValueStream]:
    return _vs_by_id().get(vs_id)


def get_value_streams_for_capability(capability_id: str) -> list[ValueStream]:
    """Value streams that include the given capability id at any stage.

    Uses the precomputed `Capability.value_stream_stages` reverse index so we
    don't re-scan the full VS list on every call.
    """
    cap = _by_id().get(capability_id)
    if cap is None:
        return []
    stream_ids: set[str] = set()
    for stage_id in cap.value_stream_stages:
        # Stage ids look like "VS-30.20". Stream id is the prefix before the dot.
        stream_ids.add(stage_id.split(".", 1)[0])
    by_id = _vs_by_id()
    return [by_id[sid] for sid in sorted(stream_ids, key=lambda s: int(s.removeprefix("VS-")))
            if sid in by_id]


def get_value_streams_for_process(bp_id: str) -> list[ValueStream]:
    """Value streams whose stages reference the given BP id.

    Uses `BusinessProcess.realized_in_value_streams` reverse index baked at
    build time.
    """
    bp = _bp_by_id().get(bp_id)
    if bp is None:
        return []
    stream_ids: set[str] = set()
    for stage_id in bp.realized_in_value_streams:
        stream_ids.add(stage_id.split(".", 1)[0])
    by_id = _vs_by_id()
    return [by_id[sid] for sid in sorted(stream_ids, key=lambda s: int(s.removeprefix("VS-")))
            if sid in by_id]


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

    `data/i18n/<lang>.json` is a flat object: {"BC-...": {name, ...}, "BP-...": {...}, "VS-...": {...}}.
    """
    if lang == "en":
        return {}
    raw = _read_optional_json(f"i18n/{lang}.json")
    if not isinstance(raw, dict):
        return {}
    out: dict[str, LocalizedFields] = {}
    for entry_id, fields in raw.items():
        if not isinstance(fields, dict):
            continue
        out[entry_id] = LocalizedFields.model_validate(fields)
    return out


def available_locales() -> tuple[str, ...]:
    """All bundled locales including 'en'. Sorted, en first."""
    locales = list(_locales_manifest().get("locales", ["en"]))
    if "en" not in locales:
        locales.insert(0, "en")
    rest = sorted(loc for loc in locales if loc != "en")
    return ("en", *rest)


def locale_coverage(lang: str) -> Optional[dict]:
    """Return coverage stats for `lang` or None.

    With schema_version >= 2 the entry includes `process_count`,
    `processes_translated`, `value_stream_count`, `value_streams_translated`
    in addition to the legacy `total`, `translated`, `l1_files`.
    """
    cov = _locales_manifest().get("coverage", {})
    if not isinstance(cov, dict):
        return None
    entry = cov.get(lang)
    return entry if isinstance(entry, dict) else None


def _localize_capability(node: Capability, lang: str, fallback: str = "en") -> Capability:
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
        update["children"] = tuple(
            _localize_capability(c, lang, fallback) for c in node.children
        )
    return node.model_copy(update=update) if update else node


def _localize_business_process(
    node: BusinessProcess, lang: str, fallback: str = "en"
) -> BusinessProcess:
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
        update["children"] = tuple(
            _localize_business_process(c, lang, fallback) for c in node.children
        )
    return node.model_copy(update=update) if update else node


# Module-level constants
_meta = _version_meta()
VERSION: str = str(_meta.get("catalogue_version", "0.0.0"))
SCHEMA_VERSION: str = str(_meta.get("schema_version", "0"))
GENERATED_AT: str = str(_meta.get("generated_at", ""))
NODE_COUNT: int = int(_meta.get("node_count", 0))
PROCESS_COUNT: int = int(_meta.get("process_count", 0))
