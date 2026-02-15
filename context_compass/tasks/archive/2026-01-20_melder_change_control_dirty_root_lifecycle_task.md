- Completed: 2026-01-20
- Summary: Added partial revalidation semantics so only validated roots are cleared, with unit coverage.

# Task: Preserve dirty roots on partial revalidation

## Metadata
- Task ID: TASK-2026-01-20-change-control-dirty-root-lifecycle
- Story: STORY-2026-01-20-change-control-review
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-20
- Updated: 2026-01-20

## Objective
Adjust dirty-root clearing behavior so roots are only cleared when they are
actually revalidated, preventing silent loss of dirty state.

## Scope Boundaries
- In scope:
  - Define a contract for revalidation completion (return set or explicit ack).
  - Update `revalidate_dirty_roots` to clear only validated roots.
- Out of scope:
  - Full mutation pipeline or new scheduling.

## Steps / Checklist
- [x] Define revalidator return semantics (validated roots).
- [x] Update dirty-root clearing logic accordingly.
- [x] Add regression tests for partial/no-op revalidation.

## Deliverables
- Updated dirty-root lifecycle with tests.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- Tests: `tests/unit/melder/aether/dev_ops/` or integration coverage.

## Validation
- Passed (reported by user).
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops/`

## Risks / Rollback Notes
- Risk: Dirty roots remain flagged longer than expected if revalidator does not
  report validated roots.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Review finding: `revalidate_dirty_roots` clears dirty roots unconditionally
after the revalidator returns, even if some roots were skipped or missing.
