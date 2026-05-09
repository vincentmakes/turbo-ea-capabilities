#!/usr/bin/env python3
"""Emit a value-stream i18n sidecar for one locale.

Reads English source `catalogue/_value-streams.yaml` plus a per-locale
translation module `scripts/_archive/_vs_i18n_data_<locale>.py` exposing
`STREAMS: dict[str,str]`, `STAGES: dict[str,str]`, `NOTES: dict[str,str]`.

Emits `catalogue/i18n/<locale>/_value-streams.yaml` translating, per
schema/i18n.schema.json (kind: value-stream):
- stream entries (id `^VS-\\d+$`): `name`, `description` (when present)
- stage  entries (id `^VS-\\d+\\.\\d+$`): `stage_name`, `description`,
  `notes`

Usage:  python3 scripts/generate_vs_i18n_sidecar.py <locale>
"""
from __future__ import annotations
import importlib.util
import os
import sys
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")
DATA_DIR = os.path.join(REPO_ROOT, "scripts", "_archive")
OUT_DIR = os.path.join(REPO_ROOT, "catalogue", "i18n")


def load_translations(locale):
    path = os.path.join(DATA_DIR, f"_vs_i18n_data_{locale}.py")
    spec = importlib.util.spec_from_file_location(f"vs_i18n_{locale}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "STREAMS", {}), getattr(mod, "STAGES", {}), getattr(mod, "NOTES", {})


def yaml_quote(s):
    """Always double-quote with escapes for YAML safety."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    locale = sys.argv[1]
    streams_t, stages_t, notes_t = load_translations(locale)

    with open(SOURCE) as f:
        data = yaml.safe_load(f)

    missing = {"streams": set(), "stages": set(), "notes": set()}
    out = []
    out.append("kind: value-stream")
    out.append(f"locale: {locale}")
    out.append("source: _value-streams.yaml")
    out.append("entries:")

    for stream in data["value_streams"]:
        sid = stream["id"]
        en_name = stream["name"]
        out.append(f"  {sid}:")
        if en_name in streams_t:
            out.append(f"    name: {yaml_quote(streams_t[en_name])}")
        else:
            missing["streams"].add(en_name)
        if stream.get("description") and stream["description"] in streams_t:
            out.append(f"    description: {yaml_quote(streams_t[stream['description']])}")

        for stage in stream.get("stages") or []:
            stid = stage["id"]
            en_stage = stage["stage_name"]
            en_note = stage.get("notes")
            stage_lines = []
            if en_stage in stages_t:
                stage_lines.append(f"    stage_name: {yaml_quote(stages_t[en_stage])}")
            else:
                missing["stages"].add(en_stage)
            if stage.get("description"):
                en_desc = stage["description"]
                if en_desc in notes_t:
                    stage_lines.append(f"    description: {yaml_quote(notes_t[en_desc])}")
            if en_note:
                if en_note in notes_t:
                    stage_lines.append(f"    notes: {yaml_quote(notes_t[en_note])}")
                else:
                    missing["notes"].add(en_note)
            if stage_lines:
                out.append(f"  {stid}:")
                out.extend(stage_lines)

    out_path = os.path.join(OUT_DIR, locale, "_value-streams.yaml")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print(f"✔ {locale}: wrote {out_path}")
    backbone_missing = len(missing["streams"]) + len(missing["stages"])
    if backbone_missing:
        print(f"  ⚠ missing {len(missing['streams'])} streams, "
              f"{len(missing['stages'])} stages — these are required")
        for kind in ("streams", "stages"):
            for x in sorted(missing[kind])[:5]:
                print(f"     [{kind}] {x[:80]}")
        return 1
    if missing["notes"]:
        print(f"  ℹ {len(missing['notes'])} notes left untranslated "
              f"(fall back to English at schema level)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
