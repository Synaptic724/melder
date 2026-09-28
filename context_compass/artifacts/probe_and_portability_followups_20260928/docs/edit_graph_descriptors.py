"""Update ConduitMeld's authored graph prose (2026-09-28, 0.2.8205) after a full read of conduit_meld.py.

Only responsibilities change; the mechanical tier is the extractor's. Written with json.dumps(indent=1) + newline,
the extractor's own format. Usage: python edit_graph_descriptors.py <graph descriptor root>
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
path = root / "melder/aether/conduit/meld/conduit_meld.json"
node_id = "melder.aether.conduit.meld.conduit_meld.ConduitMeld"
REPLACE = {
    "provides reuse-only and live-creation status probes over conduit-scoped storage":
        "provides reuse-only and live-creation status probes over the store each lifetime uses through this "
        "door: the conduit store for many and unique_per_conduit, the Spell owner's store for unique, the "
        "lineage root for unique_per_conduit_lineage and the elected leader for unique_per_conduit_cluster",
}
ADD = [
    "mints the name/class warm entries (Meld._fast_input_doors) on the same success arms as the id entry for "
    "meld('Name') and meld(Cls) shapes; it never reads them - the public front doors do",
]
data = json.loads(path.read_text(encoding="utf-8"))
node = data["nodes"][node_id]
responsibilities = list(node["responsibilities"])
for old, new in REPLACE.items():
    if responsibilities.count(old) != 1:
        raise SystemExit(f"responsibility not found once: {old!r}")
    responsibilities[responsibilities.index(old)] = new
for line in ADD:
    if line in responsibilities:
        raise SystemExit(f"responsibility already present: {line!r}")
    responsibilities.append(line)
node["responsibilities"] = responsibilities
path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
print("edited", node_id)
