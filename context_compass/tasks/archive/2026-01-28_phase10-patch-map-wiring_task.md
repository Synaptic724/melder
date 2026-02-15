# Task: Wire Phase 10 patch maps into meld runtime

## Metadata
- Task ID: TASK-2026-01-28-phase10-patch-map-wiring
- Story: STORY-2026-01-28-meld-runtime-phase-artifacts
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Use Phase 10 OverridePatchMap and MutationPatchMap during meld execution and
remove runtime fallback logic in SpellOverrider/GraphMutator while preserving
current behavior and error semantics.

## Scope Boundaries
- In scope:
  - MeldRuntime wiring for override_patch_map_phase10 and mutation_patch_map_phase10.
  - Remove or bypass SpellOverrider and GraphMutator usage for runtime overrides.
- Out of scope:
  - New mutation semantics or override precedence changes.
  - Changes outside meld runtime/engine and Phase 10 artifacts.

## Steps / Checklist
- [x] Document current override/mutation behavior and errors (evidence-based).
- [x] Implement runtime usage of OverridePatchMap for value overrides.
- [x] Implement runtime usage of MutationPatchMap for mutation rewires.
- [x] Remove or bypass SpellOverrider/GraphMutator in runtime.
- [x] Add/adjust tests for override and mutation behaviors.

## Deliverables
- Runtime uses Phase 10 patch maps for override and mutation targeting.
- SpellOverrider/GraphMutator no longer used in meld runtime flow.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py
- src/melder/aether/conduit/meld/overrides/spell_overrider.py
- src/melder/aether/conduit/meld/overrides/graph_mutator.py
- tests/unit/melder/aether/conduit/meld/

## Validation
- PYTHONPATH=/workspace/melder_private pytest -q

## Risks / Rollback Notes
- Risk: mutation rewiring diverges from current GraphMutator behavior.
- Rollback: restore runtime GraphMutator path and remove MutationPatchMap usage.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created to wire Phase 10 patch maps into meld runtime and remove runtime
fallbacks while preserving behavior.
