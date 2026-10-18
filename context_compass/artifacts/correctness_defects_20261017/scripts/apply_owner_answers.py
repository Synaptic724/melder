"""Apply the owner's answers on S2 and S5 (chat 2026-10-17) to S2, S1, S5, S10, the epic and the board. <NOW>.

Every edit is an exact replacement checked to occur once; everything is checked in memory before anything is written.
The DECISION/FACT notes are appended separately with append_note.py.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
ST = "tickets/stories/"
S1 = ST + "2026-10-17_staged_version_releases_active_signature_story.md"
S2 = ST + "2026-10-17_notch_moves_signature_by_incoming_key_only_story.md"
S5 = ST + "2026-10-17_restore_drops_separated_parked_version_story.md"
S10 = ST + "2026-10-17_minted_index_selects_its_parked_version_story.md"
EPIC = "tickets/epics/2026-10-17_correctness_defects_epic.md"
BOARD = "attention_board.md"


def sub(text: str, old: str, new: str) -> str:
    """Replace `old` (which must occur exactly once) with `new`; @@NOW@@ becomes NOW."""
    assert text.count(old) == 1, old[:80]
    return text.replace(old, new.replace("@@NOW@@", NOW), 1)


def updated(text: str) -> str:
    """Set the Metadata `- Updated:` line to NOW."""
    text, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, text, count=1)
    assert count == 1
    return text


def check(text: str) -> str:
    """Refuse long lines that hold no path."""
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


texts = {path: pathlib.Path(path).read_text(encoding="utf-8") for path in (S1, S2, S5, S10, EPIC, BOARD)}

# --- S2: the notch moves the claim; staging stays open --------------------------------------------------------------
t = texts[S2]
t = sub(t, "- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent;\n",
        "- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17);\n")
t = sub(t, "- EXECUTION_BOUNDARY: step 4 of `Spellbook._apply_notch` (the signature repoint) and, if the owner rules that one\n"
           "  index holds one signature, the admission checks of `bind_inactive` and `add_to_spell_index`; regression tests;\n"
           "  system docs with their indexes and the graph; the release note; one notch; the rebuild last.\n",
        "- EXECUTION_BOUNDARY: step 4 of `Spellbook._apply_notch` (the signature repoint and the refusal of a key another\n"
        "  active spell holds); regression tests; system docs with their indexes and the graph; the release note; one notch;\n"
        "  the rebuild last. Staging stays open to any key (owner, 2026-10-17).\n")
t = sub(t, "- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT if the notch-seam backlog task lands first\n"
           "  with another order of checks.\n",
        "- FAILURE_ESCALATION: CONFLICT if the notch-seam backlog task lands first with another order of checks, or while\n"
        "  spellbook.py is held.\n")
t = sub(t, "- In scope: the notch's signature handling; the staging admission only if the owner rules one signature per index.\n",
        "- In scope: the notch's signature handling. One index may hold versions under different signatures (owner,\n"
        "  2026-10-17), so staging and index moves keep their admission.\n")
t = sub(t, "- [ ] Task: the owner's answer on one signature per index.\n",
        "- [x] Task: the owner's answer on one signature per index (2026-10-17: one index may hold several; DECISION note).\n")
t = sub(t, "- Or, if the owner rules one signature per index: staging or adding a version keyed differently from its index's\n"
           "  signature is refused, so C5's world cannot be built; C7's refusal holds either way.\n",
        "- Staging or adding a version keyed differently from its index's other versions stays allowed (owner, 2026-10-17).\n")
t = sub(t, "  no, staging refuses a differently keyed version and C5 cannot occur. C7 needs the notch refusal either way.\n",
        "  no, staging refuses a differently keyed version and C5 cannot occur. C7 needs the notch refusal either way.\n"
        "  Answered (owner, @@NOW@@): yes - \"1 spellindex can hold versions with different binding\n"
        "  signatures, this is why revalidation happens\" (DECISION note).\n")
t = sub(t, "- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).\n",
        "- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).\n"
        "- @@NOW@@: the owner answered the open question - one index may hold versions under different\n"
        "  signatures, so the notch moves the claim (DECISION note).\n")
t = sub(t, "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the\n"
           "  owner (one signature per index?). The fix sits in spellbook.py, which melder_1 holds until its rule-2 closure.\n"
           "- Next: (1) the owner's answer and scheduling; (2) patch docs for `_apply_notch` step 4; (3) the fix, its tests,\n"
           "  docs, notch and the rebuild.\n",
        "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner answered its\n"
        "  question (one index may hold several signatures; the notch moves the claim). The fix sits in spellbook.py, which\n"
        "  melder_1 holds until its rule-2 closure.\n"
        "- Next: (1) the owner's scheduling; (2) patch docs for `_apply_notch` step 4; (3) the fix, its tests, docs, notch\n"
        "  and the rebuild.\n")
texts[S2] = check(updated(t))

# --- S1: the side question settles to the minimal fix --------------------------------------------------------------
t = texts[S1]
t = sub(t, "- FAILURE_ESCALATION: DECISION_REQUEST if the fix should make staging refuse a version keyed like another active\n"
           "  spell (C6) instead of only not releasing it; CONFLICT if the holder of spellbook.py is mid-change in the seam.\n",
        "- FAILURE_ESCALATION: CONFLICT if the holder of spellbook.py is mid-change in the seam. Staging stays open to any\n"
        "  key (DECISION note of @@NOW@@).\n")
t = sub(t, "  claim? The owner's call; the minimal fix is the latter.\n",
        "  claim? The owner's call; the minimal fix is the latter.\n"
        "  Settled (@@NOW@@) by the owner's answer on STORY-2026-10-17-notch_moves_signature_by_incoming_key_only:\n"
        "  the minimal fix - staging stays open to any key (DECISION note).\n")
t = sub(t, "- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).\n",
        "- 2026-10-17T20:23:51Z: filed under EPIC-2026-10-17-correctness_defects from sweep A1 (Notes).\n"
        "- @@NOW@@: the open question settled by the owner's answer on the notch-signature story: the minimal\n"
        "  fix (DECISION note).\n")
texts[S1] = check(updated(t))

# --- S5: restore and graft rebuild a parked-only index parked ------------------------------------------------------
t = texts[S5]
t = sub(t, "- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent; an\n"
           "  active board row; a component patch for the restore engine's staged lane.\n",
        "- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17); an\n"
        "  active board row; component patches for the restore engine's staged lane and the graft runner's fresh-index lane.\n")
t = sub(t, "  them) - rebuild a recorded index whose members are all parked through public verbs, mapping its identity; the\n"
           "  graft runner's same lane if it shares the gap; regression tests; system docs with their indexes and the graph;\n"
           "  the release note; one notch; the rebuild last.\n",
        "  them) - rebuild a recorded index whose members are all parked through public verbs, mapping its identity - and\n"
        "  `GraftRunner`'s fresh-index lane, which parks such members instead of binding the recorded selection active (G2);\n"
        "  regression tests; system docs with their indexes and the graph; the release note; one notch; the rebuild last.\n")
t = sub(t, "- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT if a public verb route needs a file melder_1\n"
           "  holds.\n",
        "- FAILURE_ESCALATION: CONFLICT if a public verb route needs a file melder_1 holds; DECISION_REQUEST if the graft\n"
        "  lane needs the selection STORY-2026-10-17-minted_index_selects_its_parked_version settles first.\n")
t = sub(t, "- The report counts the members as staged and files no `staged_member_anchor_index_not_rebuilt` shortfall for them.\n",
        "- The report counts the members as staged and files no `staged_member_anchor_index_not_rebuilt` shortfall for them.\n"
        "- A graft of such an index's record (fresh-index mode) rebuilds its members parked in a fresh index of the host\n"
        "  Book, never active, and its report counts them as parked.\n")
t = sub(t, "- In scope: the restore (and, if it shares the lane, the graft) of parked-only indexes.\n",
        "- In scope: the restore and the graft of parked-only indexes.\n")
t = sub(t, "- [ ] Task: the owner's answer on the open question.\n",
        "- [x] Task: the owner's answer on the open question (2026-10-17: restore what should be restored; DECISION note).\n")
t = sub(t, "  recorded identity maps to it, and no shortfall naming French.\n",
        "  recorded identity maps to it, and no shortfall naming French.\n"
        "- Grafting the minted index's record (G2) gives the host French parked in an index of its own, none active.\n")
t = sub(t, "  record should stop capturing it and the report should say why - the owner's call.\n",
        "  record should stop capturing it and the report should say why - the owner's call.\n"
        "  Answered (owner, @@NOW@@): \"I think we restore what should be restored\" - it is rebuilt\n"
        "  parked, by a restore and by a graft (DECISION note).\n")
t = sub(t, "- 2026-10-17T20:36:54Z: filed under EPIC-2026-10-17-correctness_defects from sweep A5 (Notes).\n",
        "- 2026-10-17T20:36:54Z: filed under EPIC-2026-10-17-correctness_defects from sweep A5 (Notes).\n"
        "- @@NOW@@: the owner answered the open question - restore what should be restored: a parked-only\n"
        "  index is rebuilt parked by a restore and by a graft (DECISION note).\n")
t = sub(t, "- Scope: a restore rebuilds a parked version that sits alone in its own index (Requirements). Defect proven on\n"
           "  0.2.8251 (Notes); probe, targets and runs in Artifact Links.\n"
           "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the\n"
           "  owner. The fix sits in restore_engine.py, which no other lane holds.\n"
           "- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
        "- Scope: a restore and a graft rebuild a parked version that sits alone in its own index, parked (Requirements).\n"
        "  Defect proven on 0.2.8251 (Notes); probes, targets and runs in Artifact Links.\n"
        "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner answered its\n"
        "  question (restore and graft rebuild a parked-only index parked). The fix sits in restore_engine.py and\n"
        "  graft_runner.py, which no other lane holds.\n"
        "- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n")
texts[S5] = check(updated(t))

# --- S10: G2's criterion narrows to "comes back parked" ------------------------------------------------------------
t = texts[S10]
t = sub(t, "- ENTRY_GATE: the owner's answer to the open question below and to the open question of\n"
           "  STORY-2026-10-17-restore_drops_separated_parked_version (what a restore or a graft of a parked-only index should\n"
           "  produce); the owner schedules the story and assigns an agent; melder_1 has released spellbook.py; an active board\n"
           "  row; patch docs for the seam (and for SpellIndex when the answer is (a)).\n",
        "- ENTRY_GATE: the owner's answer to the open question below (S5's was answered on 2026-10-17: a parked-only index is\n"
        "  rebuilt parked); the owner schedules the story and assigns an agent; melder_1 has released spellbook.py; an active\n"
        "  board row; patch docs for the seam (and for SpellIndex when the answer is (a)).\n")
t = sub(t, "- EXIT_GATE: probe G2 no longer brings French back active (it comes back parked, or the graft refuses with a reason,\n"
           "  per S5's answer), and the live minted index no longer names French as selected (or no reader treats that as\n"
           "  active, per the answer); G1, G3 and G4 unchanged; regression tests pass with the GIL off and on; docs, notch and\n"
           "  the rebuild with both checks OK.\n",
        "- EXIT_GATE: probe G2 brings French back parked (S5's answer, with S5's graft lane), and the live minted index no\n"
        "  longer names French as selected (or no reader treats that as active, per the answer); G1, G3 and G4 unchanged;\n"
        "  regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.\n")
t = sub(t, "- Grafting that index's record into a host never makes French active there.\n",
        "- Grafting that index's record into a host gives French parked there (S5's lane), never active.\n")
t = sub(t, "- [ ] Task: the owner's answer on the open question (and S5's).\n",
        "- [ ] Task: the owner's answer on the open question (S5's was answered on 2026-10-17).\n")
t = sub(t, "- Next: (1) the owner's answers (this story's and S5's) and scheduling; (2) patch docs; (3) the fix, its tests,\n"
           "  docs, notch and the rebuild.\n",
        "- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n")
t = sub(t, "- 2026-10-17T21:47:06Z: filed under EPIC-2026-10-17-correctness_defects from sweep A12 (Notes).\n",
        "- 2026-10-17T21:47:06Z: filed under EPIC-2026-10-17-correctness_defects from sweep A12 (Notes).\n"
        "- @@NOW@@: S5's question answered by the owner (rebuild parked); G2's criterion narrowed (FACT note).\n")
texts[S10] = check(updated(t))

# --- epic -------------------------------------------------------------------------------------------------------
t = texts[EPIC]
t = sub(t, "## Open Questions\n- none yet.\n",
        "## Open Questions\n- The stories' own questions, with the owner: S6, S8 and S10 (S2 and S5 answered 2026-10-17; S1 follows\n"
        "  from S2's answer).\n")
t = sub(t, "  STORY-2026-10-17-restore_drops_separated_parked_version (graft side; MEASURE note).\n",
        "  STORY-2026-10-17-restore_drops_separated_parked_version (graft side; MEASURE note).\n"
        "- @@NOW@@: the owner answered S2 (one index may hold several signatures) and S5 (restore what should be\n"
        "  restored: rebuild parked); S1 follows from S2's answer (DECISION notes).\n")
t = sub(t, "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, open question; its leaked claim\n"
           "  outlives the Book, A7),\n",
        "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2; answered: the notch moves the claim; its\n"
        "  leaked claim outlives the Book, A7),\n")
t = sub(t, "  STORY-2026-10-17-restore_drops_separated_parked_version (p2, open question; a graft activates\n"
           "  the version instead, A12),\n",
        "  STORY-2026-10-17-restore_drops_separated_parked_version (p2; answered: restore and graft rebuild it\n"
        "  parked; a graft activates it today, A12),\n")
t = sub(t, "  Fixes in spellbook.py and conduit.py (S1-S4, S7-S10) wait for melder_1's release; restore_engine.py\n"
           "  (S5) and release_managed_spell.py (S6) are free.\n",
        "  Fixes in spellbook.py and conduit.py (S1-S4, S7-S10) wait for melder_1's release; restore_engine.py and\n"
        "  graft_runner.py (S5) and release_managed_spell.py (S6) are free.\n")
t = sub(t, "  M0-184, M0-185).\n",
        "  M0-184, M0-185). The owner answered S2 and S5 (DECISION note of @@NOW@@); melder_1 told (M0-186).\n")
t = sub(t, "- Next: (1) the owner's answers on the open questions of S2, S5, S6, S8 and S10 (each story's Open Questions);\n",
        "- Next: (1) the owner's answers on the open questions of S6, S8 and S10 (each story's Open Questions);\n")
texts[EPIC] = check(updated(t))

# --- board row ---------------------------------------------------------------------------------------------------
b = texts[BOARD]
b = sub(b, "| Owner answers the open questions of S2, S5, S6, S8 and S10; then a fourth sweep tranche on the owner's word. |",
        "| Owner answers the open questions of S6, S8 and S10; then a fourth sweep tranche on the owner's word. |")
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
texts[BOARD] = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

if "--dry-run" in sys.argv:
    print("dry run OK")
    sys.exit(0)
for path, text in texts.items():
    pathlib.Path(path).write_text(text, encoding="utf-8")
print("applied", NOW)
