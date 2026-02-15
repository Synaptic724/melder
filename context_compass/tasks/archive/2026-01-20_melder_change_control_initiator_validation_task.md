- Completed: 2026-01-20
- Summary: Guarded initiator conduit ids in request creation and added unit coverage for invalid inputs.

# Task: Enforce initiator conduit id validation

## Metadata
- Task ID: TASK-2026-01-20-change-control-initiator-validation
- Story: STORY-2026-01-20-change-control-review
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-20
- Updated: 2026-01-20

## Objective
Validate `initiator_conduit_id` during request creation to prevent empty
identifiers in change-control audit data and scope derivation.

## Scope Boundaries
- In scope:
  - Add validation in request creation or caller logic.
  - Add tests for empty initiator inputs.
- Out of scope:
  - Audit log formatting changes.

## Steps / Checklist
- [x] Decide where to enforce initiator validation (builder vs. caller).
- [x] Implement validation and update tests.

## Deliverables
- Initiator validation guard with tests.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- Tests: unit coverage for transaction manager.

## Validation
- Passed (reported by user).
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops/`

## Risks / Rollback Notes
- Risk: Existing call sites may pass empty initiator ids.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Review finding: `ChangeControlTransactionRequest` requires a non-empty
initiator id, but `build_request` does not validate it.
