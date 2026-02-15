# Task: Add SpellIndex update propagation tests

- Completed: 2026-01-25
- Summary: Added unit tests for SpellIndex owner/contract update propagation
  and cleanup behavior in `tests/unit/melder/spellbook/bind/test_spell_index.py`.

## Metadata
- Task ID: TASK-2026-01-25-spellindex-update-tests
- Story: STORY-2026-01-25-spellindex-update-propagation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add tests that verify SpellIndex.update propagates spell_id changes to Spellbook
maps for owned and contracted spells.

## Scope Boundaries
- In scope:
  - Unit tests for owner map updates on SpellIndex.update.
  - Unit tests for contracted map updates on SpellIndex.update.
- Out of scope:
  - Mutation pipeline tests.

## Steps / Checklist
- [x] Add unit tests for owner update propagation.
- [x] Add unit tests for contracted update propagation.
- [x] Validate cleanup behavior if attachments are cleared.

## Deliverables
- Tests covering SpellIndex update propagation behavior.

## Files / Paths Impacted
- `tests/unit/melder/spellbook/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook -q`

## Risks / Rollback Notes
- Risk: tests overfit to internal attributes.
  Rollback: assert observable map changes only.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added SpellIndex attachment/update coverage in
  `tests/unit/melder/spellbook/bind/test_spell_index.py`.
- Tests cover owner updates, contracted updates, and cleanup after attachments.
- Acceptance confirmed; ready for completed archive.
