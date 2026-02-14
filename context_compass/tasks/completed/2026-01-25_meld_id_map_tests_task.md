# Task: Add Meld spell_id map tests

- Completed: 2026-01-25
- Summary: Added unit coverage for owned/contracted spell_id resolution and
  updated stubs to expose spell_id maps in
  `tests/unit/melder/aether/conduit/meld/test_meld.py`.

## Metadata
- Task ID: TASK-2026-01-25-meld-id-map-tests
- Story: STORY-2026-01-25-meld-spell-id-lookup
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add unit tests for Meld spell_id resolution using owned and contracted maps.

## Scope Boundaries
- In scope:
  - Tests for owned map resolution.
  - Tests for contracted map resolution.
  - Update Meld test stubs to include new map references.
- Out of scope:
  - Integration tests unless required by contract behavior.

## Steps / Checklist
- [x] Add unit tests for owned spell_id map resolution.
- [x] Add unit tests for contracted spell_id map resolution.
- [x] Update test stubs to include spell_id map attributes.

## Deliverables
- Unit tests covering Meld spell_id map lookups.

## Files / Paths Impacted
- `tests/unit/melder/aether/conduit/meld/`
- `tests/unit/melder/aether/conduit/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/meld -q`

## Risks / Rollback Notes
- Risk: tests depend on private attributes without contract coverage.
  Rollback: anchor tests on `_resolve_spell_by_id` behavior only.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Meld unit tests cover owned/contracted spell_id resolution and error paths,
  with stubs exposing spell_id maps in
  `tests/unit/melder/aether/conduit/meld/test_meld.py`.
- Acceptance confirmed by user.
