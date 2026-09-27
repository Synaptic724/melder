"""Prototype A for the self-dependency lane (VM copies only): argv[1] = tree root.

Phase 3 keeps a self-resolution as a recorded dependency without a DAG edge, so Phase 4's SELF_DEPENDENCY check
refuses the spell; CircularDependencyStrategy skips self-loops so the fault is reported once.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

ROOT = pathlib.Path(sys.argv[1])
P3 = ROOT / "src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py"
CIRC = ROOT / "src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py"

replace_block(P3, """                dependency_spell_ids.append(dep_spell_id)
                socket_targets.setdefault(key, []).append(dep_spell_id)

                dag.add_node(key=dep_spell_id, payload=spell_obj)""", """                dependency_spell_ids.append(dep_spell_id)
                socket_targets.setdefault(key, []).append(dep_spell_id)
                if dep_spell_id == root_id:
                    # A parameter that resolves to this same spell (a constructor taking its
                    # own class) cannot be a DAG edge. Its id stays recorded as a dependency so
                    # Phase 4's SELF_DEPENDENCY check refuses the spell with a readable message.
                    continue

                dag.add_node(key=dep_spell_id, payload=spell_obj)""")

replace_block(CIRC, """                if dep_id not in adjacency:""", """                if dep_id == node_id:
                    # A direct self-dependency is SelfDependencyStrategy's to report.
                    continue
                if dep_id not in adjacency:""")
BRC = ROOT / "src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py"
replace_block(BRC, """            spell_key = spell_instance.key
            topology = spell_instance._spell_system_states.get_local_topology(spell_instance.spell_index)""",
"""            spell_key = spell_instance.key
            # Phase 3 recorded this spell as its own dependency (a constructor taking its own class):
            # SelfDependencyStrategy reports that, so the spell's own-key edge is left out here.
            self_dependent = spell_instance.spell_index.selected_spell_id in spell_instance.dependencies
            topology = spell_instance._spell_system_states.get_local_topology(spell_instance.spell_index)""")
replace_block(BRC, """                target_key = self._binding_key_for_requirement(param)
                if target_key is None:
                    continue""", """                target_key = self._binding_key_for_requirement(param)
                if target_key is None:
                    continue
                if self_dependent and target_key == spell_key:
                    continue""")
print("prototype A applied to", ROOT)
