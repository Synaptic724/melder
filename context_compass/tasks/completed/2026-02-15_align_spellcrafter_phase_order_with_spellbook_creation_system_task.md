# Task: Align SpellCrafter Phase Order with SpellbookCreationSystem



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-15-align-spellcrafter-phase-order-with-spellbook-creation-system
- Story: STORY-2026-02-14-jit-aot-runtime-phase-resolution-path
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Align `SpellCrafter.run_all_phases` (and the `Spell.run_all_phases` facade) to
the same foundational-first resolution ordering contract used by
`SpellbookCreationSystem`.

## Scope Boundaries
- In scope:
- Align runtime phase ordering so foundational phases (`5/6/7`) run before plan phases (`8/9/10/11`).
- Align `Spell` facade behavior with `SpellCrafter` to prevent contract drift.
- Update targeted unit tests for the new ordering contract.
- Out of scope:
- JIT/AOT config flags or `resolution_required` lifecycle implementation.
- Broad refactors outside phase-order alignment.

## Steps / Checklist
- [x] Update `SpellCrafter.run_all_phases` ordering to foundational-first.
- [x] Add/retain foundational-error plan-skip behavior consistent with `SpellbookCreationSystem`.
- [x] Align `Spell.run_all_phases` facade ordering contract with `SpellCrafter`.
- [x] Update targeted unit tests for `SpellCrafter` and `Spell` phase-order expectations.
- [x] Run targeted unit tests for updated phase-order paths.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Updated phase-order implementation in:
  - `src/melder/spellbook/spell_crafter/spell_crafter.py`
  - `src/melder/spellbook/spell.py`
- Updated phase-order tests in:
  - `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `tests/unit/melder/spellbook/test_spell.py`

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/unit/melder/spellbook/test_spell.py`

## Validation
- Ran:
  - `python -m pytest tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k run_all_phases -q` -> `3 passed`
  - `python -m pytest tests/unit/melder/spellbook/test_spell.py -k run_all_phases -q` -> `2 passed`
- Notes:
  - Non-blocking warning: Python 3.13 GIL-enabled mode warning from `src/melder/__init__.py`.
  - Non-blocking warning: pytest cache permission warning on `.pytest_cache` (WinError 5).

## Risks / Rollback Notes
- Risk: Existing tests or runtime callers may depend on old order.
- Mitigation: keep patch scope narrow and update targeted tests with explicit order assertions.
- Rollback: revert this task's code/test deltas only.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Ordering drift is source-confirmed between SpellbookCreationSystem and SpellCrafter/Spell run-all helpers.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:852-905, src/melder/spellbook/spellbook_creation_system.py:1286-1459, src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5094, src/melder/spellbook/spell.py:1299-1349
  IMPACT: This drift weakens runtime/conjure contract parity and complicates JIT/AOT split behavior.
  NEXT: Implement the alignment patch in SpellCrafter and Spell facade, then update targeted tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Execute a narrow patch: reorder phases, preserve fail-fast behavior, and keep cleanup semantics explicit.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5094, src/melder/spellbook/spell.py:1299-1349
  IMPACT: Minimizes risk while resolving the highest-value consistency gap before compaction.
  NEXT: Apply code changes and run targeted phase-order unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Alignment patch is implemented: SpellCrafter/Spell `run_all_phases` now execute foundational phases (`5/6/7`) before plan phases (`8/9/10/11`), and SpellCrafter skips plan phases when foundational conduit resolution has errors.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5047-5105, src/melder/spellbook/spell.py:1299-1349
  IMPACT: Runtime revalidation ordering now matches conjure-system contract expectations for this lane.
  NEXT: Confirm acceptance, then move this task to completed and keep epic discovery flow active.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Targeted phase-order tests pass after patch (`3 passed` spell_crafter slice, `2 passed` spell facade slice), including explicit skip behavior when foundational resolution has conduit errors.
  EVIDENCE: tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4128-4201, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4204-4270, tests/unit/melder/spellbook/test_spell.py:883-904
  IMPACT: Confirms contract behavior at unit scope before broader JIT/AOT discovery continues.
  NEXT: Continue epic by activating `TASK-2026-02-14-discovery-jit-aot-creation-context-builder-runtime-contract`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
User requested an immediate patch to make SpellCrafter follow the same contract
as SpellbookCreationSystem. Implementation and targeted validation are complete;
task is in review pending acceptance before completed-folder move.


