"""File sweep A2's story under EPIC-2026-10-17-correctness_defects; sync the epic and the artifact board.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
S3_ID = "STORY-2026-10-17-parked_cleanup_leaves_borrower_copies"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
PROBE = "artifacts/correctness_defects_20261017/probes/probe_parked_cleanup_borrowers.py"
RUN0 = "artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt"
RUN1 = "artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil1.txt"


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


BODY = """# Story: parked_cleanup_leaves_borrower_copies - disposing a parked version removes its copy from index-link borrowers

## Metadata
- Story ID: """ + S3_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent sharing a SpellIndex with other conduits through an index link, I want `cleanup_spell` of a parked
version to remove that version from every borrower, as `remove_from_spell_index` does, so that no borrower keeps a
copy of a version that no longer exists.

## Value / MRP Alignment
Contracts and links are structure. A borrower's copy of a disposed version is a record naming something that is
gone, and today nothing removes it - not even the borrower's own unlink of the index - so the structure is stuck.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; conduit.py's holder releases it or carries the fix
  (melder_1 holds it and is reworking the contract side on the owner's sharing rule, so it may fold this in); an
  active board row; a component patch for `Conduit.cleanup_spell`'s owner-side emissions.
- EXECUTION_BOUNDARY: `Conduit.cleanup_spell` (send the member removal for a disposed parked version whose index
  survives); regression tests; system docs with their indexes and the graph; the release note; one notch; the
  rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1's contract work).
- EXIT_GATE: the probe's P2 shows the borrower dropping the disposed version's copy and id, as P1 shows after
  `remove_from_spell_index`; regression tests pass with the GIL off and on; docs, notch and the rebuild with both
  checks OK.
- FAILURE_ESCALATION: CONFLICT if melder_1's rework changes whether index-link borrowers hold parked copies at all
  (the story is then re-scoped to that design); DECISION_REQUEST if a direct `Spellbook.cleanup_spell`, which has no
  ward, should reach borrowers too.

## Requirements (Functional)
- `Conduit.cleanup_spell` of a parked version whose index survives removes that version's per-member contract, the
  borrower's copy and its borrowed id on every index-link contract covering the index - the emission
  `remove_from_spell_index` already sends, and the one whose docstring already names `Conduit.cleanup_spell` as a
  caller (`ConduitWard._emit_index_member_removed`).
- After it, a borrower's unlink of the index leaves no copy or id of the lender's versions behind.

## Requirements (Non-Functional)
- No new lock or lock-order edge: the emission runs where the destroy emission runs - after the Book's locked
  decision, outside any transaction, under the ward lock - as it does for `remove_from_spell_index`.

## Scope Boundaries
- In scope: `Conduit.cleanup_spell`'s emission for a disposed parked member.
- Out of scope: what index-link borrowers hold in general (melder_1's contract work); the binding-signature stories
  of this epic.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes).

## Dependencies / Related Work
- TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1; conduit.py and conduit_ward.py).
- 0.2.8251 (one version, one copy): the borrower removes a copy by its own spell_id, so the removal needs no new
  lookup.

## Tasks (Implementation Checklist)
- [ ] Task: patch docs for the emission; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After `cleanup_spell` of a parked member while another member keeps the index: no borrower holds a copy of it,
  active or parked, and no borrower's borrowed ids list it.
- `remove_index_from_contract` afterwards leaves the borrower with no copy or id of the lender's versions.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_cleanup_of_a_parked_member_drops_it_from_index_link_borrowers`,
  `test_unlink_after_a_parked_cleanup_leaves_no_borrowed_ids`; GIL off and on; the probe re-run.

## UX / API / Data Notes
- No public signature changes. Visible today (probe P2): after the disposal the borrower Book still holds the
  cleaned Spell as a parked copy and lists its id among the lender's borrowed ids, before and after its unlink.

## Risks / Mitigations
- The emission walks every contract of the ward; it is the walk `remove_from_spell_index` already pays.

@@ANTI@@
## Open Questions
- Should a direct `Spellbook.cleanup_spell` (no conduit, so no ward) reach borrowers too, or is
  `Conduit.cleanup_spell` the only surface that must? The A1 note on the epic records the same gap for a direct
  `Spellbook.bind_inactive`.

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A2 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases P1, P2)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - index-link borrowers after the lender disposes a parked version
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
  CLAIM: The defect, read whole and proven on 0.2.8251. `Spellbook._dispose_spell` returns None when other members
    keep the index alive, and `Conduit.cleanup_spell` then sends index-link borrowers nothing: it emits only on a
    destroyed index (`_emit_index_destroy`). `remove_from_spell_index` sends `_emit_index_member_removed`, which
    removes the member's per-member contract and the borrower's copy. Probe, English active and French parked on an
    index the borrower contracts whole: P1, `remove_from_spell_index(French)` - the borrower drops French's parked
    copy and borrowed id; P2, `cleanup_spell(French)` - the borrower keeps a parked copy holding the cleaned French
    Spell and French's id, and its own `remove_index_from_contract` then removes English and keeps French's copy
    and id. Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:6182-6234
  - src/melder/aether/conduit/conduit.py:6092-6180
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589
  - context_compass/""" + PROBE + """:1-149
  - context_compass/""" + RUN0 + """:1-29
  - context_compass/""" + RUN1 + """:1-29
  IMPACT: A borrower holds a record of a version that no longer exists, and nothing removes it.
  NEXT: The owner schedules the story (or melder_1 folds it into its contract work); patch docs first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: `Conduit.cleanup_spell` of a parked version whose index survives removes it from every index-link borrower
  (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in conduit.py,
  which melder_1 holds; melder_1 was told by mailbox.
- Next: (1) the owner schedules it, or melder_1 folds it into its contract work; (2) patch docs; (3) the fix, its
  tests, docs, notch and the rebuild.

@@TAIL@@"""

story = check(BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
              .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
              .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
              .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
              .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
              .replace("@@NOW@@", NOW))

epic = EPIC.read_text(encoding="utf-8")
anchor = "  incoming key alone: a parked version keeps its claim, or an active spell's key is taken (sweep A1).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S3_ID + " - cleanup_spell of a parked version leaves\n"
                    "  its copy and id with index-link borrowers, past their own unlink (sweep A2).\n", 1)
log_anchor = re.search(r"(?m)^  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only \(MEASURE note\)\.\n", epic).group(0)
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A2 filed " + S3_ID + " (MEASURE note).\n", 1)
start = epic.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
end = epic.index("\n## Project-Specific Additions", start)
view = ("- Scope: correctness defects - structure Melder records wrong or leaves stuck - by the owner's rulings (DECISION\n"
        "  note); read-only; one story per confirmed defect; melder_1's lane excluded.\n"
        "- State: in_progress (melder_0), discovery. Sweeps A1 and A2 done; three stories filed:\n"
        "  STORY-2026-10-17-staged_version_releases_active_signature (p1),\n"
        "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (p2, one open question) and\n"
        "  " + S3_ID + " (p2). Their fixes sit in spellbook.py and conduit.py, which\n"
        "  melder_1 holds until its rule-2 closure.\n"
        "- Next: (1) NOTICE melder_1 (S3 and the A1 surface note); (2) sweep A3, the index moves; then A4 and A5\n"
        "  (PLAN note); (3) tell the owner what was filed.\n")
epic = epic[:start] + view + epic[end:]
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S3 not in a
row = ("| " + S3 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases P1 (control) and P2 with "
       "their runs (runs/probe_parked_cleanup_borrowers_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
       + " | HELPFUL |\n")

target = pathlib.Path(S3)
assert not target.exists()
target.write_text(story, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, row + end_art, 1), encoding="utf-8")
print("filed", S3, NOW)
