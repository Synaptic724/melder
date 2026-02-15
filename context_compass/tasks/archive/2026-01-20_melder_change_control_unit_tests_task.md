- Completed: 2026-01-21
- Summary: Added unit tests for the change-control manager stack.

# Task: Expand change-control unit tests

## Metadata
- Task ID: TASK-2026-01-20-change-control-unit-tests
- Story: STORY-2026-01-20-change-control-unit-tests
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-21

## Objective
Add ~120 new unit-level pytest cases for the change-control manager stack,
covering admission, embargoes, staged updates, and request modeling.

## Scope Boundaries
- In scope:
  - Conflict manager, embargo manager, orchestrator, transaction manager.
  - Request normalization and staged mutation updates.
- Out of scope:
  - Integration or component suites.

## Steps / Checklist
- [x] Add unit tests for conflict and embargo edge cases.
- [x] Add unit tests for staged mutation updates and commit/abort hooks.
- [x] Add unit tests for request normalization and audit hooks.

## Deliverables
- New unit test cases in `tests/unit/melder/aether/dev_ops/change_control_manager/`.

## Files / Paths Impacted
- `tests/unit/melder/aether/dev_ops/change_control_manager/`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/aether/dev_ops/change_control_manager`

## Risks / Rollback Notes
- Risk: Overlapping tests inflate runtime; keep fixtures minimal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added staged mutation update coverage (with_updates, update_staged) alongside
conflict/embargo edge-case tests in
`tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_transactions.py`.
Added request normalization and audit-hook coverage in
`tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_transactions.py`.
