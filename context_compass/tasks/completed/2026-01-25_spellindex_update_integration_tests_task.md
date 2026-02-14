# Task: Add SpellIndex update integration tests

- Completed: 2026-01-25
- Summary: Added integration tests validating owned and contracted spell_id
  updates with real Spellbook/Conduit meld resolution.

## Metadata
- Task ID: TASK-2026-01-25-spellindex-update-integration-tests
- Story: STORY-2026-01-25-spellindex-update-propagation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add integration tests that validate SpellIndex.update propagates spell_id changes
through real Spellbook/Conduit wiring for owned and contracted spells.

## Scope Boundaries
- In scope:
  - Integration tests using Spellbook bind/conjure and Conduit meld.
  - Dynamic link + contract path for contracted spell_id updates.
- Out of scope:
  - Mutation pipeline changes.
  - Unit test additions.

## Steps / Checklist
- [x] Add integration test for owned spell_id update propagation.
- [x] Add integration test for contracted spell_id update propagation.
- [x] Update story task checklist with this task.

## Deliverables
- Integration tests covering owned and contracted SpellIndex.update propagation.

## Files / Paths Impacted
- `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_extra.py`
- `context_compass/stories/completed/2026-01-25_spellindex_update_propagation_story.md`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_extra.py -q`

## Risks / Rollback Notes
- Risk: Aether version registry is not refreshed by SpellIndex.update.
  Rollback: Scope tests to Conduit.meld (Spellbook maps) rather than Aether lookups.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Added integration coverage for owned and contracted SpellIndex.update behavior in
  `tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_extra.py`.
- Story checklist updated with the integration test task.
- Acceptance confirmed; ready for completed archive.
