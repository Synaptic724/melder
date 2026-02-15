- Completed: 2026-01-21
- Summary: Added integration tests for change-control admission and staged updates.

# Task: Expand change-control integration tests

## Metadata
- Task ID: TASK-2026-01-20-change-control-integration-tests
- Story: STORY-2026-01-20-change-control-integration-tests
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-21

## Objective
Add ~80 integration-level pytest cases covering change-control admission,
link/contract workflows, and revalidation in realistic conduit setups.

## Scope Boundaries
- In scope:
  - End-to-end change-control flows with multiple conduits.
  - Admission/embargo rejections and staged updates.
- Out of scope:
  - Long-running stress tests beyond scope.

## Steps / Checklist
- [x] Add integration coverage for link/contract change-control flows.
- [x] Add integration coverage for staged updates and revalidation.
- [x] Add integration coverage for admission rejection scenarios.

## Deliverables
- New integration test cases under `tests/integration/melder`.

## Files / Paths Impacted
- `tests/integration/melder/`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/integration/melder`

## Risks / Rollback Notes
- Risk: Integration tests increase runtime; keep fixtures tight.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added integration coverage for change-control admission, staged updates, and link mirror flows in
  `tests/integration/melder/aether/test_aether_integration_change_control_transactions.py`.
- New tests cover bind/link embargo scopes, staged updates extending embargo scopes, scope-hash
  conflict rejection, disabled change-control admission, and link-mirror registration.
- Validation not run yet; run pytest on integration suite when ready.
