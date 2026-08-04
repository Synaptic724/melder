Completed: 2026-06-20T15:28:05Z
Summary: Phase-11 codegen-creation regrouped into discovery-selected family
  strategies (solo / many_only / generalized) with per-family typed build-state
  objects and ordered internal steps; manifest-first lazy-door creation and
  per-family caches landed. Verified present in current src graph
  (codegen_creation_system discovery + strategies/{solo,many_only,generalized}).
  Closed per user direction (mutation-program cleanup pass).

# Epic: Group Codegen Creation Into Family Strategies

## Metadata
- Epic ID: EPIC-2026-06-01-group-codegen-creation-into-family-strategies
- Status: in_progress
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-01T11:41:02Z
- Updated: 2026-06-03T00:01:26Z
- Target Window: 2026-Q2
- Related Program/Initiative: phase11 codegen creation strategy decomposition

## Problem / Opportunity
The live phase-8-to-phase-11 compiler seam is now real, but phase 11 still has
one architectural mismatch compared to phases 8-10.

Current state:
- phase 8 is a thin live wrapper over `SpellAnalyzer`
- phase 9 is a thin live wrapper over `SpellArtifactProcessor`
- phase 10 is a thin live wrapper over `SpellCodegenPlanner`
- phase 11 is a thin live wrapper over `CodegenCreationSystem`

The phase-11 facade exists, but the codegen-creation seam still couples
discovery to internal generalized lane plumbing:
- `CodegenPlanDiscoverySystem` selects one top-level family strategy id
  (`generalized_codegen_plan`)
- `CodegenCreationDiscoverySystem` selects the ordered internal chain directly:
  - `generalized_creation_context_setup_codegen_creation`
  - `generalized_no_overrides_codegen_creation`
  - `generalized_overrides_codegen_creation`
  - `generalized_mutation_overrides_codegen_creation`

That means discovery is still choosing implementation details instead of
choosing a creation family.

The opportunity is to make phase 11 match the cleaner discovery/orchestration
pattern already used by phase 10 without forcing everything through one fake
wrapper strategy:
- discovery selects the right grouped strategy set to execute
- `CodegenCreationSystem` stays the facade/orchestrator
- builder resolves the concrete strategies in that group
- the ordered group builds `SpellCodegenCreation`
- future creation groups can compete at the discovery layer without exposing
  raw implementation plumbing everywhere

## Context
The compiler migration already moved ownership to:
- analyzer -> `_occurrence_graph_analysis`
- processor -> `_spell_codegen_model`
- planner -> `_spell_codegen_plan`
- codegen creation -> `_spell_codegen_creation`

`CreationContextBuilder` now consumes `_spell_codegen_creation`, so phase 11 is
the right place to clean up the remaining strategy layering mismatch.

This is not about redoing phases 1-7.
This is specifically about right-sizing the live phase-11 strategy seam after
the generalized creation port landed.

## MRP Alignment (Most Reasonable Product)
The MRP is:
- keep `CompilerPhase11` as the live wrapper
- keep `CodegenCreationSystem` as the facade/orchestrator
- keep `SpellCodegenStrategyBuilder` as the registry owner
- keep grouped-strategy discovery, but make it explicit and first-class
- introduce one transient build-state object in `codegen_creation/` so the
  grouped strategies stop rediscovering and recomputing the same spell-static
  data
- move the current setup/no-overrides/overrides/mutation-overrides sequence to
  operate over that shared build-state object instead of mutating the final
  artifact blindly

The MRP is not:
- rewriting planner
- deleting `CreationContext`
- inventing ranking experiments for codegen creation yet
- widening into a large runtime redesign

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a new epic and an investigation of
  phases 8-11 with emphasis on further decomposing phase-11 codegen creation
  into grouped strategies behind the facade.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation/`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/completed/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md`
  - `tickets/epics/completed/2026-05-31_substitute_new_compiler_systems_into_live_phase8_to_phase11_epic.md`
  - `tickets/epics/completed/2026-05-31_port_phase13_and_creation_context_into_codegen_creation_strategies_epic.md`
- EXIT_GATE:
  - the phase-11 mismatch is documented clearly
  - the target grouped family-strategy architecture is explicit
  - the first bounded implementation order is explicit
  - the board routes to this epic cleanly
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the user wants discovery to
  keep returning internal grouped steps instead of family strategies.

## Goals (Outcomes)
- Make phase 11 mirror the cleaner grouped-strategy selection shape already
  implied by the rest of the compiler.
- Make grouped-strategy discovery explicit instead of half-implicit.
- Introduce one transient build-state object for grouped phase-11 execution.
- Reduce duplicated spell-static route packaging across the generalized
  override lanes.
- Keep future codegen-creation experimentation open without overcoupling
  discovery to internal plumbing.

## Non-Goals (Explicit Exclusions)
- No phase-8 analyzer redesign.
- No phase-9 processor redesign.
- No phase-10 planner redesign in this epic.
- No `CreationContext` deletion in this epic.
- No codegen ranking experiments yet.
- No mutation-research or mediator-system redesign in this epic.

## Scope Boundaries
- In scope:
  - investigate live phases 8-11 as they exist now
  - formalize the grouped phase-11 strategy seam
  - define the grouped discovery contract
  - define the transient build-state object
  - define provenance fields needed on `SpellCodegenCreation`
  - define the first helper/module splits for the oversized compiler helpers
- Out of scope:
  - changing runtime override semantics
  - changing planner lane semantics
  - changing phases 1-7

## Requirements
- `CompilerPhase11` must stay a thin wrapper over `CodegenCreationSystem`.
- `CodegenCreationSystem` must stay a facade over:
  - discovery
  - builder
  - ordered strategy execution
- discovery should return a grouped selection contract, not a raw accidental
  plumbing leak.
- the generalized grouped chain must stay deterministic.
- grouped strategies should receive one shared transient build-state object.
- `SpellCodegenCreation` should remain the final artifact-owned handoff, not
  become the scratchpad for every intermediate derivation and cache.
- `SpellCodegenCreation` should preserve enough provenance to show:
  - selected strategy group
  - executed strategies

## Acceptance Criteria
- A source-backed investigation explains why phase 11 is currently less clean
  than phases 8-10.
- The epic defines one grouped discovery/build-state contract clearly enough to
  implement without guessing.
- The grouped generalized sub-strategies are named and ordered.
- The main duplication seams and helper-module split candidates are explicit.
- The board routes active compiler strategy work to this epic.

## Risks / Mitigations
- Risk: overflattening could hide useful grouped-strategy provenance.
  - Mitigation: keep selected group and executed strategy ids distinct.
- Risk: discovery and builder responsibilities could blur again.
  - Mitigation: keep discovery on grouped selection only; keep orchestration in
    `CodegenCreationSystem`.
- Risk: moving transient derivation fields onto `SpellCodegenCreation` could
  turn the final artifact into a scratch object.
  - Mitigation: use a separate transient build-state object in the
    `codegen_creation` package.

## Validation Plan
- Not run.
- Investigation-only slice.
- Validation for this epic is source-backed architectural coherence, not test
  execution yet.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to create an epic and
  investigate how phases 8-11, especially phase 11 codegen creation, should be
  regrouped into cleaner family strategies.

## Architecture Decision
### Phases 8-10
- keep their current shape
- wrappers stay thin
- discovery selects one family strategy id
- family strategy owns the real work

### Phase 11
Current mismatch:
- discovery returns the internal generalized execution chain directly
- strategies share no explicit transient build state
- override and mutation strategies duplicate route-config packaging almost
  verbatim

Target shape:
- discovery returns a grouped selection result, for example:
  - `selected_strategy_group_id`
  - `selected_strategy_ids`
  - `discovery_reason`
- builder resolves `selected_strategy_ids`
- `CodegenCreationSystem` executes the ordered group
- the grouped generalized sequence stays:
  1. creation-context setup
  2. no-overrides creation
  3. overrides creation
  4. mutation-overrides creation
- the grouped strategies operate over one shared transient build-state object

### Top-Level Output Convergence
Current transition shape still models 3 top-level runtime creation families:
- `no_overrides_creation`
- `overrides_creation`
- `mutation_overrides_creation`

The cleaner target is 2:
- `no_overrides_creation`
- `override_creation`

Mutation-aware behavior still matters, but once mutation-capable sockets are
modeled as late-bound holes, mutation should be an upstream
contract/revalidation/build concern. Phase 11 should then simply build the
correct `override_creation` for the current spell state instead of preserving
`mutation_overrides_creation` as a permanent third top-level family.

### Build-State Object
Recommended direction:
- add something like `SpellCodegenCreationBuildState` under
  `codegen_creation/`
- inputs:
  - `spell_codegen_model`
  - `spell_codegen_plan`
  - `spell_codegen_creation`
- shared derived fields:
  - `resolve_route_key`
  - `path_registry`
  - `no_overrides_plan`
  - `overrides_plan`
  - `mutation_overrides_plan`
  - `override_targeting_shape`
  - `override_targeting_creation`
  - `overrides_steps_rows`
  - `mutation_steps_rows`
  - `overrides_spell_lookup`
  - `mutation_spell_lookup`
  - `overrides_plan_signature`
  - `mutation_plan_signature`
- purpose:
  - stop recomputing identical spell-static route packaging in multiple
    strategies
  - keep scratch/build state out of the final artifact surface

### Provenance
Recommended `SpellCodegenCreation` direction:
- keep one top-level selected strategy-group field or metadata entry
- keep one ordered executed-strategy field or metadata entry

That preserves observability without leaking the internal sequence into
discovery.

## Initial Implementation Order
1. Change `CodegenCreationDiscoverySystem` to return an explicit grouped
   selection contract:
   - `selected_strategy_group_id`
   - `selected_strategy_ids`
   - `discovery_reason`
2. Introduce `SpellCodegenCreationBuildState` and make
   `CodegenCreationSystem` construct it once per build.
3. Refactor the current four generalized strategies to consume that build
   state.
4. Extract one shared override-route packaging helper/state path used by both
   generalized override strategies.
5. Collapse the top-level runtime output contract to the 2-family target once
   the mutation contract semantics are corrected.
6. Split the oversized compiler helper modules by responsibility after the
   strategy/build-state seam is stable.

## Applicable Anti-Patterns
- [ ] Do not keep discovery as a raw implementation-chain dump forever.
- [ ] Do not let the phase-11 facade absorb implementation details.
- [ ] Do not turn `SpellCodegenCreation` into a scratch/build-state bag.
- [ ] Do not widen into runtime redesign while investigating strategy shape.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Noting Behavior
- Epic notes should capture:
  - source-backed phase-8-to-phase-11 shape findings
  - strategy-family vs sub-strategy separation decisions
  - bounded implementation order only

## Notes
- DATETIME: 2026-06-01T11:41:02Z
  TYPE: FACT
  CLAIM: The live phase-8-to-phase-11 wrappers are all real facades, but phase
    11 still differs architecturally from phase 10. Planner discovery selects
    one top-level strategy id (`generalized_codegen_plan`), while codegen
    creation discovery still selects the ordered generalized implementation
    chain directly. The generalized codegen-creation sub-strategies already
    exist as separate units, which means the regrouping seam is now explicit.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-89
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:20-126
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:40-73
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:21-112
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:20-56
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:15-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:26-117
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_overrides_codegen_creation_strategy.py:32-195
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:29-174
  IMPACT: The next clean compiler-design slice is not more lane logic. It is
    regrouping phase 11 so discovery selects the grouped execution set
    intentionally instead of leaking internal plumbing directly.
  NEXT: define the grouped discovery contract and the transient build-state
    object that the current four generalized creation strategies should share.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-01T11:41:02Z
  TYPE: FACT
  CLAIM: The real sprawl is not the wrapper files; it is the phase-11 creation
    internals. The strategy files are moderate in size, but the two compiler
    helper modules are very large (`1755` LOC no-overrides, `2869` LOC
    overrides), the overrides compiler repeats the same argument bundle across
    multiple entrypoints, and the generalized override + mutation strategies
    duplicate route-config packaging almost verbatim.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_no_overrides_codegen_creation_compiler.py:57-1875
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_overrides_codegen_creation_compiler.py:22-2979
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_overrides_codegen_creation_strategy.py:51-220
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:51-203
  IMPACT: The next upgrade should introduce one transient build-state object
    and one shared override-route packaging seam before we try to split the
    giant compiler modules. Otherwise we just move duplication around.
  NEXT: define `SpellCodegenCreationBuildState` and extract the shared
    override-route package derivation used by the two generalized override
    strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-02T23:52:23Z
  TYPE: DECISION
  CLAIM: The next investigation slice for this epic will widen from the live
    phase-8-to-phase-11 seam to the full phase-1-to-phase-11 compiler chain
    plus the runtime consumer surfaces `meld`, `creations`, and
    `creation_context`. The reason is architectural, not procedural: phase 11
    produces `_spell_codegen_creation`, and the quality of the grouped
    phase-11 seam depends on understanding what phases 1-10 guarantee before
    that handoff and how runtime execution consumes it afterward.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md:15-22
  - codex/context_compass/tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md:52-54
  - codex/context_compass/tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md:181-181
  IMPACT: This keeps the work in the same routed compiler-strategy lane while
    making the investigation broad enough to prove whether phase-11 grouping
    can rely on existing upstream artifacts or needs upstream contract
    tightening.
  NEXT: read phases 1-11, then trace the artifact handoff through
    `CreationContextBuilder`, `CreationContext`, `Meld`, and `Creations`
    before proposing the grouped-discovery and build-state contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T00:14:04Z
  TYPE: DECISION
  CLAIM: The phase-11 top-level runtime contract should converge to only 2
    output families: `no_overrides_creation` and `override_creation`.
    Mutation-aware behavior still matters, but once mutation-capable sockets
    are treated as late-bound holes, mutation should affect upstream contract
    resolution and build selection rather than remain a permanent third
    top-level runtime output family.
  EVIDENCE:
  - tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py:1-437
  - codex/context_compass/tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md:1-260
  IMPACT: This removes one unnecessary top-level output family from the target
    phase-11 model and simplifies later specialization work.
  NEXT: keep grouped-strategy and build-state work aligned to the 2-output
    target while the mutation contract epic corrects the upstream semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-02T23:56:38Z
  TYPE: FACT
  CLAIM: The front-side compiler layering is now explicit. `SpellCompilerSystem`
    is the spell-facing orchestration surface that owns the reusable
    `SpellCompiler` and `SpellValidationSystem`, while `SpellCompilerArtifact`
    holds the spell-scoped mutable build state. Inside that split, phases 8-11
    are intentionally thin substitution facades over analyzer, processor,
    planner, and codegen-creation systems. The important boundary is that phase
    11 stops at producing `_spell_codegen_creation`; runtime execution and
    override specialization are downstream concerns for `CreationContext*` and
    `Meld`, not compiler-phase work.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:1-790
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:1-626
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:1-368
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-100
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-74
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-87
  IMPACT: The grouped phase-11 redesign should stay inside compiler-owned
    spell-static packaging boundaries. If a problem only appears once
    `_spell_codegen_creation` reaches `CreationContextBuilder` or `Meld`, that
    is a runtime-consumer contract issue, not a reason to collapse compiler and
    runtime responsibilities back together.
  NEXT: read the deep objects behind phases 1-11, then trace how
    `CreationContextBuilder`, `CreationContext`, `Meld`, and `Creations`
    consume the phase-11 handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-02T23:58:35Z
  TYPE: FACT
  CLAIM: Phases 1-4 are a strict structural pipeline with a deliberate
    boundary between symbolic intent and concrete dependency wiring. Phase 1
    classifies parameters into `ParameterDIShape` and emits
    `SpellRequirements`; phase 2 preserves every constructor socket as symbolic
    metadata, including plain parameters and contract sockets; phase 3 resolves
    only normal DI shapes into the local DAG and `SpellLocalTopology`, while
    leaving `SpellContract` and `MutationContract` sockets as topology-visible
    metadata only; phase 4 then validates those structural artifacts and pushes
    structural validity plus `contract_unvalidated` gating back into
    `SpellSystemStates`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:1-42
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py:1-252
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements.py:1-232
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1-1080
  - src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py:1-217
  - src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_graph.py:1-111
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:1-161
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1-674
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:1-157
  IMPACT: Phase-11 regrouping cannot assume that contract sockets or plain
    overrides were ever resolved into concrete dependency edges upstream. The
    compiler only has concrete spell wiring for normal DI sockets by the end
    of phase 3; everything else remains symbolic or gated until later runtime
    and contract machinery participates.
  NEXT: read the phase-5-to-phase-7 rooted-system objects, then the
    phase-8-to-phase-11 analyzer/processor/planner/codegen-creation objects,
    before tracing runtime consumption through `CreationContext*`, `Meld`, and
    `Creations`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-02T23:59:35Z
  TYPE: FACT
  CLAIM: Phases 5-7 form a separate rooted-system layer above the local
    structural artifacts. Phase 5 lifts `SpellSystemStates` into a
    frame-visible adjacency snapshot, filters that snapshot to the current
    spellbook, builds rooted deep DAG blueprints plus a frame-level
    `SpellSystemIndex`, and overlays socket refs plus a `DagIndex` for later
    targeting. Phase 6 then runs an ordered system-validation strategy set over
    those rooted artifacts and writes conduit-scoped validity/diagnostics back
    into `SpellSystemStates`. Phase 7 does not add new graph truth at all; it
    only rebuilds or upserts change-control component-of mappings and installs
    the dirty-root revalidator hook that re-enters `run_all_phases(...)`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/root_resolution_blueprint.py:1-239
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_builder.py:1-76
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_snapshot.py:1-127
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_index.py:1-133
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_node.py:1-130
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:1-431
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:1-236
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_state.py:1-83
  - src/melder/aether/spellbook/spell_compiler/system/system_diagnostic.py:1-146
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:1-615
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:1-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:1-235
  IMPACT: The phase-11 regrouping work is downstream of a rooted-system layer
    that is already explicit and conduit-scoped. If the grouped phase-11 seam
    needs new invariants, they likely belong either in phase-5 artifact shape
    or in phase-6 validation, not in the phase-7 change-control bridge.
  NEXT: read the phase-8-to-phase-11 analyzer/processor/planner/codegen
    objects and then trace the runtime consumption path through
    `CreationContext*`, `Meld`, and `Creations`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-03T00:01:26Z
  TYPE: FACT
  CLAIM: The live phase-8-to-phase-9 pipeline is not building one opaque
    intermediate artifact. The analyzer owns the path-aware occurrence graph:
    it expands rooted blueprint structure, applies topology-first dependency
    discovery with DAG fallback, inserts SpellContract provider edges, and
    rewrites mutation edges on top of that graph. The processor then converts
    that graph into a sectioned `SpellCodegenModel`: execution order,
    instance/sharedness, contract payload routing, runtime spell facts,
    injection wiring, and override or mutation targeting are all separate
    fitted sections with their own summary metrics.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-122
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy.py:1-77
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy_builder.py:1-110
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_graph_analysis.py:1-69
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-1207
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-156
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-310
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-143
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:1-87
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_occurrence_order_analysis.py:1-34
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_occurrence_instance_analysis.py:1-59
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_occurrence_contract_analysis.py:1-53
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_override_targeting_analysis.py:1-115
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_mutation_targeting_analysis.py:1-98
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:1-165
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:1-103
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:1-149
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:1-191
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:1-373
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:1-154
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_mutation_targeting_processor_strategy.py:1-164
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:1-204
  IMPACT: Phase-11 regrouping should build on a model that is already
    sectioned by responsibility. If phase 11 still feels tangled, the fix is
    probably in how codegen creation consumes these model sections, not in
    collapsing analyzer and processor back into one phase artifact.
  NEXT: read planner and codegen-creation objects, especially the generalized
    lane plan, discovery systems, and the large no-overrides and overrides
    codegen compilers, then trace runtime consumption through
    `CreationContext*`, `Meld`, and `Creations`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The current investigation shows that phases 8-10 already follow the cleaner
facade pattern, while phase 11 still exposes internal generalized creation
steps at the discovery boundary and lacks a shared transient build-state
object. This epic exists to regroup phase 11 so discovery selects the grouped
strategy set intentionally and the grouped strategies share typed spell-static
build state instead of rediscovering it.
