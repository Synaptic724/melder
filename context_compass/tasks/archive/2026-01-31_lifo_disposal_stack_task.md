# Task: LIFO Disposal Stack for Creations

## Metadata
- Task ID: TASK-2026-01-31-lifo-disposal-stack
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Implement a LIFO disposal stack for Creations and LesserCreations so disposal runs in reverse creation order using a shared deque.

## Scope Boundaries
- In scope:
  - Track disposable creations in a LIFO deque.
  - Drain the deque during cleanup for disposal (no per-scope disposal loops).
  - Keep existing dictionaries as caches (no behavior change for lookup).
  - Ensure extract/restore and spellspace cleanup keep the deque consistent.
  - Transfer the disposal deque on lesser -> normal upgrade.
  - Add a component test for LIFO order.
  - Update component documentation.
- Out of scope:
  - Changes to disposal method discovery at bind time.
  - Cross-conduit disposal ordering.

## Steps / Checklist
- [x] Add stack helpers to Creations and LesserCreations.
- [x] Wire disposal stack updates into add/register paths.
- [x] Update cleanup to drain the stack and clear buckets.
- [x] Update extract/restore and spellspace cleanup to keep stack consistent.
- [x] Transfer disposal stack during lesser upgrade.
- [x] Add tests for LIFO disposal order.
- [x] Update docs.

## Deliverables
- LIFO disposal stack integrated into Creations/LesserCreations.
- Tests asserting reverse-order disposal.
- Documentation update.

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/creations/lesser_creations.py`
- `tests/component/melder/aether/conduit/test_conduit_component_creations.py`
- `context_compass/components/src_components.md`

## Validation
- Not run.
- Recommended: `pytest tests/component/melder/aether/conduit/test_conduit_component_creations.py`

## Risks / Rollback Notes
- Risk: double-disposal if stack consistency is not enforced on extract/restore.
- Rollback: revert stack usage and restore per-scope disposal loops.

## Context / Handoff Summary
Track disposable Creation wrappers in a deque and drain it on cleanup to enforce LIFO disposal. Dictionaries remain for lookup. Extract/restore and spellspace cleanup must remove/add stack entries. Lesser -> normal upgrade must transfer the stack.
