# Task: Remove dead methods from MeldEngine after phase migration

## Metadata
- Task ID: TASK-2026-01-28-meld-engine-dead-methods
- Story: N/A
- Status: in_progress
- Owner: codex
- Priority: p2
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Remove unused helper methods from MeldEngine that are no longer referenced after phases 8-10 migration, without changing behavior.

## Scope Boundaries
- In scope:
  - Remove `_build_kwargs_for_node` and `_store_result` from `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`.
- Out of scope:
  - Any behavioral changes in meld runtime/engine.
  - Refactoring or renaming other methods.

## Steps / Checklist
- [x] Confirm unused methods via repo search (no references in `src/`).
- [x] Delete the methods and keep surrounding docstrings/comments intact.
- [ ] Review file for any now-stale comments and update if needed.

## Deliverables
- MeldEngine no longer contains unused `_build_kwargs_for_node` and `_store_result`.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_spell_contracts.py

## Risks / Rollback Notes
- Risk: Accidental removal of a method still used via dynamic calls.
- Rollback: Restore the removed methods verbatim.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created to remove unused MeldEngine helpers after the phase migration cleanup, with minimal scope and no behavior changes.
