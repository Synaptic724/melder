# Epic: Define Compiler Phase Artifact Directory Cache

## Metadata
- Epic ID: EPIC-2026-06-06-define-compiler-phase-artifact-directory-cache
- Status: in_progress
- Owner: codex
- Agent Name: compiler_1
- Priority: p0
- Created: 2026-06-06T18:56:56Z
- Updated: 2026-06-07T20:18:31Z
- Target Window: 2026-Q2
- Related Program/Initiative:
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`

## Problem / Opportunity
We want to cache compiler data into a directory, but the current compiler path
spans phases 1-11 plus the `CreationContext` consumer boundary. If we cache the
wrong layer, we will either freeze unstable runtime-only objects, rebuild too
much on every use, or break the current handoff contract between compiler
artifacts and meld-time execution.

The immediate opportunity is to map the full artifact chain from:
- phase 1 requirements
- phase 2 symbolic graph
- phase 3 local topology / frame
- phase 4 validation
- phase 5 root blueprints
- phase 6 system validation
- phase 7 change-control integration
- phase 8 occurrence analysis
- phase 9 codegen model
- phase 10 codegen plan
- phase 11 codegen creation
- `CreationContextBuilder` / `CreationContext`

That map should tell us exactly which compiler outputs are durable enough to
persist in a filesystem directory, which keys/invalidation inputs control those
artifacts, and where the runtime-only seam starts.

## MRP Alignment (Most Reasonable Product)
The right foundation is not "save some blobs and hope they reload." The right
foundation is a compiler cache boundary that preserves correctness, lifecycle
clarity, and the current runtime contract while giving us a real path to
durable artifact reuse. This epic treats the directory cache as a compiler
architecture problem first and a storage problem second.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the lane to a fresh compiler-cache
  epic and wants full phase 1-11 plus `CreationContext` understanding before
  implementation.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/`
  - `src/melder/aether/conduit/meld/creation_context/`
  - `tests/unit/melder/spellbook/spell_compiler/`
  - `tests/unit/melder/aether/conduit/meld/creation_context/`
  - `tests/component/melder/spellbook/`
  - `codex/context_compass/tickets/epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`
  - `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
  - `tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md`
- EXIT_GATE:
  - the phase 1-11 artifact chain is mapped end to end
  - the `CreationContext` consumer seam is explicit
  - directory-cache candidates, invalidation inputs, and exclusion zones are
    explicit
  - the first bounded implementation slice is defined before source edits widen
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a useful directory cache
  requires changing the current compiler-to-`CreationContext` handoff contract
  instead of preserving it.

## Goals (Outcomes)
- Produce one explicit phase-by-phase artifact map from phases 1-11.
- Produce one explicit `CreationContextBuilder` / `CreationContext` consumer map.
- Define which compiler outputs are plausible directory-cache artifacts.
- Define invalidation keys and runtime-only exclusions for those cache artifacts.
- Define the first bounded implementation slice for directory caching.

## Non-Goals (Explicit Exclusions)
- Immediate source refactors across the compiler/runtime hot path.
- Broad mutation-research redesign.
- Final benchmark or performance claims before the cache boundary is mapped.
- Filesystem implementation details before the artifact contract is explicit.

## Scope Boundaries
- In scope:
  - compiler phase 1-11 reads and artifact mapping
  - `CreationContextBuilder` and `CreationContext` consumer boundary
  - directory-cache candidate analysis
  - invalidation/input-key analysis
  - decomposition into follow-up stories/tasks
- Out of scope:
  - unrelated conduit/runtime redesign
  - change-control mediator cleanup
  - production cache writer/loader code before the design is explicit

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a fresh epic to understand
  the compiler phases and `CreationContext` so we can design a filesystem
  directory cache boundary.

## Success Metrics
- A future reader can explain phase outputs and handoff boundaries without
  reopening the full chat history.
- Cacheable vs non-cacheable compiler layers are explicit in epic notes.
- At least one bounded implementation slice is small enough to start without
  reopening the entire compiler architecture question.

## Requirements (Functional + Non-Functional)
- Functional:
  - map each compiler phase input/output surface
  - map how phase 11 reaches `CreationContextBuilder`
  - identify durable cache artifacts and reload prerequisites
  - identify runtime-only objects that must not be directory-cached
- Non-Functional:
  - preserve UNKNOWN-first discipline
  - preserve the current runtime handoff contract unless the user explicitly
    approves widening it
  - keep the resulting plan reviewable and trancheable

## Constraints / Assumptions
- Use the current compiler/runtime code as the source of truth.
- Do not assume every phase artifact is serializable.
- Do not assume phase 10-11 is the only relevant boundary; directory caching
  may depend on earlier artifact stability.
- Treat existing compiler tickets as supporting context, not as permission to
  silently merge scopes.

## Dependencies / External References
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/readable_src_graph.json`
- `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
- `tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md`
- `tickets/tasks/2026-06-06_add_aether_configuration_system_caching_flag_task.md`
- `tickets/tasks/2026-06-07_scaffold_caching_system_utility_task.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Phase Chain Map
      Success criteria: phases 1-11 inputs/outputs and ownership boundaries are
      written into notes with evidence.
- [ ] Milestone 2: Runtime Consumer Seam
      Success criteria: `CreationContextBuilder` / `CreationContext` consumer
      expectations are explicit with evidence.
- [ ] Milestone 3: Directory Cache Boundary
      Success criteria: cache candidates, invalidation keys, and first
      implementation slice are explicit.

## Stories (Required to Complete)
- [ ] Story: STORY-TBD-phase-chain-map - map the full compiler artifact chain.
- [ ] Story: STORY-TBD-creation-context-boundary - map runtime consumer seams.
- [ ] Story: STORY-TBD-directory-cache-design - define durable artifact and
      invalidation rules.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: re-read phase entrypoints and shared compiler execution surfaces.
- [ ] Task: re-read `creation_context_builder.py` and `creation_context.py`.
- [ ] Task: extract cacheable artifact candidates and runtime-only exclusions.
- [ ] Task: verify Ticket Microcycle enforcement across active tickets/stories/tasks.
- [ ] Task: land the first root-policy config bit for system caching.
- [ ] Task: scaffold the first Spellbook-owned cache utility object.

## Acceptance Criteria (Epic Done)
- The compiler phase chain is mapped from 1 through 11 with evidence.
- The `CreationContext` consumer seam is mapped with evidence.
- Directory-cache candidates and exclusions are explicit.
- The first bounded implementation slice is defined and reviewable.

## Risks / Mitigations
- Risk: we anchor the cache at the wrong phase boundary and freeze unstable
  runtime surfaces.
  - Mitigation: map phases 1-11 and `CreationContext` before designing the cache.
- Risk: we over-focus on phase 10-11 and miss earlier serializable artifacts.
  - Mitigation: keep the full phase chain in scope from the start.
- Risk: we widen into implementation before invalidation rules are explicit.
  - Mitigation: keep this epic analysis-first until the slice is reviewable.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed compiler/runtime notes.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No cache design that silently widens the runtime handoff contract.

## Validation / Test Approach
- Not run.
- Recommended commands:
  - `rg -n "phase[ _]?[1-9]|phase10|phase11|SpellCodegen|CreationContext" src/melder/aether/spellbook/spell_compiler src/melder/aether/conduit/meld/creation_context`

## Rollout / Adoption Plan
- First finish the artifact-boundary map.
- Then break implementation into one bounded story/task slice.
- Only then start source edits for the first cache artifact seam.

## Open Questions
- Which phase artifact is the first stable directory-cache boundary?
- Are phase 1-7 artifacts worth persisting, or is the real durable boundary
  phase 8-11 only?
- Does `CreationContext` need a new loader seam, or can it stay unchanged and
  consume restored compiler artifacts through the current contract?

## Decision Log
- The lane is analysis-first and epic-scoped because directory caching reaches
  across the full compiler chain plus the runtime consumer boundary.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - phase 1-11 compiler artifacts
  - `CreationContext` consumer seam
  - directory-cache candidates and invalidation
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-06T18:56:56Z
  TYPE: PLAN
  CLAIM: This new epic should treat the directory-cache problem as a full
    compiler artifact-chain question, not as a narrow phase-10/11 tweak. The
    phase-10/11 work remains relevant, but the cache boundary can only be
    chosen correctly once we understand the whole phase 1-11 output chain and
    exactly what `CreationContext` consumes at runtime.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md:1-147
  - codex/context_compass/tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md:1-184
  - codex/context_compass/system_docs/src_architecture.md:442-620
  IMPACT: This keeps the cache design from hard-coding the wrong layer and
    gives us a durable lane for the full compiler/runtime boundary analysis.
  NEXT: read the phase entrypoints and artifact carriers in order, then map the
    `CreationContext` consumer seam against those outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:01:37Z
  TYPE: FACT
  CLAIM: The first viable cache seam is not "somewhere inside `CreationContext`."
    It is the spell-static handoff emitted after phase 11. Phase 5 still acts
    as a structural invalidation hinge by refreshing the rooted blueprint and
    system-index artifacts while explicitly clearing downstream codegen outputs
    and the spell-owned `CreationContext`. By contrast, phases 8-11 are now
    thin facade wrappers over analyzer, processor, planner, and
    codegen-creation systems, and `CreationContextBuilder` accepts constructed
    spells only after `artifact._spell_codegen_creation` exists. The builder
    then pulls just `resolve_route_key`, the fast-transient flag, and the two
    executors from that phase-11 payload before `CreationContext` compiles the
    hooks/no-hooks runtime doors.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:181-187
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:207-211
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:22-33
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:18-29
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:18-29
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:19-31
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:38-84
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:24-39
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:72-165
  IMPACT: The directory cache should target compiler-owned artifacts before the
    builder/runtime seam. If we cache deeper than `SpellCodegenCreation`, we
    are caching runtime-specific compiled door state instead of the spell-static
    compiler handoff.
  NEXT: read the shared compiler execution layer and the phase-11 creation
    payload types so we can map exactly what `SpellCodegenCreation` contains
    and which earlier phase artifacts survive into it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:01:37Z
  TYPE: FACT
  CLAIM: The compiler already maintains two different persistence shapes in
    memory. `SpellCompilerArtifact` carries the live phase objects
    (`SpellCodegenModel`, `SpellCodegenPlan`, `SpellCodegenCreation`) and the
    phase-11 creation artifact still owns live executor callables. Separately,
    `SharedCompilerExecutions` exports a normalized `_codegen_ir` split into
    `phase2_5` and `phase8_11`, where the exported payloads are reduced to
    deterministic tuples, counts, signatures, and selected metadata such as
    `resolve_route_key` and executor signatures. `SpellCompilerSystem.run_all_phases(...)`
    ends by clearing only the transient structural artifacts, which means the
    later rooted/codegen state is intentionally the reusable side of the
    current in-memory model.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:50-368
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:30-273
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:6-85
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:6-61
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:34-57
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-374
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1326-1489
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:793-886
  IMPACT: A directory cache should likely externalize a schema-safe export that
    resembles `_codegen_ir`, not pickle the live `SpellCodegenModel`,
    `SpellCodegenPlan`, or `SpellCodegenCreation` objects directly. The live
    carriers still own cleanup contracts, borrowed analysis sections, and
    runtime callables.
  NEXT: read the analyzer, processor, planner, and codegen-creation discovery
    families behind phases 8-11 so we can see which specific fields are stable
    data, which are derived selectors, and which are runtime-only code objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:05:16Z
  TYPE: FACT
  CLAIM: Phase 10 and phase 11 are not at the same maturity level for caching.
    Phase-10 discovery is still effectively fixed to a generalized family and
    generalized default codegen style, so its output is mostly selector data
    plus lane payloads on `SpellCodegenPlan`. Phase 11 is already a true
    multi-strategy assembly: discovery chooses an ordered strategy chain,
    `CodegenCreationSystem` records that chain on `SpellCodegenCreation`, the
    setup/no-overrides/overrides strategies stage route metadata, plan rows,
    signatures, and baseline executors into metadata, and the fat
    `general_creation_context_codegen_creation` finalizer consumes those staged
    values to build a closed-over override runtime with in-memory
    specialization caches, emitted-source caches, and code-object caches.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:1-42
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:1-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:1-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:1-205
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-709
  IMPACT: The first directory cache slice should probably stop before the fat
    phase-11 finalizer closure or split its products into separate cache tiers.
    Plan rows, signatures, and perhaps emitted override source/code objects are
    plausible persisted artifacts; the live override callable plus its mutable
    in-memory specialization caches are not.
  NEXT: inspect earlier analyzer/processor/planner data structures and the
    shared step-row/schema builders so we can enumerate which specific rows and
    signatures are stable enough to serialize into a directory format.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:06:31Z
  TYPE: FACT
  CLAIM: The likely directory-cache payloads are the normalized row/schema
    surfaces, not the planner/runtime section objects. `SpellRuntimeAnalysis`
    still keeps live `spell`, `call_target`, and `user_created_object`
    references per spell. `SpellGeneralizedCodegenLanePlan` still carries live
    `_fast_spells`, `_fast_call_targets`, `_fast_existing_objects`, and the
    transient fast-plan tuple in addition to step metadata. By contrast,
    `SpellOverrideTargetingAnalysis` is already normalized into
    `SpellOverrideTargetRef` rows and counts, and `SharedCompilerExecutions`
    already knows how to export schema-only phase-5 socket rows,
    phase-5 DAG-edge rows, phase-8 occurrence rows, phase-11 step rows, and a
    schema-only fast-transient payload/signature.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:1-87
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_override_targeting_analysis.py:1-115
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:400-987
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1084-1198
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:166-241
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:503-633
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:633-760
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1004-1117
  IMPACT: A filesystem cache should probably serialize normalized IR rows and
    signatures, then rebuild any live runtime-analysis or lane-plan objects
    from that persisted data on demand. Trying to persist the raw lane plan or
    runtime section objects directly would bake process-local call targets and
    live spell objects into the cache contract.
  NEXT: inspect the analyzer/processor strategy outputs that feed those row
    builders so we can sketch the first concrete directory-cache schema split:
    structural rows, occurrence rows, planner lane rows, and phase-11
    executor/source signatures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:24:08Z
  TYPE: FACT
  CLAIM: Phase-11-only cache is sufficient for the clean runtime path, but it
    is not sufficient for dirty/gated revalidation. The current meld path
    explicitly reruns structural phases 1-4 when lineage validity is gated or
    unknown, then reruns local foundational phases 5-7 for the target/root
    closure, and only then reruns deferred phases 8-11 for the spell. This
    matters because phase 3 resolves against the live `spellbook._spell_id_pool`,
    so post-conjure `bind()` changes can alter candidate resolution and root
    topology in ways a stale phase-11 payload cannot repair by itself.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:495-532
  - src/melder/aether/spellbook/spellbook.py:3805-3845
  - src/melder/aether/spellbook/spellbook_creation_system.py:1540-1632
  - src/melder/aether/spellbook/spellbook_creation_system.py:1664-1748
  - src/melder/aether/spellbook/spell.py:1006-1030
  - src/melder/aether/spellbook/spell.py:1031-1090
  - src/melder/aether/spellbook/spellbook.py:2776-2858
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-661
  IMPACT: The cache design needs two modes. Hot path: use phase-11 cache and
    skip compiler phases entirely. Dirty path: fall back to real upstream
    recompilation for the affected target/root scope because correctness
    depends on fresh phases 1-7 before a new phase-11 package is trustworthy.
  NEXT: answer the user using this two-path model, then decide whether the
    first implementation slice is phase-11 hot-path caching only or includes a
    structured invalidation/fallback path from day one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:24:20Z
  TYPE: MEASURE
  CLAIM: The experiment layer now proves the creation-context-facing cache seam
    on real runtime paths. A saved no-overrides asset was able to rebuild a
    generic `CreationContext` after clearing both the spell-owned cached
    context and `spell._compiler_artifact`, and `conduit.meld(...)` still
    created the spell successfully. A second experiment did the same for one
    concrete override shape after aligning the root to `Existence.many`, and
    `conduit.meld(..., spell_override=...)` still produced the overridden
    consumer successfully. The current experiment helper persists the actual
    creation-context-facing executor package:
    - `no_overrides`: emitted source + marshaled compiled code object +
      `steps_rows` + `step_spell_ids` + `root_spell_id`
    - `overrides`: emitted source + marshaled compiled code object +
      `plan_rows` + target-spec rows + grouped override-target rows + one
      precomputed override shape
    - plus route metadata currently carried through the live package
    (`resolve_route_key`, and today also
    `fast_transient_no_overrides_enabled` / `transient_schema`)
    The transient fields are only present because the current no-overrides
    compiler helper still supports that branch; they are not fundamental to the
    cache boundary and can be removed if we standardize on the step-plan
    executor path.
  EVIDENCE:
  - tests/experimentation/creation_context_cache_asset_playground.py:1-558
  - tests/experimentation/test_creation_context_cache_asset_experiment.py:1-190
  - tests/experimentation/test_creation_context_override_cache_asset_experiment.py:1-194
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:178-220
  IMPACT: The viable durable boundary is narrower than the full compiler
    artifact and wider than the spell-owned `CreationContext` cache. We can
    persist the real `no_overrides` / `overrides` runtime package, rebuild a
    generic `CreationContext`, and skip the live compiler artifact on the clean
    path. The next design choice is whether to keep transient-related fields for
    backward compatibility with the current no-overrides compiler, or drop them
    and standardize the cache on only the step-plan-backed `no_overrides` and
    `overrides` executors.
  NEXT: decide whether the first real cache implementation should
    1) keep the current transient-capable no-overrides payload shape, or
    2) simplify immediately to `no_overrides` + `overrides` only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T22:15:18Z
  TYPE: MEASURE
  CLAIM: Two more experiments sharpened the practical cache story. First,
    explicitly wiping the stored phase-1-to-phase-4 artifact objects after
    dynamic late bind did not stop meld from succeeding in either a standalone
    spell case or a provider->consumer case. In both cases, the runtime rebuilt
    phase 5, and rebuilt phase 8-11 only for the target consumer, while the
    phase-1-to-phase-4 objects themselves stayed absent. That means the clean
    path is relying on spell/system-state side effects from earlier structural
    work, not on those artifact objects surviving in memory. Second, fully
    cleaning a dependency spell object is not safe unless it is removed from the
    Spellbook at the same time. Before the cleanup API fix, a cleaned
    dependency remained reachable from the spell pools and later rooted work
    tripped over the missing `_compiler_artifact`; after wiring spell cleanup
    through the Spellbook-owned removal path, the same scenario now fails for
    the correct reason: the dependency is honestly absent, so phase 3 reports
    no DI candidate.
  EVIDENCE:
  - tests/experimentation/test_forced_phase14_wipe_after_late_bind_experiment.py:1-229
  - tests/experimentation/test_dynamic_post_conjure_bind_dependency_revalidation_experiment.py:1-220
  - src/melder/aether/conduit/meld/meld.py:491-580
  - src/melder/aether/spellbook/spellbook.py:2680-2769
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:742-757
  IMPACT: The durable cache does not need to restore phase-1-to-phase-4
    artifact objects on the clean path if the spell/system-state side effects
    are already trustworthy. The cache boundary can therefore focus on the real
    creation-context-facing `no_overrides` / `overrides` package plus whatever
    structural side-state cached startup establishes up front. At the same
    time, any cleanup/removal API must remove a spell from live Spellbook pools
    before local object teardown, or later recompilation walks will touch a
    cleaned corpse.
  NEXT: Continue from a design that treats the cache as:
    1) cached startup restores structural side-state and spell registration, and
    2) clean-path execution restores the `no_overrides` / `overrides`
       creation-context-facing executors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-06T23:03:44Z
  TYPE: MEASURE
  CLAIM: The first implementation slice under this epic is now real and still
    bounded: `AetherConfiguration` owns a default-on
    `system_caching_enabled` flag, the fluent builder mirrors it, and the
    focused Aether unit file stayed green (`129 passed, 1 warning`). This does
    not wire cache behavior yet; it only establishes the root policy surface
    that later compiler/runtime consumers can read.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:126-200
  - src/melder/aether/aether_configuration.py:282-307
  - src/melder/aether/aether_configuration_builder.py:73-85
  - tests/unit/melder/aether/test_aether.py:1563-1593
  IMPACT: The cache lane now has one stable root-level toggle and can move to
    the next question cleanly: which first live consumer should read it
    (`cached_conjure`, compiler build path, or runtime rehydration seam).
  NEXT: choose the first live consumer of `system_caching_enabled` before
    widening into broader cache behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-06T23:13:54Z
  TYPE: DECISION
  CLAIM: The cache-root contract is now explicit and package-relative. The
    root config surface stores `system_cache_root_path` as the relative
    fragment `__melder_cache__`, not as a machine-specific absolute path, and
    exposes a resolver for the absolute installed-package location. This keeps
    the contract valid in this checkout and in pip installs.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:30-55
  - src/melder/aether/aether_configuration.py:141-165
  - src/melder/aether/aether_configuration.py:219-241
  - tests/unit/melder/aether/test_aether.py:1563-1608
  IMPACT: Later cache writers/loaders can resolve one canonical cache root
    under the live installed `melder` package instead of baking in repo-local
    absolute paths.
  NEXT: choose the first live consumer of the root cache policy and cache-root
    path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:18:50Z
  TYPE: FACT
  CLAIM: The next cache-lane seam is now real in code. `CachingSystem` exists
    as a Spellbook-owned utility under `src/melder/utilities/caching_system/`
    and manages one conduit cache file with:
    - one in-memory dict after first load
    - bundle-level SHA stamping
    - add/remove helpers
    - best-effort transfer into another cache utility
    - immediate file flush after successful mutation
    Spellbook now has a lazy `_get_or_create_caching_system()` seam gated by
    the activated Aether root config.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:16-430
  - src/melder/aether/spellbook/spellbook.py:672-730
  - tests/unit/melder/utilities/test_caching_system.py:1-125
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:1-158
  IMPACT: The cache lane is no longer blocked on abstract utility design. The
    next step is to choose which first live runtime mutation path should emit
    real spell payloads into this utility.
  NEXT: decide whether the first live caller should be bind-after-conjure,
    transfer of ownership, or conjure-time bundle emit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T09:29:13Z
  TYPE: MEASURE
  CLAIM: The cache utility seam now has the requested broader test floor:
    `39` unit tests for `CachingSystem`, `10` component tests for the
    Spellbook lazy-init gate, and `49` focused passing tests total.
  EVIDENCE:
  - tests/unit/melder/utilities/test_caching_system.py:1-622
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:1-324
  IMPACT: We can move into live emission wiring with a much stronger safety net
    around the cache utility and its Spellbook ownership seam.
  NEXT: choose the first live caller that should emit real spell payloads into
    the cache utility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-07T20:18:31Z
  TYPE: FACT
  CLAIM: The cache lane architecture is now materially sharper than the early
    scaffold notes imply. `CachingSystem` is storage-only again: one
    Spellbook-owned in-memory `spell_payloads` map keyed by `spell_id`,
    `upsert/remove/transfer` mutate only memory, and `emit()` is the only file
    write. It no longer owns phase-11 bundle build/load logic.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:14-35
  - src/melder/utilities/caching_system/caching_system.py:220-294
  IMPACT: The durable cache object is back in the correct ownership role, so
    later work can focus on when to stage and when to emit, not on untangling
    compiler/runtime logic from storage.
  NEXT: treat `CachingSystem` as storage-only in all follow-on slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:18:31Z
  TYPE: FACT
  CLAIM: The live cache bundle seam is now on `CreationContext`, not on a
    separate payload-builder layer. `CreationContext` exposes
    `output_cache()` and `load_cached_bundle(...)`; the latter publishes a
    cached bundle back onto `spell._creation_context` through the existing
    `publish=True` path.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:263-309
  IMPACT: The cached object is now the same runtime bundle `CreationContext`
    consumes, which removes the extra fake builder abstraction that had caused
    repeated drift.
  NEXT: keep future cache work centered on the `CreationContext` bundle seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:18:31Z
  TYPE: FACT
  CLAIM: Newly published `CreationContext`s now stage themselves into the
    Spellbook-owned in-memory cache at the publish seam. The active path is:
    `phase 11 outputs exist -> CreationContextBuilder.build(...) -> factory
    publishes onto spell -> factory calls spell.emit_cache() -> Spellbook
    stores creation_context.output_cache()` into `CachingSystem`.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:118-126
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:225-242
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:264-279
  - src/melder/aether/spellbook/spell.py:672-734
  - src/melder/aether/spellbook/spellbook.py:730-803
  IMPACT: The cache now fills from the actual publish step instead of from a
    separate compiler/storage abstraction. That gives both conjure-built and
    JIT-built contexts one shared staging seam.
  NEXT: finish the operation-boundary emit policy around that seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:18:31Z
  TYPE: FACT
  CLAIM: The in-memory cache currently deduplicates by `spell_id`, not by
    `spell_index.id`. When `Spellbook._emit_spell_cache(...)` sees that the
    current `spell_id` is already present in `CachingSystem`, it returns
    `False` and skips staging another copy. This matches the intended
    "spell_id is the SHA256 identity" rule.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:754-770
  IMPACT: Once one published context has already staged its bundle for the
    current `spell_id`, later duplicate emit attempts in the same run are
    ignored cleanly.
  NEXT: preserve `spell_id` as the only dedupe key for this cache lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:18:31Z
  TYPE: FACT
  CLAIM: The process-wide `executor_code_cache.py` is a different, much
    narrower cache layer than the durable conduit cache. It stores
    `source_hash -> compiled CodeType` in one module-level dict for the life of
    the process. Phase 11 uses it while compiling emitted executor source, but
    it is not keyed by `spell_id`, not persisted to disk, and not the same
    thing as the Spellbook/conduit cache bundle.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/executor_code_cache.py:1-123
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:37-84
  IMPACT: Future cache-hit work should not confuse the process-local compile
    memoizer with the durable bundle cache. They solve different layers:
    compile-source reuse vs cross-run `CreationContext` bundle reuse.
  NEXT: keep them conceptually separate during the next implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:18:31Z
  TYPE: FACT
  CLAIM: The missing piece is now narrow and explicit: operation-boundary file
    emission. The in-memory cache exists, Spellbook owns it, and published
    contexts stage into it. What is still not wired is:
    1. conjure-end `CachingSystem.emit()` once only when the operation actually
       acquired new cache, and
    2. the JIT/meld file-emit boundary when a newly published context was
       staged during that top-level runtime operation.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:292-300
  - src/melder/aether/spellbook/spellbook.py:773-803
  - src/melder/aether/spellbook/spellbook_creation_system.py:386-482
  IMPACT: The next session should not reopen the entire cache-boundary question.
    It should start from one concrete implementation choice: wire the
    operation-end `emit()` policy for conjure/JIT on top of the already-landed
    staging seam.
  NEXT: after refresh, implement the 3-path SpellbookCreationSystem orchestration
    with one final conjure-end emit and the JIT emit boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when the cache boundary, invalidation model, or compiler/runtime
  ownership picture sharpens.
- Reference future story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists to answer one cross-cutting question: where the compiler
artifact chain should meet a durable directory cache without breaking the
runtime consumer contract. The first pass is read-and-map only: phases 1-11,
then `CreationContextBuilder` / `CreationContext`, then cache candidates and
invalidation rules.

Current practical state:
- `CachingSystem` is storage-only and Spellbook-owned.
- `CreationContext` is the live cache-bundle seam through
  `output_cache()` / `load_cached_bundle(...)`.
- published contexts now stage themselves into Spellbook cache memory.
- staging dedupes by `spell_id`.
- the remaining implementation work is operation-boundary file emission:
  conjure-end once if new cache was acquired, and JIT/meld emit at the end of
  the top-level runtime operation that created new cache.
