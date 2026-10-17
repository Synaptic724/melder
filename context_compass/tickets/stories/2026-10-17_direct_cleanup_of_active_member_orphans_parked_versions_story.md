# Story: direct_cleanup_of_active_member_orphans_parked_versions - no parked version is left on a cleaned index

## Metadata
- Story ID: STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions
- Epic: EPIC-2026-10-17-correctness_defects
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-17T21:38:03Z
- Updated: 2026-10-17T21:38:03Z

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

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- none (the fix applies `cleanup_spell`'s own rule; the alternative is the DECISION_REQUEST above).

## Decision Log
- 2026-10-17T21:38:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A10 (Notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py (cases D1-D3)
  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt
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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:38:03Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-17T21:38:03Z
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
  - src/melder/aether/spellbook/spellbook.py:4358-4421
  - src/melder/aether/spellbook/spellbook.py:4422-4563
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py:1-186
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt:1-49
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt:1-49
  IMPACT: A parked version can be left where no call reaches it - stuck for the Book's life and beyond.
  NEXT: The owner's scheduling, after melder_1 releases spellbook.py; then patch docs for the removal path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: the Spellbook's removal path refuses the active member of an index that holds parked versions, as
  `cleanup_spell` does (Requirements). Defect proven on 0.2.8252 (Notes); probe and runs in Artifact Links.
- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in
  spellbook.py, which melder_1 holds.
- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
