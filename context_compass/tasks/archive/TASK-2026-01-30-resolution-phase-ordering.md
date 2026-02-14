# Task: Reorder resolution phases to validate before plan compilation

## Metadata
- Task ID: TASK-2026-01-30-resolution-phase-ordering
- Story: N/A
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Run Phase 6/7 system validation and change control before Phase 8-11 plan
compilation, and short-circuit plan compilation when validation reports errors.

## Scope Boundaries
- In scope:
  - Reorder conduit-scoped phase execution to 5->6->7->8-11.
  - Gate Phase 8-11 when Phase 6 reports errors.
  - Update docstrings for touched methods.
- Out of scope:
  - Changing validation strategies or diagnostics.
  - Broader refactors of phase scheduling.

## Steps / Checklist
- [x] Reorder phase registration in `_run_resolution_phases_for_conduit`.
- [x] Add Phase 6 gate before running Phase 8-11 phases.
- [x] Update method docstrings for the new ordering.

## Deliverables
- Resolution phases reordered to validate before plan compilation.
- Phase 8-11 skipped when Phase 6 errors exist.

## Files / Paths Impacted
- src/melder/spellbook/spellbook.py

## Validation
- Not run (relied on user test runs).

## Risks / Rollback Notes
- Risk: Phase 8+ artifacts no longer built when Phase 6 flags errors.
- Rollback: Restore original phase registration order in `_run_resolution_phases_for_conduit`.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Phase 8 currently runs before system validation, allowing occurrence-plan
compilation to crash on non-visible dependencies. Reorder phases so Phase 6/7
validate first, and skip Phase 8-11 when validation errors exist.
