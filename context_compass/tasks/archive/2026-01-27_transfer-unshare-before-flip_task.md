# Task: Reorder transfer unshare before ownership flip

## Metadata
- Task ID: TASK-2026-01-27-transfer-unshare-before-flip
- Story: N/A
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Reorder ownership transfer steps so contract unshare happens before spellbook ownership flip when force_unshare is enabled, preventing contracted cleanup from removing newly owned spell_id entries.

## Scope Boundaries
- In scope:
  - Change the execution order in TransferOfOwnership.execute for force_unshare.
  - Update docstrings/comments if the order changes.
- Out of scope:
  - Any other transfer logic changes.
  - Spellbook contract map or pool refactors.
  - Test additions beyond order-related updates (unless required).

## Steps / Checklist
- [x] Update TransferOfOwnership.execute to unshare before flipping spellbooks when force_unshare is True.
- [x] Review docstrings/comments for accuracy after reorder.
- [x] Update handoff summary.

## Deliverables
- Ownership transfer flow reordered for force_unshare path.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py -k transfer_ownership_force_unshare_allows_local

## Risks / Rollback Notes
- Risk: unshare-before-flip may affect borrowers if transfer fails mid-flight.
- Rollback: revert the reorder if it introduces regressions.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Completed reorder to unshare target contract before ownership flip (force_unshare) and ensured existence checks cover both contract sides to avoid removing newly owned spell_id_pool entries.
