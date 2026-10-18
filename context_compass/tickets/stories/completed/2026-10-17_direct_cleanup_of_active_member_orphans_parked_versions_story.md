# Story: direct_cleanup_of_active_member_orphans_parked_versions - no parked version is left on a cleaned index

- Completed: 2026-10-18T16:49:55Z
- Summary: landed and notched 0.2.8256 - `Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()`
  refuse the active version of an index that holds parked versions, as `cleanup_spell` refuses it, and all three
  messages name the remedies (notch first, dispose the parked versions, or move them out); Book teardown is
  unaffected. S9 tests green with the GIL off and on, the whole tree green but for S8's held red tests; release
  note section "A cleanup of an index's active version is refused while parked versions remain"; system
  documents and graph; rebuilt last. Turned in on the owner's word (2026-10-18).

## Metadata
- Story ID: STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T21:38:03Z
- Updated: 2026-10-18T17:07:19Z

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
  anything is unregistered), and so a direct `Spell.cleanup()`, which routes there; `_dispose_spell`'s refusal
  message, reworded to name the same remedies (owner, 2026-10-18); the docstrings of the three (`cleanup_spell`'s
  Contract, `cleanup_and_remove_spell`'s Contract, Raises and Threading, `Spell.cleanup`'s Raises); regression
  tests; the system documents (the Spellbook Core component, a failure mode) with their indexes and the graph; the
  release note; one notch; the rebuild last.
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
  an index that also holds parked versions before anything is unregistered, as `cleanup_spell` does (owner,
  2026-10-18). Both refusals name the remedies: "... is the active member of a multi-member index, and disposing it
  would leave the index's parked versions without an active one. Notch the index to one of them, dispose them with
  cleanup_spell, or move them out with remove_from_spell_index first."
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
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8256 and turned in on the owner's word (chat 2026-10-18, "Go (Recommended)":
  apply the edits, test, docs, release note, notch 0.2.8256, closure and rebuild; DECISION note of
  2026-10-18T16:02:48Z). Before that: ready -> in_progress when the owner scheduled the story for melder_1
  (chat 2026-10-18; DECISION note).

## Dependencies / Related Work
- STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned: the same orphaned versions are never cleaned by
  the teardown either.
- `Spell.cleanup` already refuses a parked version on the direct route ("not its Book's current active version").

## Tasks (Implementation Checklist)
- [x] Task: patch docs for the removal path; the owner's approval (the refusal, then his word on E1-E7).
- [x] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last (0.2.8256; the
  rebuild follows this closure, as the contribution guide orders).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With English active and French parked on its index: `English.cleanup()` and `cleanup_and_remove_spell(English)`
  raise the multi-member RuntimeError, and afterwards the index, English, French, the frame registry and the
  borrower are as before; `cleanup_spell(English)` raises its refusal naming the same remedies.
- After a refusal each remedy works: a notch to French, then `cleanup_spell(English)`; `cleanup_spell(French)`, then
  `English.cleanup()`; `remove_from_spell_index(French)`, then `English.cleanup()` (French stays parked, alone in a
  fresh index).
- English alone on its index is still removed by either call.

## Validation / Test Plan
- Regression tests named for the symptom - `test_direct_cleanup_of_an_active_member_with_parked_siblings_refuses`,
  `test_cleanup_and_remove_spell_refuses_a_member_with_parked_siblings`, `cleanup_spell`'s message and the three
  remedies; GIL off and on; the probe re-run. Red on 0.2.8255 (PLAN note); green not run: no fix exists yet.

## UX / API / Data Notes
- Visible today: after the call the index is cleaned; the parked version stays in the Book uncleaned, unknown to the
  frame; a notch to it raises AttributeError, `add_to_spell_index` and `cleanup_spell` of it raise "SpellIndex has
  already been cleaned.", and after the Book's teardown `cleanup()` on it raises "Spellbook has already been
  cleaned.". **Breaking change:** for code that disposes such a member directly - it is refused, as `cleanup_spell`
  refuses it.

## Risks / Mitigations
- A caller that relies on the direct route to drop a whole lineage gets an error; the remedy is the documented one:
  notch the index to a parked version first, dispose the parked versions with `cleanup_spell`, or move them out
  with `remove_from_spell_index`.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None open. The owner chose the refusal (DECISION note of 2026-10-18T15:41:09Z) and gave his word on the exact
  edits (DECISION note of 2026-10-18T16:02:48Z).

## Decision Log
- 2026-10-17T21:38:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A10 (Notes).
- 2026-10-18T14:17:20Z: the owner rejected the refusal: removing an index's active version keeps the index
  with no active version; only an emptied index is destroyed (DECISION note).
- 2026-10-18T15:04:57Z: the owner's rule: the cleanup marks the version invalid and removes it, the index keeps
  its parked versions with nothing active (no promotion), resolution meets a hole naming the index, and
  `cleanup_spell` no longer refuses (DECISION note).
- 2026-10-18T15:41:09Z: the owner chose the refusal on all three doors, the messages naming the remedies; the hole
  rule is withdrawn unmade (DECISION note).
- 2026-10-18T16:02:48Z: the owner's word on the exact edits E1-E7 ("Go"), closure included (DECISION note).
- 2026-10-18T16:49:55Z: landed at 0.2.8256 and turned in (FACT notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py (cases D1-D3)
  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_direct_cleanup_active_member_gil1.txt
  - artifacts/direct_cleanup_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)
  - system_docs/patches/completed/direct_cleanup_refusal_2026_10_18/ (architecture, component; promoted at
    landing, archived at turn-in)
- DISPOSITION: retain_as_reference (the probe, its runs and the lane folder); promote_to_documentation (the patch)
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
  direct_cleanup_refusal_2026_10_18, the red tests and their runs, the fix at 0.2.8256 (E1-E7), the system
  documents, the graph prose and the release note (2026-10-18; Notes).
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none (closure on the owner's word, DECISION note of 2026-10-18T16:02:48Z; self-checks
  only)

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

- DATETIME: 2026-10-18T15:04:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's rule (chat 2026-10-18), given the options: "I'd rather not shuffle spells randomly because thats
    like rolling back a git version for no reason, so thats a fallback mentality which is absurd, I'd rather just
    mark the spell as invalid and remove the spell and let the resolver deal with it, if nothing is there its
    considered a hole and it says spell_index is empty that makes the most sense", and "refusing cleanup of a
    spellindex is bad because this means you can never cleanup a spell as long as it has inactive spells that also
    is crazy". So cleaning up an index's active version - `cleanup_spell`, `Spell.cleanup()` or
    `cleanup_and_remove_spell` alike - marks it invalid and removes it; the index stays with its parked versions and
    nothing active, no version promoted or selected in its place; whatever resolves through the index meets a hole
    whose error says the index has no active spell; only an index left without members is destroyed.
    `cleanup_spell`'s refusal goes (the Open Question is answered). Options B, C and E are out, and so is A's
    repointed selection: the fix needs a SpellIndex that can hold no selection (`selected_spell_id` is a str today,
    and 154 lines in 53 files of src mention it, most for indexes of active spells).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:143-205
  - src/melder/aether/spellbook/bind/spell_index.py:241-275
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4363-4568
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:326-358
  IMPACT: S9's scope grows past `cleanup_and_remove_spell`: `cleanup_spell`'s active branch, SpellIndex's selection
    contract and the readers that can meet an index with nothing active. The EXECUTION_BOUNDARY is rewritten with
    the patch, and the exact edits go to the owner before any src edit.
  NEXT: Inventory the readers of `selected_spell_id` that can meet an index with nothing active; then the patch, the
    tests, the Requirements and the Acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T15:13:56Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The map of "no active spell" (the owner asked for it, chat 2026-10-18: a hole object, a broken index, or a
    reserved "no_active_spell" id with a flag), read on 0.2.8255 and written to the lane's
    notes/no_active_spell_map.md. `selected_spell_id` appears 143 times in 52 files outside spell_index.py and the
    build assets; about 70 read it through an active spell and can never meet an index with nothing active; 14
    readers take an index directly (the map's table). Nine of those already guard for None - raise, skip or fall
    back - and the record's index crystal types it Optional[str], though no index can hold None today. A reserved
    id would slip past every one of those guards (truthy, not None) and be registered, gated and recorded as a
    spell; a hole object in the active slot would be treated as a spell everywhere; a broken mark over the old
    pointer would be read as the removed spell. Recommended: None plus a flag (`has_active_spell`). The fix then
    needs the pointer Optional and a clear-selection method; the removal keeping a non-empty index (frame
    registry, crystal re-emitted); `cleanup_spell` without its refusal, sending the member-removed emission;
    `Conduit.notch_spell`'s borrower fan-out when nothing was active; `_apply_add_to_index`'s ownership proven by a
    member; IndexDetail's head Optional; the hole's message naming the index.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/notes/no_active_spell_map.md:1-136
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:437-441
  - src/melder/aether/conduit/meld/meld.py:1243-1248
  - src/melder/crystallizer/crystals/spell_index_crystal.py:79-106
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2271-2321
  - src/melder/aether/conduit/conduit.py:5735-5787
  - src/melder/aether/spellbook/spellbook.py:4155-4167
  IMPACT: The representation is the owner's call; the map gives him what each idea breaks. Open beside it: the
    minted index's selection (one state, not two), the direct doors' silence to borrowers, `cleanup_spell` being
    dynamic-only for an active version, and restore of such an index (S5).
  NEXT: The owner's pick; then the patch, the tests, the Requirements and the Acceptance for it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T15:27:07Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: TRADEOFF
  CLAIM: The owner reopened the rule (chat 2026-10-18): "originally we also said that a spell_index cannot be empty
    which is fine ... refusing a cleanup makes sense too maybe we just go that route? ... what are the concequences
    of refusal?". Read on 0.2.8255 (src unchanged since its landing). Both rules keep his first point: no index is
    ever left without members - the hole rule leaves one with parked members and nothing active, refusal never
    does. Refusal is the PLAN note's patch: `cleanup_and_remove_spell` makes `_dispose_spell`'s multi-member check,
    so `Spell.cleanup()` and `cleanup_and_remove_spell` refuse what `cleanup_spell` refuses today. Nothing else
    changes: SpellIndex keeps one selection, every reader in the map stays as written, two src files take a check
    and a Raises line. Its cost: retiring the active version while parked ones remain takes an order the agent
    picks - (a) notch to a parked version, then `cleanup_spell` the old one, now parked; (b) `cleanup_spell` the
    parked ones, then the active one alone, and its index goes; (c) move a parked one out with
    `remove_from_spell_index` (each call mints a fresh index), then dispose the active one - the parked one lives on
    with nothing active, the hole's end state, but under a new index id, so index-link borrowers lose the index.
    Melder picks no version. Gaps on those paths, already filed: a parked `cleanup_spell` leaves index-link
    borrowers a copy (S3); a minted index is missing from the frame registry (S4); an active `cleanup_spell` is
    dynamic-only (`invalidate_spell`), the direct doors are not. What refusal cannot give is the same index id alive
    with nothing active. It breaks only code that disposes such a member directly, which corrupts the index today;
    a later move to the hole rule would only turn its refusals into successes.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - src/melder/aether/spellbook/spellbook.py:4276-4361
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spell.py:581-763
  - src/melder/aether/spellbook/spell.py:1597-1663
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/component_patch_spellbook_removal_path.md:1-47
  - context_compass/artifacts/direct_cleanup_refusal_20261018/notes/no_active_spell_map.md:1-136
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:372-400
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:402-433
  IMPACT: The pick decides the patch and the file order: refusal keeps the PLAN note's patch and red tests and can
    land before S1 (M1-36); the hole rule needs the map's edits in at least five src files and follows S1.
  NEXT: The owner's pick; then M1-37 to melder_0 and the patch for it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T15:27:07Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-196 (15:01:53Z, QUESTION) and M0-197 (15:15:34Z, NOTICE) from melder_0, consumed. M0-196: on the
    owner's word to land S1 now (S1 with S2's binding hash; duplicates strictly refused), S1 edits spell.py (a
    binding-manifest field on Spell, its describe and cleanup, the spell_id docstrings) and spellbook.py (the bind,
    bind_inactive and conjure-integrity refusal texts, `inspect_spell`'s stage-3 text) - neither
    `cleanup_and_remove_spell` nor `Spell.cleanup`'s Raises entry - and he asks for both until S1 lands, or when S9
    lands. M0-197: spell_index.py is melder_1's for S9; of S1 and S2's planned files only meld.py and
    generalized_manifest.py read `selected_spell_id`. Answered by M1-36: the order waits for the owner's pick
    (TRADEOFF note) - under the refusal S9 lands first and hands both files back; under the hole rule both go to
    melder_0 at once and S9 follows S1; neither file is edited before M1-37.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:528-553
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:950-977
  IMPACT: S9 keeps spellbook.py, spell.py and spell_index.py until the owner's pick sets the order with S1.
  NEXT: The owner's pick; then M1-37.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T15:30:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner asked what happens when the Spellbook itself cleans up and the refusal stands in its way (chat
    2026-10-18: "if a spellbook is trying to cleanup something then the spellindex says ... you can't clean ... then
    what happens?"). It never meets the refusal. The SpellIndex refuses nothing: the check is the Spellbook's own,
    made in the removal of one version a caller asks for (`_dispose_spell` today; `cleanup_and_remove_spell` under
    the refusal), and only two src calls reach that removal - `_dispose_spell` for a sole member and a direct
    `Spell.cleanup()` from user code. Book teardown - `Spellbook.cleanup()`, which root and frame teardown reach -
    runs `_cleanup_spells`: for every active spell it unregisters the index, sets `_spellbook_cleanup` so
    `Spell.cleanup()` skips the removal route and tears the spell down locally, and cleans the index; there is no
    membership check on that path, today or under the refusal. What teardown leaves today is S7's defect: the parked
    versions are dropped from `_inactive_spells` uncleaned, and an index holding only parked versions is never
    cleaned.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:370-460
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spell.py:581-763
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/cleanup_and_remove_spell_callers_0_2_8255.txt:1-41
  IMPACT: The refusal constrains a caller asking to remove one version, never a Book tearing itself down; S7, next
    after S9, is what makes teardown clean the parked versions too.
  NEXT: The owner's pick between the refusal and the hole rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T15:41:09Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner chose the refusal (chat 2026-10-18), shown its costs (TRADEOFF note) and that Book teardown never
    meets it (FACT note): asked which rule S9 should use when an agent cleans up an index's active version while
    parked versions remain, he picked "Refusal (Recommended)" - "All three cleanup calls refuse with a message naming
    the remedies (notch first, clean the parked ones, or move them out). Book teardown is unaffected. Small change;
    lands before S1." The hole rule of the DECISION note of 2026-10-18T15:04:57Z is withdrawn unmade. So
    `cleanup_and_remove_spell` - and a direct `Spell.cleanup()` through it - refuses the active member of an index
    that also holds parked versions before anything is unregistered, as `cleanup_spell` refuses it; both refusals
    name the three remedies (`_dispose_spell`'s message is reworded to match); SpellIndex, `cleanup_spell`'s
    behaviour and every other reader stay as they are. The PLAN note's patch and red tests stand, updated for the
    remedies' wording, `cleanup_spell`'s message and the third remedy. S9 lands before S1 and hands spellbook.py
    and spell.py back to melder_0 after it (M1-37); spell_index.py is released now.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4363-4425
  - src/melder/aether/spellbook/spellbook.py:4427-4568
  - src/melder/aether/spellbook/spell.py:581-763
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md:1-49
  IMPACT: S9's scope is the removal path plus one reworded message and three docstrings in spellbook.py and spell.py;
    no file of the identity epic is needed. The exact edits go to the owner before the first one.
  NEXT: Update the patch docs and the red tests; then the exact edits to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T15:52:18Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S9's patch, tests and exact edits for the owner's pick, ready for his word. The patch docs state the refusal
    on all three doors with its remedies. The red tests add `cleanup_spell`'s reworded message and the third remedy
    (move the parked version out, then dispose the active one) and match the new wording: on 0.2.8255, 7 failed
    and 2 passed (the sole-member controls), the same with the GIL off and on - "DID NOT RAISE" for both doors and
    the three remedies, "Regex pattern did not match" for `cleanup_spell`. The edits (apply_s9_refusal.py, E1-E7;
    the preview diff): E1 `cleanup_and_remove_spell` refuses an active member that is not its index's sole member,
    in its first Book-locked section before `unregister_index`, logging and raising "Spellbook cannot remove spell
    <id>: it is the active member of a multi-member index, and disposing it would leave the index's parked versions
    without an active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with
    remove_from_spell_index first."; E2-E4 its Contract, Raises and Threading; E5 `_dispose_spell`'s refusal
    reworded to the same tail; E6 `cleanup_spell`'s Contract; E7 `Spell.cleanup`'s Raises. Mapping, patch section
    -> step -> validation: the invariants and the component's After -> E1 -> the two door tests and probe D2-D3;
    `cleanup_spell`'s interface delta -> E5 -> its message test; the remedies -> the three remedy tests; the
    docstrings -> E2-E4, E6, E7 -> the documentation ritual. Preview in a /tmp mirror of 0.2.8255 with E1-E7
    applied: the 33 test files that call `cleanup_spell` or `cleanup_and_remove_spell` pass - 491 passed, 3 xfailed
    (open graft conflicts), 1 xpassed (an intermittent race) - with the GIL off and on, the S9 file green. The
    structural-snapshot parity tests fail when run from the repository only because their cache root sits in the
    connected folder, which refuses deletes (the same 7 on the unpatched tree); from the mirror they pass.
  EVIDENCE:
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/architecture_patch.md:1-61
  - context_compass/system_docs/patches/active/direct_cleanup_refusal_2026_10_18/component_patch_spellbook_removal_path.md:1-51
  - tests/integration/melder/spellbook/test_direct_cleanup_refuses_active_member_with_parked_versions_integration.py:1-312
  - context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py:1-155
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/s9_refusal_preview_0_2_8255.diff:1-105
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/red_tests_refusal_remedies_0_2_8255_gil0.txt:1-27
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/red_tests_refusal_remedies_0_2_8255_gil1.txt:1-35
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/preview_shard_a_gil0.txt:1-6
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/preview_shard_a_gil1.txt:1-14
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/preview_shard_b_gil0.txt:1-4
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/preview_shard_b_gil1.txt:1-18
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/baseline_structural_parity_gil0.txt:1-25
  IMPACT: The ENTRY_GATE is met but for the owner's word on E1-E7; nothing in src/ is written before it.
  NEXT: The exact edits to the owner; on his word, apply E1-E7 and run the tests and the probe in the repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:02:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner gave his word on the exact edits (chat 2026-10-18): shown E1-E7 (the check in
    `cleanup_and_remove_spell` with its message, `cleanup_spell`'s reworded message, the docstrings), the red tests
    and the mirror preview, and asked "Go ahead with these S9 edits as listed (the check, the reworded cleanup_spell
    message, the docstrings)?", he chose "Go (Recommended)" - "Apply the edits, run the tests and probe in the repo,
    then docs, release note, notch 0.2.8256, closure and rebuild; hand the files to melder_0." The ENTRY_GATE is met;
    the landing follows the contribution guide's order, closure included on this word.
  EVIDENCE: context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py:1-155
  IMPACT: E1-E7 are applied as previewed, nothing else in src/ beyond the notch.
  NEXT: Apply E1-E7; the tests and the probe in the repository, GIL off and on.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T16:27:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-198 from melder_0 (2026-10-18T16:24:40Z, NOTICE), consumed. S1 and S2 of
    EPIC-2026-10-18-spell_identity_is_the_code are built and run in a /tmp mirror while S9 lands; nothing of
    theirs enters the repository's src until spellbook.py and spell.py are handed back, and both notch above
    0.2.8256. Besides those two they will edit bind.py, the new spell_code_digest.py and binding_manifest.py,
    binding_profile.py, binding_profile_strategy.py, structural_snapshot.py, caching_system.py (generation
    23), spellbook_creation_system.py, the two generalized manifest modules, spell_crystal.py and
    record_version.py (restore_engine.py and graft_runner.py if the record patch needs them), and docstrings in
    lookup_container.py, aether.py, aether_configuration.py, conduit_meld.py, meld.py, spellspace_meld.py,
    contract/details.py, inspector_utility.py and maybe spell_index.py; the bind-guard manifest regenerates
    (628 -> 630). He asked whether S9 touches any of them: it does not. S9's src edits are E1-E7 in
    spellbook.py and spell.py and the notch in __version__.py; the answer rides M1-38 with the landing notice.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md:29-34
  - context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/apply_s9_refusal.py:1-155
  IMPACT: S9 and S1/S2 share no src file but the two handed back at S9's landing; they meet again in the
    system documents, the graph descriptors and the release note, which S1/S2 change in the mirror, so their
    landing re-reads what S9 lands there (M1-38 names it).
  NEXT: Land S9 - docs, indexes, graph, notch 0.2.8256, release note, closure, rebuild; then M1-38.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T16:35:46Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: E1-E7 are in src as previewed and approved (apply_s9_refusal.py --apply: "all anchors found", "applied").
    E1: `cleanup_and_remove_spell`, in its first Book-locked section after the spell is resolved and before
    `unregister_index`, refuses an active member that is not its index's sole member (`SpellIndex.is_sole_member`),
    logging and raising RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a multi-member
    index, and disposing it would leave the index's parked versions without an active one. Notch the index to one of
    them, dispose them with cleanup_spell, or move them out with remove_from_spell_index first."; E2-E4 its
    Contract, Raises and Threading; E5 `_dispose_spell`'s refusal reworded to the same tail after its "cleanup_spell:
    spell <id>" prefix (its log line keeps the short form); E6 `cleanup_spell`'s Contract names the three remedies;
    E7 `Spell.cleanup`'s Raises names the refusal. spellbook.py is 7802 lines (+31), spell.py 1972 (+4); no other src
    file changed, and `__version__` is still 0.2.8255 until the notch.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-775
  - src/melder/aether/spellbook/spellbook.py:4390-4455
  - src/melder/aether/spellbook/spellbook.py:4457-4599
  - src/melder/aether/spellbook/spell.py:581-727
  - src/melder/aether/spellbook/bind/spell_index.py:421-452
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/apply_s9_refusal_apply.txt:1-2
  IMPACT: The refusal is in place on all three doors; Book teardown (`_cleanup_spells`) and the parked disposal still
    set `_spellbook_cleanup` first and never reach the check.
  NEXT: The tests, the probe and the whole tree, GIL off and on (MEASURE note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:35:46Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green with the fix, the same with the GIL off and on (Python 3.14.7t). The S9 integration file: 9 passed in
    the repository (the 7 that were red now pass; the 2 sole-member controls still pass). Probe D1-D3 re-run at the
    fix: D1 `cleanup_spell(English)`, D2 `English.cleanup()` and D3 `cleanup_and_remove_spell(english_id)` are all
    refused - D2 and D3 with the Spellbook's message - and after each the index is live and selects English, both
    versions are uncleaned and found by the frame, and the borrower holds English active and French parked; a notch
    to French then works and the root's teardown cleans French. The whole tree in a /tmp mirror of 0.2.8255 with
    E1-E7 (the structural-parity tests need a deletable cache root): unit 9647 passed, 3 skipped, 7 xfailed;
    component 2396 passed, 23 skipped, 1 xfailed; integration spellbook 657 passed, 2 skipped, 2 xpassed; aether 823
    passed, 5 xfailed; conduit 353 passed, 1 xpassed; crystallizer, multithreading, mutation_research and live_sim
    398 passed, 4 xfailed; experimentation, experiments, tests and mocks 250 passed, 4 skipped. The only failures
    are the 18 red tests written for the held STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (7 in
    test_spellbook_validation_error_preface.py, 11 in test_notch_refused_at_commit_integration.py), red on purpose
    until S8 lands; nothing else fails.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/green_tests_0_2_8256_gil0.txt:1-2
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/green_tests_0_2_8256_gil1.txt:1-10
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_at_fix_gil0.txt:1-49
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_at_fix_gil1.txt:1-53
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/unit_gil0.txt:1-168
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/unit_gil1.txt:1-176
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/component_gil0.txt:1-35
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/component_gil1.txt:1-43
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_spellbook_gil1.txt:1-19
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_aether_gil1.txt:1-79
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_conduit_gil1.txt:1-14
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_rest_gil0.txt:1-7
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_rest_gil1.txt:1-15
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/exp_and_misc_gil1.txt:1-13
  IMPACT: The EXIT_GATE's code and test parts are met (probe D2 and D3 refused as D1; a sole member still removed;
    regression tests green with the GIL off and on). Two empty logs of a background run that died with its call are
    under runs/full_tree_0_2_8256/_to_delete/ for the owner to delete.
  NEXT: The system documents with their indexes and the graph; then the notch, the release note, closure, rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:45:25Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The system documents and the graph carry 0.2.8256. land_s9_docs.py (32 replacements, four documents):
    src_architecture gains an operational invariant (an index keeps an active version while it holds parked ones:
    the three doors, the remedies a-c with their filed gaps S3 and S4, the lock order, Book teardown, the
    cleanup_spell race), a Breaking failure mode with both messages, a handoff entry and the code map (spellbook.py
    7802, spell.py 1972); src_components gains Spellbook Core's refusal bullet, invariant and failure entry, the
    Binding Pipeline's direct-route refusal and failure entry, Conduit Runtime's remedies, the code map and a
    handoff entry; tests_components the new test file (protection bullet, key file, code-map record, source) and
    tests_architecture its inventory, each with a handoff entry. Counts are recounted from disk (unit 510 of 513,
    utilities tree 54; integration 175 of 182, aether tree 49, conduit tree 45 - one short since 0.2.8254 -
    spellbook tree 52; 851 modules); they include S8's two held red-test modules, named as such. The numeric
    citations into spellbook.py (25 lines) were remapped before (remap_s9_citations.py); the recipe finds none out of
    bounds (its two MISSING rows are bare file names in old handoff text). The four indexes are regenerated, --check
    OK. Graph: re-extracted - 103 descriptors were behind their source (other lanes' landings, and the rebuild's
    payload modules, which change after every assembly) and refresh their mechanical tier; the Spellbook and Spell
    nodes' prose was read against the source since their last stamp (the 0.2.8253 docstring wording, then E1-E7):
    Spellbook's managed-options responsibility said the options "become part of the spell id", false since
    0.2.8254, and is corrected; each node gains a 0.2.8256 responsibility; both accepted; assembled (591 sections,
    28086 lines, --check OK; no package path in src_graph).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1126-1152
  - context_compass/system_docs/src_architecture.md:2250-2263
  - context_compass/system_docs/src_components.md:725-735
  - context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/land_s9_docs.py:1-368
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/land_s9_docs_apply.txt:1-5
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/citation_check_0_2_8256.txt:1-3
  - context_compass/artifacts/direct_cleanup_refusal_20261018/scripts/graph_prose_s9.py:1-68
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/graph_extract_0_2_8256.txt:1-46
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/graph_accept_0_2_8256.txt:1-6
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/graph_assemble_0_2_8256.txt:1-4
  IMPACT: The EXIT_GATE's docs part is met; the patch docs' content is promoted, so the patch folder can be archived
    at closure. melder_0's S1/S2 landing meets these sections in the four documents and the two descriptors.
  NEXT: The notch to 0.2.8256 and the release note; then closure, M1-38 and the rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T16:48:02Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Landed and turned in at 0.2.8256 on the owner's word (DECISION note of 2026-10-18T16:02:48Z: "... notch
    0.2.8256, closure and rebuild"). `__version__` still read 0.2.8255 (no one notched meanwhile, no new message)
    and is notched to 0.2.8256. The running release note's header reads "# Melder 0.2.8256", and a new section, "A
    cleanup of an index's active version is refused while parked versions remain" (the Breaking change, the three
    remedies, `cleanup_spell`'s reworded message, what stays the same), comes before Packaging, which gains the
    system-documents line and the rebuild line for 0.2.8256; its example runs as written with the GIL off and on
    (probe_release_note_s9.py, cases E1-E4: the refusal, each remedy, `cleanup_spell`'s message). Acceptance: the
    criteria hold (MEASURE note); no independent review was asked for - the closure is on the owner's word. Turn-in:
    Completed and Summary at the top, Status done, the move to completed/, the board's row and detail out with a
    closed anchor and the notch notice, the artifact rows cleared (the lane folder and the probe retained as
    reference, the patch promoted and archived under system_docs/patches/completed/), M1-38, the rebuild last.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:903-959
  - release_docs/next_version_release.md:1060-1063
  - context_compass/artifacts/direct_cleanup_refusal_20261018/probes/probe_release_note_s9.py:1-65
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_release_note_s9_gil0_gil1.txt:1-15
  IMPACT: S9 is done; spellbook.py and spell.py go back to melder_0 for S1 (M1-38), which notches above 0.2.8256.
  NEXT: M1-38 and the rebuild; then S4, re-verified on the current tree before any change.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T17:07:19Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last at 0.2.8256, from the repository root on Python 3.14.7t, after the notch, the release note,
    the Notes and the closure. The asset runner ran whole in a /tmp mirror of src/ and the system documents,
    because its system-documents writer unlinks its payloads and the connected folder refuses deletes: all three
    assets at v0.2.8256 (468, 628 and 4 entries). It changed eight files under src/melder/_build_assets - five
    manifests and the src_architecture, src_components and src_graph payloads - and nothing else; each was copied
    over its original and compared byte-equal, the mirror's src/ and system documents then equal to the
    repository's (only melder_0's patch docs under patches/active/ had changed since the copy), and the asset
    --check on the repository printed only OK lines. The LLM bundles (--include-untracked) rewrote src (583
    files), tests (1132) and other (400) and the manifest; their --check printed only OK lines, and so did the
    asset --check run again after them. The other bundle lists four files fewer than the one committed at HEAD:
    release_docs/0.2.43.md, 0.2.50.md, 0.2.77.md and 0.2.82.md are gone from the working tree and the git index,
    not by this lane (HEAD still holds them). No .git/index.lock.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/rebuild_assets_0_2_8256_mirror.txt:1-12
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/rebuild_assets_0_2_8256_check.txt:1-3
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/rebuild_llm_0_2_8256.txt:1-8
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/rebuild_llm_0_2_8256_check.txt:1-7
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/rebuild_assets_0_2_8256_check_after_llm.txt:1-7
  IMPACT: 0.2.8256 is landed whole; nothing is committed (the owner commits). spellbook.py and spell.py go back to
    melder_0 with M1-38.
  NEXT: M1-38 to melder_0 and the report to the owner; then S4, re-verified on the current tree before any change.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (the landing report, chat 2026-10-18, sent with this turn-in)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: the Spellbook's removal path refuses the active member of an index that holds parked versions, as
  `cleanup_spell` does, and all three messages name the remedies (Requirements). Defect proven on 0.2.8252 and
  re-verified on 0.2.8255 (Notes); probe and runs in Artifact Links.
- State: done (melder_1; turned in 2026-10-18T16:49:55Z on the owner's word). Landed at 0.2.8256: E1-E7 in
  spellbook.py and spell.py (FACT note); the S9 tests green with the GIL off and on, probe D1-D3 refused, the
  whole tree green but for S8's 18 held red tests (MEASURE note); the system documents with their indexes and
  the graph (FACT note); the notch and the release-note section (FACT note); rebuilt last, both checks OK
  (MEASURE note).
  The hole rule (an index kept with parked versions and nothing active) was weighed and withdrawn by the owner
  for the refusal (DECISION notes, the lane's notes/no_active_spell_map.md).
- Open elsewhere: index-link borrowers on the direct doors (no ward emission; the A1 note of
  EPIC-2026-10-17-correctness_defects); Book teardown's parked versions
  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned, S7); the remedies' filed gaps S3 and S4.
- Next: none here; spellbook.py and spell.py went back to melder_0 for S1 (M1-38); melder_1 takes S4 next.

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
