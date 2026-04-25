"""Hatch version source.

Reads the catalogue version from the bundled `data/version.json` file. Falls
back to `0.0.0` if the data has not been built yet (so editable installs work
even before the first build).
"""
from __future__ import annotations

import json
from pathlib import Path

_VERSION_PATH = Path(__file__).parent / "data" / "version.json"


def _read() -> str:
    if not _VERSION_PATH.exists():
        return "0.0.0"
    raw = json.loads(_VERSION_PATH.read_text(encoding="utf-8"))
    cv = str(raw.get("catalogue_version", "0.0.0"))
    # Hatch wants a PEP 440-compatible version. The build pipeline emits
    # `<lasttag>+<sha>` for non-tagged builds — that is already PEP 440 local-
    # version syntax, so we pass it through.
    return cv


VERSION: str = _read()
