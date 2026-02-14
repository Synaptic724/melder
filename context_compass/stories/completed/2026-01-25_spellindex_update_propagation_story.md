# Story: SpellIndex update propagation to Spellbook maps

- Completed: 2026-01-25
- Summary: SpellIndex attachments, update propagation, and unit/integration
  coverage delivered; acceptance confirmed by user.

## Metadata
- Story ID: STORY-2026-01-25-spellindex-update-propagation
- Epic: EPIC-2026-01-25-spell-id-lookup-foundation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As SpellIndex, we want version updates to notify owning and contracted
Spellbooks so spell_id maps stay in sync with the current head version.

## Value / MRP Alignment
SpellIndex is the lineage anchor. Propagating updates from SpellIndex keeps
resolution correct without external mutation hooks.

## Requirements (Functional)
- SpellIndex can attach to an owning Spellbook and spell object.
- SpellIndex can attach to contracted Spellbooks with conduit identifiers.
- SpellIndex.update captures old id and notifies Spellbook maps for owned and
  contracted entries.
- Cleanup clears SpellIndex references to Spellbooks and spells.

## Requirements (Non-Functional)
- Preserve existing SpellIndex hashing and equality behavior.
- Maintain thread safety using the existing SpellIndex lock.
- No module-level mutable state added.

## Scope Boundaries
- In scope:
  - `src/melder/spellbook/bind/spell_index.py` attachments and update behavior.
  - Spellbook helper methods used by SpellIndex for map updates.
- Out of scope:
  - Mutation pipelines and mutation contract changes.

## Dependencies / Related Work
- Story: STORY-2026-01-25-spellbook-spell-id-maps

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-spellindex-attach-ownership - Add attachment APIs.
- [x] Task: TASK-2026-01-25-spellindex-update-notify - Wire update propagation.
- [x] Task: TASK-2026-01-25-spellindex-update-tests - Add update tests.
- [x] Task: TASK-2026-01-25-spellindex-update-integration-tests - Add integration tests.

## Acceptance Criteria
- SpellIndex update notifies the owner Spellbook and contracted Spellbooks.
- SpellIndex cleanup clears attachments and prevents use-after-clean.
- Tests cover owner and contracted update paths.

## Validation / Test Plan
- Unit tests that exercise SpellIndex.update and map propagation.

## UX / API / Data Notes
- Internal-only behavior; no public API exposure expected.

## Risks / Mitigations
- Risk: update during cleanup could touch cleared references.
  Mitigation: use SpellIndex check_cleaned guard and explicit nulling.

## Open Questions
- UNKNOWN: Should SpellIndex.update also update Spell.spell_id or only maps?
  Investigate: `src/melder/spellbook/spell.py` and binding flows.

## Decision Log
- 2026-01-25: Use SpellIndex as the single update signal for spell_id maps.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
- SpellIndex attachments, update propagation, and tests are complete; user
  confirmed acceptance and reported tests passed.
