# Task: Require Phase 8-10 artifacts in MeldRuntime/MeldEngine

## Metadata
- Task ID: TASK-2026-01-28-meld-runtime-phase-artifact-gating
- Story: STORY-2026-01-28-meld-runtime-phase-artifacts
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Remove meld runtime/engine fallback compilation paths and require Phase 8-10
artifacts for occurrence planning, injection wiring, and override targeting,
while preserving existing behavior and error semantics.

## Scope Boundaries
- In scope:
  - MeldRuntime and MeldEngine changes to require phase artifacts.
  - Eliminate duplicated occurrence planning and contract override compilation
    in runtime/engine when phase artifacts exist.
- Out of scope:
  - Any new behavior or API changes.
  - Refactors outside meld runtime/engine.

## Steps / Checklist
- [x] Identify all runtime/engine fallback code paths and their behaviors.
- [x] Decide required artifact presence and error messages when missing.
- [x] Remove or gate fallback logic in MeldEngine.
- [x] Ensure runtime always passes phase artifacts from SpellCrafter.
- [x] Update tests for missing-artifact errors and normal execution.

## Deliverables
- MeldRuntime/MeldEngine uses Phase 8-10 artifacts as the source of truth.
- Duplicate runtime planning logic removed or gated.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- tests/unit/melder/aether/conduit/meld/

## Validation
- PYTHONPATH=/workspace/melder_private pytest -q

## Risks / Rollback Notes
- Risk: tighter artifact requirements change error behavior for unphased spells.
- Rollback: restore previous fallback paths in MeldEngine.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created to remove meld runtime/engine fallback compilation paths so phase
artifacts are required without semantic drift.
