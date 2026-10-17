"""File sweep A10's story (a direct cleanup of an active member orphans its parked versions); sync epic and boards.

Everything is rendered and checked in memory first, then written. Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S9 = "tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
S9_ID = "STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions"
S8_ID = "STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers"
TEMPLATE = pathlib.Path("templates/story_template.md").read_text(encoding="utf-8")
ART = "artifacts/correctness_defects_20261017/"
PROBE = ART + "probes/probe_direct_cleanup_active_member.py"
RUN0 = ART + "runs/probe_direct_cleanup_active_member_gil0.txt"
RUN1 = ART + "runs/probe_direct_cleanup_active_member_gil1.txt"
SB = "src/melder/aether/spellbook/spellbook.py"
SP = "src/melder/aether/spellbook/spell.py"


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


BODY = """# Story: direct_cleanup_of_active_member_orphans_parked_versions - no parked version is left on a cleaned index

## Metadata
- Story ID: """ + S9_ID + """
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: @@NOW@@
- Updated: @@NOW@@

## User Narrative
As an agent who keeps parked versions on an index while its active version serves, I want every public way of
disposing the active version to treat the parked ones the way `cleanup_spell` does, so that no parked version is
ever left on a cleaned index where I can neither notch, move nor dispose it.

## Value / MRP Alignment
A SpellIndex and its members are Melder's record of a lineage (owner ruling: structure is the contract).
`cleanup_spell` refuses the active member of a multi-member index because disposing it "would leave the index
headless"; a direct `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell` do it anyway, cleaning the index
under its parked versions - structure no later call can repair.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent; melder_1 has released spellbook.py (its rule-2
  hold); an active board row; a component patch for the Spellbook's removal path.
- EXECUTION_BOUNDARY: `Spellbook.cleanup_and_remove_spell` (the multi-member check `_dispose_spell` makes, before
  anything is unregistered), and so a direct `Spell.cleanup()`, which routes there; regression tests; the system
  documents (the Spellbook Core component, a failure mode) with their indexes and the graph; the release note; one
  notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned (Book teardown, which must keep cleaning through
  its own route); melder_1's release of spellbook.py.
- EXIT_GATE: probe D2 and D3 show the call refused with nothing changed, as D1 shows for `cleanup_spell`; a sole
  active member still disposes as today; regression tests pass with the GIL off and on; docs, notch and the rebuild
  with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if the owner wants a direct cleanup to retire the whole index with its parked
  versions instead of refusing; CONFLICT while spellbook.py is held.

## Requirements (Functional)
- `Spellbook.cleanup_and_remove_spell` - and a direct `Spell.cleanup()` through it - refuses the active member of
  an index that also holds parked versions before anything is unregistered, with the error `cleanup_spell` raises
  ("... is the active member of a multi-member index; notch away from it before disposing it.").
- The active sole member of an index, Book teardown and the parked disposal keep today's paths.

## Requirements (Non-Functional)
- The check reads the index's membership under the Book lock the method already takes; no new lock or lock-order
  edge. Callers that set `_spellbook_cleanup` first (Book teardown, the parked disposal) never reach the method,
  and `_dispose_spell` reaches it only for a sole member.

## Scope Boundaries
- In scope: the multi-member check on the Spellbook's removal path.
- Out of scope: index-link borrowers on a direct removal (the direct path sends no ward emission; that gap is with
  melder_1's index-link work, A1 note of the epic); parked versions at Book teardown (S7).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes).

## Dependencies / Related Work
- STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned: the same orphaned versions are never cleaned by
  the teardown either.
- `Spell.cleanup` already refuses a parked version on the direct route ("not its Book's current active version").

## Tasks (Implementation Checklist)
- [ ] Task: patch docs for the removal path; the owner's approval.
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With English active and French parked on its index: `English.cleanup()` and `cleanup_and_remove_spell(English)`
  raise the multi-member RuntimeError, and afterwards the index, English, French, the frame registry and the
  borrower are as before.
- English alone on its index is still removed by either call.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_direct_cleanup_of_an_active_member_with_parked_siblings_refuses`
  and `test_cleanup_and_remove_spell_refuses_a_member_with_parked_siblings`; GIL off and on; the probe re-run. Not
  run: no fix exists yet.

## UX / API / Data Notes
- Visible today: after the call the index is cleaned; the parked version stays in the Book uncleaned, unknown to the
  frame; a notch to it raises AttributeError, `add_to_spell_index` and `cleanup_spell` of it raise "SpellIndex has
  already been cleaned.", and after the Book's teardown `cleanup()` on it raises "Spellbook has already been
  cleaned.". **Breaking change:** for code that disposes such a member directly - it is refused, as `cleanup_spell`
  refuses it.

## Risks / Mitigations
- A caller that relies on the direct route to drop a whole lineage gets an error; the remedy is the documented one:
  notch away first, or dispose the parked versions with `cleanup_spell`.

@@ANTI@@
## Open Questions
- none (the fix applies `cleanup_spell`'s own rule; the alternative is the DECISION_REQUEST above).

## Decision Log
- @@NOW@@: filed under EPIC-2026-10-17-correctness_defects from sweep A10 (Notes).

@@ARTIFACT_HEAD@@- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - """ + PROBE + """ (cases D1-D3)
  - """ + RUN0 + """
  - """ + RUN1 + """
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - disposing the active member of an index that holds parked versions
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
  CLAIM: The defect, read whole and proven on 0.2.8252. `cleanup_spell` refuses the active member of a multi-member
    index (`_dispose_spell`; D1: nothing changes). A direct `Spell.cleanup()` routes to
    `Spellbook.cleanup_and_remove_spell` (`_direct_removal_route`), which resolves the active spell and then
    unregisters its whole index from SpellSystemStates, removes the index's crystal from the record, drops the index
    from the frame registry and cleans it, with no check for parked members. D2 (`English.cleanup()`) and D3
    (`cleanup_and_remove_spell(english_id)`), French parked on English's index: the index is cleaned; French stays
    parked in the Book, uncleaned, on the cleaned index, unknown to the frame; a notch to it raises AttributeError,
    `add_to_spell_index` and `cleanup_spell` of it raise "SpellIndex has already been cleaned.", the Book's teardown
    leaves it and `French.cleanup()` then raises "Spellbook has already been cleaned.". Identical with the GIL off
    and on.
  EVIDENCE:
  - """ + SB + """:4358-4421
  - """ + SB + """:4422-4563
  - """ + SB + """:602-748
  - """ + SP + """:581-723
  - """ + SP + """:725-763
  - context_compass/""" + PROBE + """:1-186
  - context_compass/""" + RUN0 + """:1-49
  - context_compass/""" + RUN1 + """:1-49
  IMPACT: A parked version can be left where no call reaches it - stuck for the Book's life and beyond.
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py; then patch docs for the removal path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

@@CLOSURE@@@@NOTING@@## Context / Handoff Summary
- Scope: the Spellbook's removal path refuses the active member of an index that holds parked versions, as
  `cleanup_spell` does (Requirements). Defect proven on 0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py, which melder_1 holds.
- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

@@TAIL@@"""

story = check(BODY.replace("@@ANTI@@\n", block("## Applicable Anti-Patterns", "## Open Questions"))
              .replace("@@ARTIFACT_HEAD@@", block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED:"))
              .replace("@@CLOSURE@@", block("## Closure Confirmation", "## Noting Behavior"))
              .replace("@@NOTING@@", block("## Noting Behavior", "## Context / Handoff Summary"))
              .replace("@@TAIL@@", TEMPLATE[TEMPLATE.index("## Project-Specific Additions"):])
              .replace("@@NOW@@", NOW))

epic = EPIC.read_text(encoding="utf-8")
anchor = "  validation fails keeps its switch and leaves its borrowers behind (sweep A9).\n"
assert epic.count(anchor) == 1
epic = epic.replace(anchor, anchor + "- [ ] Story: " + S9_ID + " - a direct cleanup\n"
                    "  of an index's active member leaves its parked versions on a cleaned index (sweep A10).\n", 1)
log_anchor = "  " + S8_ID + " (MEASURE note).\n"
assert epic.count(log_anchor) == 1
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A10 filed\n  " + S9_ID + " (MEASURE note).\n", 1)
old_view = re.search(r"(?ms)^- State: in_progress \(melder_0\), discovery\. A1-A9 are done.*?\(S6\) are free\.\n",
                     epic).group(0)
new_view = old_view.replace("A1-A9 are done; eight stories filed", "A1-A10 are done; nine stories filed")
new_view = new_view.replace("  " + S8_ID + " (p2, open question).\n",
                            "  " + S8_ID + " (p2, open question) and\n  " + S9_ID + " (p2).\n")
new_view = new_view.replace("(p3) and\n", "(p3),\n").replace("(S1-S4, S7, S8)", "(S1-S4, S7-S9)")
assert new_view != old_view and S9_ID in new_view
epic = epic.replace(old_view, new_view, 1)
old_next = ("- Next: tranche 3 (PLAN note): (1) A10 cleanup_spell of an active version with parked siblings; (2) A11 a bind\n"
            "  whose commit validation fails; (3) A12 graft of an index with parked versions.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: tranche 3 (PLAN note): (1) A11 a bind whose commit validation fails; (2) A12 graft of an\n"
                    "  index with parked versions; (3) NOTICE melder_1 of S9 and tell the owner.\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1 and S9 not in a
rows = ("| " + S9 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases D1 (control), D2 and D3 "
        "with their runs (runs/probe_direct_cleanup_active_member_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
        + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A10: read the active branch of _dispose_spell and Conduit.cleanup_spell whole for an "
                "active version with parked siblings, then probe. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| Sweep A11: read a post-conjure bind whose commit validation fails whole (what the raise "
              "leaves registered), then probe. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

if "--dry-run" in sys.argv:
    print(new_view)
    print("dry run OK")
    sys.exit(0)
target = pathlib.Path(S9)
assert not target.exists()
target.write_text(story, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, rows + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("filed", S9, NOW)
