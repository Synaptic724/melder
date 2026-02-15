# Task: Add SpellIndex ownership and contract attachments

- Completed: 2026-01-25
- Summary: Added SpellIndex owner/contract attachment APIs with cleanup
  clearing references and registration into Spellbook maps.

## Metadata
- Task ID: TASK-2026-01-25-spellindex-attach-ownership
- Story: STORY-2026-01-25-spellindex-update-propagation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add SpellIndex APIs to attach owning and contracted Spellbooks with explicit
ownership metadata.

## Scope Boundaries
- In scope:
  - SpellIndex fields to track owner Spellbook and owned Spell.
  - SpellIndex fields to track contracted Spellbooks per conduit id.
  - Attach and detach methods with rich docstrings.
- Out of scope:
  - SpellIndex update propagation logic (separate task).

## Steps / Checklist
- [x] Add SpellIndex fields for owner and contracted attachments.
- [x] Implement attach/detach methods for owner and contracted Spellbooks.
- [x] Update cleanup to clear attachment references.
- [x] Update docstrings for new methods and cleanup.

## Deliverables
- SpellIndex attachment API ready for update propagation.

## Files / Paths Impacted
- `src/melder/spellbook/bind/spell_index.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook -q`

## Risks / Rollback Notes
- Risk: attachment references leak if cleanup is incomplete.
  Rollback: remove attachment fields and rely on existing behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- SpellIndex attachments for owner and contracted Spellbooks are implemented in
  `src/melder/spellbook/bind/spell_index.py` with cleanup nulling.
- Acceptance confirmed; ready for completed archive.
