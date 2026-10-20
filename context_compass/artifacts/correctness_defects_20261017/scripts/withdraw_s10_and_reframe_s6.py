"""Withdraw S10 on the owner's ruling (not a defect) and reframe S6's open question (chat 2026-10-17). <NOW>.

Edits S10 (closure block, status, transition, tasks, question, log, artifact trigger, closure checks, handoff), S5
(both lanes read recorded custody), S6 (the question reframed to options 1-4), the epic, the attention board (row,
closed anchor capped at 12) and the artifact board (S10's row cleared). Every edit is an exact replacement checked to
occur once; everything is checked in memory before anything is written. Notes are appended with append_note.py; the
move of S10 to completed/ is a separate `mv -n`.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
ST = "tickets/stories/"
S10 = ST + "2026-10-17_minted_index_selects_its_parked_version_story.md"
S10_DONE = ST + "completed/2026-10-17_minted_index_selects_its_parked_version_story.md"
S5 = ST + "2026-10-17_restore_drops_separated_parked_version_story.md"
S6 = ST + "2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
EPIC = "tickets/epics/2026-10-17_correctness_defects_epic.md"
BOARD = "attention_board.md"
ART = "artifact_board.md"


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


assert not pathlib.Path(S10_DONE).exists()
texts = {path: pathlib.Path(path).read_text(encoding="utf-8") for path in (S10, S5, S6, EPIC, BOARD, ART)}

# --- S10: withdrawn, not a defect ------------------------------------------------------------------------------
t = texts[S10]
t = sub(t, "# Story: minted_index_selects_its_parked_version - an index never names a parked version as its active one\n\n"
           "## Metadata\n",
        "# Story: minted_index_selects_its_parked_version - an index never names a parked version as its active one\n\n"
        "- Completed: @@NOW@@\n"
        "- Summary: withdrawn on the owner's ruling (chat 2026-10-17), not a defect: moving a version with\n"
        "  `remove_from_spell_index` is the agent's call and making it active takes a notch, so the split-off index naming\n"
        "  its parked member stays as it is. No fix, no notch; nothing edited. The graft side (a graft activating that\n"
        "  member without a notch) stays in STORY-2026-10-17-restore_drops_separated_parked_version.\n\n"
        "## Metadata\n")
t = sub(t, "- Status: ready\n", "- Status: done\n")
t = sub(t, "- from_state: draft\n- to_state: ready\n"
           "- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes); one open question\n"
           "  for the owner.\n",
        "- from_state: ready\n- to_state: done\n"
        "- transition_reason: withdrawn on the owner's ruling (chat 2026-10-17): not a defect - moving a version is the\n"
        "  agent's call and making it active takes a notch (DECISION note). Filed draft -> ready at 2026-10-17T21:47:06Z.\n")
t = sub(t, "- [ ] Task: the owner's answer on the open question (S5's was answered on 2026-10-17).\n",
        "- [x] Task: the owner's answer on the open question (2026-10-17: not a defect; withdrawn, DECISION note).\n")
t = sub(t, "- [ ] Task: patch docs for the seam; the owner's approval.\n",
        "- [ ] Task: patch docs for the seam; the owner's approval (not needed: withdrawn).\n")
t = sub(t, "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n",
        "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last (not needed: withdrawn).\n")
t = sub(t, "  instead of trusting the selection?\n",
        "  instead of trusting the selection?\n"
        "  Answered (owner, @@NOW@@): neither - not a defect: \"if you go into a [...] spell index and you move\n"
        "  the version [...] then its not my [...] problem you gotta use notch\" (DECISION note).\n")
t = sub(t, "- 2026-10-17T21:55:46Z: S5's question answered by the owner (rebuild parked); G2's criterion narrowed (FACT note).\n",
        "- 2026-10-17T21:55:46Z: S5's question answered by the owner (rebuild parked); G2's criterion narrowed (FACT note).\n"
        "- @@NOW@@: the owner ruled it not a defect - moving a version is the agent's call, activation takes a\n"
        "  notch; withdrawn (DECISION note).\n")
t = sub(t, "- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer\n",
        "- CLEANUP_TRIGGER: withdrawn with no fix; the probe and its runs stay rowed under\n"
        "  STORY-2026-10-17-restore_drops_separated_parked_version (G2) and\n"
        "  STORY-2026-10-17-staged_version_releases_active_signature (G4)\n")
t = sub(t, "## Closure Confirmation\n- [ ] Work walkthrough shared with user\n"
           "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
           "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
        "## Closure Confirmation\n- [x] Work walkthrough shared with user\n"
        "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n")
t = sub(t, "- Scope: the index `remove_from_spell_index` mints never names its parked version as active (Requirements). Defect\n"
           "  proven on 0.2.8252 (Notes); probe and runs in Artifact Links.\n"
           "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the\n"
           "  owner. The fix sits in spellbook.py (S4's seam), which melder_1 holds.\n"
           "- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
        "- Scope: the index `remove_from_spell_index` mints names its parked member as its selection (Notes, probe G2).\n"
        "- State: done - withdrawn on the owner's ruling (2026-10-17): not a defect; moving a version is the agent's call and\n"
        "  making it active takes a notch. No fix, no notch; nothing edited.\n"
        "- Next: none here. The graft side (a graft activating the parked member without a notch) stays in\n"
        "  STORY-2026-10-17-restore_drops_separated_parked_version, whose lanes read each member's recorded custody.\n")
texts[S10] = check(updated(t))

# --- S5: both lanes read recorded custody ---------------------------------------------------------------------------
t = texts[S5]
t = sub(t, "  `GraftRunner`'s fresh-index lane, which parks such members instead of binding the recorded selection active (G2);\n"
           "  regression tests; system docs with their indexes and the graph; the release note; one notch; the rebuild last.\n",
        "  `GraftRunner`'s fresh-index lane, which parks such members instead of binding the recorded selection active (G2).\n"
        "  Both lanes decide from each member's recorded custody: the selection of such an index names its parked member,\n"
        "  and that stays (STORY-2026-10-17-minted_index_selects_its_parked_version, withdrawn). Regression tests; system\n"
        "  docs with their indexes and the graph; the release note; one notch; the rebuild last.\n")
t = sub(t, "- FAILURE_ESCALATION: CONFLICT if a public verb route needs a file melder_1 holds; DECISION_REQUEST if the graft\n"
           "  lane needs the selection STORY-2026-10-17-minted_index_selects_its_parked_version settles first.\n",
        "- FAILURE_ESCALATION: CONFLICT if a public verb route needs a file another lane holds.\n")
t = sub(t, "  STORY-2026-10-17-staged_version_releases_active_signature lands; land that one first or heal it in the test.\n",
        "  STORY-2026-10-17-staged_version_releases_active_signature lands; land that one first or heal it in the test.\n"
        "- The restore's selection stage (`_enforce_selections`) notches a rebuilt index whose live selection differs from\n"
        "  the recorded one, and a parked-only index's recorded selection is its parked member: the rebuild must not reach\n"
        "  that notch, or the member comes back active.\n")
t = sub(t, "  index is rebuilt parked by a restore and by a graft (DECISION note).\n",
        "  index is rebuilt parked by a restore and by a graft (DECISION note).\n"
        "- @@NOW@@: STORY-2026-10-17-minted_index_selects_its_parked_version withdrawn (owner: not a defect); the\n"
        "  selection stays, so both lanes read each member's recorded custody (FACT note).\n")
texts[S5] = check(updated(t))

# --- S6: the question reframed after the owner asked to talk it through ---------------------------------------------
t = texts[S6]
t = sub(t, "- When two versions of one index share a class, should a release with no filter (a) raise ValueError naming each\n"
           "  version's spell_id, as two roots or two binding names do today (recommended: no identity record, no silent\n"
           "  count drift), (b) keep preferring the active version and document the drift with its remedy (`spell_id=`), or\n"
           "  (c) record which version leased each object (the identity tracking ruled out on 2026-10-14)?\n",
        "- When one class object backs two managed versions of one index, which way (owner, chat 2026-10-17: \"we gotta\n"
        "  talk about S6 properly\")? (1) pools remember what they lent - exact release, a record per lease, reversing the\n"
        "  2026-10-14 \"we don't care about identity\"; (2) managed settings leave the spell_id - alone it does not close the\n"
        "  hole (the same class under another binding name); (3) one managed version per class per index - `bind_inactive`\n"
        "  and `add_to_spell_index` refuse a second, no lease or release cost (recommended); (4) one shared pool per class\n"
        "  per index, its settings following the active version - reworks pool ownership. The earlier (a), a ValueError\n"
        "  on an ambiguous release, is withdrawn: both pools stay registered, so every release of the class would raise,\n"
        "  and a holder of an injected object has no spell_id to pass (STRATEGY_DISCUSSION note).\n")
t = sub(t, "- 2026-10-17T21:07:53Z: filed under EPIC-2026-10-17-correctness_defects from sweep A6 (Notes).\n",
        "- 2026-10-17T21:07:53Z: filed under EPIC-2026-10-17-correctness_defects from sweep A6 (Notes).\n"
        "- @@NOW@@: the open question reframed to options 1-4 with 3 recommended; the earlier (a) withdrawn\n"
        "  (STRATEGY_DISCUSSION note).\n")
texts[S6] = check(updated(t))

# --- epic -------------------------------------------------------------------------------------------------------
t = texts[EPIC]
t = sub(t, "- [ ] Story: STORY-2026-10-17-minted_index_selects_its_parked_version - the index\n"
           "  remove_from_spell_index mints selects its parked version, so a graft activates it (sweep A12).\n",
        "- [x] Story: STORY-2026-10-17-minted_index_selects_its_parked_version - the index\n"
        "  remove_from_spell_index mints selects its parked version, so a graft activates it (sweep A12). Withdrawn on\n"
        "  the owner's ruling (2026-10-17): not a defect; in tickets/stories/completed/.\n")
t = sub(t, "- The stories' own questions, with the owner: S6 and S10 (S2, S5 and S8 answered 2026-10-17; S1 follows from\n"
           "  S2's answer).\n",
        "- The stories' own questions, with the owner: S6 (S2, S5 and S8 answered 2026-10-17, S10 withdrawn as not a\n"
        "  defect; S1 follows from S2's answer).\n")
t = sub(t, "  refused with nothing moved (DECISION note).\n",
        "  refused with nothing moved (DECISION note).\n"
        "- @@NOW@@: the owner ruled S10 not a defect - moving a version is the agent's call and activation takes a\n"
        "  notch; S10 withdrawn, its graft side stays in S5; S6 reframed to options 1-4 (DECISION note).\n")
t = sub(t, "- State: in_progress (melder_0), discovery. A1-A12 are done; ten stories filed (ready, unassigned):\n",
        "- State: in_progress (melder_0), discovery. A1-A12 are done; ten stories filed - nine ready and unassigned, S10\n"
        "  withdrawn:\n")
t = sub(t, "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2, open question),\n",
        "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2, open question: options 1-4),\n")
t = sub(t, "  STORY-2026-10-17-minted_index_selects_its_parked_version (p3, open question).\n",
        "  STORY-2026-10-17-minted_index_selects_its_parked_version (p3; withdrawn: not a defect, owner 2026-10-17).\n")
t = sub(t, "  Fixes in spellbook.py and conduit.py (S1-S4, S7-S10) wait for melder_1's release; restore_engine.py and\n",
        "  Fixes in spellbook.py and conduit.py (S1-S4, S7-S9) wait for melder_1's release; restore_engine.py and\n")
t = sub(t, "  The owner answered S8 (DECISION note of 2026-10-17T22:12:58Z); melder_1 told (M0-187).\n",
        "  The owner answered S8 (DECISION note of 2026-10-17T22:12:58Z); melder_1 told (M0-187). The owner withdrew S10 as\n"
        "  not a defect (DECISION note of @@NOW@@); melder_1 told (M0-188). S6 was talked through with him:\n"
        "  the raise-on-ambiguity recommendation is withdrawn and options 1-4 are with him (S6's notes).\n")
t = sub(t, "- Next: (1) the owner's answers on the open questions of S6 and S10 (each story's Open Questions);\n"
           "  (2) a fourth tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S10 with its hand-back.\n",
        "- Next: (1) the owner's choice on S6 (its Open Questions: options 1-4, 3 recommended); (2) a fourth tranche on\n"
        "  the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n")
texts[EPIC] = check(updated(t))

# --- attention board: the row, and a closed anchor capped at 12 ------------------------------------------------
b = texts[BOARD]
b = sub(b, "| Owner answers the open questions of S6 and S10; then a fourth sweep tranche on the owner's word. |",
        "| Owner picks S6's direction (options 1-4); then a fourth sweep tranche on the owner's word. |")
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)
begin, end = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n", "<!-- END USER-DEFINED: closed_anchors -->"
assert b.count(begin) == 1 and b.count(end) == 1
head, rest = b.split(begin)
region, tail = rest.split(end)
rows = [line for line in region.splitlines() if line.startswith("| ")]
assert len(rows) == len(region.splitlines()), "unexpected non-row lines in closed_anchors"
rows.append("| minted_index_selection | done | melder_0 | " + S10_DONE + " | Withdrawn on the owner's ruling, no source change "
            "(not a defect: moving a version is the agent's call; activation takes a notch). Next: none; the graft side "
            "stays in STORY-2026-10-17-restore_drops_separated_parked_version. | " + NOW + " |")
while len(rows) > 12:
    rows.pop(0)
texts[BOARD] = head + begin + "\n".join(rows) + "\n" + end + tail

# --- artifact board: S10's row cleared ----------------------------------------------------------------------------
a = texts[ART]
active_row = [line for line in a.splitlines()
              if line.startswith("| " + S10 + " | artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py |")]
assert len(active_row) == 1
a = a.replace(active_row[0] + "\n", "", 1)
cleared_begin = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
assert a.count(cleared_begin) == 1
a = a.replace(cleared_begin, cleared_begin + "| " + S10_DONE + " | artifacts/correctness_defects_20261017/probes/"
              "probe_graft_parked_members.py | retain_as_reference | Withdrawn on the owner's ruling (not a defect); the "
              "probe and its runs stay rowed under the restore story (G2) and the signature story (G4). | " + NOW + " |\n", 1)
texts[ART] = a

if "--dry-run" in sys.argv:
    print("dry run OK")
    sys.exit(0)
for path, text in texts.items():
    pathlib.Path(path).write_text(text, encoding="utf-8")
print("applied", NOW)
