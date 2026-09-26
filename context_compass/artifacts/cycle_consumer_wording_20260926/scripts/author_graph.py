"""Author graph prose for the cycle-consumer lane in a scratch descriptor tree (2026-09-26).

Usage: python author_graph.py <descriptor_root>. Authored fields only; idempotent.
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
REL = "melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.json"
NODE = "melder.aether.spellbook.spell_compiler.validation.strategies.circular_dependency_strategy.CircularDependencyStrategy"
OLD = "names the cycle's members (the loop closed once) and says how to break it"
NEW = ("names the cycle's members (the loop closed once) and says how to break it; a spell outside the cycle is "
       "told which of its dependencies leads there and that it is not part of that cycle (_cycle_message)")

path = root / REL
data = json.loads(path.read_text(encoding="utf-8"))
items = data["nodes"][NODE]["responsibilities"]
if NEW not in items:
    assert OLD in items, OLD
    items[items.index(OLD)] = NEW
path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("authored", NODE)
