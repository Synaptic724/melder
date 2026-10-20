"""Refine the rule-1 graph prose after re-reading the source against it (melder_1, 2026-10-16).

usage (from the repository root): python <this script> [--check]
Run after graph_semantics_2026_10_16.py. Edits only authored `responsibilities` entries of four nodes, each
refusing unless the field holds exactly the value it replaces: SpellSystemState (the re-publication runs on the
registry's request), SpellSystemStates (it decides that re-publication), RiskManager (register_conduit refreshes
once) and Spellbook (bind and notch pass the capability to register_index). Writes JSON as the extractor does.
"""
import json
import pathlib
import sys

CHECK = "--check" in sys.argv[1:]
G = pathlib.Path("context_compass/system_docs/graph/melder/aether")


def edit(rel, node_id, old, new):
    path = G / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    resp = data["nodes"][node_id]["responsibilities"]
    assert resp.count(old) == 1, (node_id, resp)
    resp[resp.index(old)] = new
    if not CHECK:
        path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(("checked " if CHECK else "edited ") + node_id.rsplit(".", 1)[1])


DEV = "aetheric_frame/dev_ops/"
NS = "melder.aether.aetheric_frame.dev_ops."
edit(DEV + "spell_system_states/spell_system_state.json",
     NS + "spell_system_states.spell_system_state.SpellSystemState",
     "updates flags without touching validity (update_flags) and re-publishes the current validity to RiskManager "
     "when a flag it reads changed while the validity did not (_republish_validity, 0.2.8247)",
     "updates flags without touching validity or publishing (update_flags), and on the registry's request publishes "
     "its unchanged validity to RiskManager again (_republish_validity, 0.2.8247)")
edit(DEV + "spell_system_states/spell_system_states.json",
     NS + "spell_system_states.spell_system_states.SpellSystemStates",
     "records the selected version's capability as SpellState.non_resolvable in register_index before the gate "
     "publishes, and publishes the flagged lineages as one frozenset (non_resolvable_index_ids) that RiskManager "
     "reads without a lock (0.2.8247)",
     "records the selected version's capability as SpellState.non_resolvable in register_index before the gate "
     "publishes - re-publishing the validity when the write changed the flag on a lineage already gated - and "
     "publishes the flagged lineages as one frozenset (non_resolvable_index_ids) that RiskManager reads without a "
     "lock (0.2.8247)")
edit(DEV + "risk_manager/risk_manager.json",
     NS + "risk_manager.risk_manager.RiskManager",
     "leaves a lineage flagged SpellState.non_resolvable out of the Book flag with one subset test against "
     "SpellSystemStates.non_resolvable_index_ids, while its risk stays tracked (0.2.8247)",
     "leaves a lineage flagged SpellState.non_resolvable out of the Book flag with one subset test against "
     "SpellSystemStates.non_resolvable_index_ids, while its risk stays tracked, and register_conduit seeds every "
     "visible spell before refreshing the flag once (0.2.8247)")
edit("spellbook/spellbook.json",
     "melder.aether.spellbook.spellbook.Spellbook",
     "forwards native resolvable policy through active and inactive binding and exposes it in spell descriptions",
     "forwards native resolvable policy through active and inactive binding, into the lineage state at bind and "
     "notch (register_index(resolvable=...), 0.2.8247), and exposes it in spell descriptions")
