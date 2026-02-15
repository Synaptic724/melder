# Task: Fail fast on phase scheduler exceptions

## Metadata
- Task ID: TASK-2026-01-18-melder-phase-scheduler-fail-fast
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: complete
- Owner:
- Priority: p2
- Created: 2026-01-18
- Updated: 2026-01-18

## Objective
Ensure PhaseScheduler exits promptly when a unit of work fails or cancellation is signaled, rather than waiting for the full barrier timeout.

## Scope Boundaries
- In scope: PhaseScheduler wait logic and exception handling, tests.
- Out of scope: reordering phase semantics.

## Steps / Checklist
- [x] Define fail-fast behavior on first exception or cancel signal.
- [x] Update `_run_single_phase` to short-circuit waits when cancellation is set.
- [x] Add unit tests to confirm fast failure behavior.

## Deliverables
- PhaseScheduler fail-fast behavior on exceptions.
- Tests validating cancellation/exception handling.

## Files / Paths Impacted
- `src/melder/utilities/synchronization/phase_scheduler.py`
- `tests/integration/melder/spellbook/` or `tests/unit/`

## Validation
- User reported tests passing after updates.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`

## Risks / Rollback Notes
- Risk: fast failure changes timing assumptions in existing tests. Mitigation: update tests to align with fail-fast semantics.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Implemented fail-fast polling in `_run_single_phase` using FIRST_EXCEPTION
  with a 1ms poll interval and cancellation checks, plus unit tests covering
  exception and cancellation short-circuiting.
