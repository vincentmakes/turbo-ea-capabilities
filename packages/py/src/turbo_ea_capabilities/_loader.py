"""Load the bundled JSON catalogue via importlib.resources.

`importlib.resources.files()` works correctly with wheels, editable installs,
zipapps, PyInstaller, and Docker layers - no `__file__` hacks.
"""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import as_file, files
from typing import Iterable, Optional

from ._models import Capability

_PACKAGE = "turbo_ea_capabilities"


def _read_json(name: str) -> object:
    res = files(_PACKAGE) / "data" / name
    with as_file(res) as path:
        return json.loads(path.read_text(encoding="utf-8"))


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


# Module-level constants
_meta = _version_meta()
VERSION: str = str(_meta.get("catalogue_version", "0.0.0"))
SCHEMA_VERSION: str = str(_meta.get("schema_version", "0"))
GENERATED_AT: str = str(_meta.get("generated_at", ""))
NODE_COUNT: int = int(_meta.get("node_count", 0))
