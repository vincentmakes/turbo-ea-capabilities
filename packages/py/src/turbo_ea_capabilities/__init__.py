# SPDX-License-Identifier: MIT
"""Reference Business Architecture catalogue.

Three artefact types are exposed: capabilities (BC), business processes (BP),
and value streams (VS). All data is bundled inside the wheel — no network
access required.

Capabilities answer WHAT the business does. Processes answer HOW work is done.
Value streams describe end-to-end value delivery and link to both other
artefacts. The three layers are orthogonal: capabilities, processes, and value
streams cross-reference each other but none nests under the others.
"""
from ._loader import (
    GENERATED_AT,
    NODE_COUNT,
    PROCESS_COUNT,
    SCHEMA_VERSION,
    VERSION,
    available_locales,
    get_ancestors,
    get_bp_children,
    get_bp_subtree,
    get_business_process,
    get_by_id,
    get_capabilities_in_macro,
    get_children,
    get_macro,
    get_macros_for_capability,
    get_processes_for_capability,
    get_subtree,
    get_value_stream,
    get_value_streams_for_capability,
    get_value_streams_for_process,
    iter_subtree,
    load_all,
    load_business_processes,
    load_macros,
    load_process_tree,
    load_tree,
    load_value_streams,
    locale_coverage,
)
from ._models import (
    BusinessProcess,
    Capability,
    FrameworkRef,
    LocalizedFields,
    MacroCapability,
    ValueStream,
    ValueStreamStage,
)

__all__ = [
    "BusinessProcess",
    "Capability",
    "FrameworkRef",
    "GENERATED_AT",
    "LocalizedFields",
    "MacroCapability",
    "NODE_COUNT",
    "PROCESS_COUNT",
    "SCHEMA_VERSION",
    "VERSION",
    "ValueStream",
    "ValueStreamStage",
    "available_locales",
    "get_ancestors",
    "get_bp_children",
    "get_bp_subtree",
    "get_business_process",
    "get_by_id",
    "get_capabilities_in_macro",
    "get_children",
    "get_macro",
    "get_macros_for_capability",
    "get_processes_for_capability",
    "get_subtree",
    "get_value_stream",
    "get_value_streams_for_capability",
    "get_value_streams_for_process",
    "iter_subtree",
    "load_all",
    "load_business_processes",
    "load_macros",
    "load_process_tree",
    "load_tree",
    "load_value_streams",
    "locale_coverage",
]
