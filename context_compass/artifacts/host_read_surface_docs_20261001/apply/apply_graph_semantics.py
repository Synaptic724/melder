"""
Author the 0.2.8208 read accessors into four graph descriptors (Aether already names its frame lookups).

Usage: python apply_graph_semantics.py <repository root>
Edits authored fields only (responsibilities); the mechanical tier, already current for these files, stays the
extractor's. Writes in the extractor's JSON format (indent=1). Refuses a node or a duplicate it does not expect.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) / "context_compass" / "system_docs" / "graph" / "melder"

ADDITIONS = {
    ("aether/aetheric_frame/aetheric_frame.json", "melder.aether.aetheric_frame.aetheric_frame.AethericFrame"): [
        "reports the frame-wide shared rich Spellbook configuration (shared_spellbook_configuration) only while its"
        " posture shares one; None otherwise or before a Book binds one",
    ],
    ("aether/aetheric_frame/aetheric_frame_configuration.json",
     "melder.aether.aetheric_frame.aetheric_frame_configuration.AethericFrameConfiguration"): [
        "reports whether the posture is frozen, the world's settlement point, under its lock without changing it"
        " (frozen)",
    ],
    ("aether/spellbook/configuration/spellbook_configuration.json",
     "melder.aether.spellbook.configuration.spellbook_configuration.SpellbookConfiguration"): [
        "reports its target frame (aether_frame, fixed at construction) and its freeze state (frozen, read under its"
        " lock) without changing either",
    ],
    ("aether/conduit/conduit.json", "melder.aether.conduit.conduit.Conduit"): [
        "returns the Spellbook it resolves through, borrowed (spellbook): the conjuring Book for a root, the root's"
        " Book for a lesser, the new Book after upgrade_to_normal",
    ],
}

touched = {}
for (relative, node_id), items in ADDITIONS.items():
    if relative not in touched:
        raw = (ROOT / relative).read_text(encoding="utf-8")
        if json.dumps(json.loads(raw), indent=1) + "\n" != raw:
            raise SystemExit(f"{relative}: not in the extractor's format; refusing to rewrite it")
        touched[relative] = json.loads(raw)
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
