"""Author graph prose for the class binding-profile annotation fix in a scratch descriptor tree (2026-09-26).

Usage: python author_graph.py <descriptor_root>
Edits authored fields only; the mechanical tier comes from extract_graph.py.
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
REL = "melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.json"
NODE = "melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy.BindingProfileStrategy"
ADD = ("reads class-level annotations evaluated where every name resolves, otherwise without evaluating the "
       "unavailable names (kept as source text, the ClassInspector read), so the fingerprint's sorted annotation keys "
       "cover every annotated field; any other read failure yields an empty mapping")

path = root / REL
data = json.loads(path.read_text(encoding="utf-8"))
items = data["nodes"][NODE].setdefault("responsibilities", [])
if ADD not in items:
    items.append(ADD)
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("authored", NODE)
