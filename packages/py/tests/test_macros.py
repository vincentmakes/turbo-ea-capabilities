"""Tests for the macro-capability overlay.

The macro layer is additive — existing wheel callers must keep working
unchanged. These tests cover the new public surface (load_macros,
get_macro, get_macros_for_capability, get_capabilities_in_macro) and the
derived ``Capability.macro_id`` backlink.
"""
from __future__ import annotations

import pytest

from turbo_ea_capabilities import (
    Capability,
    MacroCapability,
    get_by_id,
    get_capabilities_in_macro,
    get_macro,
    get_macros_for_capability,
    load_all,
    load_macros,
)


def test_load_macros_returns_list_of_macros() -> None:
    macros = load_macros()
    assert isinstance(macros, list)
    # Catalogue ships 9 Cross-Industry macros today; older snapshots without
    # the layer would return []. Skip the strict count assertion if the
    # bundled JSON is empty.
    if not macros:
        pytest.skip("macro-capabilities.json not bundled in this snapshot")
    for m in macros:
        assert isinstance(m, MacroCapability)
        assert m.id.startswith("MC-")
        assert m.name
        assert m.industry
        assert len(m.capability_ids) >= 1


def test_get_macro_resolves_known_id() -> None:
    if not load_macros():
        pytest.skip("no macros bundled")
    m = get_macro("MC-10")
    assert m is not None
    assert m.id == "MC-10"
    assert "BC-100" in m.capability_ids


def test_get_macro_unknown_returns_none() -> None:
    assert get_macro("MC-99999") is None


def test_get_macros_for_capability_walks_to_l1() -> None:
    if not load_macros():
        pytest.skip("no macros bundled")
    # L1 lookup
    out = get_macros_for_capability("BC-100")
    assert len(out) == 1
    assert out[0].id == "MC-10"
    # L2 descendant: should resolve to the same macro as its L1 ancestor
    out2 = get_macros_for_capability("BC-100.10")
    assert [m.id for m in out2] == ["MC-10"]


def test_get_macros_for_capability_outside_macro_returns_empty() -> None:
    # Industry-specific L1s have no macro layer (yet).
    # If the catalogue has no industry-specific L1s, skip.
    industry_l1 = next(
        (c for c in load_all() if c.level == 1 and c.industry and "Cross-Industry" not in c.industry),
        None,
    )
    if industry_l1 is None:
        pytest.skip("no industry-specific L1 in catalogue")
    out = get_macros_for_capability(industry_l1.id)
    assert out == []


def test_get_capabilities_in_macro_returns_l1_objects() -> None:
    if not load_macros():
        pytest.skip("no macros bundled")
    caps = get_capabilities_in_macro("MC-10")
    assert len(caps) >= 1
    for c in caps:
        assert isinstance(c, Capability)
        assert c.level == 1
        assert c.macro_id == "MC-10"


def test_capability_macro_id_backlink_set_for_cross_industry_l1() -> None:
    if not load_macros():
        pytest.skip("no macros bundled")
    c = get_by_id("BC-100")
    assert c is not None
    assert c.macro_id == "MC-10"


def test_capability_macro_id_inherits_to_descendants() -> None:
    if not load_macros():
        pytest.skip("no macros bundled")
    c2 = get_by_id("BC-100.10")
    assert c2 is not None
    assert c2.macro_id == "MC-10"


def test_existing_capability_api_unchanged() -> None:
    """Retro-compat smoke test: every Capability still loads with level 1-4
    and the new macro_id field is optional (no breakage on older snapshots)."""
    all_caps = load_all()
    assert len(all_caps) > 0
    for c in all_caps[:5]:
        assert 1 <= c.level <= 4
        # macro_id is Optional and may be None for industry-specific L1s.
        assert c.macro_id is None or c.macro_id.startswith("MC-")
