# Meld Engine and Phase Migration Audit

## Metadata
- Status: draft
- Owner: codex
- Created: 2026-01-28
- Updated: 2026-01-28
- Related task: TASK-2026-01-28-phase8-10-migration-audit

## Purpose
Produce an evidence-based audit of duplicated or misplaced responsibilities between SpellCrafter phases 1-10 and meld runtime/engine, and map each behavior to its correct phase owner.

## Scope
- In scope:
  - SpellCrafter phases 1-10 wiring and phase outputs.
  - Meld runtime and meld engine responsibilities during resolution.
- Out of scope:
  - Behavior changes (this document is investigation only).
  - Refactors outside the meld/phase pipeline.

## Investigation Plan
- Inventory meld runtime/engine behaviors and identify compile-time logic still running in runtime.
- Identify which SpellCrafter phases already compile or should compile those behaviors.
- Record duplicated behaviors and mismatched ownership.
- Capture invalidation/refresh paths for phase artifacts that feed runtime.

## Evidence Log
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_occurrence_plan
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_injection_plan
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_extend_occurrence_graph_with_ordered_nodes
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_execution_order
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_instance_plan
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_compile_contract_overrides
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_normalize_contract_override_payload
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance_from_plan
- src/melder/aether/conduit/meld/overrides/graph_mutator.py:GraphMutator.apply
- src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider.apply
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_requirements
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_symbolic_graph
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_local_frame
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_validation
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_occurrence_plan
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_injection_plan
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_patch_maps
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_system_validation
- src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_change_control
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder.build
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._build_occurrence_graph
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._extend_occurrence_graph_with_ordered_nodes
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._build_execution_order
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._build_instance_plan
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._compile_contract_overrides
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._normalize_contract_override_payload
- src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:InjectionPlanBuilder.build
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:PatchMapBuilder.build_override_patch_map
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:OverridePatchMap.apply
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:PatchMapBuilder.build_mutation_patch_map

## Findings
- Phase 8 OccurrencePlanBuilder duplicates MeldEngine's occurrence planning logic (occurrence graph, execution order, instance plan, canonical occurrence selection). This appears in both the phase builder and the runtime engine. Evidence: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_occurrence_graph and src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._build_occurrence_graph (also _extend_occurrence_graph_with_ordered_nodes, _build_execution_order, _build_instance_plan, _select_canonical_occurrence).
- SpellContract override compilation is duplicated between MeldEngine and OccurrencePlanBuilder. Evidence: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_compile_contract_overrides and src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:OccurrencePlanBuilder._compile_contract_overrides (also _normalize_contract_override_payload, _record_contract_override).
- Override TargetSpec resolution and specificity logic exists both in Phase 10 OverridePatchMap and in runtime SpellOverrider. MeldRuntime uses OverridePatchMap when present but falls back to SpellOverrider when absent. Evidence: src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:OverridePatchMap.apply, src/melder/aether/conduit/meld/overrides/spell_overrider.py:SpellOverrider.apply, src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute.
- Mutation patch maps are compiled in Phase 10, but MeldRuntime applies mutation overrides by cloning and rewiring the blueprint via GraphMutator; there is no usage of MutationPatchMap in runtime. Evidence: src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:PatchMapBuilder.build_mutation_patch_map and src/melder/aether/conduit/meld/overrides/graph_mutator.py:GraphMutator.apply, src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute.
- InjectionPlanBuilder only records dependency wiring (ParamSource kind "dependency"); MeldEngine still merges overrides and SpellContract payloads at runtime even when an InjectionPlan is present. Evidence: src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:InjectionPlanBuilder.build and src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance_from_plan.
- MeldRuntime passes dag/requirements/resolution_frame into MeldEngine; within meld_engine.py these fields are assigned/cleared but not referenced elsewhere in the file. Evidence: src/melder/aether/conduit/meld/meld_engine/meld_engine.py (__init__ assignments and cleanup).

## Phase Map (1-10, evidence-based)
- Phase 1 (requirements): SpellCrafter builds SpellRequirements and stores on crafter. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_requirements.
- Phase 2 (symbolic graph): SpellCrafter builds SpellSymbolicGraph for sockets and contract metadata. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_symbolic_graph.
- Phase 3 (local frame/DAG): SpellCrafter builds local topology and resolution frame (stored on spell/crafter). Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_local_frame (see Phase 3 section).
- Phase 4 (validation): SpellCrafter validates using Phase 1-3 artifacts and sets flags. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_validation.
- Phase 5 (root blueprints): SpellCrafter builds RootResolutionBlueprints and SpellSystemIndex. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_root_blueprints.
- Phase 6 (system validation): SpellCrafter validates system-level invariants and records validation state. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_system_validation.
- Phase 7 (change control): SpellCrafter wires change-control and component-of index. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_change_control.
- Phase 8 (occurrence plan): SpellCrafter compiles OccurrencePlan from Phase 5 blueprint. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_occurrence_plan.
- Phase 9 (injection plan): SpellCrafter compiles InjectionPlan from OccurrencePlan. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_injection_plan.
- Phase 10 (patch maps): SpellCrafter compiles OverridePatchMap and MutationPatchMap from Phase 5 blueprint. Evidence: src/melder/spellbook/spell_crafter/spell_crafter.py:run_phase_patch_maps.

## Duplication Map (Runtime/Engine -> Phase Owner)
- Occurrence graph + execution order (MeldEngine _build_occurrence_graph/_build_execution_order) -> Phase 8 OccurrencePlanBuilder (compiled plan already exists; engine still rebuilds when plan absent).
- Instance plan + canonical occurrences (MeldEngine _build_instance_plan/_select_canonical_occurrence) -> Phase 8 OccurrencePlanBuilder.
- SpellContract override compilation (MeldEngine _compile_contract_overrides/_normalize_contract_override_payload) -> Phase 8 OccurrencePlanBuilder.
- Override TargetSpec resolution/specificity (SpellOverrider.apply) -> Phase 10 OverridePatchMap.apply.
- Mutation override rewiring (GraphMutator.apply) -> Phase 10 MutationPatchMap (compiled but unused; runtime does its own rewiring).
- Dependency wiring (MeldEngine _build_kwargs_for_instance) -> Phase 9 InjectionPlan (currently partial; plan only captures dependency sources, runtime still merges overrides/contract payloads).

## Unknowns
- Whether MutationPatchMap is intended to replace GraphMutator at runtime or is a future artifact with no runtime wiring yet.
  - Investigate: src/melder/spellbook/spell_crafter/blueprints/patch_maps.py
  - Investigate: src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- Whether InjectionPlan is intended to encode override/contract sourcing (beyond dependencies) to eliminate runtime merging.
  - Investigate: src/melder/spellbook/spell_crafter/blueprints/injection_plan.py
  - Investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_build_kwargs_for_instance_from_plan
- Whether runtime should require Phase 8/9/10 artifacts instead of recomputing (i.e., eliminate fallback paths).
  - Investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_occurrence_plan
  - Investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py:_select_injection_plan
- Whether stored dag/requirements/resolution_frame in MeldEngine are legacy or should be consumed by phase artifacts.
  - Investigate: src/melder/aether/conduit/meld/meld_engine/meld_engine.py (__init__ fields)

## Next Steps
- Continue audit by tracing Phase 1-7 artifacts into runtime/engine usage (if any), and confirm where runtime gating overlaps with phase invariants.
- Expand the duplication map with file+symbol references for each item.
- Propose follow-up tasks once the duplication and ownership decisions are confirmed.
