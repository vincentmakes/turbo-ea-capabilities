#!/usr/bin/env python3
"""Backfill realizes_capability_ids on cross-industry BP nodes that have
empty arrays — via parent inheritance.

Strategy: a BP3 with no own realizes inherits its BP2 parent's realizes
(or BP2 parent's *inherited* realizes if the BP2 also has none, walking
up to BP1). A BP2 with no own realizes inherits its BP1 parent's realizes.

This is a defensible default: a child process realises *at minimum* the
same capabilities its parent realises. Specific nodes that should realise
*additional* capabilities can be refined manually in follow-up edits.

Out of scope: industry-specific BP1s (BP-130..BP-490 except BP-370). Those
are already populated with realizes_capability_ids per their import.
"""
from __future__ import annotations
import os, glob
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")

CROSS_INDUSTRY = {
    "BP-10", "BP-20", "BP-30", "BP-40", "BP-50", "BP-60",
    "BP-70", "BP-80", "BP-90", "BP-100", "BP-110", "BP-120", "BP-370",
}


def backfill(node, parent_inherited=None):
    """Walk tree, fill empty realizes from parent_inherited."""
    own = node.get("realizes_capability_ids") or []
    if not own and parent_inherited:
        node["realizes_capability_ids"] = list(parent_inherited)
        # Use the inherited set for children
        effective = parent_inherited
    elif own:
        effective = own
    else:
        effective = []
    for c in node.get("children") or []:
        backfill(c, effective)


def emit_yaml(node, indent=0, is_root=False):
    """Re-emit a BP1 tree to preserve formatting consistent with the existing
    files. This is a faithful round-trip emitter."""
    sp = "  " * indent
    L = []
    if is_root:
        L.append(f"id: {node['id']}")
        L.append(f"name: {node['name']}")
        L.append(f"level: {node['level']}")
        if node.get("industry"):
            L.append(f"industry: {node['industry']}")
        if node.get("description"):
            L.append("description: >-")
            L.append(f"  {node['description']}")
        if node.get("framework_refs"):
            L.append("framework_refs:")
            for fr in node["framework_refs"]:
                L.append(f"  - framework: {fr['framework']}")
                L.append(f"    external_id: \"{fr['external_id']}\"")
                if fr.get("version"):
                    L.append(f"    version: \"{fr['version']}\"")
        L.append("realizes_capability_ids:")
        if node["realizes_capability_ids"]:
            for bc in node["realizes_capability_ids"]:
                L.append(f"  - {bc}")
        else:
            L[-1] = "realizes_capability_ids: []"
        L.append("children:")
        for c in node.get("children") or []:
            L.extend(emit_yaml(c, indent=1))
    else:
        # Child node, formatted as `  - id: ...`
        prefix = sp + "- "
        L.append(f"{prefix}id: {node['id']}")
        L.append(f"{sp}  name: {node['name']}")
        L.append(f"{sp}  level: {node['level']}")
        if node.get("description"):
            L.append(f"{sp}  description: >-")
            L.append(f"{sp}    {node['description']}")
        if node.get("framework_refs"):
            L.append(f"{sp}  framework_refs:")
            for fr in node["framework_refs"]:
                L.append(f"{sp}    - framework: {fr['framework']}")
                L.append(f"{sp}      external_id: \"{fr['external_id']}\"")
                if fr.get("version"):
                    L.append(f"{sp}      version: \"{fr['version']}\"")
        if node["realizes_capability_ids"]:
            L.append(f"{sp}  realizes_capability_ids:")
            for bc in node["realizes_capability_ids"]:
                L.append(f"{sp}    - {bc}")
        else:
            L.append(f"{sp}  realizes_capability_ids: []")
        children = node.get("children") or []
        if not children:
            L.append(f"{sp}  children: []")
        else:
            L.append(f"{sp}  children:")
            for c in children:
                L.extend(emit_yaml(c, indent=indent + 2))
    return L


def process_file(path):
    with open(path) as f:
        tree = yaml.safe_load(f)
    if tree["id"] not in CROSS_INDUSTRY:
        return None
    # Count empties before
    def count_empties(node):
        n = 0
        if not (node.get("realizes_capability_ids") or []) and node["level"] >= 2:
            n += 1
        for c in node.get("children") or []:
            n += count_empties(c)
        return n
    before = count_empties(tree)

    backfill(tree, parent_inherited=tree.get("realizes_capability_ids") or [])

    after = count_empties(tree)
    out_lines = emit_yaml(tree, is_root=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")
    return tree["id"], before, after


def main():
    total_before = 0
    total_after = 0
    for path in sorted(glob.glob(os.path.join(PROCESSES_DIR, "BP1-*.yaml"))):
        result = process_file(path)
        if not result: continue
        bp1_id, before, after = result
        total_before += before
        total_after += after
        print(f"  {bp1_id}: {before} empty → {after} empty (filled {before - after})")
    print(f"\nTotal: {total_before - total_after} nodes filled (was {total_before} empty, now {total_after})")


if __name__ == "__main__":
    main()
