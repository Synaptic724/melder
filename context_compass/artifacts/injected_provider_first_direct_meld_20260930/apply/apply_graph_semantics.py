"""
Author the injected_provider_first_direct_meld semantics (0.2.8215) into the two touched graph descriptors.

Usage: python apply_graph_semantics.py <repository root>
Edits authored fields only (responsibilities); the mechanical tier stays the extractor's. Writes in the
extractor's JSON format (indent=1). Refuses a node or a duplicate it does not expect.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) / "context_compass" / "system_docs" / "graph" / "melder"

ADDITIONS = {
    ("aether/conduit/meld/meld.json", "melder.aether.conduit.meld.meld.Meld"): [
        "routes a spell flagged resolution_required through the deferred lane: phases 8-11 for an existing creation"
        " or its current Phase 5 root, otherwise the full target pass 5-11 followed by a resolution-validity check"
        " for the conduit (_requires_own_target_pass, _raise_unless_resolution_valid)",
    ],
    ("aether/spellbook/spellbook_creation_system.json",
     "melder.aether.spellbook.spellbook_creation_system.SpellbookCreationSystem"): [
        "after a successful target-local pass, flags each owned, resolvable, non-existing-creation dependency in its"
        " scope that has no phase-11 plan, no published context and no flag yet with resolution_required and a"
        " door-epoch bump, under that dependency's spell lock (flag_dependencies_without_own_plan)",
    ],
}

touched = {}
for (relative, node_id), items in ADDITIONS.items():
    if relative not in touched:
        touched[relative] = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    node = touched[relative]["nodes"][node_id]
    for item in items:
        if item in node.get("responsibilities", []):
            raise SystemExit(f"{node_id}: responsibility already present")
        node.setdefault("responsibilities", []).append(item)
for relative, descriptor in touched.items():
    text = json.dumps(descriptor, indent=1) + "\n"
    if "context_compass/" in text:
        raise SystemExit(f"{relative}: package path in a descriptor")
    (ROOT / relative).write_text(text, encoding="utf-8", newline="\n")
    print("authored", relative)
