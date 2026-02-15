- Completed: 2026-01-20
- Summary: Wired link-mirror register/unregister to link contracts and added spellbook unit coverage.

# Task: Wire link mirror lifecycle or remove unused registry

## Metadata
- Task ID: TASK-2026-01-20-change-control-link-mirror
- Story: STORY-2026-01-20-change-control-review
- Status: completed
- Owner:
- Priority: p3
- Created: 2026-01-20
- Updated: 2026-01-20

## Objective
Decide whether the link-mirror registry should be populated and used or removed,
then implement the chosen path to avoid dead code.

## Scope Boundaries
- In scope:
  - Identify intended consumers of link mirror data.
  - Either wire `register_link`/`unregister_link` into link/contract flows or
    remove the registry if unused.
- Out of scope:
  - New conflict policies beyond existing scope keys.

## Steps / Checklist
- [x] Locate call sites for link/contract lifecycle events.
- [x] Decide: wire link mirror or remove it.
- [x] Implement and add unit tests.

## Deliverables
- Link mirror lifecycle behavior clarified and implemented.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`
- `src/melder/aether/conduit/conduit.py`
- Tests: unit coverage for transaction manager or conduit link flows.

## Validation
- Passed (reported by user).
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops/`

## Risks / Rollback Notes
- Risk: Wiring link mirror without correct scoping could over-block transactions.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Review finding: link mirror registry exists but has no call sites, so it never
captures link topology for conflict/embargo decisions.
