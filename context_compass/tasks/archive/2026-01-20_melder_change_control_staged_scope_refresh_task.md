- Completed: 2026-01-20
- Summary: Refreshed staged scope updates to extend embargoes and documented the behavior with tests.

# Task: Refresh embargo scopes when staged metadata updates

## Metadata
- Task ID: TASK-2026-01-20-change-control-staged-scope-refresh
- Story: STORY-2026-01-20-change-control-review
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-20
- Updated: 2026-01-20

## Objective
Ensure embargo/conflict scope checks incorporate binding/contract keys discovered
after admission by refreshing staged scope metadata (and any implicit embargoes).

## Scope Boundaries
- In scope:
  - Update staged scope keys when `update_staged_request` is called.
  - Decide whether embargoes should be recalculated or re-opened.
- Out of scope:
  - Queueing or retry behavior.

## Steps / Checklist
- [x] Map how staged metadata is used by embargo/conflict logic today.
- [x] Decide whether to re-run embargo scope derivation on updates.
- [x] Implement scope refresh behavior and tests.

## Deliverables
- Updated staged/embargo refresh behavior with tests.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/aether/dev_ops/change_control_manager/orchestrator/orchestrator.py`
- `src/melder/aether/dev_ops/change_control_manager/embargo_manager/embargo_manager.py`
- Tests: `tests/integration/melder/spellbook/` or `tests/unit/melder/aether/dev_ops/`

## Validation
- Passed (reported by user).
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/`

## Risks / Rollback Notes
- Risk: Recalculating embargoes may reject concurrent requests unexpectedly.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Review finding: staged metadata updates do not affect embargo scope keys, which
can allow overlapping requests to slip through when binding/contract keys are
discovered after admission.
