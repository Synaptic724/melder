# Phase 10 Patch Map Compiler Plan (2026-01-27)

## Purpose
Define how Phase 10 compiles patch maps for overrides and mutation rewires,
and how meld runtime will apply them in the fast path.

## Evidence Anchors
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider.apply`
- `src/melder/aether/conduit/meld/overrides/spell_overrider.py:_specificity_for_spec`
- `src/melder/aether/conduit/meld/overrides/graph_mutator.py:GraphMutator.apply`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute`

## Phase 10 Insertion Point (Draft)
Phase 10 depends on Phase 5 artifacts and (optionally) Phase 8 outputs.
Candidate insertion:
- After Phase 9 (if present), otherwise after Phase 8.

Rationale:
- Patch maps are independent of InjectionPlan, but often consume the same
  blueprint/index data.

## Compiler Responsibilities
Override patch map:
- Pre-resolve TargetSpec keys to SocketRef lists using DagTargetingEngine.
- Persist specificity data for conflict resolution.

Mutation patch map:
- Pre-resolve mutation TargetSpec keys to mutation socket refs.
- Encode edge replacement intent (child_id, param_name, new_parent_id).
- Record when additional SocketRef/DagIndex updates are required.
- Flag cases requiring full DAG rebuild (fallback).

## Proposed SpellCrafter API
Add:
- `run_phase_patch_maps(conduit_id, cancel_event=None)`
Store:
- `_override_patch_map_phase10`
- `_mutation_patch_map_phase10`

Add Spell facade:
- `Spell.run_phase_patch_maps(conduit_id, cancel_event=None)`

## Runtime Application (Draft)
- If override payloads exist:
  - Apply OverridePatchMap to translate TargetSpec -> SocketRef list.
  - Build override_map without DagTargetingEngine on the hot path.
- If mutation overrides exist:
  - Apply MutationPatchMap for supported rewires.
  - If unsupported, fallback to GraphMutator.

## Tests (Draft)
- Unit: patch map resolution matches SpellOverrider socket targeting.
- Unit: mutation patch map flags unsupported rewires.
- Integration: override payloads use patch maps and skip DagTargetingEngine.
- Integration: mutation patch map falls back to GraphMutator when marked unsupported.

## Open Questions
- Exact supported mutation subset for patching vs DAG rebuild.
- Where to store patch maps for cleanup and invalidation.
