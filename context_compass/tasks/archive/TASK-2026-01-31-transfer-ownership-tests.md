# Task: Refresh TransferOfOwnership unit tests for current behavior

## Metadata
- Task ID: TASK-2026-01-31-transfer-ownership-tests
- Story: N/A
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-31
- Updated: 2026-01-31

## Objective
Update the TransferOfOwnership unit tests and fakes to match current runtime
behavior, eliminating failures caused by outdated test doubles and expectations.

## Scope Boundaries
- In scope:
  - Update test fakes and harness in `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`.
  - Update contract-focused transfer tests in `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`.
  - Adjust outdated test expectations for error propagation in mark_lineage_* helpers.
- Out of scope:
  - Any production code changes in `src/`.

## Steps / Checklist
- [x] Align Fake* classes with required methods/fields used by TransferOfOwnership.
- [x] Set SpellIndex/spell ownership references in the test harness.
- [x] Update tests that expect swallowed errors to assert raised exceptions.
- [x] Re-scan for any remaining mismatches in test expectations.

## Deliverables
- Updated TransferOfOwnership unit tests and fakes.

## Files / Paths Impacted
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`

## Validation
- Attempted: `pytest tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py` (pytest not found on PATH).
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
  - `pytest tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`

## Risks / Rollback Notes
- Risk: test doubles may still diverge from runtime interfaces; mitigate by mirroring required attributes/methods only.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Updated the TransferOfOwnership test harness to match current behaviors:
added missing spell-state, risk manager, cluster, and conduit hooks; set
SpellIndex/spell ownership fields; and adjusted two tests to expect raised
exceptions plus the invalidate-false test to assert on the current state.
Mirrored the same fake updates and ownership wiring in the contract-focused
transfer tests to support unregister_lineage, impact gating, and risk calls.
