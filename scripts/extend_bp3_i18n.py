#!/usr/bin/env python3
"""Extend the existing BP1 i18n sidecars with BP3 name translations for a
locale (idempotent).

Reads:
- catalogue/processes/BP1-*.yaml          (English source)
- catalogue/i18n/<locale>/processes/BP1-*.yaml  (existing sidecar)
- scripts/_archive/_bp3_i18n_data_<locale>.py   exposes BP3_NAMES dict

Writes:
- catalogue/i18n/<locale>/processes/BP1-*.yaml  (BP1+BP2 entries preserved,
  any existing BP3 entries discarded and re-emitted from the translation
  dict — so the script is safe to re-run after editing the dict).
"""
from __future__ import annotations
import importlib.util
import os
import re
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")
DATA_DIR = os.path.join(REPO_ROOT, "scripts", "_archive")
I18N_DIR = os.path.join(REPO_ROOT, "catalogue", "i18n")

BP3_ID = re.compile(r"^BP-\d+\.\d+\.\d+$")


def load_translations(locale):
    path = os.path.join(DATA_DIR, f"_bp3_i18n_data_{locale}.py")
    spec = importlib.util.spec_from_file_location(f"bp3_i18n_{locale}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "BP3_NAMES", {})


def yaml_quote(s):
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def emit_sidecar(locale, fname, entries_in_order):
    """Re-emit the sidecar from a list of (id, fields_dict) tuples."""
    out_path = os.path.join(I18N_DIR, locale, "processes", fname)
    L = []
    L.append("kind: business-process")
    L.append(f"locale: {locale}")
    L.append(f"source: {fname}")
    L.append("entries:")
    for entry_id, fields in entries_in_order:
        L.append(f"  {entry_id}:")
        for fname_key, fval in fields.items():
            L.append(f"    {fname_key}: {yaml_quote(fval)}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    locale = sys.argv[1]
    bp3_t = load_translations(locale)

    missing = set()
    written = 0
    for fname in sorted(os.listdir(PROCESSES_DIR)):
        if not (fname.startswith("BP1-") and fname.endswith(".yaml")):
            continue
        src_path = os.path.join(PROCESSES_DIR, fname)
        sidecar_path = os.path.join(I18N_DIR, locale, "processes", fname)

        with open(src_path) as f:
            src = yaml.safe_load(f)
        with open(sidecar_path) as f:
            sidecar = yaml.safe_load(f)

        # Preserve BP1 + BP2 entries from the existing sidecar; drop any BP3.
        kept = []
        for k, v in (sidecar.get("entries") or {}).items():
            if BP3_ID.match(k):
                continue
            kept.append((k, v))

        # Append BP3 entries in source order.
        for bp2 in src.get("children") or []:
            for bp3 in bp2.get("children") or []:
                en_name = bp3["name"]
                if en_name not in bp3_t:
                    missing.add(en_name)
                    continue
                kept.append((bp3["id"], {"name": bp3_t[en_name]}))

        emit_sidecar(locale, fname, kept)
        written += 1

    if missing:
        print(f"⚠ {locale}: missing {len(missing)} BP3 name translations")
        for x in sorted(missing)[:8]:
            print(f"   {x[:80]}")
        return 1
    print(f"✔ {locale}: rewrote {written} sidecars with BP3 names")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
