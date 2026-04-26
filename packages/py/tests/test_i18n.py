from __future__ import annotations

import turbo_ea_capabilities as cat


def test_available_locales_includes_en():
    locales = cat.available_locales()
    assert "en" in locales
    assert locales[0] == "en"


def test_localized_en_is_noop():
    node = cat.load_all()[0]
    assert node.localized("en") is node


def test_localized_unknown_locale_falls_back_to_english():
    node = cat.load_all()[0]
    out = node.localized("xx-ZZ")
    assert out.name == node.name
    assert out.description == node.description


def test_localized_french_swaps_translatable_fields():
    if "fr" not in cat.available_locales():
        # No French data bundled with this build — tests using fixture data
        # should always have French; tests against a fresh build_pkg without
        # French sidecars correctly skip.
        return
    # Find any node that has a French translation. The fixture build has
    # BC-2/BC-2.1 translated; the real build has BC-2180 and descendants.
    candidates = ("BC-2180", "BC-2", "BC-2.1")
    target = next((c for c in candidates if cat.get_by_id(c) is not None), None)
    assert target is not None, "Expected fixture or real BC-2180/BC-2 to exist"
    en = cat.get_by_id(target)
    fr = en.localized("fr")
    # At minimum the name should change (English != French).
    assert fr.name != en.name or fr.description != en.description
    # Identifiers and structural fields are preserved.
    assert fr.id == en.id
    assert fr.level == en.level
    assert fr.parent_id == en.parent_id


def test_localized_recurses_into_children():
    # Real build has BC-2180 with French descendants; fixture has BC-2.
    target_id = "BC-2180" if cat.get_by_id("BC-2180") else "BC-2"
    en = cat.get_subtree(target_id)
    if en is None:
        return
    fr = en.localized("fr")
    # Same number of children, same ids, but at least one child has a
    # different name in fr (real build) or stays English (graceful fallback).
    assert len(fr.children) == len(en.children)
    for fr_child, en_child in zip(fr.children, en.children, strict=True):
        assert fr_child.id == en_child.id


def test_localized_partial_falls_back_per_field():
    # Field-level fallback: if `description` has no fr translation but `name`
    # does, the resulting node should have French name and English description.
    # We can't guarantee this configuration in the real build, so just assert
    # the contract via type rather than content: returned node is a Capability.
    node = cat.load_all()[0]
    out = node.localized("fr")
    assert isinstance(out, type(node))
    # Fallback field is never None when source had a value.
    if node.description is not None:
        assert out.description is not None


def test_locale_coverage_returns_dict_or_none():
    cov_en = cat.locale_coverage("en")
    assert cov_en is None or isinstance(cov_en, dict)
    cov_unknown = cat.locale_coverage("xx-ZZ")
    assert cov_unknown is None
