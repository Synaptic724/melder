"""Author graph prose for the self-dependency lane in a scratch descriptor tree (2026-09-26).

Usage: python author_graph.py <descriptor_root>. Authored fields only; idempotent.
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])


def edit(rel: str, node_id: str, add: str = None, replace: tuple = None) -> None:
    """Append one responsibility, or replace one exactly, on one node."""
    path = root / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data["nodes"][node_id].setdefault("responsibilities", [])
    if replace is not None:
        old, new = replace
        if new not in items:
            assert old in items, (node_id, old)
            items[items.index(old)] = new
    if add is not None and add not in items:
        items.append(add)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("authored", node_id)


edit("melder/aether/spellbook/spell_compiler/validation/strategies/self_validation_strategy.json",
     "melder.aether.spellbook.spell_compiler.validation.strategies.self_validation_strategy.SelfDependencyStrategy",
     add="names the constructor parameter(s) that resolve to the spell itself from its Phase-3 local topology "
         "(details parameter_names); the message stays generic without a topology; since 2026-09-26 Phase 3 "
         "records a self-resolution instead of aborting, so this check is what refuses such a spell")
edit("melder/utilities/custom_exceptions/spellbook_validation_error.json",
     "melder.utilities.custom_exceptions.spellbook_validation_error.SpellbookValidationError",
     replace=("drop exact repeats, a binding-key cycle already reported as CIRCULAR_DEPENDENCY, and restating codes "
              "(root_not_viable, broken_spell_in_dag) when another error is shown",
              "drop exact repeats, a binding-key cycle already reported as CIRCULAR_DEPENDENCY, a CIRCULAR_DEPENDENCY on "
              "a spell that reports SELF_DEPENDENCY, and restating codes (root_not_viable, broken_spell_in_dag) when "
              "another error is shown"))
print("done")
