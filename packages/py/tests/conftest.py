"""Test setup.

The package's `data/` directory is gitignored and only populated by the
TypeScript build pipeline. For tests we lay down a tiny fixture catalogue at
import time so `pytest` can run without depending on the JS toolchain.

If real data is already present (e.g., after `npm run build:pkg`), we keep it.
Otherwise we copy `tests/fixtures/*.json` (and the optional i18n overlay)
into `src/turbo_ea_capabilities/data/`.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

PKG_DATA_DIR = Path(__file__).parent.parent / "src" / "turbo_ea_capabilities" / "data"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _data_present() -> bool:
    return all(
        (PKG_DATA_DIR / f).exists()
        for f in ("capabilities.json", "tree.json", "version.json")
    )


def pytest_configure(config: pytest.Config) -> None:
    if _data_present():
        return
    PKG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for f in ("capabilities.json", "tree.json", "version.json"):
        src = FIXTURE_DIR / f
        if not src.exists():
            raise RuntimeError(f"Missing fixture {src}")
        shutil.copyfile(src, PKG_DATA_DIR / f)
    # Optional translation overlay - localization tests depend on it; core
    # tests still pass without it.
    locales_src = FIXTURE_DIR / "locales.json"
    if locales_src.exists():
        shutil.copyfile(locales_src, PKG_DATA_DIR / "locales.json")
    i18n_src = FIXTURE_DIR / "i18n"
    if i18n_src.is_dir():
        i18n_dst = PKG_DATA_DIR / "i18n"
        i18n_dst.mkdir(exist_ok=True)
        for f in i18n_src.glob("*.json"):
            shutil.copyfile(f, i18n_dst / f.name)
