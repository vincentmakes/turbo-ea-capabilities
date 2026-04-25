from __future__ import annotations

import turbo_ea_capabilities as cat


def test_version_constants_present():
    assert cat.VERSION
    assert cat.SCHEMA_VERSION
    assert cat.GENERATED_AT


def test_load_all_returns_every_node():
    nodes = cat.load_all()
    assert len(nodes) == cat.NODE_COUNT
    ids = {n.id for n in nodes}
    assert "BC-2" in ids
    assert "BC-3" in ids


def test_load_tree_returns_l1_nodes_with_children():
    tree = cat.load_tree()
    assert any(t.id == "BC-2" for t in tree)
    bc2 = next(t for t in tree if t.id == "BC-2")
    assert len(bc2.children) >= 1


def test_get_by_id():
    bc2 = cat.get_by_id("BC-2")
    assert bc2 is not None
    assert bc2.name == "Production Management"
    assert cat.get_by_id("DOES-NOT-EXIST") is None


def test_get_children_direct_only():
    kids = cat.get_children("BC-2")
    ids = [k.id for k in kids]
    assert "BC-2.1" in ids
    # Grandchild must not appear
    assert "BC-2.1.1" not in ids


def test_get_subtree_recursively_populates_children():
    sub = cat.get_subtree("BC-2.1")
    assert sub is not None
    assert sub.id == "BC-2.1"
    nested_ids = {c.id for c in sub.children}
    assert "BC-2.1.1" in nested_ids


def test_get_ancestors_returns_root_to_parent():
    chain = cat.get_ancestors("BC-2.1.1")
    assert [a.id for a in chain] == ["BC-2", "BC-2.1"]


def test_get_ancestors_for_root_is_empty():
    assert cat.get_ancestors("BC-2") == []


def test_get_ancestors_for_unknown_is_empty():
    assert cat.get_ancestors("DOES-NOT-EXIST") == []


def test_iter_subtree_bfs():
    seen = [c.id for c in cat.iter_subtree("BC-2")]
    assert seen[0] == "BC-2"
    # All descendants present
    assert "BC-2.1" in seen
    assert "BC-2.1.1" in seen


def test_every_node_has_resolvable_parent_or_is_root():
    by_id = {n.id: n for n in cat.load_all()}
    for n in by_id.values():
        if n.level == 1:
            assert n.parent_id is None
        else:
            assert n.parent_id in by_id


def test_successor_id_resolves_when_present():
    by_id = {n.id: n for n in cat.load_all()}
    for n in by_id.values():
        if n.successor_id:
            assert n.successor_id in by_id
