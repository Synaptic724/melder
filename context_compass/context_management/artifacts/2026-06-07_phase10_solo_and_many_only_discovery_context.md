# Context Artifact: Phase 10 Solo And Many-Only Discovery

## Metadata
- Context ID: CTX-2026-06-07-phase10-solo-and-many-only-discovery
- Status: active
- Owner: codex
- Agent Name: compiler_0
- Created: 2026-06-07T00:17:18Z
- Updated: 2026-06-07T09:23:42Z
- Related Tickets:
  - `tickets/stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md`
  - `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`

## Purpose
Keep the bounded reread pack for the phase-10 `solo` and `many_only`
category work so later implementation passes reopen the producer truth and the
phase-10 discovery/planner seams directly instead of rebuilding the lane from
chat.

## Required Reads
- `tickets/stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md`
- `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
- `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
- `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`
- `src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py`
- `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_state.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_no_overrides_codegen_creation_step.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_overrides_codegen_creation_step.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py`
- `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
- `artifacts/2026-05-30_phase12_north_star_runtime_model.md`
- `artifacts/2026-06-02_topdown_compiler_exploration_strategy.md`

## Topics
- phase-8 production of existence and disposal facts
- phase-9 exposure of those facts on `SpellCodegenModel`
- phase-4 structural validity and contract gating
- phase-5 rooted-blueprint and system-index production
- phase-6 conduit-scoped system validation
- phase-7 change-control revalidation wiring
- phase-10 discovery precedence:
  - `solo` first
  - `many_only` second
  - `generalized` fallback
- phase-10 planner strategy ids and plan-family/style outputs
- phase-10 dedicated lane-building gap:
  - `solo` and `many_only` still reuse generalized lane building today
- phase-11 spell-static handoff into `CreationContextBuilder`
- `CreationContext` as the thin runtime binder over the two emitted executor doors
- remaining generalized route-wrapper ownership split between phase 11 and
  `creation_context_codegen.py`
- which final route decisions are runtime policy and which can move into
  phase-11 output
- solo family route variants:
  - `existing_creation`
  - `many`
  - `unique_per_conduit`
  - `spellspace`
  - `shared`

## Unknowns
- UNKNOWN: whether `many_only` should later split by disposal posture into
  distinct candidate style ids.
  Why it matters: disposal pressure may justify a tighter family/style split
  later even when the whole visible spell set is `Existence.many`.
  Next step: decide after the first `solo` / `many_only` planner and creation
  families are implemented and benchmarked.

## Optional Reads
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_codegen_creation_strategy.py`

## Exclusions
- phase-11 family implementation details for `solo` and `many_only`
- runtime emitter changes beyond the current `SpellCodegenCreation` seam
- unrelated cache, mutation, or DevOps lanes

## Reread Order
1. `tickets/stories/2026-06-06_phase10_solo_and_many_only_discovery_story.md`
2. `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
3. `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
4. `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`
5. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py`
6. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py`
7. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py`
8. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py`
9. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py`
10. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py`
11. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
12. `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
13. `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
14. `src/melder/aether/conduit/meld/creation_context/creation_context.py`
15. `src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py`
16. `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py`
17. `src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py`
18. `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py`
19. `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py`
20. `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py`
21. `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py`
22. `src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py`
23. `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
24. `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py`
25. `src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py`
26. `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py`
27. `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py`
28. `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py`
29. `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
30. `artifacts/2026-05-30_phase12_north_star_runtime_model.md`
31. `artifacts/2026-06-02_topdown_compiler_exploration_strategy.md`

## Notes
- Keep this pack focused on phase-8/9 producer truth and phase-10 category
  selection.
- This pack exists because the story now requires context management before
  implementation/validation.
- The reread pack is intentionally wider now because the active `solo` and
  `many_only` lane depends on the phase-4-to-7 compiler foundations and the
  already-thin `CreationContextBuilder -> CreationContext` runtime seam, not
  only on the newer phase-8/9/10 surfaces.
- The immediate implementation gap is now explicit: the category strategies
  exist, but real solo and many-only lane builders do not.
- The first solo-family study shows that solo is one visible spell across 5
  runtime route families, not one generic runtime route.
- The solo implementation is now the active phase-11 family under study, so
  the solo-owned strategy, steps, and compilers are part of the required
  reread pack for safe continuation.
- The current extraction target is broader than solo now. The generalized
  finalizer plus generalized no-overrides/overrides compilers are part of the
  required reread pack because the final route-wrapper ownership is still split
  across those files and `creation_context_codegen.py`.
