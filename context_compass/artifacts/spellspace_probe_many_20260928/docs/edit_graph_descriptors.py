"""Update the authored tier of SpellSpaceMeld for the 2026-09-28 probe fix (0.2.8204).

Only responsibilities change; the mechanical tier is the extractor's. Written with json.dumps(indent=1) + newline,
the extractor's own format. Usage: python edit_graph_descriptors.py <graph descriptor root>
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
path = root / "melder/aether/conduit/meld/spellspace_meld.json"
node_id = "melder.aether.conduit.meld.spellspace_meld.SpellSpaceMeld"
REPLACE = {
    "routes unique_per_spell_space storage through spellspace-local Creations":
        "routes unique_per_spell_space storage through spellspace-local Creations, which also hold the "
        "disposal-bearing many objects melded through this door (the innermost scope)",
    "provides live-creation status over spellspace-local and owner-conduit storage":
        "reports live-creation status from the store each lifetime uses through this door: many and "
        "unique_per_spell_space from spellspace-local Creations, unique_per_conduit from the owner conduit's, "
        "unique, lineage and cluster from their shared stores",
}
data = json.loads(path.read_text(encoding="utf-8"))
node = data["nodes"][node_id]
responsibilities = list(node["responsibilities"])
for old, new in REPLACE.items():
    if responsibilities.count(old) != 1:
        raise SystemExit(f"responsibility not found once: {old!r}")
    responsibilities[responsibilities.index(old)] = new
node["responsibilities"] = responsibilities
path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
print("edited", node_id)
