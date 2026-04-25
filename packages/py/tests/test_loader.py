from __future__ import annotations

import turbo_ea_capabilities as cat

# Stable fixture ids drawn from the canonical dataset.
# BC-100 (Strategic Management) and BC-200 (Financial Management) are the
# first two L1 capabilities in the Strategy/Finance clusters; both have
# multiple L2 children and are very unlikely to be renamed.
ROOT_ID = "BC-100"
ROOT_NAME = "Strategic Management"
SECOND_ROOT_ID = "BC-200"
CHILD_ID = "BC-100.10"  # Strategic Planning (L2 under BC-100)


def test_version_constants_present():
    assert cat.VERSION
    assert cat.SCHEMA_VERSION
    assert cat.GENERATED_AT


def test_load_all_returns_every_node():
    nodes = cat.load_all()
    assert len(nodes) == cat.NODE_COUNT
    ids = {n.id for n in nodes}
    assert ROOT_ID in ids
    assert SECOND_ROOT_ID in ids


def test_load_tree_returns_l1_nodes_with_children():
    tree = cat.load_tree()
    assert any(t.id == ROOT_ID for t in tree)
    root = next(t for t in tree if t.id == ROOT_ID)
    assert len(root.children) >= 1


def test_get_by_id():
    root = cat.get_by_id(ROOT_ID)
    assert root is not None
    assert root.name == ROOT_NAME
    assert cat.get_by_id("DOES-NOT-EXIST") is None


def test_get_children_direct_only():
    kids = cat.get_children(ROOT_ID)
    ids = [k.id for k in kids]
    assert CHILD_ID in ids
    # Children's parent_id must point back at the root
    for k in kids:
        assert k.parent_id == ROOT_ID


def test_get_subtree_recursively_populates_children():
    sub = cat.get_subtree(ROOT_ID)
    assert sub is not None
    assert sub.id == ROOT_ID
    nested_ids = {c.id for c in sub.children}
    assert CHILD_ID in nested_ids


def test_get_ancestors_returns_root_to_parent():
    chain = cat.get_ancestors(CHILD_ID)
    assert [a.id for a in chain] == [ROOT_ID]


def test_get_ancestors_for_root_is_empty():
    assert cat.get_ancestors(ROOT_ID) == []


def test_get_ancestors_for_unknown_is_empty():
    assert cat.get_ancestors("DOES-NOT-EXIST") == []


def test_iter_subtree_bfs():
    seen = [c.id for c in cat.iter_subtree(ROOT_ID)]
    assert seen[0] == ROOT_ID
    assert CHILD_ID in seen
    # All ids in the iteration must belong to the subtree (root or descendant)
    for cid in seen:
        assert cid == ROOT_ID or cid.startswith(ROOT_ID + ".")


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
