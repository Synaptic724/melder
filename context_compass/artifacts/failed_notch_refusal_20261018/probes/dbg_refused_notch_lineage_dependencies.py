"""
Probe: what a refused notch leaves on the lender's lineage, and whether the borrower's consumer melds after it
(STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers).

Usage: python dbg_refused_notch_lineage_dependencies.py <tree root>   (the tree's src/ and tests/ are imported)

It builds the S8 integration file's borrower world (English active, an index-linked borrower with `Speaker`),
stages SelfMade (its constructor takes its own class), notches to it, then prints the lineage's registered
dependencies and validity, the consumer's catch-up view, and the borrower's meld result.
"""
import sys

sys.path.insert(0, sys.argv[1] + "/src")
sys.path.insert(0, sys.argv[1])

import tests.integration.melder.aether.conduit.test_notch_refused_at_commit_integration as T

T._reset_world()
with T._world("dbg_borrower", borrower=True) as world:
    broken_id = world.stage(T.SelfMade)
    states = world.book._spell_system_states
    lineage = states.get_by_index_id(world.index.id)
    print("before notch: lineage deps", [d[:8] for d in lineage.direct_dependencies], "validity", lineage.validity)
    speaker = world.borrower_book.find_spell_by_spell_id(world.speaker_id)
    topology = states.get_local_topology_by_id(world.speaker_id)
    print("speaker topology", [(s.param_name, s.socket_kind.name, s.target_spell_ids) for s in topology.sockets])
    try:
        world.lender.notch_spell(spell_index=world.index, spell_id=broken_id)
    except Exception as error:
        print("notch raised:", type(error).__name__, "|", str(error).splitlines()[0][:72])
    lineage = states.get_by_index_id(world.index.id)
    print("after refusal: english", world.english_id[:8], "selfmade", broken_id[:8])
    print("after refusal: lineage current", lineage.current_spell_id[:8], "deps",
          [d[:8] for d in lineage.direct_dependencies], "validity", lineage.validity)
    meld = world.borrower._meld
    print("speaker may compile:", meld._may_compile(speaker), "planned deps:",
          [d.spell_name for d in meld._iter_planned_dependencies(speaker, speaker._spellbook, states)])
    try:
        world.borrower.meld(spell_id=world.speaker_id)
        print("borrower meld of Speaker: ok")
    except Exception as error:
        print("borrower meld of Speaker failed:", type(error).__name__, "|", " / ".join(str(error).splitlines()))
