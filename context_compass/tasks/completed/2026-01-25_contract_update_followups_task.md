# Task: Implement contract and ownership follow-up updates

- Completed: 2026-01-25
- Summary: Updated ownership transfer to move Spellbook spell_id maps and
  SpellIndex owner references, plus unit coverage for id map movement in
  `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`.

## Metadata
- Task ID: TASK-2026-01-25-contract-update-followups
- Story: STORY-2026-01-25-contract-link-ownership-impacts
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Implement contract and ownership updates identified by audit tasks.

## Scope Boundaries
- In scope:
  - Apply updates identified in contract and ownership audits.
  - Update docstrings and tests for touched code.
- Out of scope:
  - New contract policy behavior.
  - Mutation pipeline changes.

## Steps / Checklist
- [x] Review audit findings from TASK-2026-01-25-contract-link-audit.
- [x] Review audit findings from TASK-2026-01-25-ownership-transfer-audit.
- [x] Implement required map update or attachment changes.
- [x] Add or update tests for modified flows.

## Deliverables
- Updated contract and ownership flows aligned with spell_id maps.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/`
- `tests/unit/melder/aether/conduit/`
- `tests/integration/melder/conduit/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit -q`
  - `pytest tests/integration/melder/conduit -q`

## Risks / Rollback Notes
- Risk: contract updates change behavior without adequate tests.
  Rollback: gate changes behind tests and keep scope minimal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Ownership transfer now updates `_spells_by_id` maps and SpellIndex owner
  references in
  `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`.
- Added unit test coverage for spell_id map movement during transfer in
  `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`.
- Acceptance confirmed by user.
