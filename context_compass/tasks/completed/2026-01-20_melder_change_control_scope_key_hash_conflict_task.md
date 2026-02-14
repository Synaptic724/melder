- Completed: 2026-01-20
- Summary: Normalized conflict checks to derive hashes when missing and added mixed hash/key test coverage.

# Task: Normalize scope key/hash conflict checks

## Metadata
- Task ID: TASK-2026-01-20-change-control-scope-key-hash-conflict
- Story: STORY-2026-01-20-change-control-review
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-20

## Objective
Ensure conflict and embargo checks cannot be bypassed when a request
supplies only scope hashes or only scope keys.

## Scope Boundaries
- In scope:
  - Request normalization and conflict/embargo overlap logic.
  - Guardrails for missing scope key/hash coverage.
- Out of scope:
  - Cross-frame coordination or queueing behavior.

## Steps / Checklist
- [x] Review scope hashing flow in transaction manager.
- [x] Decide on enforcement: require keys, derive hashes, or check both.
- [x] Update conflict/embargo checks to handle mixed key/hash inputs.
- [x] Add tests for mixed-scope admissions.

## Deliverables
- Updated conflict scope comparison logic and tests.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/conflict_manager/conflict_manager.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_transactions.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_transactions.py`

## Risks / Rollback Notes
- Risk: Tightening scope enforcement may reject legacy callers lacking keys.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Conflict detection now derives hashes when missing so hash-only requests can
match key-only requests; added unit coverage for mixed hash/key conflicts.
