"""File sweep A5's story under EPIC-2026-10-17-correctness_defects; sync the epic, the artifact board and the row.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S5 = "tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md"
S5_ID = "STORY-2026-10-17-restore_drops_separated_parked_version"
S1_ID = "STORY-2026-10-17-staged_version_releases_active_signature"
S4_ID = "STORY-2026-10-17-minted_index_missing_from_frame_registry"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
PROBE = "artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py"
TARGETS = "artifacts/correctness_defects_20261017/probes/restore_targets.py"
RUN0 = "artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil0.txt"
RUN1 = "artifacts/correctness_defects_20261017/runs/probe_restore_staged_structure_gil1.txt"


def block(start: str, end: str) -> str:
    """Verbatim template text from heading `start` up to (not including) `end`."""
    i = TEMPLATE.index(start)
    return TEMPLATE[i:TEMPLATE.index(end, i)]


def check(text: str) -> str:
    """Refuse placeholders left and long lines that hold no path."""
    assert "@@" not in text
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


BODY = """# Story: restore_drops_separated_parked_version - a restore rebuilds a parked version alone in its own index

## Metadata
- Story ID: """ + S5_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent who separated a version into its own index with `remove_from_spell_index` and checkpointed the world, I
want a restore of that checkpoint to rebuild the version, parked in an index of its own, so that the restored world
holds every version the recorded one held.

## Value / MRP Alignment
A restore rebuilds structure (owner ruling: structure is the contract; a restore rebuilds structure with fresh
identities). The record already captures the separated version and its index; the restore drops the version and
still calls itself complete, so the restored structure is wrong while the report reads as success.

## Ticket Contract
- ENTRY_GATE: the owner's answer to the open question below; the owner schedules the story and assigns an agent; an
  active board row; a component patch for the restore engine's staged lane.
- EXECUTION_BOUNDARY: `RestoreEngine` (the staged lane: `_bind_one_staged`, `_live_index_for`, or a step after
  them) - rebuild a recorded index whose members are all parked through public verbs, mapping its identity; the
  graft runner's same lane if it shares the gap; regression tests; system docs with their indexes and the graph;
  the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe, its targets and runs (Artifact Links);
  """ + S4_ID + """ (a rebuilt minted index must also be known to the frame);
  """ + S1_ID + """ (staging during a restore releases the sibling's claim).
- EXIT_GATE: the probe's R2 rebuilds French parked in its own index with no shortfall for it; R1 and R3 unchanged;
  regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST for the open question; CONFLICT if a public verb route needs a file melder_1
  holds.

## Requirements (Functional)
- A restore of a record holding an index whose members are all parked rebuilds that index in the same Book, with
  every member parked and the recorded index identity mapped to the new one - through public verbs only (for example
  staging each member onto a live anchor of its Book, then separating it with `remove_from_spell_index`).
- The report counts the members as staged and files no `staged_member_anchor_index_not_rebuilt` shortfall for them.

## Requirements (Non-Functional)
- All-or-nothing stays: a failure while rebuilding such an index tears the restore down like any other stage.

## Scope Boundaries
- In scope: the restore (and, if it shares the lane, the graft) of parked-only indexes.
- Out of scope: the claims and registry those verbs leave behind (the sibling stories); the record format.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe through a real checkpoint, flush, boot and restore,
  GIL off and on (Notes); one open question for the owner.

## Dependencies / Related Work
- """ + S4_ID + """.
- """ + S1_ID + """.

## Tasks (Implementation Checklist)
- [ ] Task: the owner's answer on the open question.
- [ ] Task: patch docs for the restore engine's staged lane; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Restoring R2's checkpoint gives a Book with English active and French parked, French in an index of its own whose
  recorded identity maps to it, and no shortfall naming French.
- A world whose separated version was then notched active (R3) and a plain staged world (R1) restore as before.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_restore_rebuilds_a_parked_version_separated_into_its_own_index`;
  GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today: `load_checkpoint` returns status "complete" with the shortfall
  "staged_member_anchor_index_not_rebuilt: <index id>", and the version is gone from the rebuilt Book.

## Risks / Mitigations
- Rebuilding by staging then separating goes through `bind_inactive`, which releases a sibling's claim until
  """ + S1_ID + """ lands; land that one first or heal it in the test.

@@ANTI@@
## Open Questions
- Is a parked-only index meant to survive a restore? The record captures it today; if it is not meant to, the
  record should stop capturing it and the report should say why - the owner's call.

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A5 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases R1-R3)
  - """ + TARGETS + """
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - restore of a parked version separated into its own index
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed @@NOW@@.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: @@NOW@@
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8251. The restore replays a Book as: active binds, conjure, staged
    members onto live anchors (`_bind_one_staged`), selections. A staged member's anchor is found by
    `_live_index_for`, which translates a recorded index id only after one of its members was bound active; an
    index whose members are all parked - the index `remove_from_spell_index` mints - never gets one, so the member
    is skipped with the shortfall "staged_member_anchor_index_not_rebuilt: <index>" and the report still says
    "complete". The record does hold it: `_apply_remove_from_index` emits both index snapshots. Probe R2 (record,
    seal, flush, fresh boot, reload, restore): the recorded Book has English active and French parked in its own
    index; the rebuilt Book has English alone. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1915-2003
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2201-2269
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2400-2441
  - src/melder/aether/spellbook/spellbook.py:4271-4356
  - context_compass/""" + PROBE + """:1-160
  - context_compass/""" + RUN0 + """:1-18
  - context_compass/""" + RUN1 + """:1-18
  IMPACT: A restored world silently holds fewer versions than the recorded one, under a "complete" report.
  NEXT: The owner's answer on the open question, then patch docs for the staged lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: a restore rebuilds a parked version that sits alone in its own index (Requirements). Defect proven on
  0.2.8251 (Notes); probe, targets and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects; one open question for the
  owner. The fix sits in restore_engine.py, which no other lane holds.
- Next: (1) the owner's answer and scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

@@TAIL@@"""

story = check(BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
              .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
              .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
              .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
              .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
              .replace("@@NOW@@", NOW))

epic = EPIC.read_text(encoding="utf-8")
anchor = "  mints is missing from the frame's spell registry, so its version is unknown by spell_id (sweep A3).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S5_ID + " - a restore drops a parked version\n"
                    "  alone in its own index and still reports complete (sweep A5).\n", 1)
log_anchor = re.search(r"(?m)^- \S+: sweep A3 filed " + re.escape(S4_ID) + r" \(MEASURE note\)\.\n", epic).group(0)
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A4 checked, no story; sweep A5 filed\n  " + S5_ID
                    + " (MEASURE note).\n", 1)
old_m2 = "- [ ] Milestone 2: areas swept - each recorded as a defect or as checked with its reason.\n"
assert epic.count(old_m2) == 1
epic = epic.replace(old_m2, old_m2.replace("- [ ]", "- [x]"), 1)
start = epic.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
end = epic.index("\n## Project-Specific Additions", start)
view = ("- Scope: correctness defects - structure Melder records wrong or leaves stuck - by the owner's rulings (DECISION\n"
        "  note); read-only; one story per confirmed defect; melder_1's lane excluded.\n"
        "- State: in_progress (melder_0), discovery. The planned sweep A1-A5 is done; five stories filed (ready,\n"
        "  unassigned): " + S1_ID + " (p1),\n"
        "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, open question),\n"
        "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (p2),\n"
        "  " + S4_ID + " (p2) and\n  " + S5_ID + " (p2, open question). The first four fixes\n"
        "  sit in spellbook.py and conduit.py, which melder_1 holds; the fifth in restore_engine.py (free).\n"
        "- Next: (1) tell the owner what was filed and the two open questions; (2) NOTICE melder_1 of the fourth\n"
        "  story; (3) the next sweep areas on the owner's word.\n")
epic = epic[:start] + view + epic[end:]
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S5 not in a
row = ("| " + S5 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases R1-R3 with restore_targets.py "
       "and their runs (runs/probe_restore_staged_structure_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
       + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_next = "| Sweep A5: restore and graft of a world with parked versions and index moves, read whole, then probed. |"
assert b.count(old_next) == 1
b = b.replace(old_next, "| Tell the owner the five stories filed and their two open questions; then the next areas on his word. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

target = pathlib.Path(S5)
assert not target.exists()
target.write_text(story, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, row + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("filed", S5, NOW)
