"""Apply the owner's answer on S8 (chat 2026-10-17: refuse, nothing moved) to S8, the epic and the board. <NOW>.

Every edit is an exact replacement checked to occur once; everything is checked in memory before anything is written.
The DECISION notes are appended separately with append_note.py.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
S8 = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
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


texts = {path: pathlib.Path(path).read_text(encoding="utf-8") for path in (S8, EPIC, BOARD)}

# --- S8: answer (a), refuse with nothing moved ---------------------------------------------------------------------
t = texts[S8]
t = sub(t, "- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent;\n",
        "- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17);\n")
t = sub(t, "- EXECUTION_BOUNDARY: `Conduit.notch_spell` (its commit and its fan-out) and whatever the answer needs around the\n"
           "  seam - a structural check of the incoming version before `_apply_notch` runs, rollback actions that undo the seam\n"
           "  when the commit fails, or a fan-out that runs whatever the commit raises; regression tests; the system documents\n"
           "  (the SpellIndex Mutation Entry sequence, a failure mode) with their indexes and the graph; the release note; one\n"
           "  notch; the rebuild last.\n",
        "- EXECUTION_BOUNDARY: `Conduit.notch_spell` (its commit) and what the refusal needs around the seam - a structural\n"
        "  check of the incoming version before `_apply_notch` runs, or rollback actions that undo the seam when the commit\n"
        "  fails (the patch picks); the stale docstring of `_stage_spell_for_structural_phases` (FACT note); regression\n"
        "  tests; the system documents (the SpellIndex Mutation Entry sequence, a failure mode) with their indexes and the\n"
        "  graph; the release note; one notch; the rebuild last.\n")
t = sub(t, "- EXIT_GATE: probe N2 ends with the lender and its borrower on one version, as the answer says, and the exception\n"
           "  saying which; N1 and N3 unchanged; regression tests pass with the GIL off and on; docs, notch and the rebuild with\n"
           "  both checks OK.\n",
        "- EXIT_GATE: probe N2 ends with the lender and its borrower on English, the staged version still parked, and the\n"
        "  exception saying the notch did not happen; N1 unchanged and N3 ending as today, English on both sides; regression\n"
        "  tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.\n")
t = sub(t, "- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT while conduit.py or spellbook.py is held, or\n"
           "  if the seam task lands first with another order of checks.\n",
        "- FAILURE_ESCALATION: CONFLICT while conduit.py or spellbook.py is held, or if the seam task lands first with another\n"
        "  order of checks.\n")
t = sub(t, "- A notch that raises from its commit leaves the lender and every linked borrower selecting the same version.\n"
           "- Answer (a): nothing moves - the index still selects the outgoing version, the incoming one stays parked, the frame\n"
           "  claim and the Nexus record name the outgoing version, the lender melds it by address and by spell_id, and the\n"
           "  borrowers are untouched; the error says the notch did not happen and names the broken version.\n"
           "- Answer (b): the switch stands and the borrower fan-out runs before the error propagates, so the borrowers follow\n"
           "  the lender; the error says the broken version is now active and that a notch back restores the previous one.\n",
        "- A notch whose incoming version fails its structural check is refused with nothing moved (owner, 2026-10-17): the\n"
        "  index still selects the outgoing version, the incoming one stays parked, the frame claim and the Nexus record name\n"
        "  the outgoing version, the lender melds it by address and by spell_id, and the borrowers are untouched.\n"
        "- The error says the notch did not happen, names the broken version with its validation errors, and says the\n"
        "  outgoing version is still active.\n")
t = sub(t, "  beyond what the answer needs (under (a), a check that runs only for a version never compiled - the case the\n"
           "  commit validator already compiles today).\n",
        "  beyond the refusal's check, which runs only for a version never compiled - the case the commit validator already\n"
        "  compiles today.\n")
t = sub(t, "- [ ] Task: the owner's answer on the open question.\n",
        "- [x] Task: the owner's answer on the open question (2026-10-17: refuse with nothing moved; DECISION note).\n")
t = sub(t, "  constructor that takes its own class): `notch_spell` to it raises, and afterwards the lender's index and the\n"
           "  borrower select the same version - English under (a), the broken version under (b); under (a) the lender melds\n"
           "  English by address and by its spell_id.\n"
           "- A notch to a sound version (N1) and a notch back (N3) behave as today.\n",
        "  constructor that takes its own class): `notch_spell` to it raises, and afterwards the lender's index and the\n"
        "  borrower both select English, the broken version is still parked, and the lender melds English by address and by\n"
        "  its spell_id.\n"
        "- A notch to a sound version (N1) behaves as today; after the refused notch a notch to English (N3) changes nothing.\n")
t = sub(t, "  KeyError \"[MELD] No spell found with spell_id: ...\" while the borrower holds the old version active. Under (a) the\n"
           "  exception keeps its meaning and the world keeps working; under (b) the exception reports a notch that happened.\n",
        "  KeyError \"[MELD] No spell found with spell_id: ...\" while the borrower holds the old version active. After the fix\n"
        "  the exception keeps its meaning - nothing moved - and the world keeps working.\n")
t = sub(t, "- The seam journals the promotion and emits the index crystal inside the window; whichever answer is chosen, the\n"
           "  research journal and the record should end up telling what happened.\n",
        "- The seam journals the promotion and emits the index crystal inside the window; under the refusal the research\n"
        "  journal and the record must not keep a promotion that did not happen (a check before the switch writes none; an\n"
        "  undo must reverse or supersede them).\n")
t = sub(t, "broken version before\n  the error propagates?\n",
        "broken version before\n  the error propagates?\n"
        "  Answered (owner, @@NOW@@): (a) - \"Yeah sure you can refuse it and throw and move on if you mean\n"
        "  it couldn't notch\"; it is that case: the incoming version failed its check, so the notch could not happen\n"
        "  (DECISION note).\n")
t = sub(t, "- 2026-10-17T21:32:09Z: filed under EPIC-2026-10-17-correctness_defects from sweep A9 (Notes).\n",
        "- 2026-10-17T21:32:09Z: filed under EPIC-2026-10-17-correctness_defects from sweep A9 (Notes).\n"
        "- @@NOW@@: the owner answered the open question - (a): refuse with nothing moved (DECISION note).\n")
t = sub(t, "- Scope: a notch whose commit fails leaves the lender and its borrowers on one version (Requirements). Defect proven\n"
           "  on 0.2.8252 (Notes); probe and runs in Artifact Links.\n"
           "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the\n"
           "  owner. The fix sits in conduit.py and spellbook.py, which melder_1 holds.\n"
           "- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
        "- Scope: a notch whose incoming version fails its commit check is refused with nothing moved - the lender and its\n"
        "  borrowers stay on the outgoing version (Requirements; the owner's answer (a)). Defect proven on 0.2.8252 (Notes);\n"
        "  probe and runs in Artifact Links.\n"
        "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner answered its\n"
        "  question (refuse, nothing moved). The fix sits in conduit.py and spellbook.py, which melder_1 holds.\n"
        "- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n")
texts[S8] = check(updated(t))

# --- epic -------------------------------------------------------------------------------------------------------
t = texts[EPIC]
t = sub(t, "- The stories' own questions, with the owner: S6, S8 and S10 (S2 and S5 answered 2026-10-17; S1 follows\n"
           "  from S2's answer).\n",
        "- The stories' own questions, with the owner: S6 and S10 (S2, S5 and S8 answered 2026-10-17; S1 follows from\n"
        "  S2's answer).\n")
t = sub(t, "  restored: rebuild parked); S1 follows from S2's answer (DECISION notes).\n",
        "  restored: rebuild parked); S1 follows from S2's answer (DECISION notes).\n"
        "- @@NOW@@: the owner answered S8 - (a): a notch whose incoming version fails its commit check is\n"
        "  refused with nothing moved (DECISION note).\n")
t = sub(t, "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2, open question),\n",
        "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (p2; answered: refused with nothing moved),\n")
t = sub(t, "  M0-184, M0-185). The owner answered S2 and S5 (DECISION note of 2026-10-17T21:55:46Z); melder_1 told (M0-186).\n",
        "  M0-184, M0-185). The owner answered S2 and S5 (DECISION note of 2026-10-17T21:55:46Z); melder_1 told (M0-186).\n"
        "  The owner answered S8 (DECISION note of @@NOW@@); melder_1 told (M0-187).\n")
t = sub(t, "- Next: (1) the owner's answers on the open questions of S6, S8 and S10 (each story's Open Questions);\n",
        "- Next: (1) the owner's answers on the open questions of S6 and S10 (each story's Open Questions);\n")
texts[EPIC] = check(updated(t))

# --- board row ---------------------------------------------------------------------------------------------------
b = texts[BOARD]
b = sub(b, "| Owner answers the open questions of S6, S8 and S10; then a fourth sweep tranche on the owner's word. |",
        "| Owner answers the open questions of S6 and S10; then a fourth sweep tranche on the owner's word. |")
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
texts[BOARD] = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

if "--dry-run" in sys.argv:
    print("dry run OK")
    sys.exit(0)
for path, text in texts.items():
    pathlib.Path(path).write_text(text, encoding="utf-8")
print("applied", NOW)
