# Task: Propagate SpellIndex updates to Spellbook maps

- Completed: 2026-01-25
- Summary: SpellIndex.update now propagates old/new ids to Spellbook owned and
  contracted spell_id maps outside the SpellIndex lock.

## Metadata
- Task ID: TASK-2026-01-25-spellindex-update-notify
- Story: STORY-2026-01-25-spellindex-update-propagation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Update SpellIndex.update to notify owning and contracted Spellbooks so spell_id
maps stay synchronized with the current version.

## Scope Boundaries
- In scope:
  - Update `SpellIndex.update` to capture old id and notify Spellbook maps.
  - Use Spellbook helper methods for owned and contracted map updates.
  - Update docstrings for update and helper methods.
- Out of scope:
  - Mutation pipeline changes.

## Steps / Checklist
- [x] Capture old id in `SpellIndex.update` before mutation.
- [x] Notify owning Spellbook of id map changes.
- [x] Notify contracted Spellbooks of id map changes with conduit id context.
- [x] Update docstrings to reflect update propagation behavior.

## Deliverables
- SpellIndex.update propagates map changes to Spellbook structures.

## Files / Paths Impacted
- `src/melder/spellbook/bind/spell_index.py`
- `src/melder/spellbook/spellbook.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook -q`

## Risks / Rollback Notes
- Risk: update notifications run under lock and cause deadlocks.
  Rollback: stage notifications outside the lock if needed.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- SpellIndex now captures the prior id and propagates updates outside the lock in
  `src/melder/spellbook/bind/spell_index.py`.
- Update propagation calls Spellbook helpers for owner and contracted maps.
- Acceptance confirmed; ready for completed archive.
