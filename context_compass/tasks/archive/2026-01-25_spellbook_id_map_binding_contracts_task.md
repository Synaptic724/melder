# Task: Wire Spellbook spell_id maps into bind and contracts

- Completed: 2026-01-25
- Summary: Wired bind and contract flows to keep spell_id maps synchronized
  via SpellIndex attachments in `src/melder/spellbook/spellbook.py` and
  `src/melder/spellbook/bind/spell_index.py`.

## Metadata
- Task ID: TASK-2026-01-25-spellbook-id-map-binding-contracts
- Story: STORY-2026-01-25-spellbook-spell-id-maps
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Update Spellbook bind and contract flows to populate and maintain spell_id maps.

## Scope Boundaries
- In scope:
  - Bind path adds owned spell_id entries.
  - Contract add/remove/clear updates contracted spell_id maps.
  - Link contract create/remove initializes and clears contracted maps.
- Out of scope:
  - Mutation pipeline changes.
  - Public API changes.

## Steps / Checklist
- [x] Wire spell_id map updates into local bind registration.
- [x] Initialize contracted spell_id maps on link creation.
- [x] Update contracted spell_id maps on add/remove/clear contract flows.
- [x] Update docstrings for touched methods.

## Deliverables
- Spellbook bind and contract flows keep spell_id maps consistent.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook -q`

## Risks / Rollback Notes
- Risk: contract map updates missed in a contract branch.
  Rollback: remove map updates and fall back to current lookup behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- SpellIndex attaches to Spellbook and drives owned/contracted spell_id map
  updates; contract link creation initializes `_contracted_spells_by_id`.
- Acceptance confirmed by user.
