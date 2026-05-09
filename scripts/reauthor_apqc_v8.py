#!/usr/bin/env python3
"""Re-author cross-industry BP1 files from APQC PCF v8.0 ground truth.

For each top-level v8.0 category (1.0..13.0):
1. Build the v8.0 BP2/BP3 tree from the official Excel `Combined` sheet.
2. Read the existing BP1 YAML, build a fuzzy name index of existing BP2/BP3
   nodes (name → local_id + realizes_capability_ids + description).
3. For each v8.0 BP2/BP3 node:
   - If a fuzzy name match exists in the v7.4 file, reuse the local id and
     realizes_capability_ids (preserves VS process_ids continuity).
   - Else, assign a new sparse 10/20/30 local id and leave realizes empty.
4. Re-emit the BP1 YAML with v8.0 names, descriptions, and external_ids.
5. Emit an id-mapping report (old_local_id → new_local_id or None) for each
   removed/renamed node so VS process_ids can be patched in a separate step.

Naming: v8.0 names use sentence case for sub-levels; this script Title-Cases
them to match the catalogue's naming convention.
"""
from __future__ import annotations
import argparse, json, os, re
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")

with open("/tmp/apqc_v8_full.json") as f:
    V8_ROWS = json.load(f)

# Category → BP1 file
CATEGORY_TO_FILE = {
    "1": ("BP-10",  "BP1-develop-vision-and-strategy.yaml"),
    "2": ("BP-20",  "BP1-develop-and-manage-products-and-services.yaml"),
    "3": ("BP-30",  "BP1-market-and-sell-products-and-services.yaml"),
    "4": ("BP-40",  "BP1-manage-supply-chain-for-physical-products.yaml"),
    "5": ("BP-50",  "BP1-deliver-services.yaml"),
    "6": ("BP-60",  "BP1-manage-customer-service.yaml"),
    "7": ("BP-70",  "BP1-develop-and-manage-human-capital.yaml"),
    "8": ("BP-80",  "BP1-manage-information-technology.yaml"),
    "9": ("BP-90",  "BP1-manage-financial-resources.yaml"),
    "10": ("BP-100","BP1-acquire-construct-and-manage-assets.yaml"),
    "11": ("BP-110","BP1-manage-enterprise-risk-compliance-remediation-and-resiliency.yaml"),
    "12": ("BP-120","BP1-manage-external-relationships.yaml"),
    "13": ("BP-370","BP1-develop-and-manage-business-capabilities.yaml"),
}

# BP1 metadata (industry, description, realizes_capability_ids — from existing files)
# The BP1 *name* for cat 7/8 was renamed in v8.0, but we preserve the local
# file slug/name as is to avoid file rename cascades.
BP1_META = {
    # cat → (industry, top-level realizes)
    "1":  ("Cross-Industry", ["BC-100"]),
    "2":  ("Cross-Industry", ["BC-820", "BC-810", "BC-800"]),
    "3":  ("Cross-Industry", ["BC-400", "BC-410", "BC-420", "BC-440"]),
    "4":  ("Cross-Industry", ["BC-520", "BC-530"]),
    "5":  ("Cross-Industry", ["BC-430", "BC-720"]),
    "6":  ("Cross-Industry", ["BC-430", "BC-420"]),
    "7":  ("Cross-Industry", ["BC-300"]),
    "8":  ("Cross-Industry", ["BC-600", "BC-610", "BC-620"]),
    "9":  ("Cross-Industry", ["BC-200", "BC-230", "BC-210", "BC-220"]),
    "10": ("Cross-Industry", ["BC-700", "BC-710"]),
    "11": ("Cross-Industry", ["BC-120", "BC-130", "BC-160", "BC-730"]),
    "12": ("Cross-Industry", ["BC-240", "BC-150", "BC-850", "BC-110"]),
    "13": ("Cross-Industry", ["BC-170", "BC-100", "BC-920"]),
}


def normalize_name(s):
    if not s: return ""
    s = s.lower()
    s = re.sub(r"[/\&\-,;:\(\)\[\]\.\?]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def title_case(s):
    """Catalogue naming convention: Title Case at every level."""
    if not s: return s
    # Words to keep lowercase mid-phrase
    LOWER = {"and", "or", "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "by", "from", "via"}
    words = s.split()
    out = []
    for i, w in enumerate(words):
        # Preserve all-uppercase acronyms (IT, HR, GMP, IBNR, etc.)
        if w.isupper() and len(w) <= 5:
            out.append(w)
        elif i > 0 and w.lower() in LOWER:
            out.append(w.lower())
        else:
            # Capitalize first letter, keep rest as-is for camelCase preservation
            out.append(w[0].upper() + w[1:] if w else w)
    return " ".join(out)


def fuzzy_match_local(v8_name, local_index):
    """Try to find a v7.4 local node whose name fuzzy-matches the v8.0 name.
    Returns the matched local_id or None.
    """
    n = normalize_name(v8_name)
    # Direct match
    for ln_name, lid in local_index.items():
        if normalize_name(ln_name) == n:
            return lid
    # Plural/singular tolerance on trailing word
    for ln_name, lid in local_index.items():
        ln = normalize_name(ln_name)
        if n.rstrip("s") == ln.rstrip("s"):
            return lid
    return None


def build_local_index(tree):
    """Walk an existing BP1 yaml tree, return {name: local_id} and {local_id: realizes}."""
    name_to_id = {}
    id_to_realizes = {}
    id_to_desc = {}
    def walk(node):
        if "name" in node and node.get("level", 1) >= 2:
            name_to_id[node["name"]] = node["id"]
            id_to_realizes[node["id"]] = node.get("realizes_capability_ids", [])
            id_to_desc[node["id"]] = node.get("description", "")
        for c in node.get("children") or []:
            walk(c)
    walk(tree)
    return name_to_id, id_to_realizes, id_to_desc


def get_v8_subtree(category):
    """Return v8.0 BP2/BP3 nodes under a category as nested dict.
    Returns: {bp2_code: {"name": ..., "desc": ..., "bp3s": [{"code": ..., "name": ..., "desc": ...}, ...]}}
    """
    bp2 = {}
    for r in V8_ROWS:
        parts = r["id"].split(".")
        if parts[0] != category: continue
        if len(parts) == 2 and parts[1] != "0":
            bp2[r["id"]] = {"name": r["name"], "desc": r["desc"], "bp3s": []}
    for r in V8_ROWS:
        parts = r["id"].split(".")
        if parts[0] != category: continue
        if len(parts) == 3:
            parent = f"{parts[0]}.{parts[1]}"
            if parent in bp2:
                bp2[parent]["bp3s"].append({"code": r["id"], "name": r["name"], "desc": r["desc"]})
    return bp2


def yaml_safe(s):
    """Avoid YAML quoting hazards by escaping if needed."""
    if not s: return ""
    s = s.replace("\n", " ").strip()
    return s


def emit_yaml(bp1_id, bp1_name, industry, bp1_desc, bp1_realizes,
              cat_code, bp2_data, id_mapping):
    """Emit YAML; bp2_data is list of (bp2_local_id, bp2_v8_code, bp2_name, bp2_desc, bp2_realizes,
                                       [(bp3_local_id, bp3_v8_code, bp3_name, bp3_desc, bp3_realizes), ...]).
    Tags are version "8.0"."""
    L = []
    L.append(f"id: {bp1_id}")
    L.append(f"name: {bp1_name}")
    L.append("level: 1")
    L.append(f"industry: {industry}")
    L.append("description: >-")
    L.append(f"  {yaml_safe(bp1_desc)}")
    L.append("framework_refs:")
    L.append("  - framework: APQC-PCF")
    L.append(f"    external_id: \"{cat_code}\"")
    L.append("    version: \"8.0\"")
    L.append("realizes_capability_ids:")
    for bc in bp1_realizes:
        L.append(f"  - {bc}")
    L.append("children:")
    for bp2_lid, bp2_code, bp2_name, bp2_desc, bp2_realizes, bp3s in bp2_data:
        L.append(f"  - id: {bp2_lid}")
        L.append(f"    name: {bp2_name}")
        L.append("    level: 2")
        L.append("    description: >-")
        L.append(f"      {yaml_safe(bp2_desc)}")
        L.append("    framework_refs:")
        L.append("      - framework: APQC-PCF")
        L.append(f"        external_id: \"{bp2_code}\"")
        L.append("        version: \"8.0\"")
        if bp2_realizes:
            L.append("    realizes_capability_ids:")
            for bc in bp2_realizes:
                L.append(f"      - {bc}")
        else:
            L.append("    realizes_capability_ids: []")
        if not bp3s:
            L.append("    children: []")
        else:
            L.append("    children:")
            for bp3_lid, bp3_code, bp3_name, bp3_desc, bp3_realizes in bp3s:
                L.append(f"      - id: {bp3_lid}")
                L.append(f"        name: {bp3_name}")
                L.append("        level: 3")
                L.append("        description: >-")
                L.append(f"          {yaml_safe(bp3_desc)}")
                L.append("        framework_refs:")
                L.append("          - framework: APQC-PCF")
                L.append(f"            external_id: \"{bp3_code}\"")
                L.append("            version: \"8.0\"")
                if bp3_realizes:
                    L.append("        realizes_capability_ids:")
                    for bc in bp3_realizes:
                        L.append(f"          - {bc}")
                else:
                    L.append("        realizes_capability_ids: []")
                L.append("        children: []")
    return "\n".join(L) + "\n"


def reauthor_category(cat):
    bp1_id, fname = CATEGORY_TO_FILE[cat]
    industry, bp1_realizes = BP1_META[cat]
    path = os.path.join(PROCESSES_DIR, fname)
    with open(path) as f: existing = yaml.safe_load(f)

    # Existing local id space (under this BP1)
    local_name_to_id, local_id_to_realizes, local_id_to_desc = build_local_index(existing)

    # v8.0 subtree for this category
    v8_subtree = get_v8_subtree(cat)

    # v8.0 BP1 metadata
    v8_bp1 = next((r for r in V8_ROWS if r["id"] == f"{cat}.0"), None)
    if not v8_bp1:
        raise SystemExit(f"v8.0 has no category {cat}.0")
    bp1_name_v8 = title_case(v8_bp1["name"])
    bp1_desc_v8 = v8_bp1["desc"]

    # Sort v8.0 BP2 by code (1.1, 1.2, ...)
    sorted_bp2_codes = sorted(v8_subtree.keys(), key=lambda c: tuple(int(p) for p in c.split(".")))

    # Build BP2 data with assigned local ids
    bp2_data = []
    next_bp2_n = 10  # sparse 10/20/30
    used_local_bp2_ids = set()
    id_mapping = {}  # old_local_id → new_local_id (for re-routing VS process_ids)

    for bp2_code in sorted_bp2_codes:
        v8_bp2 = v8_subtree[bp2_code]
        v8_bp2_name = title_case(v8_bp2["name"])
        # Try fuzzy-match against existing local nodes
        matched_id = fuzzy_match_local(v8_bp2["name"], local_name_to_id)
        if matched_id and matched_id not in used_local_bp2_ids and matched_id.count(".") == 1:
            # Reuse the existing local BP2 id (preserves VS process_ids)
            bp2_lid = matched_id
            bp2_realizes = local_id_to_realizes.get(matched_id, [])
        else:
            bp2_lid = f"{bp1_id}.{next_bp2_n}"
            while bp2_lid in used_local_bp2_ids:
                next_bp2_n += 10
                bp2_lid = f"{bp1_id}.{next_bp2_n}"
            next_bp2_n += 10
            bp2_realizes = []
        used_local_bp2_ids.add(bp2_lid)

        # BP3 children
        bp3_list = []
        next_bp3_n = 10
        used_local_bp3_ids = set()
        sorted_bp3 = sorted(v8_bp2["bp3s"], key=lambda b: tuple(int(p) for p in b["code"].split(".")))
        for v8_bp3 in sorted_bp3:
            v8_bp3_name = title_case(v8_bp3["name"])
            matched_bp3_id = fuzzy_match_local(v8_bp3["name"], local_name_to_id)
            if (matched_bp3_id
                    and matched_bp3_id not in used_local_bp3_ids
                    and matched_bp3_id.startswith(bp2_lid + ".")
                    and matched_bp3_id.count(".") == 2):
                bp3_lid = matched_bp3_id
                bp3_realizes = local_id_to_realizes.get(matched_bp3_id, [])
            else:
                bp3_lid = f"{bp2_lid}.{next_bp3_n}"
                while bp3_lid in used_local_bp3_ids:
                    next_bp3_n += 10
                    bp3_lid = f"{bp2_lid}.{next_bp3_n}"
                next_bp3_n += 10
                bp3_realizes = []
            used_local_bp3_ids.add(bp3_lid)
            bp3_list.append((bp3_lid, v8_bp3["code"], v8_bp3_name, v8_bp3["desc"], bp3_realizes))

        bp2_data.append((bp2_lid, bp2_code, v8_bp2_name, v8_bp2["desc"], bp2_realizes, bp3_list))

    # Compute id_mapping: old local ids that no longer exist → None
    new_ids = set()
    for bp2_lid, _, _, _, _, bp3s in bp2_data:
        new_ids.add(bp2_lid)
        for bp3_lid, _, _, _, _ in bp3s:
            new_ids.add(bp3_lid)
    for old_id in local_name_to_id.values():
        if old_id not in new_ids:
            id_mapping[old_id] = None  # orphaned

    # Emit YAML — use existing BP1 name (preserve local convention) but log if v8.0 differs
    out = emit_yaml(bp1_id, existing["name"], industry, bp1_desc_v8, bp1_realizes,
                    f"{cat}.0", bp2_data, id_mapping)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)

    return {
        "bp1_id": bp1_id,
        "bp1_name_local": existing["name"],
        "bp1_name_v8": bp1_name_v8,
        "bp2_count": len(bp2_data),
        "bp3_count": sum(len(b[5]) for b in bp2_data),
        "orphaned_old_ids": list(id_mapping.keys()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cat", help="Category number, e.g. 1, 2, ..., 13. Omit for all.")
    args = ap.parse_args()

    cats = [args.cat] if args.cat else list(CATEGORY_TO_FILE.keys())
    all_orphans = {}
    for cat in cats:
        if cat not in CATEGORY_TO_FILE:
            raise SystemExit(f"Unknown category {cat}")
        result = reauthor_category(cat)
        print(f"✔ Cat {cat} → {result['bp1_id']} ({result['bp2_count']} BP2, {result['bp3_count']} BP3); "
              f"{len(result['orphaned_old_ids'])} orphaned old ids")
        if result["bp1_name_v8"] != result["bp1_name_local"]:
            print(f"   note: v8.0 name '{result['bp1_name_v8']}' ≠ local '{result['bp1_name_local']}' (kept local)")
        if result["orphaned_old_ids"]:
            for oid in sorted(result["orphaned_old_ids"]):
                all_orphans[oid] = cat

    if all_orphans:
        with open("/tmp/orphaned_bp_ids.json", "w") as f:
            json.dump(all_orphans, f, indent=2)
        print(f"\nTotal orphaned old local ids across cats: {len(all_orphans)}")
        print("Written to /tmp/orphaned_bp_ids.json (used by patch_value_streams.py)")


if __name__ == "__main__":
    main()
