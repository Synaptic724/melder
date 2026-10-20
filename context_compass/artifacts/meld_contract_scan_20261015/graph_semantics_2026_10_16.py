"""Author the graph semantics of rule 1 (0.2.8247) in four descriptors (melder_1, 2026-10-16).

usage (from the repository root): python <this script> [--check]
Edits only authored fields (role, responsibilities, owns_state); the extractor owns every other field. Each edit
refuses when the field does not hold the value it expects. Writes JSON the way the extractor does (indent=1, LF).
"""
import json
import pathlib
import sys

CHECK = "--check" in sys.argv[1:]
G = pathlib.Path("context_compass/system_docs/graph/melder/aether/aetheric_frame/dev_ops")
DOTTED = "melder.aether.aetheric_frame.dev_ops."


def edit(rel, node_id, change):
    path = G / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    node = data["nodes"][DOTTED + node_id]
    change(node)
    if not CHECK:
        path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(("checked " if CHECK else "edited ") + rel + " " + node_id)


def spell_state(node):
    owned = node["owns_state"]
    assert owned.count("new_lineage") == 1 and "non_resolvable" not in owned, owned
    owned[owned.index("new_lineage")] = "new_index"
    owned.append("non_resolvable")
    assert node["responsibilities"] == ["labels topology, contract, mutation, and ops state flags for a lineage"]
    node["responsibilities"] = [
        "labels topology, contract, mutation, ops and capability state flags for a lineage",
        "non_resolvable marks a lineage whose selected version was bound resolvable=False: it owes no resolution "
        "verdict, validation never clears it, and RiskManager leaves its risk out of the Book flag (0.2.8247)",
    ]


def spell_system_state(node):
    resp = node["responsibilities"]
    assert len(resp) == 2 and not any("update_flags" in r for r in resp), resp
    resp.append(
        "updates flags without touching validity (update_flags) and re-publishes the current validity to "
        "RiskManager when a flag it reads changed while the validity did not (_republish_validity, 0.2.8247)"
    )


def spell_system_states(node):
    resp = node["responsibilities"]
    assert not any("non_resolvable" in r for r in resp), resp
    resp.append(
        "records the selected version's capability as SpellState.non_resolvable in register_index before the gate "
        "publishes, and publishes the flagged lineages as one frozenset (non_resolvable_index_ids) that RiskManager "
        "reads without a lock (0.2.8247)"
    )
    owned = node["owns_state"]
    assert "_non_resolvable_index_ids" not in owned, owned
    owned.append("_non_resolvable_index_ids")


def risk_manager(node):
    resp = node["responsibilities"]
    assert resp == ["tracks structural and resolution risk per conduit", "reacts to validity changes from spell-system "
                    "state", "pushes validation-required flags back onto spellbooks"], resp
    resp.append(
        "leaves a lineage flagged SpellState.non_resolvable out of the Book flag with one subset test against "
        "SpellSystemStates.non_resolvable_index_ids, while its risk stays tracked (0.2.8247)"
    )


edit("spell_system_states/spell_state.json", "spell_system_states.spell_state.SpellState", spell_state)
edit("spell_system_states/spell_system_state.json", "spell_system_states.spell_system_state.SpellSystemState",
     spell_system_state)
edit("spell_system_states/spell_system_states.json", "spell_system_states.spell_system_states.SpellSystemStates",
     spell_system_states)
edit("risk_manager/risk_manager.json", "risk_manager.risk_manager.RiskManager", risk_manager)
