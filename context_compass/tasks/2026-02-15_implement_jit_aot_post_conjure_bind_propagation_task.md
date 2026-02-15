# Task: Implement JIT/AOT Post-Conjure Bind Propagation

## Metadata
- Task ID: TASK-2026-02-15-implement-jit-aot-post-conjure-bind-propagation
- Story: STORY-2026-02-15-jit-aot-post-conjure-bind-propagation
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Apply mode propagation when `bind()` executes after conduit creation.

## Scope Boundaries
- In scope:
- Bind branch where `_conjured` and `_conduit` are active.
- Out of scope:
- Conjure path and transfer path.

## Steps / Checklist
- [x] Implement mode/flag stamp in post-conjure bind branch.
- [x] Preserve existing owner/conduit/risk-manager behavior.
- [x] Add targeted late-bind tests.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Late-bind propagation implementation and tests.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `tests/unit/melder/spellbook/`

## Validation
- Ran:
  - `python -m pytest tests/unit/melder/spellbook/test_spellbook.py -q` -> `130 passed`
  - `python -m pytest tests/unit/melder/spellbook/test_spell.py -q` -> `69 passed`
- Notes:
  - Non-blocking warning from `src/melder/__init__.py` about GIL-enabled Python 3.13 mode.
  - Non-blocking pytest cache permission warning on `.pytest_cache` (WinError 5).

## Risks / Rollback Notes
- Risk: propagation order conflict with existing-object registration or risk-manager updates.
- Mitigation: preserve branch order and assert behavior with tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Simplified late-bind propagation (`resolution_required = not full_ahead_of_time_compilation`) passes full spellbook + spell unit suites after user-requested removal of extra type/error fallback logic.
  EVIDENCE: src/melder/spellbook/spellbook.py:2537-2550, tests/unit/melder/spellbook/test_spellbook.py:1353-1466, tests/unit/melder/spellbook/test_spell.py:1-1104
  IMPACT: Lane-3 implementation is validated and ready for review/acceptance.
  NEXT: Route active implementation to transfer-ownership propagation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Implementation was simplified per user direction to trust `full_ahead_of_time_compilation` directly from configuration during late-bind propagation and remove additional type/error fallback handling in `Spellbook.bind`.
  EVIDENCE: src/melder/spellbook/spellbook.py:2537-2550
  IMPACT: Bind-path behavior remains focused and minimal, with no extra branch-local exception policy.
  NEXT: Re-run spellbook unit tests to confirm the simplified path preserves expected propagation behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: `Spellbook.bind` post-conjure branch now reads `full_ahead_of_time_compilation` directly and stamps `new_spell.resolution_required` before existing-object creation registration, and targeted tests cover JIT opt-in and default AOT behavior for late binds.
  EVIDENCE: src/melder/spellbook/spellbook.py:2534-2556, tests/unit/melder/spellbook/test_spellbook.py:1353-1466
  IMPACT: Lane-3 propagation behavior is implemented and ready for targeted validation.
  NEXT: Run targeted spellbook bind tests and record outcomes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The late-bind touchpoint is the existing post-conjure branch in `Spellbook.bind` that stamps owner conduit metadata, sets owner conduit id, optionally registers existing objects into Creations, then performs risk-manager registration.
  EVIDENCE: src/melder/spellbook/spellbook.py:2536-2564
  IMPACT: `resolution_required` propagation can be added locally in this branch without changing bind flow shape.
  NEXT: Add config-driven `resolution_required` stamping in that branch and validate with targeted bind-path tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: ALIGNMENT_CHECK
  CLAIM: Active routing is synchronized to this task; conjure lane remains in review and active implementation now proceeds in the post-conjure bind lane.
  EVIDENCE: context_compass/attention_board.md:16-23, context_compass/tasks/2026-02-15_implement_jit_aot_conjure_propagation_task.md:5-11
  IMPACT: Execution gates are satisfied for lane-3 source investigation and edits.
  NEXT: Verify exact bind-after-conjure touchpoint in `Spellbook.bind` and implement config-driven `resolution_required` stamping there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Late-bind propagation should attach to the current branch that already stamps owner conduit metadata for new spells after conjure.
  EVIDENCE: src/melder/spellbook/spellbook.py:2534-2574, context_compass/tasks/2026-02-15_discovery_jit_aot_propagation_contract_surfaces_task.md:1-88
  IMPACT: Avoids introducing a second late-bind pathway and keeps side effects centralized.
  NEXT: Implement after discovery confirms exact ordering and state writes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Late-bind propagation is implemented and validated; task is ready for review.
Next implementation lane is transfer-ownership propagation for owned spells.
