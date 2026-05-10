"""Contract tests guarding the data ↔ model ↔ schema invariants.

These tests catch the class of regression where the *shipped data* moves
ahead of the *Pydantic model* (or vice versa) and consumers crash on
``model_validate``. Concretely:

1. **Every record in the bundled data must validate against its model.**
   If the data layer adds, say, a new ``framework_refs.framework`` value
   that the Pydantic ``Literal`` doesn't list yet, the wheel build still
   succeeds today — but every consumer hits ``ValidationError`` on first
   use. This test fails loudly in upstream CI before the wheel ships.

2. **Every Literal[...] enum must mirror the corresponding JSON Schema
   enum.** Field-level whitelists living in two places drift the moment
   one is edited without the other. We assert they are equal so the
   schema is the single source of truth and a missed update is a test
   failure rather than a silent runtime crash for downstream consumers.

The tests skip gracefully when the bundled ``data/*.json`` files are
absent (e.g. a fixture-only checkout that has not run ``npm run build``).
"""

from __future__ import annotations

import json
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, get_args

import pytest

import turbo_ea_capabilities as cat
from turbo_ea_capabilities._models import FrameworkRef


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bundled_data_path(name: str) -> Path | None:
    """Resolve a bundled data file or return ``None`` when it isn't shipped."""
    res = files("turbo_ea_capabilities") / "data" / name
    try:
        with as_file(res) as path:
            return path if path.is_file() else None
    except (FileNotFoundError, ModuleNotFoundError):
        return None


def _load_bundled(name: str) -> Any:
    """Load a bundled JSON file and return its parsed contents (or skip)."""
    path = _bundled_data_path(name)
    if path is None:
        pytest.skip(f"data/{name} not shipped in this wheel — skipping contract test")
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_path(name: str) -> Path:
    """Resolve a schema file at the repo root.

    The schemas live outside the package (one level up from ``packages/py``);
    when the repo is checked out (CI, dev) the path is reachable via
    ``__file__``-anchored navigation. When only the wheel is installed
    (downstream consumer) the schemas aren't shipped — the schema-vs-model
    consistency test is a build-time guard, not a runtime one, so it skips
    gracefully in that case.
    """
    here = Path(__file__).resolve()
    # tests/ → packages/py/ → packages/ → repo-root/schema/
    candidate = here.parents[3] / "schema" / name
    if candidate.is_file():
        return candidate
    pytest.skip(f"schema/{name} not present (running outside source tree?)")


# ---------------------------------------------------------------------------
# Data → Model: every shipped record must validate
# ---------------------------------------------------------------------------


def test_capabilities_data_validates_against_capability_model() -> None:
    """``load_all()`` must succeed on every record the wheel ships."""
    nodes = cat.load_all()
    assert len(nodes) > 0


def test_processes_data_validates_against_business_process_model() -> None:
    """``load_business_processes()`` must succeed on every record the wheel
    ships. This is the test that would have caught the 2026-05 incident
    where ``framework_refs.framework`` data added new codes (DCOR, COBIT,
    SHRM-BoCK, ISO-31000, ISO-55000, COSO-ERM, TOGAF) that the Pydantic
    ``Literal`` did not list.
    """
    if _bundled_data_path("business-processes.json") is None:
        pytest.skip("data/business-processes.json not shipped — skipping")
    procs = cat.load_business_processes()
    assert len(procs) > 0


def test_value_streams_data_validates_against_value_stream_model() -> None:
    if _bundled_data_path("value-streams.json") is None:
        pytest.skip("data/value-streams.json not shipped — skipping")
    streams = cat.load_value_streams()
    assert len(streams) > 0


# ---------------------------------------------------------------------------
# Schema ↔ Model: enum whitelists must agree
# ---------------------------------------------------------------------------


def test_framework_literal_matches_schema_enum() -> None:
    """``FrameworkRef.framework`` (Pydantic ``Literal``) must equal the
    ``framework`` enum in ``schema/business-process.schema.json``.

    The schema's ``framework`` description is the documented source of
    truth (it spells out what each code means). When upstream adds a new
    code there it must also land in the model — which is what this test
    enforces. Drift here is exactly the failure mode that crashed every
    consumer of ``load_business_processes()``.
    """
    schema = json.loads(_schema_path("business-process.schema.json").read_text(encoding="utf-8"))
    schema_enum = (
        schema["properties"]["framework_refs"]["items"]["properties"]["framework"]["enum"]
    )
    schema_set = set(schema_enum)

    # Pull the Literal arg list off the field annotation. Pydantic v2
    # exposes the original annotation via ``model_fields[field].annotation``.
    annotation = FrameworkRef.model_fields["framework"].annotation
    literal_set = set(get_args(annotation))

    missing_in_model = schema_set - literal_set
    extra_in_model = literal_set - schema_set
    assert not missing_in_model, (
        f"Schema lists framework codes the model does not: {sorted(missing_in_model)}. "
        "Add them to FrameworkRef.framework's Literal so consumers can "
        "validate them."
    )
    assert not extra_in_model, (
        f"Model lists framework codes the schema does not: {sorted(extra_in_model)}. "
        "Add them to schema/business-process.schema.json's framework enum "
        "so the schema stays the source of truth."
    )
