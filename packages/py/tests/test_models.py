from __future__ import annotations

import pytest
from pydantic import ValidationError

from turbo_ea_capabilities import Capability


def test_minimal_capability_loads():
    c = Capability(id="BC-1", name="Foo", level=1, children=[])
    assert c.id == "BC-1"
    assert c.children == ()


def test_level_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Capability(id="BC-1", name="Foo", level=5, children=[])
    with pytest.raises(ValidationError):
        Capability(id="BC-1", name="Foo", level=0, children=[])


def test_missing_required_field_rejected():
    with pytest.raises(ValidationError):
        Capability(id="BC-1", level=1, children=[])  # type: ignore[call-arg]


def test_frozen_after_load():
    c = Capability(id="BC-1", name="Foo", level=1, children=[])
    with pytest.raises((ValidationError, TypeError)):
        c.name = "Bar"  # type: ignore[misc]


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        Capability(id="BC-1", name="Foo", level=1, children=[], not_a_field="x")  # type: ignore[call-arg]


def test_flat_form_strips_string_children_ids():
    # capabilities.json shape: children is a list of ids; loader replaces them later.
    c = Capability(id="BC-2", name="Production", level=1, parent_id=None, children=["BC-2.1", "BC-2.2"])
    assert c.children == ()


def test_nested_form_keeps_capability_children():
    c = Capability(
        id="BC-2",
        name="Production",
        level=1,
        children=[{"id": "BC-2.1", "name": "Planning", "level": 2, "children": []}],
    )
    assert len(c.children) == 1
    assert c.children[0].id == "BC-2.1"
