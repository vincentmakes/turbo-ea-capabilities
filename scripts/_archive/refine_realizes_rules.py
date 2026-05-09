#!/usr/bin/env python3
"""Targeted refinement of realizes_capability_ids on cross-industry BP nodes.

Rule-based augment: for each BP node, scan its name for capability-keyword
patterns and add the corresponding BC L1 ids to its realizes (deduplicating).
This catches obvious cross-references the parent-inheritance backfill missed.

E.g. a BP3 "Calculate Payroll Taxes" inherits BC-300 (HR) from its BP2
parent — but it should also realise BC-220 (Tax) and BC-200 (Financial)
because of the keywords in its name.
"""
from __future__ import annotations
import os, glob, re
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSES_DIR = os.path.join(REPO_ROOT, "catalogue", "processes")

# Keyword → BC L1 ids that should be added to realizes when keyword is in
# the node name (case-insensitive). Whitespace-bounded.
RULES = [
    (r"\btax(es|ation)?\b", ["BC-220"]),
    (r"\baudit\b", ["BC-140"]),
    (r"\bcompli(ance|e)\b", ["BC-130"]),
    (r"\bregulatory\b", ["BC-130"]),
    (r"\bpayroll\b", ["BC-300", "BC-200"]),
    (r"\b(financial|finance) (statement|report|reporting)", ["BC-200", "BC-230"]),
    (r"\btreasury\b", ["BC-210"]),
    (r"\bcash\b", ["BC-210"]),
    (r"\b(risk|risks)\b", ["BC-120"]),
    (r"\b(cyber|cybersecurity|cyberattack)\b", ["BC-620"]),
    (r"\bsecurity\b", ["BC-620"]),
    (r"\bknowledge\b", ["BC-830"]),
    (r"\binnovation\b", ["BC-800"]),
    (r"\bcustomer\b", ["BC-420"]),
    (r"\bmarketing\b", ["BC-400"]),
    (r"\b(procure|procurement|sourcing)\b", ["BC-500"]),
    (r"\bsupplier\b", ["BC-510"]),
    (r"\bsupply[\s-]?chain\b", ["BC-520"]),
    (r"\binventory\b", ["BC-530"]),
    (r"\b(quality|qa|qc)\b", ["BC-720"]),
    (r"\b(hse|safety|health and safety)\b", ["BC-730"]),
    (r"\bsustainab(le|ility|ly)\b", ["BC-740"]),
    (r"\b(sales|selling)\b", ["BC-410"]),
    (r"\bpricing\b", ["BC-440"]),
    (r"\bproject\b", ["BC-900"]),
    (r"\bportfolio\b", ["BC-900"]),
    (r"\bchange management\b", ["BC-910"]),
    (r"\btransform(ation|ing)\b", ["BC-920"]),
    (r"\bbusiness process\b", ["BC-930"]),
    (r"\bbusiness continuit(y|ies)\b", ["BC-160"]),
    (r"\bdisaster recovery\b", ["BC-160"]),
    (r"\binvestor\b", ["BC-240"]),
    (r"\blegal\b", ["BC-150"]),
    (r"\b(facilit(y|ies))\b", ["BC-700"]),
    (r"\b(real estate|property)\b", ["BC-710"]),
    (r"\b(intellectual property|IP)\b", ["BC-840"]),
    (r"\bgovernance\b", ["BC-110"]),
    (r"\bbrand\b", ["BC-400"]),
    (r"\bcommunication\b", ["BC-850"]),
    (r"\b(corporate|enterprise) strategy\b", ["BC-100"]),
    (r"\barchitecture\b", ["BC-170"]),
    (r"\bproduct (lifecycle|management)\b", ["BC-820"]),
    (r"\b(R&D|research and development|research)\b", ["BC-810"]),
    (r"\bdata (governance|management|quality)\b", ["BC-610"]),
    (r"\bIT (operation|operations|service)\b", ["BC-600"]),
    (r"\bhuman (capital|resources|resource)\b", ["BC-300"]),
]


def augment_node(node):
    realizes = list(node.get("realizes_capability_ids") or [])
    name = node.get("name", "")
    added = 0
    for pattern, bcs in RULES:
        if re.search(pattern, name, re.IGNORECASE):
            for bc in bcs:
                if bc not in realizes:
                    realizes.append(bc)
                    added += 1
    if added:
        node["realizes_capability_ids"] = sorted(
            realizes,
            key=lambda x: tuple(int(s) for s in x.replace("BC-", "").split("."))
        )
    return added


def walk(node, total_added=0):
    if node.get("level", 1) >= 2:
        total_added += augment_node(node)
    for c in node.get("children") or []:
        total_added = walk(c, total_added)
    return total_added


def emit_yaml(node, indent=0, is_root=False):
    sp = "  " * indent
    L = []
    if is_root:
        L.append(f"id: {node['id']}")
        # Quote name if it contains parens (otherwise YAML may misparse)
        nm = node['name']
        if '(' in nm or ':' in nm: L.append(f'name: "{nm}"')
        else: L.append(f"name: {nm}")
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
        if node["realizes_capability_ids"]:
            L.append("realizes_capability_ids:")
            for bc in node["realizes_capability_ids"]:
                L.append(f"  - {bc}")
        else:
            L.append("realizes_capability_ids: []")
        L.append("children:")
        for c in node.get("children") or []:
            L.extend(emit_yaml(c, indent=1))
    else:
        prefix = sp + "- "
        L.append(f"{prefix}id: {node['id']}")
        nm = node['name']
        if '(' in nm or ':' in nm: L.append(f'{sp}  name: "{nm}"')
        else: L.append(f"{sp}  name: {nm}")
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


def main():
    total = 0
    for path in sorted(glob.glob(os.path.join(PROCESSES_DIR, "BP1-*.yaml"))):
        with open(path) as f:
            tree = yaml.safe_load(f)
        n = walk(tree)
        if n == 0: continue
        out = "\n".join(emit_yaml(tree, is_root=True)) + "\n"
        with open(path, "w") as f:
            f.write(out)
        total += n
        print(f"  {tree['id']:<8} +{n} BC ids")
    print(f"\nTotal augmented: {total}")


if __name__ == "__main__":
    main()
