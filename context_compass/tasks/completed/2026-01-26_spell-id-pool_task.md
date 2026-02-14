# Task: Add Spellbook spell_id_pool for meld lookup

## Metadata
- Task ID: TASK-2026-01-26-spell-id-pool
- Story: STORY-2026-01-25-fast-path-runtime
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-26
- Updated: 2026-01-26

## Objective
Add a simple spell_id_pool that aggregates owned + contracted spell ids for
fast O(1) lookup in meld, while keeping existing per-conduit maps.

## Scope Boundaries
- In scope:
  - Add spell_id_pool to Spellbook and keep it updated on owned/contracted changes.
  - Use spell_id_pool in Meld._resolve_spell_by_id before scanning per-conduit maps.
- Out of scope:
  - Changing contract collision rules or ownership semantics.
  - Removing existing contracted maps.

## Steps / Checklist
- [x] Add spell_id_pool storage and cleanup in Spellbook.
- [x] Update owned/contracted spell_id register/update/unregister paths.
- [x] Wire Meld._resolve_spell_by_id to prefer spell_id_pool.
- [x] Document behavior and update task context.

## Deliverables
- Updated Spellbook and Meld to use spell_id_pool.

## Files / Paths Impacted
- src/melder/spellbook/spellbook.py
- src/melder/aether/conduit/meld/meld.py
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py
- context_compass/tasks/2026-01-26_spell-id-pool_task.md

## Validation
- Not run.
- Recommended commands:
  - pytest -k resolve_spell_by_id

## Risks / Rollback Notes
- Risk: stale entries if pool is not kept in sync.
  Mitigation: update pool in owned/contracted register/update/unregister paths.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Added spell_id_pool to Spellbook, kept in sync with owned/contracted spell_id
updates, wired Meld._resolve_spell_by_id to prefer the pool, and updated
ownership transfer paths to keep the pool consistent.
