"""Authored-tier update for the creations_disposal_failures lane (graph descriptor, melder_0, 2026-09-27).

Replaces the Creations node's stale responsibility (first failure stops the object) with the 0.2.80 contract.
Formatting is verified to round-trip (json indent=1 plus a trailing newline) before the write.
Usage: python apply_graph_semantics.py <graph descriptor root (.../graph/melder)>
"""
import json
import os
import sys

assert sys.version_info >= (3, 14), "run with the 3.14 venv"
path = os.path.join(sys.argv[1], "aether/conduit/creations/creations.json")
node_id = "melder.aether.conduit.creations.creations.Creations"
old = "invokes methods in list order; the first method failure stops its object while other objects continue"
new = ("invokes every declared method in list order even after one fails; collects one RuntimeError per failing "
       "method, chained from the raised exception, and never lets one failing object strand the rest")
with open(path, encoding="utf-8", newline="") as handle:
    original = handle.read()
data = json.loads(original)
assert json.dumps(data, indent=1) + "\n" == original, "formatting does not round-trip"
responsibilities = data["nodes"][node_id]["responsibilities"]
if new not in responsibilities:
    assert responsibilities.count(old) == 1, responsibilities
    responsibilities[responsibilities.index(old)] = new
with open(path, "w", encoding="utf-8", newline="") as handle:
    handle.write(json.dumps(data, indent=1) + "\n")
print("updated", node_id)
