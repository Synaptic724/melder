# Story: Spellbook spell_id maps for owned and contracted spells

- Completed: 2026-01-25
- Summary: Spellbook maintains owned/contracted spell_id maps with bind/contract
  updates, plus unit tests and docs; acceptance confirmed by user.

## Metadata
- Story ID: STORY-2026-01-25-spellbook-spell-id-maps
- Epic: EPIC-2026-01-25-spell-id-lookup-foundation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As the meld resolution path, we want Spellbook to maintain O(1) spell_id to spell
maps for owned and contracted spells, so that resolution avoids linear scans.

## Value / MRP Alignment
This hardens the core resolution path with constant-time lookups while keeping
the existing SpellIndex lineage model intact.

## Requirements (Functional)
- Spellbook maintains an owned spell_id map keyed by current spell_id.
- Spellbook maintains per-conduit contracted spell_id maps keyed by current
  spell_id.
- Bind and contract flows insert and remove entries from these maps.
- Cleanup nulls the new maps and preserves existing cleanup ordering.

## Requirements (Non-Functional)
- O(1) lookup behavior for spell_id in owned and contracted contexts.
- No new module-level mutable state.
- Docstrings updated for touched methods.

## Scope Boundaries
- In scope:
  - `src/melder/spellbook/spellbook.py` internal maps and update helpers.
  - Contract add/remove/clear updates to new maps.
  - Bind path updates to new maps.
- Out of scope:
  - Mutation pipeline updates.
  - Public API changes.

## Dependencies / Related Work
- Story: STORY-2026-01-25-spellindex-update-propagation
- Story: STORY-2026-01-25-meld-spell-id-lookup

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-spellbook-id-map-structure - Add maps and helpers.
- [x] Task: TASK-2026-01-25-spellbook-id-map-binding-contracts - Wire bind and contracts.
- [x] Task: TASK-2026-01-25-spellbook-id-map-docs-tests - Add tests and doc updates.

## Acceptance Criteria
- Spellbook has owned and contracted spell_id maps initialized and cleaned up.
- Bind and contract paths update the maps without changing external behavior.
- Tests cover map updates for add/remove/clear and cleanup.

## Validation / Test Plan
- Unit tests for Spellbook map updates and cleanup behavior.
- Component tests if contract flows require real wiring.

## UX / API / Data Notes
- Internal-only change; no public API changes expected.

## Risks / Mitigations
- Risk: map divergence when SpellIndex updates occur.
  Mitigation: use explicit update helpers and SpellIndex notifications.

## Open Questions
- Resolved: `_find_contracted_spell_by_id` retains SpellIndex version scans
  because spell_id maps track only the current id.

## Decision Log
- 2026-01-25: Keep spell_id maps internal to Spellbook to avoid API changes.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Spellbook now initializes owned/contracted spell_id maps, wires bind and
  contract flows via SpellIndex attachments, and cleans them on teardown.
- Unit tests cover owned/contracted map registration, updates, and cleanup;
  architecture/components docs note O(1) spell_id map usage.
- Acceptance confirmed by user.
