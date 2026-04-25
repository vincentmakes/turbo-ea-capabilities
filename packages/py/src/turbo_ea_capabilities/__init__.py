"""Reference Business Capability catalogue.

All data is bundled inside the wheel - no network access required.
"""
from ._loader import (
    GENERATED_AT,
    NODE_COUNT,
    SCHEMA_VERSION,
    VERSION,
    get_ancestors,
    get_by_id,
    get_children,
    get_subtree,
    iter_subtree,
    load_all,
    load_tree,
)
from ._models import Capability

__all__ = [
    "Capability",
    "GENERATED_AT",
    "NODE_COUNT",
    "SCHEMA_VERSION",
    "VERSION",
    "get_ancestors",
    "get_by_id",
    "get_children",
    "get_subtree",
    "iter_subtree",
    "load_all",
    "load_tree",
]
