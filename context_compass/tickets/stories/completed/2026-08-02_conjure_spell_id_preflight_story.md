# Story: Refuse a colliding conjure before the Conduit is built

- Completed: 2026-08-02T20:35:00Z
- Summary: `Spellbook._spell_id_integrity_checker` refuses a conjure whose owned
  spell_ids are already registered in the frame, before phases 1-11 and before
  the Conduit is constructed, naming the offending spells rather than bare SHAs.
  The owner's four-call reproduction now raises; an owner-run sweep was 3224
  passed with ZERO regressions from this change.
- CLOSED WITH A NAMED GAP, not a clean claim. Two acceptance criteria were never
  executed: the dedicated three-test component guard
  (`test_spellbook_component_spell_id_integrity.py`) has NOT been run even once,
  and no full suite has run since the `bind_inactive` rename and the
  `AetherConfiguration` addition landed after the 3224 sweep. The two NEGATIVE
  controls in that guard are the ones that matter - they assert the check does
  not over-block - so if either reds, this closure should REOPEN. Closed on
  explicit owner acceptance 2026-08-02.

## Metadata
- Story ID: STORY-2026-08-02-conjure-spell-id-preflight
- Epic ID: EPIC-2026-08-02-process-wide-spell-id-uniqueness
- Status: done
- Owner: cowork
- Agent Name: tester_0
- Priority: p1
- Created: 2026-08-02T20:15:00Z
- Updated: 2026-08-02T20:35:00Z

## Problem / Opportunity
Two Spellbooks that bind before either conjures are invisible to each other, so
the frame existence check at `bind` (`spellbook.py:4988`) queries an empty
aggregate and passes. Since the ordinary flow is bind -> bind -> conjure ->
conjure, that guard effectively never fires across Spellbooks.

## Ticket Contract
- ENTRY_GATE: owner ruling on process-wide uniqueness; reproduction confirmed.
- EXECUTION_BOUNDARY: `spellbook.py` only - the preflight, its message helper,
  and the component test. No frame or Aether changes.
- DEPENDENCIES: none.
- EXIT_GATE: reproduction refused with a named spell and frame; negative controls
  pass; owner-run suite green.
- FAILURE_ESCALATION: `DECISION_REQUEST` if a legitimate feature needs duplicate
  ids in one frame.

## Goals
- Refuse at the cheapest moment, before phases 1-11 and Conduit construction.
- Refusals that name the spell, not just a SHA.

## Non-goals
- The authoritative check-and-set. This is a PREFLIGHT; it holds the Spellbook
  lock while the frame write happens later under the FRAME lock, so two
  concurrent conjures can still both pass. That belongs in S2 at
  `AethericFrame.register_conduit_spells`.

## Requirements
- Set INTERSECTION against the frame aggregate, not per-id lookups.
- Runs inside the CONJURE transaction, before `SpellbookCreationSystem`.
- Name resolution only on the failure path.

## Acceptance criteria
- [x] Owner's four-call reproduction raises at `book_b.conjure()`
- [x] Refusal names the frame and the colliding id
- [x] `book_b._conduit is None` after refusal - nothing half-built
- [ ] Three-test component guard runs green (NOT YET RUN)
- [ ] Owner-run full suite green

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: implementation landed and verified against the owner's
  reproduction plus a 3224-test sweep; awaiting the dedicated guard run and
  owner acceptance.
- from_state: review
- to_state: done
- transition_reason: explicit owner acceptance 2026-08-02. Closed with the unrun
  component guard recorded as a named gap in the completion summary rather than
  claimed as green - `ticketing.md` forbids claiming tests that did not run, and
  the guard's negative controls are what would prove the check does not
  over-block.

## Deliverables
- `Spellbook._spell_id_integrity_checker()` - snapshot under lock, one
  `_get_all_spell_ids(frame)` call, set intersection, raise.
- `Spellbook._describe_colliding_spells()` - resolves ids to
  `name [binding_key] state id=prefix`, failure path only, capped at 10.
- Call site in `_conjure_within_transaction_window` before
  `SpellbookCreationSystem` is constructed.
- `tests/component/melder/spellbook/test_spellbook_component_spell_id_integrity.py`
  - one positive, two negative controls.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook.py
- tests/component/melder/spellbook/test_spellbook_component_spell_id_integrity.py
- tests/integration/melder/aether/test_aether_integration_registry_ops.py
- tests/integration/melder/conduit/test_conduit_integration_scope_structural_resolution.py

## Validation
- Owner-run sweep after implementation: 3224 passed, 23 skipped, 1 failed - the
  single red being an unrelated experiment since deleted. ZERO regressions.
- Owner-run reproduction: refused correctly, id `6779b6004ace653d...`.
- Not run: the three-test component guard.

## Risks / Rollback Notes
- RISK: over-blocking. MITIGATED by two negative controls - same class across
  different frames, and distinct classes in one frame.
- ROLLBACK: delete the call site; the method is additive and has no callers else.

## Applicable Anti-Patterns
- [x] Did not edit a diagnostic probe to go green - it was deleted under owner
      ruling instead, with a tombstone recording why.
- [ ] No closure without owner acceptance and board sync.

## Notes

- DATETIME: 2026-08-02T20:15:00Z
  TYPE: DECISION
  CLAIM: The sweep is a PREFLIGHT, not a guarantee, and the docstring says so.
    It holds the Spellbook lock; the frame write happens later under the FRAME
    lock inside `Conduit.__init__`. Two concurrent conjures can both pass. Its
    value is failing fast with a good message before phases 1-11 and Conduit
    construction are paid for - a collision detected at the frame write surfaces
    inside a constructor with a half-built conduit to unwind.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:6343-6343
  - src/melder/aether/conduit/conduit.py:1375-1377
  IMPACT: S2 must still add the atomic check-and-set. Do not read this story's
    green sweep as the race being closed.
  NEXT: S2 moves the authoritative check into `register_conduit_spells`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T20:15:00Z
  TYPE: RISK
  CLAIM: SELF-MATCH TRAP FOR WHOEVER DOES THE BIND-TIME FIX. This works today
    ONLY because a Spellbook has no entry in the frame registry until its Conduit
    is constructed, so its own ids cannot be in the aggregate. The obvious next
    fix - register the live `_spell_ids` alias earlier to close the bind-time
    hole - makes this method match its OWN ids and refuse every conjure. The
    frame stores the live reference, so `other_ids is self._spell_ids` is the
    cheapest exclusion. This is recorded in the method docstring too.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2600-2610
  IMPACT: Total breakage on first run if missed - every conjure raises.
  NEXT: Carry into S2 as an explicit precondition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-02T20:15:00Z
  TYPE: FACT
  CLAIM: TWO FIXTURES WERE FLAWED, RULED BY THE OWNER, AND HANDLED DIFFERENTLY.
    `test_aether_rejects_duplicate_root_conduit_names_per_frame` bound
    `BasicService` in both books as incidental setup for a CONDUIT NAME test -
    repaired to bind `BasicConfig` in the second book, same assertion.
    `test_cluster_dependency_on_member_resolves_leader_instance` bound `_Leaf` in
    two books on one frame so a member could meld a holder depending on it -
    DELETED, because `_Holder.__init__(self, dep: _Leaf)` resolves at conjure
    while cluster shares arrive afterwards, so no ordering repairs it. A
    tombstone comment holds section 7's slot.
  EVIDENCE:
  - tests/integration/melder/aether/test_aether_integration_registry_ops.py:218-232
  - tests/integration/melder/conduit/test_conduit_integration_scope_structural_resolution.py:342-353
  IMPACT: Cluster coverage intact - ~226 cluster test functions across 47 files
    remain, including a dedicated `test_conduit_integration_cluster_dependency.py`.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Landed and green. The reproduction that started this now refuses with a readable
message before anything is built. Two things stay open: the dedicated component
guard has never been run, and the concurrent race is still open by design - this
is a preflight and S2 owns the atomic check.
