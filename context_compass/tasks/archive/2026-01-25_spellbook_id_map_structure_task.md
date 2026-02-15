# Task: Add Spellbook spell_id map structure

- Completed: 2026-01-25
- Summary: Initialized owned and contracted spell_id maps in Spellbook with
  helper methods and cleanup nulling in `src/melder/spellbook/spellbook.py`.

## Metadata
- Task ID: TASK-2026-01-25-spellbook-id-map-structure
- Story: STORY-2026-01-25-spellbook-spell-id-maps
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add Spellbook-owned spell_id maps and internal update helpers with explicit
initialization and cleanup.

## Scope Boundaries
- In scope:
  - Add owned and contracted spell_id maps to Spellbook initialization.
  - Add helper methods for updating owned and contracted spell_id maps.
  - Update cleanup to null the new maps.
- Out of scope:
  - Mutation pipeline changes.
  - Public API changes.

## Steps / Checklist
- [x] Review `src/melder/spellbook/spellbook.py` init and cleanup ordering.
- [x] Add owned and contracted spell_id maps with deterministic init.
- [x] Add internal helper methods with rich docstrings for map updates.
- [x] Update cleanup to clear and null new maps.

## Deliverables
- Spellbook has initialized and cleaned spell_id maps.
- Internal helper methods exist for map updates.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook -q`

## Risks / Rollback Notes
- Risk: map divergence if helper methods are not used consistently.
  Rollback: remove maps and revert to current resolution behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added `_spells_by_id` and `_contracted_spells_by_id` initialization plus
  owned/contracted helper methods and cleanup nulling in
  `src/melder/spellbook/spellbook.py`.
- Acceptance confirmed by user.
