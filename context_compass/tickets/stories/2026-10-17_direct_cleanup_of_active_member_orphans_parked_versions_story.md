# Story: direct_cleanup_of_active_member_orphans_parked_versions - no parked version is left on a cleaned index

## Metadata
- Story ID: STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions
- Epic: EPIC-2026-10-17-correctness_defects
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T21:38:03Z
- Updated: 2026-10-18T14:25:49Z

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
- ENTRY_GATE: the owner schedules the story and assigns an agent (2026-10-18: melder_1 - DECISION note);
  spellbook.py claimed from melder_0 by message before any edit (M1-33); an active board row; a component patch
  for the Spellbook's removal path, and the owner's word on the exact edits before the first one.
- EXECUTION_BOUNDARY: `Spellbook.cleanup_and_remove_spell` (the multi-member check `_dispose_spell` makes, before
  anything is unregistered), and so a direct `Spell.cleanup()`, which routes there; regression tests; the system
  documents (the Spellbook Core component, a failure mode) with their indexes and the graph; the release note; one
  notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned (Book teardown, which must keep cleaning through
  its own route); spellbook.py, released by melder_1 (M1-28) and claimed back from melder_0 for this fix (M1-33).
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
- from_state: ready
- to_state: in_progress
- transition_reason: the owner scheduled the story for melder_1 (chat 2026-10-18; DECISION note); the
  defect is re-verified on the current tree before any change.

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
- What should removing an index's active version do while parked versions remain: (A) keep the index with nothing
  active, (B) notch to a parked version in the same call, (C) remove the whole index, or (E) B when the caller
  names a successor, else A? Under discussion with the owner (STRATEGY_DISCUSSION note, 2026-10-18); whichever
  he picks, `cleanup_spell` and the two direct doors follow one rule.

## Decision Log
- 2026-10-17T21:38:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A10 (Notes).
- 2026-10-18T14:17:20Z: the owner rejected the refusal: removing an index's active version keeps the index
  with no active version; only an emptied index is destroyed (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py (cases D1-D3)
  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt
  - artifacts/direct_cleanup_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)
  - system_docs/patches/active/direct_cleanup_refusal_2026_10_18/ (architecture, component)
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
- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8255, the patch docs
  direct_cleanup_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes).
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

- DATETIME: 2026-10-18T13:40:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner scheduled this story for melder_1 (chat 2026-10-18). His order is parallel: melder_0 keeps
    EPIC-2026-10-18-spell_identity_is_the_code, melder_1 takes the correctness fixes one at a time; of the stories
    after S8 he said "do the ones without open questions please" - S9, S4 and S7 - with "go over them again before
    you make changes and let him know". S8 is on hold by his word (its DECISION note), so S9 goes next, in his
    original order with S3 (open question) skipped. The defect is re-verified on 0.2.8255 and its code path re-read
    whole before any change; the exact edits go to the owner before the first one; melder_0 is told (M1-33).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:904-919
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:437-452
  IMPACT: The ENTRY_GATE's scheduling and assignment are met; the patch, the owner's word on the edits and the file
    claim remain before any src edit.
  NEXT: Re-run probe D1-D3 on 0.2.8255 with the GIL off and on; re-read the removal path whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:44:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8255, re-verified before any change as the owner asked. melder_0's probe, copied
    with its two calls renamed for 0.2.8253 (`find_spell_by_id` -> `find_spell_by_spell_id`; for an active spell_id
    both return the same Spell), ran on Python 3.14.7t: with the GIL off its output equals his 0.2.8252 run with the
    ids masked, and with the GIL on it is the same apart from the GIL-mode warning. D1: `cleanup_spell(English)` is
    refused, nothing changes. D2 (`English.cleanup()`) and D3 (`cleanup_and_remove_spell(english_id)`), French
    parked on English's index: the index is cleaned; French stays parked in the Book, uncleaned, unknown to the
    frame; a notch to it raises AttributeError, `add_to_spell_index` and `cleanup_spell` raise "SpellIndex has
    already been cleaned."; the root's teardown leaves it and `French.cleanup()` then raises "Spellbook has already
    been cleaned."; the borrower keeps an active copy of the cleaned English and a parked copy of French.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/probes/probe_direct_cleanup_active_member_0_2_8255.py:1-190
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_0_2_8255_gil0.txt:1-49
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_0_2_8255_gil1.txt:1-53
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt:1-49
  IMPACT: Nothing landed since 0.2.8252 changed the failure; the acceptance criteria stand as written.
  NEXT: The removal path read whole (FACT note), then the patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T13:44:35Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The removal path, read whole on 0.2.8255; melder_0's FACT note stands. `cleanup_and_remove_spell` resolves
    only an active spell (`_spells_by_id`), then under the Book lock unregisters its index from SpellSystemStates,
    emits the spell's and the index's removal to the record, and pops `_spells` and its address lookup; outside the
    lock it unregisters the RiskManager entry and the frame registry's index, drops the id maps, releases the frame
    claim by spell_id, and cleans the spell and the index - with no membership check. It has two callers:
    `_dispose_spell`, only for an active sole member (it refuses an active member of a multi-member index under the
    Book lock with `index.is_sole_member`), and `Spell.cleanup` through `_direct_removal_route` when
    `_spellbook_cleanup` is unset. Every internal `Spell.cleanup()` sets that flag first (Book teardown, this
    method's own tail, the parked disposal, Bind's retirement of an unpublished spell), so the missing check is
    reached only by a direct call from user code. `SpellIndex.is_sole_member` is O(1) under the index lock, and
    `_dispose_spell` already takes it under the Book lock (Book -> index). The tests that call the method today
    remove sole members (structural-snapshot `_event_remove`, per-frame custody, the restore tombstone, membership
    eviction). `Spell.cleanup`'s docstring lists the method's refusals, so spell.py takes a docstring line too.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4427-4569
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - src/melder/aether/spellbook/bind/spell_index.py:421-451
  - src/melder/aether/spellbook/bind/bind.py:455-463
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py:203-206
  - tests/integration/melder/crystallizer/test_crystallizer_membership_integration.py:154-175
  IMPACT: The fix is the story's: the multi-member check `_dispose_spell` makes, in `cleanup_and_remove_spell` before
    anything is unregistered; no lock added, no other caller affected. spell.py is not among the files melder_0
    released (M0-194), so it is claimed before its docstring line is written.
  NEXT: Write the patch (architecture and component, direct_cleanup_refusal_2026_10_18) and the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:59:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written (direct_cleanup_refusal_2026_10_18: architecture and component; no code-description -
    a plain refusal with no new control flow) and red tests run. Mapping, patch section -> step -> validation: the
    invariants and the component's After -> `Spellbook.cleanup_and_remove_spell`: in its first Book-locked section,
    after the spell is resolved and before `unregister_index`, `SpellIndex.is_sole_member` False logs and raises
    RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a multi-member index; notch away
    from it before disposing it, or dispose the index's parked versions first with cleanup_spell."; its docstring's
    Contract and Raises; `Spell.cleanup`'s Raises -> the integration tests (7) and probe D1-D3 re-run, GIL off and
    on. The Breaking interface delta -> the release note and a src_architecture failure mode; the Spellbook Core
    contract -> src_components; the new test file -> tests_components. Red on 0.2.8255, the same with the GIL off
    and on: 5 failed ("DID NOT RAISE RuntimeError": both doors, by Spell and by spell_id, and the two remedies), 2
    passed (the sole-member controls, either door). Two findings on the way: every test that calls the method
    removes a sole member (ten files, not only the four the FACT note named; the other six stage no version), so
    none changes; and `cleanup_spell`, which decides and removes in two Book-locked sections with no transaction,
    now refuses a version staged in between instead of orphaning it - so the message names no door.
  EVIDENCE:
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md:1-49
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/component_patch_spellbook_removal_path.md:1-47
  - tests/integration/melder/spellbook/test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py:1-269
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/red_tests_0_2_8255_gil0.txt:1-19
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/red_tests_0_2_8255_gil1.txt:1-27
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/cleanup_and_remove_spell_callers_0_2_8255.txt:1-41
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - src/melder/aether/conduit/conduit.py:6212-6264
  - src/melder/aether/spellbook/spell.py:1597-1663
  IMPACT: The ENTRY_GATE's patch exists and the validation step precedes the code; what remains before any src edit
    is the owner's word on the exact edits and melder_0's answer on spell.py (M1-34).
  NEXT: Put the exact edits and the message wording to the owner; claim spell.py from melder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T14:17:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-195 from melder_0 (14:14:10Z), consumed: spell.py is released to melder_1 for S9 until it lands, beside
    spellbook.py (M1-33). The identity epic edits both files only at its S1 landing, which waits for the owner's
    approval, a blast-radius run and S2's patches, so S9 lands first and melder_0 claims both back by message after
    it. conduit.py, spellbook_validation_error.py and change_control_manager.py stay free while S8 is on hold.
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:136-150
  IMPACT: The ENTRY_GATE's file claim is met for both files S9 edits.
  NEXT: The owner's word on the new edits (DECISION note below).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T14:17:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner rejected the refusal (chat 2026-10-18), shown the edits and the English/French example: "the
    spellindex isn't empty it just doesn't have an active spell, its not up to the agent to notch this, someone can
    cleanup a spell and leave the index the way it is, its not up to us to care about what happens to the this area,
    spellindex if it was empty would be destroyed and french just stays inactive because it hasn't been notched,
    whats wrong with cleaning up the spell? not sure I understand here why are we forcing a user to pick a different
    version". So disposing an index's active version is allowed: that version goes, the index stays with no active
    version and its parked versions as they are, and only an emptied index is destroyed. The defect is the removal
    tearing down an index that still holds versions (D2, D3), not a missing refusal. An index with no active
    version already exists in Melder - the one `remove_from_spell_index` mints - and a notch into it works (the
    correctness epic's A3 note). The refusal edits are withdrawn unmade; the patch docs, the red tests, the
    Requirements and the Acceptance Criteria are rewritten for this rule before any src edit. `cleanup_spell`'s own
    refusal of the active member ("notch away from it first") rests on the rule he rejected; whether S9 removes it
    too is asked of him (Open Questions).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4276-4361
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:397-428
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:42-80
  IMPACT: The fix changes direction: `cleanup_and_remove_spell` keeps a non-empty index instead of refusing. No src
    edit was made, so nothing is reverted.
  NEXT: Read whole what an index with no active version touches - SpellIndex selection and membership, the frame
    registry, the record's index snapshot, index-link borrowers, a notch into it - and bring the owner new edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T14:25:49Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: The owner asked to talk through what cleaning up an index's active version should do while parked
    versions remain (chat 2026-10-18: "perhaps cleaning up a spell thats active with inactive spells in it should do
    something else ... lets talk about it"). Facts, read whole: a SpellIndex cannot say "nothing active" -
    `selected_spell_id` is always a str, and `remove_member` of the selected id leaves it naming a non-member
    ("Callers retiring the head must select a new one"); the index `remove_from_spell_index` mints selects its
    parked member while the Book holds it parked (the owner's S10 ruling: activation takes a notch). Readers take the
    selection for the active version: `_apply_add_to_index` proves the Book owns a target index by
    `selected_spell_id in _spell_ids` (a stale selection refuses `add_to_spell_index` and `bind_inactive` onto it),
    the record captures it and a graft binds it active, and ReleaseManagedSpell prefers its pool. Options: (A) remove
    that version; the index stays with its parked versions and nothing active, its selection repointed at a parked
    member as in a minted index; the index's consumers and borrowers have no provider until someone notches. (B)
    Remove it and notch to a parked version in the same call: which one when several are parked, and S8's failure
    when that version fails its check. (C) Remove the whole index with every version. (D) Refuse - today's
    `cleanup_spell`; rejected by the owner. (E) The caller may name a successor (`successor_spell_id=`) and gets B;
    without one, A. Recommended: A - the owner's stated rule - with E only if agents ask for it; whichever is chosen,
    `cleanup_spell` and the two direct doors follow the one rule.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:83-116
  - src/melder/aether/spellbook/bind/spell_index.py:143-205
  - src/melder/aether/spellbook/bind/spell_index.py:241-275
  - src/melder/aether/spellbook/bind/spell_index.py:361-392
  - src/melder/aether/spellbook/spellbook.py:4101-4195
  - src/melder/aether/spellbook/spellbook.py:4276-4361
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:725-752
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:797-812
  IMPACT: The pick decides the patch; nothing is written for S9 until the owner chooses.
  NEXT: The owner's pick; then the patch, the tests, the Requirements and the Acceptance for it.
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
- State: in_progress (melder_1), discovery; filed by melder_0 under EPIC-2026-10-17-correctness_defects; the owner
  scheduled it on 2026-10-18 (DECISION note). Re-verified on 0.2.8255 and the removal path read whole (MEASURE and
  FACT notes). The owner rejected the refusal (DECISION note, 2026-10-18): removing an index's active version keeps
  the index, with no active version and its parked versions as they are; only an emptied index is destroyed. The
  refusal patch and its red tests (PLAN note) are superseded and get rewritten; the Requirements and Acceptance
  Criteria above still describe the refusal until then. spellbook.py and spell.py are melder_1's for S9 (M1-33,
  M0-195). No src edit made.
- Next: (1) the owner's pick among A, B, C and E (STRATEGY_DISCUSSION note); (2) the patch, the tests, the
  Requirements and the Acceptance for it, and his word on the exact edits; (3) the fix, green with the GIL off and
  on, docs, the release note, the next free notch, closure, the rebuild last.

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
