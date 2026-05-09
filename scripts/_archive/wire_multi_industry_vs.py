#!/usr/bin/env python3
"""Wire process_ids for multi-industry value streams (VS-130, VS-350) and add
Mining-specific BPs to VS-330 mining-variant stages.

These streams have industry_variant on each stage; the mapping key is
(stream_id, stage_name, industry_variant). For VS-330 the new BP-310 (Mining
& Metals) ids are APPENDED to existing process_ids on Mining-tagged stages.
"""
from __future__ import annotations
import argparse, os, yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_ROOT, "catalogue", "_value-streams.yaml")

# Map: (stream_id, stage_name, industry_variant_or_None) -> [BP ids]
MAPPING: dict[tuple, list[str]] = {}

# --------------------------------------- VS-330: append Mining BPs to mining variants
APPEND_MAPPING: dict[tuple, list[str]] = {
    ("VS-330", "Acreage Acquisition", "Mining & Metals"): ["BP-310.10"],
    ("VS-330", "Prospect Maturation", "Mining & Metals"): ["BP-310.10"],
    ("VS-330", "Exploration Drilling", "Mining & Metals"): ["BP-310.10"],
    ("VS-330", "Reserves Maturation", "Mining & Metals"): ["BP-310.10"],
    ("VS-330", "Field Development Sanction", "Mining & Metals"): ["BP-310.20"],
    ("VS-330", "First Production", "Mining & Metals"): ["BP-310.30"],
    ("VS-330", "Operations Handover", "Mining & Metals"): ["BP-310.30"],
}

# --------------------------------------- VS-130 Concept-to-Manufacture (multi-industry)
# Stage names: Concept Design, FEED & Specification, Detailed Design, Design Review,
#              Manufacturing Engineering, Production Ramp-Up, Quality & Yield Stabilisation,
#              Configuration Baseline
_VS130 = {
    # Concept Design
    ("Concept Design", "Automotive"): ["BP-290.10", "BP-20.30"],
    ("Concept Design", "Electrical Components & Equipment"): ["BP-460.10", "BP-20.30"],
    ("Concept Design", "Engineering Services"): ["BP-440.20", "BP-20.30"],
    ("Concept Design", "HVAC & Building Automation Systems"): ["BP-450.10", "BP-20.30"],
    # FEED & Specification (no-variant + 4 variants)
    ("FEED & Specification", None): ["BP-20.30"],
    ("FEED & Specification", "Automotive"): ["BP-290.10", "BP-20.30"],
    ("FEED & Specification", "Electrical Components & Equipment"): ["BP-460.10", "BP-20.30"],
    ("FEED & Specification", "Engineering Services"): ["BP-440.20"],
    ("FEED & Specification", "HVAC & Building Automation Systems"): ["BP-450.10"],
    # Detailed Design
    ("Detailed Design", "Automotive"): ["BP-290.10", "BP-20.30"],
    ("Detailed Design", "Electrical Components & Equipment"): ["BP-460.10"],
    ("Detailed Design", "Engineering Services"): ["BP-440.20", "BP-440.50"],
    ("Detailed Design", "HVAC & Building Automation Systems"): ["BP-450.10"],
    # Design Review
    ("Design Review", "Automotive"): ["BP-290.10", "BP-20.30"],
    ("Design Review", "Defense"): ["BP-230.30", "BP-230.40"],
    ("Design Review", "Electrical Components & Equipment"): ["BP-460.10", "BP-460.20"],
    ("Design Review", "Engineering Services"): ["BP-440.20"],
    ("Design Review", "HVAC & Building Automation Systems"): ["BP-450.10"],
    # Manufacturing Engineering
    ("Manufacturing Engineering", None): ["BP-20.50"],
    ("Manufacturing Engineering", "Automotive"): ["BP-290.10", "BP-470.10"],
    ("Manufacturing Engineering", "Electrical Components & Equipment"): ["BP-460.10", "BP-470.10"],
    ("Manufacturing Engineering", "Manufacturing"): ["BP-470.10", "BP-470.20"],
    # Production Ramp-Up
    ("Production Ramp-Up", "Automotive"): ["BP-290.10", "BP-470.10"],
    ("Production Ramp-Up", "Manufacturing"): ["BP-470.10", "BP-470.20", "BP-20.50"],
    # Quality & Yield Stabilisation
    ("Quality & Yield Stabilisation", None): ["BP-470.30", "BP-720"][:1] + ["BP-20.30"],  # BP-470.30 (Mfg Maintenance) + Cross-Industry BP-20.30
    ("Quality & Yield Stabilisation", "Manufacturing"): ["BP-470.30", "BP-470.10"],
    # Configuration Baseline
    ("Configuration Baseline", "Automotive"): ["BP-290.10", "BP-820"][:1] + ["BP-20.30"],
    ("Configuration Baseline", "Defense"): ["BP-230.40"],
    ("Configuration Baseline", "Electrical Components & Equipment"): ["BP-460.30"],
    ("Configuration Baseline", "Engineering Services"): ["BP-440.50"],
}
for (stage, variant), bps in _VS130.items():
    MAPPING[("VS-130", stage, variant)] = bps

# --------------------------------------- VS-350 Maintenance-Request-to-Closure
_VS350 = {
    # Notification / Request
    ("Notification / Request", None): ["BP-100.30"],
    ("Notification / Request", "HVAC & Building Automation Systems"): ["BP-450.30", "BP-100.30"],
    ("Notification / Request", "Manufacturing"): ["BP-470.30", "BP-100.30"],
    ("Notification / Request", "Real Estate"): ["BP-320.30"],
    ("Notification / Request", "Transportation & Logistics"): ["BP-100.30", "BP-410.20"],
    # Triage & Planning
    ("Triage & Planning", None): ["BP-100.30"],
    ("Triage & Planning", "Electrical Components & Equipment"): ["BP-460.30"],
    ("Triage & Planning", "HVAC & Building Automation Systems"): ["BP-450.30", "BP-100.30"],
    ("Triage & Planning", "Manufacturing"): ["BP-470.30"],
    ("Triage & Planning", "Real Estate"): ["BP-320.30"],
    ("Triage & Planning", "Transportation & Logistics"): ["BP-100.30"],
    # Execution
    ("Execution", None): ["BP-100.30"],
    ("Execution", "Electrical Components & Equipment"): ["BP-460.30"],
    ("Execution", "HVAC & Building Automation Systems"): ["BP-450.30", "BP-100.30"],
    ("Execution", "Manufacturing"): ["BP-470.30", "BP-40.30"],
    ("Execution", "Real Estate"): ["BP-320.30"],
    ("Execution", "Transportation & Logistics"): ["BP-100.30", "BP-410.20"],
    # Parts & Logistics
    ("Parts & Logistics", None): ["BP-40.20", "BP-40.40"],
    ("Parts & Logistics", "HVAC & Building Automation Systems"): ["BP-40.20", "BP-450.40"],
    ("Parts & Logistics", "Manufacturing"): ["BP-40.20", "BP-470.30"],
    ("Parts & Logistics", "Transportation & Logistics"): ["BP-40.40", "BP-410.30"],
    # Verification & Closure
    ("Verification & Closure", None): ["BP-100.30", "BP-720"][:1] + ["BP-50.40"],
    ("Verification & Closure", "HVAC & Building Automation Systems"): ["BP-450.30", "BP-50.40"],
    ("Verification & Closure", "Manufacturing"): ["BP-470.30", "BP-50.40"],
    ("Verification & Closure", "Real Estate"): ["BP-320.30"],
    ("Verification & Closure", "Transportation & Logistics"): ["BP-100.30"],
    # Performance & Cost Analysis
    ("Performance & Cost Analysis", None): ["BP-90.10", "BP-50.40"],
    ("Performance & Cost Analysis", "HVAC & Building Automation Systems"): ["BP-90.10", "BP-450.30"],
}
for (stage, variant), bps in _VS350.items():
    MAPPING[("VS-350", stage, variant)] = bps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream", required=True, choices=["VS-330", "VS-130", "VS-350"])
    args = ap.parse_args()

    with open(PATH) as f: data = yaml.safe_load(f)
    updated, appended, skipped, seen = 0, 0, 0, set()

    for stream in data["value_streams"]:
        if stream["id"] != args.stream: continue
        for stage in stream["stages"]:
            variant = stage.get("industry_variant") or None
            key = (stream["id"], stage["stage_name"], variant)

            # VS-330 uses APPEND_MAPPING (additive)
            if args.stream == "VS-330" and key in APPEND_MAPPING:
                seen.add(key)
                existing = stage.get("process_ids") or []
                new = list(existing)
                for bp in APPEND_MAPPING[key]:
                    if bp not in new: new.append(bp)
                if new != existing:
                    stage["process_ids"] = new
                    appended += 1
                continue

            # VS-130 / VS-350 use MAPPING (replace empty)
            if key in MAPPING:
                seen.add(key)
                if stage.get("process_ids"):
                    skipped += 1; continue
                stage["process_ids"] = list(MAPPING[key])
                updated += 1

    if args.stream == "VS-330":
        unmapped = {k for k in APPEND_MAPPING.keys() if k[0] == args.stream} - seen
    else:
        unmapped = {k for k in MAPPING.keys() if k[0] == args.stream} - seen
    if unmapped:
        for k in sorted(unmapped, key=lambda x: (x[0], x[1], x[2] or "")):
            print(f"⚠ unmapped: {k}")
        raise SystemExit(1)

    preamble = ("# Value Streams (orthogonal artefact, not part of the capability hierarchy).\n"
                "# Each stream has a stable VS-<n> id (sparse 10/20/30 numbering); each stage\n"
                "# has a stable VS-<n>.<m> id and links to L1 capabilities (`capability_ids`)\n"
                "# and to business processes (`process_ids`) that realize the work. The site\n"
                "# auto-expands an L1 to its descendants when filtering. Use 'notes' to capture\n"
                "# sub-scope detail.\n"
                "#\n"
                "# Each stream declares an `industries` array using the canonical L1 industry\n"
                "# vocabulary. `Cross-Industry`, when present, must stand alone.\n")
    body = yaml.safe_dump({"value_streams": data["value_streams"]}, sort_keys=False, width=10**9, allow_unicode=True)
    with open(PATH, "w", encoding="utf-8") as f: f.write(preamble + body)
    print(f"✔ Updated {updated}; appended {appended}; skipped {skipped}.")


if __name__ == "__main__":
    main()
