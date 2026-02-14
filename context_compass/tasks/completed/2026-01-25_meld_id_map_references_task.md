# Task: Update Meld to reference spell_id maps

- Completed: 2026-01-25
- Summary: Meld now references Spellbook spell_id maps on initialization and
  resolves spell_id via those maps in
  `src/melder/aether/conduit/meld/meld.py`.

## Metadata
- Task ID: TASK-2026-01-25-meld-id-map-references
- Story: STORY-2026-01-25-meld-spell-id-lookup
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Update Meld to reference Spellbook spell_id maps and use them for spell_id
resolution.

## Scope Boundaries
- In scope:
  - Add spell_id map references in Meld initialization.
  - Use maps in `_resolve_spell_by_id`.
- Out of scope:
  - Spellbook or SpellIndex changes.

## Steps / Checklist
- [x] Add references to owned and contracted spell_id maps in `Meld.__init__`.
- [x] Replace linear scans in `_resolve_spell_by_id` with map lookups.
- [x] Keep error messages and behavior consistent.

## Deliverables
- Meld resolves spell_id via O(1) maps.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/meld -q`

## Risks / Rollback Notes
- Risk: contract map shape mismatch in Meld.
  Rollback: revert to linear scan until map shape is confirmed.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Meld now holds owned/contracted spell_id map references and resolves
  spell_id lookups against them in
  `src/melder/aether/conduit/meld/meld.py`.
- Acceptance confirmed by user.
