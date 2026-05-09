#!/usr/bin/env python3
"""Verify cross-industry BP nodes' framework_refs against APQC PCF v8.0.

For each cross-industry BP1 file, walk every node and:
1. Read its framework_refs[0].external_id (the APQC code) and current name.
2. Look up that code in the v8.0 hierarchy.
3. If v8.0[code] name matches local name (fuzzy / case-insensitive),
   the node's v8.0 label is correct → leave version "8.0".
4. If v8.0[code] is a *different* process (or absent), the local node
   actually anchors on v7.4 → revert version label to "7.4.0" and add an
   inline note that v8.0 reorganised this position.

Outputs a report and (with --apply) applies the corrections in place.
"""
from __future__ import annotations
import argparse, json, os, re
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")

with open("/tmp/apqc_v8.json") as f:
    V8 = json.load(f)

CROSS_INDUSTRY = [
    "BP1-develop-vision-and-strategy.yaml",
    "BP1-develop-and-manage-products-and-services.yaml",
    "BP1-market-and-sell-products-and-services.yaml",
    "BP1-manage-supply-chain-for-physical-products.yaml",
    "BP1-deliver-services.yaml",
    "BP1-manage-customer-service.yaml",
    "BP1-develop-and-manage-human-capital.yaml",
    "BP1-manage-information-technology.yaml",
    "BP1-manage-financial-resources.yaml",
    "BP1-acquire-construct-and-manage-assets.yaml",
    "BP1-manage-enterprise-risk-compliance-remediation-and-resiliency.yaml",
    "BP1-manage-external-relationships.yaml",
    "BP1-develop-and-manage-business-capabilities.yaml",
]


def normalize(s):
    """Strip case, punctuation, and common style differences for fuzzy match."""
    if not s: return ""
    s = s.lower()
    s = re.sub(r"[/\&\-,;:\(\)\[\]\.]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Common minor wording variants: ignore plural-vs-singular trailing 's'
    return s


def names_match(local, v8):
    n_local = normalize(local)
    n_v8 = normalize(v8)
    if n_local == n_v8: return True
    # Allow plural/singular drift on the trailing word
    if n_local.rstrip("s") == n_v8.rstrip("s"): return True
    # Allow "and" vs "&"
    return n_local.replace(" and ", " & ") == n_v8.replace(" and ", " & ")


def get_apqc(node):
    for fr in node.get("framework_refs") or []:
        if fr.get("framework") == "APQC-PCF":
            return fr
    return None


def classify_node(node, depth=0):
    fr = get_apqc(node)
    if not fr: return None
    code = fr.get("external_id", "")
    if not re.match(r"^\d+(\.\d+){0,3}$", code):
        return None  # framework_refs uses prose label, not numeric code (industry-specific BP1)
    v8_name = V8.get(code)
    if v8_name is None:
        return ("removed_in_v8", code, node["name"], None)
    if names_match(node["name"], v8_name):
        return ("preserved", code, node["name"], v8_name)
    return ("redefined_in_v8", code, node["name"], v8_name)


def walk(tree, out=None, depth=0):
    if out is None: out = []
    c = classify_node(tree, depth)
    if c: out.append((tree["id"], depth, c))
    for child in tree.get("children") or []:
        walk(child, out, depth + 1)
    return out


def patch_file(path, apply=False):
    """Walk YAML; for each redefined_in_v8 / removed_in_v8 node, patch the
    `version: "8.0"` line under that node's framework_refs to `"7.4.0"`.
    """
    with open(path) as f: tree = yaml.safe_load(f)
    classifications = walk(tree)
    preserved = [c for c in classifications if c[2][0] == "preserved"]
    redefined = [c for c in classifications if c[2][0] == "redefined_in_v8"]
    removed = [c for c in classifications if c[2][0] == "removed_in_v8"]

    print(f"\n{os.path.basename(path)}")
    print(f"  preserved (v8.0 holds): {len(preserved)}")
    print(f"  redefined in v8.0 (revert to 7.4.0): {len(redefined)}")
    print(f"  removed in v8.0 (revert to 7.4.0): {len(removed)}")
    for nid, depth, (status, code, lname, vname) in redefined[:10]:
        print(f"    REDEFINED {nid:<14} {code:<10} '{lname}' (v8 has: '{vname}')")
    for nid, depth, (status, code, lname, vname) in removed[:10]:
        print(f"    REMOVED   {nid:<14} {code:<10} '{lname}' (v8 has no such code)")

    if not apply:
        return preserved, redefined, removed

    # Build set of node ids that should be reverted to v7.4.0
    revert_ids = {c[0] for c in redefined + removed}
    if not revert_ids:
        return preserved, redefined, removed

    # Read raw lines and patch
    with open(path) as f: lines = f.readlines()
    new_lines = []
    current_node_id = None
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)(?:- )?id: (BP-\S+)$", line)
        if m:
            current_node_id = m.group(2)
        # Look for `version: "8.0"` lines and check if we're inside a redefined node
        if current_node_id in revert_ids and re.match(r"^\s*version: \"8\.0\"$", line):
            indent = re.match(r"^(\s*)", line).group(1)
            new_lines.append(f'{indent}version: "7.4.0"\n')
            continue
        new_lines.append(line)
    with open(path, "w") as f: f.writelines(new_lines)
    return preserved, redefined, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--file")
    args = ap.parse_args()

    grand = {"preserved": 0, "redefined": 0, "removed": 0}
    for fname in CROSS_INDUSTRY:
        if args.file and args.file not in fname: continue
        path = os.path.join(PROCESSES_DIR, fname)
        if not os.path.exists(path): continue
        p, r, rm = patch_file(path, apply=args.apply)
        grand["preserved"] += len(p)
        grand["redefined"] += len(r)
        grand["removed"] += len(rm)
    print("\n" + "=" * 60)
    print(f"GRAND TOTAL: preserved={grand['preserved']}, redefined={grand['redefined']}, removed={grand['removed']}")
    if args.apply:
        print("(applied — version labels updated)")


if __name__ == "__main__":
    main()
