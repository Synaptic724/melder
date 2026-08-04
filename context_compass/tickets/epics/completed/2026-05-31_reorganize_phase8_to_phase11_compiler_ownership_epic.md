# Epic: Reorganize Phase 8 To Phase 11 Compiler Ownership

## Metadata
- Epic ID: EPIC-2026-05-31-reorganize-phase8-to-phase11-compiler-ownership
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-05-31T13:49:04Z
- Updated: 2026-06-01T11:05:49Z
- Target Window: 2026-Q2
- Related Program/Initiative: Right-size execution strategy compiler outputs

## Problem / Opportunity
The current Phase 8 to Phase 11 rework is structurally closer than it was, but
the ownership boundaries are still wrong.

Current state:
- the occurrence analyzer now owns the 4 real occurrence seams directly
- but order, instance/sharedness, and contract payload routing are still living
  in the analyzer lane even though they are consumers of graph truth
- Phase 9 injection planning and Phase 10 patch targeting are still old
  compiler-phase outputs instead of processor-owned concrete derived artifacts
- the current processor still reads late Phase 11 outputs directly
- the current planner still emits one summary plan object instead of owning the
  3 real runtime/codegen plan variants already present in current Phase 11

The opportunity is to reorganize the compiler around clean ownership:
- analyzer builds primary graph truth
- processor owns derived concrete artifacts
- planner owns planning outcomes
- Phase 13 becomes a pure backend emitter over planner output

## MRP Alignment (Most Reasonable Product)
The MRP is not a whole compiler rewrite in one pass.

It is:
- keep the current code working while we reorganize ownership
- move outputs one ownership layer at a time
- keep each prompt bounded to one coherent slice
- preserve compatibility outputs until downstream consumers are converted

That gives us a sane staged migration instead of another fake rename or proxy
layer.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a proper epic that defines the
  architecture and a bounded implementation order so future prompts do not
  sprawl.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/tickets/tasks/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `tickets/tasks/2026-05-30_scaffold_phase12_artifact_processor_and_codegen_plan_task.md`
  - `tickets/tasks/2026-05-30_define_execution_strategy_phase12_task.md`
- EXIT_GATE:
  - analyzer/processor/planner ownership is explicitly defined for Phase 8-11
  - one bounded implementation order exists
  - the 3 runtime/codegen planner outputs are explicit
  - compatibility seams are called out so later prompts can stay narrow
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one slice reveals that a
  downstream consumer cannot be moved without breaking the agreed layered
  ownership model.

## Goals (Outcomes)
- Keep only primary occurrence graph truth in the analyzer lane.
- Move occurrence-derived consumers out of analyzer and into processor-owned
  artifacts where appropriate.
- Treat Phase 9 and Phase 10 as processor-owned concrete artifact generation,
  not planner outputs.
- Treat current Phase 11 logic as planner-owned outcome generation.
- Make planner output the 3 real variants explicitly:
  - no-overrides
  - overrides
  - mutation-overrides
- Keep Phase 13 narrow as the backend emitter over chosen planner outputs.

## Non-Goals (Explicit Exclusions)
- No broad runtime rewrite in this epic.
- No CreationContext rewrite in the same pass.
- No scheduler redesign.
- No fake abstraction layers that just proxy old builder methods under new
  names.
- No patch-doc lane in this epic unless the user explicitly asks for one.

## Scope Boundaries
- In scope:
  - ownership reorganization for Phase 8-11 outputs
  - analyzer / processor / planner boundaries
  - compatibility-output decisions for `OccurrencePlan`
  - bounded implementation order for later slices
- Out of scope:
  - final emitter redesign beyond boundary clarification
  - meld / creation-context consumer replacement in this epic
  - broad Phase 1-7 compiler changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a proper umbrella epic so
  future prompts stay bounded and stop drifting.

## Ownership Model
### Analyzer
- owns primary occurrence graph truth only
- facade should stay thin and deterministic
- graph output remains analyzer-owned

### Artifact Processor
- owns concrete derived artifacts built from upstream truth
- occurrence order belongs here
- occurrence instance/sharedness belongs here
- occurrence contract payload routing/completeness belongs here
- Phase 9 injection plan belongs here
- Phase 10 override/mutation patch targeting belongs here
- processor should output a processor-owned model surface built from those
  concrete artifacts

### Codegen Planner
- owns all planning outcomes
- consumes processor outputs and emits the 3 runtime/codegen plans:
  - no-overrides plan
  - overrides plan
  - mutation-overrides plan
- planner should be the home of current Phase 11 planning logic

### Phase 13
- backend emitter only
- should consume chosen planner outputs and emit final runtime/codegen lanes

## Proposed Implementation Order
1. Keep the current occurrence graph in analyzer and leave it as the only
   analyzer-owned occurrence artifact family.
2. Assess whether order / instance / contract outputs should move from analyzer
   to processor or remain temporarily mirrored for compatibility.
3. Introduce processor-owned occurrence-derived artifact slots on
   `SpellCompilerArtifact`.
4. Migrate occurrence order into processor-owned output.
5. Migrate occurrence instance/sharedness into processor-owned output.
6. Migrate occurrence contract payload routing into processor-owned output.
7. Re-home Phase 9 injection-plan ownership under processor.
8. Re-home Phase 10 patch-map ownership under processor.
9. Refactor `SpellCodegenModel` so it consumes processor outputs instead of
   late Phase 11 output directly.
10. Move current Phase 11 execution-plan build logic into planner-owned
    orchestration and expose the 3 explicit planner outputs.
11. Decide whether `OccurrencePlan`, `InjectionPlan`, and patch maps remain
    compatibility artifacts or become synthesized output layers during the
    transition.

## Milestones
- [ ] Milestone 1: analyzer / processor / planner ownership map is explicit
- [ ] Milestone 2: processor owns occurrence-derived artifacts
- [ ] Milestone 3: processor owns Phase 9 and Phase 10 concrete artifacts
- [ ] Milestone 4: planner owns the 3 runtime/codegen plans
- [ ] Milestone 5: Phase 12 orchestration is clean analyzer -> processor ->
      planner instead of late Phase 11/CreationContext dependency leakage

## Stories (Required to Complete)
- [ ] Story: define the compatibility role of `OccurrencePlan`
- [ ] Story: move occurrence-derived outputs under processor ownership
- [ ] Story: move Phase 9 injection-plan ownership under processor
- [ ] Story: move Phase 10 patch-targeting ownership under processor
- [ ] Story: refactor `SpellCodegenModel` to consume processor outputs only
- [ ] Story: move current Phase 11 logic into planner-owned output generation
- [ ] Story: expose the 3 explicit planner outputs and keep Phase 13 as emitter

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: keep current lanes working while ownership moves
- [ ] Task: avoid fake proxy/shim layers during the reorganization
- [ ] Task: keep future prompts scoped to one bounded ownership slice at a time
- [ ] Task: record each compatibility seam before changing downstream consumers

## Acceptance Criteria (Epic Done)
- The ownership map is explicit and reflected in code.
- Analyzer is thin and owns only primary occurrence graph truth.
- Processor owns derived concrete artifacts from occurrence / injection / patch
  truth.
- Planner owns the 3 runtime/codegen planning outputs.
- Phase 13 is reduced to backend-emitter role over planner output.
- The implementation order is explicit enough that future prompts can take one
  bounded slice at a time without drifting.

## Risks / Mitigations
- Risk: ownership reorg drifts into a whole compiler rewrite.
  - Mitigation: keep each later prompt to one ownership seam only.
- Risk: compatibility artifacts linger forever and keep the architecture muddy.
  - Mitigation: record each compatibility seam explicitly and choose the next
    downstream consumer deliberately.
- Risk: analyzer/processor boundaries get blurred again.
  - Mitigation: keep analyzer outputs primary and processor outputs derived.

## Implementation Steps
### Step 1
- create this umbrella epic and route active work to it

### Step 2
- keep analyzer graph truth stable
- assess whether order / instance / contract should migrate into processor

### Step 3
- add processor-owned occurrence-derived artifact surfaces

### Step 4
- migrate Phase 9 and Phase 10 ownership into processor

### Step 5
- move current Phase 11 logic into planner and make the 3 planner outputs
  explicit

### Step 6
- assess which compatibility artifacts can be retired next

## Validation / Test Approach
- Architecture and ownership planning only in this epic.
- Future implementation slices can choose narrow syntax or focused unit rings
  when the user wants them.

## Applicable Anti-Patterns
- [ ] No fake proxy migrations
- [ ] No ownership blur between analyzer and processor
- [ ] No planning outputs stranded outside the planner
- [ ] No giant multi-slice implementation passes in one prompt

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-31T20:33:45Z
  TYPE: PLAN
  CLAIM: The next bounded compiler pass is a source reread, not another
    ownership move. The user explicitly asked for Phases 1-13 plus
    `creations.py`, `conduit_creations.py`, `meld.py`, and
    `creation_context.py` to be reloaded together so the new
    analyzer/processor/planner/codegen-creation work stays grounded in the
    live compiler and runtime seams.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:1-134
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:1-222
  - src/melder/aether/conduit/creations/creations.py:1-401
  - src/melder/aether/conduit/creations/conduit_creations.py:1-75
  - src/melder/aether/conduit/meld/meld.py:1-1218
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1253
  IMPACT: This pass should rebuild the practical compiler/runtime mental model
    before any further execution-plan or codegen-creation cutover work.
  NEXT: finish the chunked reread, then summarize the Phase 1-13 and runtime
    seams that matter for the new compiler stack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T20:31:27Z
  TYPE: FACT
  CLAIM: The generalized planner lane now carries the full execution-plan
    builder logic in the new system. `SpellGeneralizedCodegenPlanBuilder`
    ports the old `ExecutionPlanBuilder` semantics into
    `codegen_planner/data/spell_generalized_codegen_lane_plan.py`, including
    step construction, per-spell index maps, fast-plan packing, and
    fast-transient packing. The generalized strategy now delegates to that
    builder for all 3 lanes instead of manually assembling a partial step bag.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1-2059
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-72
  IMPACT: The old `execution_plan.py` logic is now ported into the new
    planner-owned lane builder surface. The remaining migration work is
    downstream consumer cutover, not "execution plan builder still missing."
  NEXT: choose the next seam: switch Phase 13/runtime consumers onto the new
    lane plan objects or add discovery ranking / specialized strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T20:18:49Z
  TYPE: FACT
  CLAIM: The generalized strategy is not yet a full replacement for
    `execution_plan.py`. The remaining legacy parity buckets are explicit:
    `ExecutionPlanStep` completeness, base lane-building parity,
    `fast_plan` packing, `fast_transient_plan` packing, and the later
    overrides/mutation-specific lane semantics. That means the current
    generalized strategy is still an incomplete replacement candidate and the
    old file cannot be deleted yet.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:83-379
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:380-1763
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1764-2059
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-396
  IMPACT: Future planner work must be tracked as explicit execution-plan parity
    slices instead of being described as “ported” before the legacy file is
    actually replaced.
  NEXT: port full `ExecutionPlanStep` and base lane-building parity into the
    generalized planner surfaces as the next real slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T20:07:18Z
  TYPE: FACT
  CLAIM: The generalized planner strategy is now model-native instead of a
    compatibility lift. The processor now fits one additional
    `spell_runtime_shape` section, and the generalized plan strategy builds its
    3 lane payloads from model sections (`graph`, `order`, `instance`,
    `contract`, `runtime`, `injection`, `override_targeting`,
    `mutation_targeting`) rather than lifting old `ExecutionPlan` objects.
    The discovery seam still defaults to `generalized_codegen_plan`, but that
    strategy is now the first real planner-native execution strategy.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:1-89
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:1-117
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-326
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1-184
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-396
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:1-54
  IMPACT: The legacy Phase 11 `ExecutionPlan` is no longer needed as the
    source of truth for the generalized planner output. The new system now has
    a real model-native execution strategy to converge on.
  NEXT: pause here and choose whether the next bounded seam is the first
    non-generalized specialized strategy or discovery ranking logic for
    generalized versus future alternatives.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T19:58:26Z
  TYPE: PLAN
  CLAIM: The next bounded seam is the deep model-native generalized execution
    strategy. One extra model section is required to do it honestly:
    `spell_runtime_shape`. The exact cut is: add processor-owned runtime spell
    facts to the model, add a runtime-shape processor strategy, replace the
    generalized compatibility wrapper with a real model-native generalized
    execution strategy under `codegen_planner/strategies/`, and have that
    strategy build the 3 lane payloads from model sections instead of lifting
    old `ExecutionPlan` objects.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1043-1409
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-310
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-62
  IMPACT: This is the first planner-native replacement of legacy Phase 11
    logic instead of another compatibility lift.
  NEXT: patch the model/runtime section and generalized strategy, then stop
    there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T19:33:12Z
  TYPE: FACT
  CLAIM: The planner discovery seam is now landed correctly. `SpellCodegenPlanner`
    is back to a real facade: it reads the artifact-owned model, asks
    `CodegenPlanDiscoverySystem` for the selected strategy id, resolves that
    strategy through `SpellCodegenPlanStrategyBuilder`, and lets the selected
    strategy populate the generic `SpellCodegenPlan`. The legacy Phase 11 trio
    now lives only inside `SpellGeneralizedCodegenPlanStrategy`, which means
    the old execution-plan surface is a compatibility strategy source instead
    of the planner contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system.py:1-54
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-119
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:1-106
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_generalized_codegen_plan_strategy.py:1-62
  IMPACT: Future planner work can add model-native strategy families without
    changing the planner facade or letting the legacy execution-plan shape
    dictate architecture again.
  NEXT: pause here and choose whether the next planner slice is ranking
    criteria inside discovery or the first non-generalized specialized plan
    strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T19:22:31Z
  TYPE: PLAN
  CLAIM: The next bounded seam is planner discovery plus one compatibility
    strategy. The exact cut is: add `CodegenPlanDiscoverySystem`, add one
    explicit generalized-codegen compatibility strategy that lifts the legacy
    Phase 11 trio into the generic `SpellCodegenPlan` container, register that
    strategy in the planner builder, and make `SpellCodegenPlanner` select it
    through discovery instead of hardcoding legacy packaging in the facade.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-108
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:1-103
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy.py:1-76
  IMPACT: This keeps the old execution-plan trio as one selected compatibility
    strategy instead of letting it remain the planner contract.
  NEXT: patch the discovery system, generalized strategy, planner builder, and
    planner facade, then stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T19:12:08Z
  TYPE: DECISION
  CLAIM: The legacy Phase 11 trio must not remain the planner contract. The
    generic artifact-owned `spell_codegen_model` / `spell_codegen_plan`
    surfaces stay, but the planner packaging cut is now explicitly downgraded
    to a transitional mistake rather than target architecture. The next
    correction is to decouple `SpellCodegenPlanner` from direct legacy
    `ExecutionPlan` packaging and return the plan container to a neutral
    strategy-owned output surface.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-108
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-78
  IMPACT: This preserves the generic new-system contract without letting the
    old execution-plan object shape dictate planner architecture.
  NEXT: patch the planner so it stops packaging legacy Phase 11 variants into
    `SpellCodegenPlan`, then stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T18:58:03Z
  TYPE: FACT
  CLAIM: The planner packaging seam is now landed. `SpellCodegenPlanner`
    reads the artifact-owned `spell_codegen_model`, packages the 3 legacy Phase
    11 execution-plan variants into the generic `SpellCodegenPlan` container
    (`no_overrides_plan`, `overrides_plan`, `mutation_overrides_plan`), and
    publishes that container back onto `SpellCompilerArtifact`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-108
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-78
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:102-123
  IMPACT: The old Phase 11 trio now has a planner-owned home in the new stack,
    so later planner strategy work can replace or reshape those lane payloads
    without changing the artifact contract again.
  NEXT: pause here and choose whether the next seam is planner strategy
    population or deeper execution-fact normalization ahead of that work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T18:52:14Z
  TYPE: PLAN
  CLAIM: The next bounded seam is planner packaging over the existing legacy
    execution-plan variants. The exact cut is: make `SpellCodegenPlanner`
    package the 3 current Phase 11 variants into the generic
    `SpellCodegenPlan` container (`no_overrides_plan`, `overrides_plan`,
    `mutation_overrides_plan`) and publish that container on the
    `SpellCompilerArtifact`. This slice uses the old Phase 11 plans as
    migration-oracle planner truth and does not widen into new planner strategy
    families yet.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:777-822
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:102-123
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-78
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-102
  IMPACT: This moves the legacy execution-plan trio one layer up into the new
    planner-owned container without pretending the real planner strategy layer
    is already finished.
  NEXT: patch the planner to package the 3 legacy execution plans into the
    artifact-owned `SpellCodegenPlan`, then stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T18:36:54Z
  TYPE: FACT
  CLAIM: The Phase 10 patch-targeting seam is now processor-owned in the new
    stack. The model now has `override_targeting_shape` and
    `mutation_targeting_shape` sections, processor-owned targeting data classes
    exist for both lanes, and 2 new processor strategies derive override and
    mutation targeting directly from the rooted blueprint instead of reading old
    `OverridePatchMap` or `MutationPatchMap` objects. Processor strategy
    registration order now runs: occurrence sections -> injection ->
    override targeting -> mutation targeting.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-310
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_override_targeting_analysis.py:1-131
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_mutation_targeting_analysis.py:1-102
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:1-172
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_mutation_targeting_processor_strategy.py:1-171
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-137
  IMPACT: The new processor path now owns occurrence, injection, and patch
    targeting truth without leaning on old Phase 8/9/10 plan objects in the
    fitted model path. The next clean seam is the legacy execution-plan layer.
  NEXT: pause here and choose whether the next bounded seam is the execution
    plan transition into planner-owned output or a narrower pre-planner model
    refinement around execution facts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T18:22:47Z
  TYPE: PLAN
  CLAIM: The next bounded seam is Phase 10 patch targeting only. The exact cut
    is: add processor-owned patch-targeting section homes to
    `SpellCodegenModel`, introduce processor data classes for override and
    mutation targeting, port old Phase 10 patch-map truth into processor
    strategy objects, and update the processor builder ordering so those
    strategies run after injection. No execution-plan or planner-lane work is
    part of this slice.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py:1-1018
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-216
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-252
  IMPACT: This keeps the migration order honest: Phase 10 becomes
    processor-owned before we touch legacy execution-plan truth.
  NEXT: patch the model, add patch-targeting data/strategies, wire them into
    the processor builder, and stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T18:11:08Z
  TYPE: FACT
  CLAIM: The injection seam is now processor-owned in the new stack. The model
    now has an `injection_shape` section, the processor owns new injection data
    classes (`SpellInjectionParamSource`, `SpellInjectionInstanceSpec`,
    `SpellInjectionAnalysis`), and `SpellInjectionProcessorStrategy` now fits
    per-instance injection specs directly from `graph_shape`, `instance_shape`,
    and `contract_shape` without touching old `InjectionPlan` objects.
    Processor strategy registration order is now explicit insertion order, so
    the injection strategy runs after the occurrence-derived sections it
    depends on.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:1-184
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:1-205
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-252
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-127
  IMPACT: The new processor path no longer depends on legacy Phase 9 objects to
    understand injection wiring, so the next migration seam can move to patch
    maps or later planner-facing execution truth without reopening this same
    injection adapter problem.
  NEXT: pause here and choose whether the next bounded seam is patch maps or
    the later execution-plan/planner transition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T17:55:06Z
  TYPE: PLAN
  CLAIM: The next bounded seam is injection-only. The exact cut is: add one
    `injection_shape` section to `SpellCodegenModel`, introduce processor-owned
    injection data objects under `artifact_processor/data`, implement one real
    injection processor strategy that fits injection specs directly from
    `graph_shape`, `instance_shape`, and `contract_shape`, and register that
    strategy after the occurrence-derived section strategies. No old
    `InjectionPlan` objects should be referenced in the new processor path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:1-591
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-209
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1061-1409
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-240
  IMPACT: This keeps the migration order clean: injection moves into processor
    before execution-plan work moves into planner.
  NEXT: patch the model, add injection data objects and strategy, wire the
    strategy into the processor builder, and stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T17:43:31Z
  TYPE: FACT
  CLAIM: The model/plan ownership contract is now artifact-owned and generic.
    `SpellCompilerArtifact` now stores `_spell_codegen_model` and
    `_spell_codegen_plan`; the processor publishes the fitted model onto the
    artifact instead of returning it; the planner reads the artifact-owned
    model and publishes the plan back onto the artifact; and
    `SpellCodegenPlan` is now the neutral 3-lane container
    (`no_overrides_plan`, `overrides_plan`, `mutation_overrides_plan`) rather
    than the old overfit family bag.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:1-198
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:266-337
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:519-549
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-110
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-78
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-102
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-81
  IMPACT: Analyzer, processor, and planner now all converge back onto one
    compiler-owned artifact surface instead of returning transient objects
    through mismatched facade contracts.
  NEXT: pause here and choose whether the next bounded slice is planner
    strategy population or processor-owned Phase 9/10 model sections.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T17:28:19Z
  TYPE: FACT
  CLAIM: The processor model cut is now landed. `SpellCodegenModel` is
    section-first around `graph_shape`, `order_shape`, `instance_shape`, and
    `contract_shape`; the fake `occurrence_shape_profile` path is gone; the 3
    occurrence processor strategies now fit those model sections directly; and
    `SpellArtifactProcessor` is reduced to shell-model creation plus
    analyzer-graph handoff before strategy execution.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-240
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-164
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy.py:1-77
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:1-163
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:1-199
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:1-328
  IMPACT: The processor is no longer acting like an adapter over old
    occurrence-plan shape summaries. The next real step can focus on either
    phase 9/10 processor-owned sections or later planner strategy work without
    reopening this same facade/model argument.
  NEXT: pause here and review whether the next slice should add processor-owned
    phase 9/10 model sections or start carving the planner's real strategy
    layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T17:13:51Z
  TYPE: PLAN
  CLAIM: The next bounded implementation slice is processor-only model
    restructuring. The exact cut is: reshape `SpellCodegenModel` around the
    4 occurrence-derived section homes (`graph_shape`, `order_shape`,
    `instance_shape`, `contract_shape`), remove
    `occurrence_shape_profile`, make the 3 processor strategies populate those
    sections directly, and strip `SpellArtifactProcessor` down to shell-model
    creation plus analyzer graph handoff only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-283
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-374
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:1-141
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:1-204
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:1-367
  IMPACT: This removes the processor-side adapter posture without widening
    into planner or phase 9/10 ownership migration yet.
  NEXT: patch the model, processor facade, and the 3 occurrence processor
    strategies, then stop without tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T17:02:44Z
  TYPE: FACT
  CLAIM: The requested `attention_board.md` trim is now applied to the stale
    detail/history surfaces, not to the active routing table. Old active
    attention-detail blocks older than 2026-05-29 and old closed anchors are
    removed, but stale active-item rows remain because deleting them would
    orphan still-routed tickets without first resolving ticket state.
  EVIDENCE:
  - codex/context_compass/attention_board.md:84-234
  - codex/context_compass/attention_board.md:235-240
  - codex/context_compass/attention_board.md:19-83
  IMPACT: The board is materially smaller and the compiler lane is easier to
    reread, while current routing invariants are preserved.
  NEXT: summarize the compiler, analyzer, processor, planner, meld, and
    creation-context ownership state from the completed reread so the next
    implementation slice can be chosen cleanly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T16:41:12Z
  TYPE: FACT
  CLAIM: The current replacement stack is still structurally transitional.
    Analyzer is now truly graph-only and self-owned, but processor still
    contains facade-breaking model classification work in `_build_model(...)`
    and `_refresh_model_from_processor_outputs(...)`, while planner still has
    zero real strategies and only materializes a neutral plan shell. The code
    still depends on old Phase 8-11 artifacts as the real upstream truth.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-122
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy_builder.py:1-110
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-1207
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-374
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-283
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-109
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:1-103
  IMPACT: The next real compiler work still needs to strip processor-owned
    computation out of the processor facade and then give planner actual
    strategy-owned output logic, instead of treating the replacement stack as
    already authoritative.
  NEXT: finish the requested reread of old blueprint/runtime support objects
    (`OccurrencePlan`, `InjectionPlan`, patch maps, execution plan, meld,
    creation_context`, and `creations`) so downstream replacement scope is
    based on current source rather than earlier assumptions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T16:28:42Z
  TYPE: PLAN
  CLAIM: The current compiler_0 tranche is a bounded reread and state-hygiene
    pass before any new ownership edits. The requested source bundle is:
    compiler phases `1-13`, the current analyzer/processor/planner surfaces,
    `meld`, `creation_context`, `creations`, and the active/previous compiler
    epics. The same tranche also includes trimming stale `attention_board.md`
    detail older than 2026-05-29 while preserving live routing.
  EVIDENCE:
  - codex/context_compass/attention_board.md:22-22
  - codex/context_compass/tickets/epics/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md:35-55
  - codex/context_compass/tickets/epics/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md:112-126
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md:44-60
  IMPACT: This keeps the lane inside the active epic boundary and forces the
    next summary to come from current source and current direction docs instead
    of stale chat memory.
  NEXT: read the requested source bundle and then trim stale attention-board
    detail older than 2026-05-29 without disturbing active routing rows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T15:25:35Z
  TYPE: FACT
  CLAIM: The facade contracts are now aligned to the intended layered model.
    `SpellAnalyzer` remains the thin artifact-mutating facade, the processor
    strategies now mutate `SpellCodegenModel` instead of writing derived
    occurrence outputs back onto `SpellCompilerArtifact`, and the planner no
    longer treats a baseline `SpellCodegenPlan` as its working state. It now
    builds mutable planner-owned state first and materializes the final plan
    only after planner strategies run.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:15-109
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:21-287
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_state.py:1-144
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-163
  IMPACT: The next work can stop revisiting facade semantics and focus on the
    real ownership migration: processor artifact slots and Phase 9/10 movement.
  NEXT: choose the first processor-owned artifact-slot slice so the new model
    no longer relies on the old occurrence fields as transitional storage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T15:01:37Z
  TYPE: FACT
  CLAIM: The first ownership slice is now landed in code. `SpellAnalyzer`
    runs only the occurrence graph strategy, the 3 derived occurrence consumers
    now live under `artifact_processor/strategies/`, and
    `SpellArtifactProcessor` runs those strategies before building
    `SpellCodegenModel`. Phase 12 now executes analyzer first and processor
    second.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:64-109
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy_builder.py:59-85
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:1-157
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:1-217
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:1-311
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:21-201
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-87
  IMPACT: The analyzer/processor boundary is no longer theoretical for the
    occurrence lane. Future reorganization can now focus on artifact-slot
    ownership and model inputs instead of arguing about where the 3 derived
    strategies live.
  NEXT: choose whether the next slice adds explicit processor-owned occurrence
    artifact slots or immediately starts moving Phase 9 and Phase 10 under
    processor ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T13:49:04Z
  TYPE: FACT
  CLAIM: Current Phase 8, 9, 10, and 11 outputs already show the ownership
    tension clearly. Phase 8 stores `artifact._occurrence_plan_phase8`, Phase
    9 consumes that occurrence output and stores `artifact._injection_plan_phase9`,
    Phase 10 stores `artifact._override_patch_map_phase10` and
    `artifact._mutation_patch_map_phase10`, and current Phase 11 consumes the
    occurrence and injection outputs before storing 3 execution-plan variants:
    no-overrides, overrides, and mutation-overrides.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:520-520
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:119-119
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:233-233
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:235-236
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:777-777
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:876-878
  IMPACT: The current code already proves that Phase 9 and Phase 11 are
    occurrence-derived consumers and that current Phase 11 is the real planner
    layer.
  NEXT: use this as the ownership baseline instead of inventing a fresh model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T13:49:04Z
  TYPE: FACT
  CLAIM: The current processor and planner are still too late and too thin.
    `SpellArtifactProcessor._build_model(...)` still reads the no-overrides
    Phase 11 plan directly, and `SpellCodegenPlanner` still emits one summary
    `SpellCodegenPlan` object instead of explicitly owning the 3 real planner
    outputs already present in current Phase 11.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:89-198
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:106-106
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:15-134
  IMPACT: Reorganization should move concrete artifact ownership earlier into
    the processor and move actual plan ownership fully into the planner.
  NEXT: future slices should stop teaching processor to depend on late Phase 11
    state and instead promote Phase 11 planning logic into planner ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T13:49:04Z
  TYPE: DECISION
  CLAIM: The implementation order for this epic is intentionally bounded and
    ownership-first: analyzer keeps the primary graph truth, processor takes
    derived occurrence / injection / patch artifacts, planner takes the 3 real
    runtime/codegen plans, and Phase 13 stays emitter-only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:520-520
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:233-233
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:235-236
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:876-878
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:89-198
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:15-134
  IMPACT: Future prompts can take one narrow slice at a time without drifting
    back into ad hoc architecture changes.
  NEXT: review this epic and choose the first implementation slice from the
    listed order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic exists to reorganize current Phase 8-11 ownership so analyzer,
processor, planner, and emitter each own the right layer. The important
outcome is not speed in one prompt; it is a clean implementation order that
keeps later work bounded and honest.

