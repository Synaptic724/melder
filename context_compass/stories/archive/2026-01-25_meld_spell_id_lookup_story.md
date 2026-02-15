# Story: Meld O(1) spell_id resolution

- Completed: 2026-01-25
- Summary: Meld now references Spellbook spell_id maps for O(1) lookup with
  updated docstrings and unit tests; acceptance confirmed by user.

## Metadata
- Story ID: STORY-2026-01-25-meld-spell-id-lookup
- Epic: EPIC-2026-01-25-spell-id-lookup-foundation
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As a Conduit, we want Meld to resolve by spell_id using O(1) maps so the hot
path avoids linear scans.

## Value / MRP Alignment
This change keeps the resolution path fast and predictable without changing
Spellbook or Conduit public APIs.

## Requirements (Functional)
- Meld references Spellbook-owned spell_id maps for owned and contracted spells.
- `_resolve_spell_by_id` uses O(1) lookups and preserves existing error behavior.
- Cleanup nulls new references.

## Requirements (Non-Functional)
- No behavior changes outside the spell_id resolution path.
- Maintain existing locking and cleanup patterns.

## Scope Boundaries
- In scope:
  - `src/melder/aether/conduit/meld/meld.py` (init, cleanup, and lookup).
- Out of scope:
  - SpellIndex changes.
  - Contract or ownership semantics.

## Dependencies / Related Work
- Story: STORY-2026-01-25-spellbook-spell-id-maps

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-meld-id-map-references - Add map references and lookup.
- [x] Task: TASK-2026-01-25-meld-id-map-cleanup-docs - Update cleanup and docstrings.
- [x] Task: TASK-2026-01-25-meld-id-map-tests - Add unit tests for lookup.

## Acceptance Criteria
- Meld uses spell_id maps without linear scans.
- Meld cleanup nulls new references.
- Tests cover owned and contracted spell_id lookups.

## Validation / Test Plan
- Unit tests for `_resolve_spell_by_id` using owned and contracted maps.

## UX / API / Data Notes
- Internal-only change; no user-facing API change.

## Risks / Mitigations
- Risk: test stubs missing new map fields.
  Mitigation: update relevant test stubs as part of the task.

## Open Questions
- Resolved: Updated Meld test stubs to expose spell_id maps in
  `tests/unit/melder/aether/conduit/meld/test_meld.py`.

## Decision Log
- 2026-01-25: Keep spell_id lookup changes isolated to Meld.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
- Meld now references owned/contracted spell_id maps in `__init__`, resolves
  spell_id via those maps, and clears the references on cleanup.
- Unit tests validate owned/contracted map resolution and missing-map errors.
- Acceptance confirmed by user.
