Completed: 2026-06-06T18:18:17Z
Summary: Phase 9-11 mutation-lane convergence landed, the runtime handoff collapsed to the two executor doors, and the hot-path wrapper/probe regression was removed. Remaining red tests are only in the explicitly ignored change-control mediator lane.

# Task: Map Mutation Planner And Phase11 Convergence

## Metadata
- Task ID: TASK-2026-06-06-map-mutation-planner-phase11-convergence
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-06T09:44:36Z
- Updated: 2026-06-06T18:18:17Z

## Objective
Map the downstream convergence after the front-door mutation contract fix:
- planner
- codegen-creation discovery
- phase-11 output shape
- `CreationContextBuilder` / `CreationContext`

The goal is to determine exactly how the permanent third mutation family is
currently baked in and what the correct collapse path is.

## Parent Link
- Epic:
  `tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md`

## Ticket Contract
- ENTRY_GATE: front-door mutation semantics are corrected enough that the next
  useful question is downstream packaging, not analyzer churn.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py`
  - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py`
  - `tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py`
  - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py`
  - `tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py`
  - `codex/context_compass/tickets/tasks/2026-06-06_map_mutation_planner_phase11_convergence_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-06-06_align_mutation_contract_phase4_to_late_bound_hole_task.md`
  - `tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md`
- EXIT_GATE:
  - the current downstream mutation-lane assumptions are mapped explicitly
  - the target planner/phase-11/runtime shape is explicit enough to review
  - no implementation starts until the downstream plan is explicit in notes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if planner/phase-11 collapse
  cannot be separated cleanly from broader runtime semantics.

## Scope Boundaries
- In scope:
  - planner lane assumptions
  - phase-11 discovery/strategy assumptions
  - `SpellCodegenCreation` mutation fields
  - `CreationContextBuilder` mutation route selection
  - tests that currently encode the third-lane assumption
- Out of scope:
  - MutationContract removal
  - analyzer change unless new evidence appears
  - implementation before the downstream plan is reviewed

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: current evidence says analyzer is likely fine and the
  stronger structural problem is downstream permanent-third-lane packaging.

## Steps / Checklist
- [ ] Map planner assumptions about `mutation_overrides_plan`.
- [ ] Map phase-11 discovery and strategy assumptions about permanent mutation lanes.
- [ ] Map `SpellCodegenCreation` mutation payload fields and builder/runtime usage.
- [ ] Map the current test surface that encodes the third-lane assumption.
- [ ] Write the target downstream convergence plan before code edits.

## Validation
- Run:
  - `.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py -q`
  - `.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py -q`
  - `.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py -q`
  - `.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py -q`
  - `.venv_new\Scripts\python.exe -m pytest tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py -q`

## Applicable Anti-Patterns
- [ ] Do not re-open analyzer changes without new evidence.
- [ ] Do not remove `MutationContract` itself.
- [ ] Do not jump into code edits before the downstream convergence map is explicit.

## Notes
- DATETIME: 2026-06-06T09:44:36Z
  TYPE: FACT
  CLAIM: The stronger evidence now points downstream, not at the analyzer.
    Planner always builds `no_overrides`, `overrides`, and
    `mutation_overrides`; codegen-creation discovery always includes the
    mutation strategy in the generalized chain; `SpellCodegenCreation` carries
    a full second override-route payload for mutation; and
    `CreationContextBuilder` still selects a separate mutation route off
    `spell.has_mutation_override`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:43-60
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:12-26
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system.py:41-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:49-108
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:47-53
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:122-136
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:272-323
  IMPACT: The next real convergence target is planner/phase-11/runtime packaging.
  NEXT: map the downstream third-lane assumptions and define the collapse path
    without touching code yet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:51:35Z
  TYPE: FACT
  CLAIM: The strongest downstream pressure is not necessarily the planner
    *algorithm* itself, but the output shape and binder assumptions that freeze
    mutation into a permanent third family. The current planner always carries
    `mutation_overrides_plan`, which may be acceptable as an intermediate plan
    artifact, but phase-11 creation packaging then materializes that into
    explicit `override_mutation_*` fields on `SpellCodegenCreation`, and
    `CreationContextBuilder` / `CreationContext` use `spell.has_mutation_override`
    to activate a separate mutation route at runtime. That is where the
    stronger structural commitment lives.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:43-60
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:12-26
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system.py:41-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:49-108
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:47-53
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:101-149
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:269-323
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:116-174
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:728-819
  IMPACT: The likely collapse point is phase-11 output plus runtime binder
    selection, not necessarily the planner builder itself. We should keep
    verifying before changing planner structure, because planner may just be a
    neutral carrier while creation-context/runtime makes the wrong permanent
    distinction.
  NEXT: map the exact runtime branch points that turn the `override_mutation_*`
    payload into a permanent separate route and compare that against the target
    "resolved mutation socket should run as normal no-overrides" contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:58:55Z
  TYPE: FACT
  CLAIM: The downstream mutation management model currently splits into three
    layers:
    1. processor metrics/analysis:
       `SpellMutationTargetingAnalysis` plus mutation-target counts on
       `SpellCodegenModel`
    2. planner carrier:
       `mutation_overrides_plan` on `SpellCodegenPlan`
    3. runtime-activating output:
       `override_mutation_*` fields on `SpellCodegenCreation`, which
       `CreationContextBuilder` rehydrates into `override_route_config_mutation`,
       and `CreationContext` / `ConduitMeld` then use to replace the normal
       no-overrides lane whenever `spell.has_mutation_override` is true
       even if the caller supplied no runtime overrides
    The key management difference is that layers 1 and 2 may be acceptable as
    descriptive/carrier state, but layer 3 turns mutation into a permanent
    runtime-family switch.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_mutation_targeting_processor_strategy.py:1-122
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_mutation_targeting_analysis.py:1-98
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:64-88
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:12-26
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:47-53
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:101-149
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:269-323
  - src/melder/aether/conduit/meld/conduit_meld.py:228-267
  - src/melder/aether/conduit/meld/spellspace_meld.py:234-276
  IMPACT: The likely safe collapse point is not "remove every mutation field at
    once." It is to stop layer 3 from turning mutation into a separate active
    runtime family, while deciding later whether layers 1 and 2 still carry
    useful descriptive or logistical separation.
  NEXT: compare each layer against the target contract and decide the exact
    change boundary for the first runtime/output collapse pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T10:23:00Z
  TYPE: FACT
  CLAIM: Phase 9 already computes most of the mutation information phase 10
    would need, but it does not yet expose it in the exact "baseline strategy
    selection" form. Right now phase 9 gives us:
    - `graph_shape.mutation_override_dependency_count`
      from phase 8 graph truth
    - `mutation_targeting_shape` plus target-spec / patch metrics from the
      processor mutation-targeting strategy
    - `spell_runtime_shape`, which carries live `SpellRuntimeRecord` objects
      and therefore preserves access to the actual runtime `Spell` objects
    What phase 10 does not currently have is one explicit processor-owned field
    answering the real strategy question:
    "is the current baseline graph mutation-bound?"
    That means phase 10 can probably be changed without a large phase-9
    rewrite, but it may still benefit from one explicit model flag so planner
    logic does not infer intent indirectly from counts or by reaching through
    runtime records into live spell objects.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_graph_analysis.py:23-31
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_mutation_targeting_processor_strategy.py:1-122
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_mutation_targeting_analysis.py:39-88
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:51-100
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:7-86
  IMPACT: We likely do not need a big phase-9 redesign before changing phase
    10. The key decision is whether to add one explicit processor-owned
    baseline-selection flag or let phase 10 infer mutation-active baseline
    from existing model sections.
  NEXT: decide whether the planner should key off a new explicit model flag or
    off existing model sections when selecting the baseline strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T10:42:27Z
  TYPE: FACT
  CLAIM: Phase-10 and phase-11 discovery now use the same strategy/builder
    facade pattern as the rest of the compiler. Both discovery systems were
    migrated behind owned discovery-strategy builders that iterate registered
    strategies in order, while preserving the exact current default behavior:
    phase 10 still resolves to `generalized_codegen_plan`, and phase 11 still
    resolves to the generalized creation chain or the fallback no-overrides
    chain. That means the package move is complete and the next real work is
    selection logic, not more structural migration.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_strategy.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_strategy_builder.py:1-94
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:1-44
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_system.py:1-53
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy.py:1-46
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy_builder.py:1-102
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-56
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/fallback_no_overrides_codegen_creation_discovery_strategy.py:1-42
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_system.py:1-63
  IMPACT: We now have the proper seam to implement real phase-10 discovery
    criteria without reopening package layout. The next mutation-planner step
    should change discovery/selection behavior, not discovery architecture.
  NEXT: define the first real phase-10 discovery conditions for selecting which
    strategy fills `no_overrides_plan` and which strategy fills
    `overrides_plan` from current processor/model truth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T10:42:27Z
  TYPE: MEASURE
  CLAIM: The discovery migration preserves current behavior on the targeted
    planner and codegen-creation unit surface.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-183
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-819
  IMPACT: The discovery seam is stable enough to use as the basis for the next
    phase-10 selection change.
  NEXT: move from package migration into real discovery criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T10:49:33Z
  TYPE: MEASURE
  CLAIM: The new discovery seams now have dedicated unit and component
    coverage, not just the older planner/creation facade tests. We now have:
    - 7 unit tests for phase-10 discovery contract/builder/facade behavior
    - 8 unit tests for phase-11 discovery contract/builder/facade behavior
    - 5 component tests for planner/creation facades using the real discovery
      seams with lightweight strategy doubles
    This keeps the moved discovery packages and builders under direct test
    instead of relying on indirect coverage only.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:1-178
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-237
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-177
  IMPACT: The discovery seam is now properly pinned down, so the next phase-10
    work can change discovery criteria with immediate localized feedback.
  NEXT: implement the first real phase-10 discovery criteria for baseline and
    secondary override plan selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T11:35:47Z
  TYPE: FACT
  CLAIM: Lowest-overhead implementation does not require a phase-8 algorithm
    rewrite. Phase 8 is already doing the key semantic job: it resolves
    mutation bindings into ordinary dependency occurrences by rewriting the
    dependency map before phase-9 processors consume it. The missing piece is
    an explicit phase-8 output signal that says whether the **current baseline
    graph was actually mutation-shaped**. Right now the nearest output is
    `graph_shape.mutation_override_dependency_count`, but that is too indirect
    because it counts spells carrying mutation payloads, not confirmed
    occurrence rewrites on the current graph. The cheapest correct change is:
    - keep `_apply_mutation_overrides_to_dependencies(...)` as-is
    - add one explicit field on `SpellOccurrenceGraphAnalysis` derived from
      actual applied mutation rewrites
    - let phase 9/10 read that explicit graph-level fact instead of inferring
      mutation state from raw payload presence or from live spell objects
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:711-724
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1218-1245
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_graph_analysis.py:23-31
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:59-73
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:61-94
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:61-89
  IMPACT: The next code slice should add one explicit graph-level mutation
    baseline signal in phase 8, not redesign the phase-8 occurrence algorithm.
    That gives phase 10 a cheap, truthful discovery input with minimal churn.
  NEXT: define the exact phase-8 output field shape and then make phase-10
    discovery consume it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T12:12:18Z
  TYPE: FACT
  CLAIM: The current runtime still gives `SpellContract` and mutation two
    different activation paths. `Meld._ensure_lineage_resolvable(...)` calls
    `_check_contracts_and_force_revalidation(...)`, and that helper only
    inspects `SpellContract` defaults, resolves them from contracted spell
    maps, and gates conduit-local resolution validity when they are present.
    Mutation does not have an equivalent meld-side contract pass. Instead,
    `Spell.apply_mutation_override(...)` and `clear_mutation_override(...)`
    dirty the spell through `invalidate_spell(...)`, and phase 8 then makes
    the override real by rewriting dependency occurrences in
    `_apply_mutation_overrides_to_dependencies(...)`. So today mutation takes
    effect through invalidation plus compiler rebuild, not through a parallel
    meld-time contract gate.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:510-514
  - src/melder/aether/conduit/meld/meld.py:764-918
  - src/melder/aether/spellbook/spell.py:1146-1232
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1218-1245
  IMPACT: This narrows the real convergence question. If we keep the current
    architecture, mutation should either stay a compiler-resolved override
    model and lose the downstream third family, or we redesign runtime to
    consume mutation bindings directly. Right now it is not "SpellContract but
    slightly different" at meld time.
  NEXT: compare this compiler-resolved mutation path against phase-10 plan
    selection and decide whether the planner can treat the mutation-resolved
    graph as the normal baseline with no separate public mutation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T12:29:42Z
  TYPE: FACT
  CLAIM: The current codebase has two different mutation mapping surfaces, and
    they are not equivalent. `MutationContract` can store
    `spell` / `spellframe` / `binding_name` / `spell_override` on the
    descriptor itself, so the socket object is not structurally empty. But the
    active runtime/compiler path does not use that descriptor-side mapping to
    resolve providers the way `SpellContract` does. Instead, the actual fill
    path comes from `Spell.mutation_override`, which is a separate map of
    target-spec key -> target spell id. Phase 8 parses that target-spec map,
    finds matching `SocketKind.MUTATION_CONTRACT` sockets in the DAG index,
    and rewrites dependency occurrences from there. So today:
    - `MutationContract` = socket identity metadata
    - `spell.mutation_override` = actual socket-target assignment
    They are two different mapping models, not one shared mapping surface.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:66-134
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:296-330
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:123-177
  - src/melder/aether/spellbook/spell.py:1106-1232
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:968-1245
  IMPACT: The semantic question is no longer "is mutation just like
    SpellContract?" The actual issue is whether we want one mapping model or
    intentionally keep the current split between declared mutation socket
    identity and spell-local override targeting.
  NEXT: decide whether mutation should converge onto one provider-mapping model
    or keep the current two-layer model while only stripping the downstream
    third runtime family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T12:35:04Z
  TYPE: DECISION_REQUEST
  CLAIM: There is now a legitimate design fork: remove `MutationContract`
    entirely and collapse the feature into one special spell-local overlay
    system, or keep `MutationContract` as the declaration surface for legal
    mutation sockets while stripping only the downstream third runtime family.
    The code evidence says the active fill path already comes from
    `spell.mutation_override`, not from descriptor-side provider resolution,
    so an overlay-first model aligns better with current execution. But
    `MutationContract` is also the current source of "which sockets are legal
    mutation targets" because phase 8 resolves target specs only against
    `SocketKind.MUTATION_CONTRACT` sockets.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:66-134
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:627-638
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1123-1215
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1218-1245
  IMPACT: If we remove `MutationContract`, we must replace its current role as
    the declaration/filter surface for mutation-legal sockets, or consciously
    widen mutation overlays to arbitrary graph targets. That is a different
    design than merely collapsing planner/runtime outputs.
  NEXT: decide whether the desired end state is:
    1. overlay-only with a new explicit declaration surface,
    2. overlay-only with arbitrary targeting,
    or 3. declaration-only `MutationContract` plus overlay fill.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T12:38:41Z
  TYPE: FACT
  CLAIM: The repo needs a stricter vocabulary split. `override` should refer
    to meld-time caller payload only: the thing passed into `meld(...)` as
    `spell_override`. That is the real runtime override surface. The
    persistent `Spell.mutation_override` map is a different concept: a
    spell-local graph overlay that dirties the spell and changes later phase-8
    occurrence rewriting. Conflating those two surfaces is what keeps muddying
    the mutation discussion.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1037-1102
  - src/melder/aether/spellbook/spell.py:1106-1232
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1218-1245
  IMPACT: The right comparison is no longer "MutationContract vs override" in
    a generic sense. It is:
    - `spell_override` = true meld-time runtime override
    - `spell.mutation_override` = persistent graph overlay
    Any mutation redesign should keep those surfaces distinct.
  NEXT: re-evaluate mutation using the corrected vocabulary and decide whether
    the persistent graph overlay should remain separate from meld-time
    overrides or collapse toward one model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T13:10:46Z
  TYPE: PLAN
  CLAIM: First implementation slice should stop treating
    `spell.mutation_override` as a recompilation trigger and instead treat it
    as a pre-normalized persistent default override payload. The normal
    override machinery is already expressive enough: the processor/codegen
    override targeting path targets arbitrary sockets, while the current
    mutation-specific runtime behavior comes only from separate route selection
    in `CreationContextBuilder`, `CreationContext`, `ConduitMeld`, and
    `SpellSpaceMeld`. So the smallest coherent slice is:
    1. normalize/store mutation payloads in `Spell`
    2. remove spell invalidation from mutation apply/clear
    3. merge persistent mutation payload under caller `spell_override` with
       caller keys winning
    4. route that merged payload through the normal overrides path
    5. stop selecting the mutation-specific override route in runtime context
       build/use
  EVIDENCE:
  - src/melder/aether/conduit/meld/overrides/spell_overrider.py:31-126
  - src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:291-293
  - src/melder/aether/conduit/meld/conduit_meld.py:217-281
  - src/melder/aether/conduit/meld/spellspace_meld.py:223-290
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:101-149
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:266-279
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:650-760
  IMPACT: This slice lets us preserve `mutation_override` as a concept while
    stripping out the revalidation contract and the mutation-specific runtime
    branch. It does not yet remove the planner/phase-11 mutation fields, but
    it makes them dead weight instead of active behavior.
  NEXT: patch `Spell`, `Meld`/front-door meld surfaces, and creation-context
    routing to implement the overlay-first model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T13:21:11Z
  TYPE: FACT
  CLAIM: The first overlay-first runtime slice is now in place. `Spell` no
    longer dirties or invalidates itself when `mutation_override` changes;
    instead it stores a pre-normalized persistent default override payload
    using the same normalizer used by meld-time caller overrides.
    `ConduitMeld` and `SpellSpaceMeld` now merge that stored payload under the
    caller `spell_override` payload with caller keys winning, then route the
    effective payload through the normal overrides door. `CreationContext`
    no longer switches its active override route to the mutation-specific
    route just because mutation payload exists; normal no-mutation route
    config stays active.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1108-1230
  - src/melder/aether/conduit/meld/meld.py:1037-1152
  - src/melder/aether/conduit/meld/conduit_meld.py:217-280
  - src/melder/aether/conduit/meld/spellspace_meld.py:223-289
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:238-346
  IMPACT: Mutation override is now materially closer to a persistent default
    override payload and materially further from a recompilation contract.
    The downstream mutation-specific planner/creation artifacts still exist,
    but this slice makes them inactive for the main runtime selection path.
  NEXT: inspect and remove the remaining dead mutation-specific downstream
    plan/creation surfaces now that runtime no longer depends on them for this
    behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T13:28:43Z
  TYPE: FACT
  CLAIM: The runtime precedence rule is now the explicit one the user asked
    for, not a merge model. `Spell` owns its own local mutation-payload
    normalizer and no longer imports or delegates to `Meld` for that logic.
    At meld time:
    - if caller `spell_override` is present, use that payload
    - else if `spell.mutation_override` is present, use that payload
    - else run the no-overrides path
    So caller overrides replace stored mutation overrides instead of merging
    with them.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1147-1230
  - src/melder/aether/conduit/meld/meld.py:1037-1113
  - src/melder/aether/conduit/meld/conduit_meld.py:217-249
  - src/melder/aether/conduit/meld/spellspace_meld.py:223-259
  IMPACT: The overlay-first model now matches the agreed contract exactly:
    persistent mutation payload is a default override surface, caller payload
    fully replaces it, and no hidden merge semantics remain in runtime.
  NEXT: remove the still-dead mutation-specific planner and codegen-creation
    route fields now that runtime selection no longer relies on them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T13:21:11Z
  TYPE: MEASURE
  CLAIM: The focused spell/meld/creation-context unit surface passes after the
    overlay-first slice landed.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spell.py:122-149
  - tests/unit/melder/aether/conduit/meld/test_meld.py:865-930
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:50-115
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:224-352
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:95-116
  IMPACT: The first runtime slice is stable enough to continue into the next
    mutation-lane cleanup step without guessing.
  NEXT: carry the same model into planner/codegen cleanup or add the next
    targeted regression tests before widening scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-06T13:46:10Z
  TYPE: FACT
  CLAIM: `Spell.cleanup()` still drifts from the stricter owned-state cleanup
    contract. The constructor initializes several owned container fields as
    always-live structures (`tags`, `metadata`, `_mutation_override`,
    `disposal_method_names`, hook lists, `dependencies`), but cleanup still
    treats some of them as optional via truthy/None checks and never clears or
    deletes `_mutation_override` at all. Cleanup also leaves several scalar
    owned fields alive after teardown (`_id`, `binding_name`, `existence`,
    `permissions`, `retries`, `spell_id`, `spell_name`, `spell_type`,
    `spellframe`, `timeout`). That means the object is not fully covered by
    its own teardown contract, and some dead spell state remains readable after
    cleanup.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:192-237
  - src/melder/aether/spellbook/spell.py:334-349
  - src/melder/aether/spellbook/spell.py:421-511
  IMPACT: The current cleanup path is still mixing always-live owned
    structures with fake optionality, and it leaves stale mutation/scalar
    state attached to the cleaned object. That is exactly the contract drift
    the Python cleanup rules are meant to prevent.
  NEXT: tighten `Spell.cleanup()` so owned containers are cleared directly and
    the remaining owned state surface is deleted unless an explicit
    post-cleanup tombstone is actually required.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T13:55:04Z
  TYPE: PLAN
  CLAIM: The next focused proof slice is a cleanup micro-benchmark for
    always-live built-in containers. We want to compare:
    - 20 `if container: container.clear()` checks
    - 20 unconditional `container.clear()` calls
    on empty built-in containers, repeated 1000 times per repeat, so the hot
    path argument is measured instead of argued from intuition.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:460-476
  - tests/experimentation/none_vs_del_cleanup_performance_experiment.py:1-168
  IMPACT: This will give us a repo-local measurement for the exact cleanup
    style question before making broader cleanup-policy claims.
  NEXT: add one experimentation benchmark under `tests/experimentation/`,
    run it with pytest, and record the measured result in this ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-06T13:56:24Z
  TYPE: MEASURE
  CLAIM: The empty-container benchmark contradicts the earlier intuition for
    this exact scenario. For 20 empty built-in lists, repeated 1000 times per
    repeat across 20 repeats, `if container: container.clear()` measured about
    0.193 ms mean total repeat time, while unconditional `container.clear()`
    measured about 0.387 ms mean total repeat time. That is roughly a 2.0x
    advantage for the empty-guarded path on empty built-in lists in this local
    bench.
  EVIDENCE:
  - tests/experimentation/test_empty_clear_guard_experiment.py:8-10
  - tests/experimentation/test_empty_clear_guard_experiment.py:121-157
  IMPACT: We should stop arguing this from intuition. For the exact empty-list
    case you asked about, the guard is faster in this repo-local measurement.
    That does not automatically justify fake optionality elsewhere, but it does
    mean "always call clear because it is cheaper" is not true for this narrow
    scenario.
  NEXT: decide whether `Spell.cleanup()` should optimize for this measured
    empty-builtins case or whether we still prefer the stricter always-live
    container contract despite the micro-benchmark result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T13:57:54Z
  TYPE: FACT
  CLAIM: `Spell.cleanup()` now matches the measured empty-builtins rule
    without pretending the container fields are optional. The always-live
    built-in containers (`_pre_hooks`, `_activation_hooks`, `_post_hooks`,
    `tags`, `metadata`, `_mutation_override`, `dependencies`,
    `disposal_method_names`) still stay on the owned-state contract, but the
    cleanup path now guards `clear()` by truthiness instead of calling `clear()`
    unconditionally on empty containers. The cleanup pass still deletes the
    owned container attributes afterward, and basic scalar/tuple metadata
    remains on the cleaned object.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:335-349
  - src/melder/aether/spellbook/spell.py:457-487
  IMPACT: The spell cleanup path now aligns with both the measured empty-list
    behavior and the requested scalar-vs-container teardown boundary.
  NEXT: continue the mutation lane from the next real seam instead of spending
    more time on spell cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-06T14:13:38Z
  TYPE: MEASURE
  CLAIM: The two reported regressions from the mutation override slice are now
    fixed and passing. The component spell mutation test now matches the new
    non-dirty mutation contract: applying/clearing `mutation_override` updates
    stored payload state but does not mutate `SpellSystemState.change_reason`
    or dirty-lineage queues. The no-overrides codegen compiler unit test now
    monkeypatches the actual transient-source builder symbol present in the
    compiler module.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spell.py:248-292
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:495-530
  IMPACT: The front-door mutation contract and the no-overrides compiler test
    surface are back in sync with the current code after the runtime slice.
  NEXT: resume the next mutation-lane cleanup step instead of spending more
    time on stale expectations from the pre-overlay model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-06T14:29:47Z
  TYPE: FACT
  CLAIM: First `MutationContract` removal slice is in. The class file is
    deleted, the direct source imports are gone from Phase 1/2/4 validation
    and binding-cycle logic, and the dedicated class/experiment tests plus the
    obvious mixed-file class-instantiation tests were removed or rewritten.
    Focused changed-file validation passed. The remaining mutation references
    are the dead enum/socket-kind/mutation-targeting surfaces:
    `ParameterDIShape.MUTATION_CONTRACT`, `SocketKind.MUTATION_CONTRACT`,
    `graph_mutator`, mutation-targeting processor/analyzer paths, and tests
    that still assert those old metadata/socket contracts.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:22-24
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:14-15
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:5-6
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py:15-17
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py:468-634
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_binding_resolution_cycle_strategy.py:667-675
  - tests/unit/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder/test_spell_requirements_finder.py:554-624
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_2.py:97-195
  IMPACT: The class itself is gone and the direct import chain is stable, but
    the repo still carries a second-stage cleanup job for dead
    mutation-contract enums/socket kinds and the analyzer/processor code that
    still assumes a special mutation socket family.
  NEXT: remove the remaining dead enum/socket-kind surfaces or repoint
    mutation targeting onto the normal override targeting model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T14:40:22Z
  TYPE: FACT
  CLAIM: Phase-1 to phase-4 cleanup is still incomplete even after the class
    deletion. The compiler-facing remnants are:
    - `ParameterDIShape.MUTATION_CONTRACT`
    - phase-1 mutation-contract count in the requirements shape profile
    - phase-3 mutation-contract socket-kind mapping and metadata-only socket
      prose
    - phase-4 gating for `MUTATION_CONTRACT_MISSING_PROVIDER`
    Those remnants now describe a class and validation path that no longer
    exists.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:37-53
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:82-101
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:347-367
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:124-151
  IMPACT: We need one follow-up slice focused only on phases 1-4 so the front
    of the compiler stops advertising mutation-contract semantics that the
    runtime no longer supports.
  NEXT: remove the phase-1..4 mutation-contract enum/use sites and update the
    direct unit tests for requirements finder and compiler phases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T14:42:56Z
  TYPE: MEASURE
  CLAIM: The phase-1 to phase-4 cleanup slice is now in place and passing.
    `ParameterDIShape.MUTATION_CONTRACT` is gone, phase 1 no longer counts
    mutation-contract parameters, phase 3 no longer maps mutation-contract
    socket kinds or describes them in its local-DAG contract, and phase 4 no
    longer gates on `MUTATION_CONTRACT_MISSING_PROVIDER`. The directly coupled
    unit/component/integration tests for those fronts were removed or updated,
    and the focused changed-file test set passed. The remaining mutation
    remnants are now second-stage dead socket-kind/analyzer/graph-mutator
    surfaces, not class/import breakage in phases 1-4.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:1-50
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:68-96
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:347-367
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:124-147
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py:902-1080
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py:200-235
  IMPACT: The front of the compiler is now largely free of direct
    `MutationContract` semantics. The next cleanup slice should target the
    dead socket-kind and analyzer/graph-mutator assumptions, not revisit
    phase-1..4.
  NEXT: remove or repoint `SocketKind.MUTATION_CONTRACT` and the mutation-only
    analyzer/graph-mutator paths onto the normal override targeting model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T14:53:24Z
  TYPE: MEASURE
  CLAIM: The phase-6 and phase-8 cleanup slice is now in place and passing.
    Contract-cycle validation is SpellContract-only now, and the phase-8
    occurrence analyzer no longer treats stored `mutation_override` payloads
    as a graph-shaping concern: fast key/signature ignore them, the graph build
    no longer applies mutation override rewrites into dependencies, and the
    compatibility `mutation_override_dependency_count` is frozen to zero.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/contract_graph_cycle_strategy.py:101-103
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:157-198
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:261-274
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:392-400
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:704-719
  IMPACT: Phases 5-8 no longer carry active mutation-contract semantics in the
    front of the compiler. The remaining mutation-specific cleanup work is
    outside this pass: phase-9 model/processor fields, phase-10/11 mutation
    lanes, and dead runtime helpers like `graph_mutator`.
  NEXT: stop here for the phases-5..8 pass and only continue into phase 9+
    when explicitly directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:04:44Z
  TYPE: FACT
  CLAIM: The last active phase-8 compiler residue is gone. The occurrence
    graph artifact no longer carries `mutation_override_dependency_count`,
    shared export rows no longer serialize it, and the phase-8 unit/component
    tests no longer assert mutation-specific analyzer behavior. The only
    mutation-specific compiler surfaces still left in the repo now live after
    phase 8: phase-9 mutation-targeting model/processor fields, phase-10/11
    mutation lanes, and dead helper/doc strings around `SocketKind.MUTATION_CONTRACT`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_graph_analysis.py:23-31
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1428-1436
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:131-301
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:92-104
  IMPACT: Phases 1-8 are no longer carrying live mutation-override accounting
    or mutation-contract compiler behavior. The remaining mutation-specific
    cleanup work is truly phase 9+ and runtime/helper cleanup now.
  NEXT: stop phase-1..8 cleanup here and move to phase-9+ only when directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:17:34Z
  TYPE: FACT
  CLAIM: The remaining compiler mutation lane after phase 8 is still explicit
    in both phase 9 and phase 10. Phase 9 still carries a dedicated
    `mutation_targeting_shape` section plus mutation-specific top-level
    counters on `SpellCodegenModel`, and phase 10 still materializes a third
    public planner lane through `mutation_overrides_plan` in the generalized
    planner strategy. That means the compiler still treats mutation as its own
    processor/planner family instead of as ordinary override truth.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:32-305
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_mutation_targeting_analysis.py:1-99
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_mutation_targeting_processor_strategy.py:1-164
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-80
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-69
  IMPACT: The next cleanup slice is no longer "look for leftover phase-8
    behavior." It is to delete the mutation-specific processor section/counters
    and collapse the planner output to only `no_overrides_plan` and
    `overrides_plan`.
  NEXT: inspect the remaining phase-9 shell/builder/discovery surfaces and the
    directly coupled planner tests, then remove the third lane with the smallest
    coherent edit set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:18:17Z
  TYPE: FACT
  CLAIM: The phase-9 and phase-10 removal surface is tightly bounded now.
    Phase 9 still auto-loads `SpellMutationTargetingProcessorStrategy` from the
    processor strategy builder, and the direct planner/discovery tests still
    assert `mutation_overrides_plan` exists on the plan shell and cleanup path.
    That means the smallest coherent edit set is not broad discovery rewiring.
    It is:
    - delete the mutation-targeting processor section from the phase-9 model
      and builder chain
    - delete `mutation_overrides_plan` from the plan object and generalized
      planner strategy
    - update the directly coupled unit/component tests that still pin the third
      lane
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-150
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-147
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-199
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:1-172
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:154-154
  IMPACT: We do not need more mapping to start the phase-9/10 cleanup slice.
    The direct source/test boundary is clear enough to edit now.
  NEXT: remove the mutation processor/model/plan surfaces and then run the
    directly coupled phase-9/10 planner tests before widening outward.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:26:02Z
  TYPE: MEASURE
  CLAIM: The phase-9/10 cleanup slice is landed on the focused compiler
    surface. Phase 9 no longer carries a mutation-targeting data section,
    mutation-targeting processor strategy, or mutation-specific top-level model
    counters. Phase 10 no longer carries `mutation_overrides_plan`, and the
    generalized planner now builds only `no_overrides` and `overrides`. The
    shared phase8_11 IR export also stopped serializing mutation-target counts
    and mutation step counts. The directly coupled processor/planner/migration
    and component discovery tests pass after the removal.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-274
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-144
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-72
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-131
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-64
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:22-39
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1391-1458
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py:1-208
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py:1-215
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-190
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:1-697
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:1-154
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-176
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-206
  IMPACT: Phases 9-10 no longer encode mutation as a first-class processor or
    planner lane. The remaining special mutation surfaces now start in phase 11
    codegen creation and its directly coupled tests/strategies.
  NEXT: move to the phase-11/codegen-creation removal slice and delete the
    mutation-specific creation discovery/strategy/output family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:28:01Z
  TYPE: FACT
  CLAIM: One narrow phase-11 follow-through was required to keep the compiler
    coherent after the phase-10 lane removal. Generalized phase-11 discovery
    no longer selects `generalized_mutation_overrides_codegen_creation`, so the
    full compiler path does not immediately route into a dead mutation plan
    surface after `mutation_overrides_plan` was removed. This was a discovery
    selection fix only; the remaining mutation-specific creation strategy,
    creation payload fields, and creation-core tests are still the next cleanup
    seam.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-52
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-206
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-176
  IMPACT: The active compiler path is no longer selecting the removed mutation
    planner lane. The remaining work can now stay focused on phase-11 creation
    artifacts instead of backfilling broken discovery wiring.
  NEXT: remove the unused mutation-specific creation strategy/output family,
    then do the final creation-context cleanup pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:31:32Z
  TYPE: FACT
  CLAIM: The remaining mutation-specific runtime family is now tightly bounded
    to phase 11 creation payload fields plus `CreationContextBuilder` /
    `CreationContext` rehydration. `SpellCodegenCreation` still stores a full
    second override route under `override_mutation_*`, the codegen strategy
    builder still registers `generalized_mutation_overrides_codegen_creation`,
    and `CreationContextBuilder.build(...)` still rehydrates both
    `override_route_config_no_mutation` and `override_route_config_mutation`
    even though the front-door runtime now routes caller overrides and stored
    mutation payloads through the same normal override path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-175
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-110
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_mutation_overrides_codegen_creation_strategy.py:1-184
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-197
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1377
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-819
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-216
  IMPACT: The final cleanup can stay narrow. We do not need more planner work;
    we need to delete the mutation-specific creation strategy/output family and
    collapse runtime rehydration to one normal override route config.
  NEXT: remove `generalized_mutation_overrides_codegen_creation`,
    delete `override_mutation_*` fields from `SpellCodegenCreation`, collapse
    `CreationContextBuilder` / `CreationContext` to one override route config,
    and update the directly coupled tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:42:01Z
  TYPE: MEASURE
  CLAIM: The phase-11 creation and `CreationContext` cleanup slice is landed on
    the focused runtime/compiler surface. The mutation-specific creation
    strategy file is deleted, the creation strategy builder no longer registers
    it, `SpellCodegenCreation` now carries one generic override route payload
    instead of split `override_no_mutation_*` / `override_mutation_*` fields,
    and `CreationContextBuilder` / `CreationContext` now rehydrate and retain
    exactly one `OverrideRouteConfig`. The directly coupled creation/discovery
    and creation-context tests pass after the collapse.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-159
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-105
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-85
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:1-180
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-172
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1370
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-747
  - tests/unit/melder/spellbook/spell_compiler/test_creation_context_core.py:1-314
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-200
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-1573
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-206
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-176
  IMPACT: The compiler/runtime no longer preserves a mutation-specific public
    phase-11 creation family. Stored `mutation_override` now feeds the same
    normal override runtime path end-to-end, and caller `spell_override`
    remains the replacing higher-priority payload.
  NEXT: run one broader spell-compiler/runtime sanity pass if we want extra
    confidence, otherwise the remaining work is ticket/epic cleanup and any
    leftover dead helper/tests outside the focused surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T15:51:27Z
  TYPE: FACT
  CLAIM: The remaining no-compat cleanup is now narrowly bounded to dead
    metadata/comment/helper residue, not live planner/runtime behavior.
    Current leftovers are:
    - dead symbolic/IR commentary still naming `MUTATION_CONTRACT`
    - the `DagIndex` docstring still saying it powers `mutation_override`
    - a small test stub field `has_mutation_override` in creation-context
      factory tests
    - phase-8 analyzer tests still constructing `mutation_override=None` on
      spell stubs even though the analyzer no longer reads it
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/dag_index.py:286-293
  - src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_graph.py:124-131
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py:96-104
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:47-55
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:137-145
  IMPACT: We do not need another semantic pass. The remaining work is a final
    no-compat scrub so the compiler and creation-context surfaces stop even
    naming removed mutation-era concepts where they are no longer real.
  NEXT: remove the last dead comments/fields/test-stub inputs and then run a
    focused sanity pass over the touched compiler/creation-context files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-06T15:54:32Z
  TYPE: MEASURE
  CLAIM: The final no-compat scrub is complete on the targeted surfaces.
    Compiler phases 1-11 and `CreationContext` no longer carry mutation-era
    compatibility names or helper structures:
    - no `MUTATION_CONTRACT` / `MutationContract` references remain under the
      targeted compiler and creation-context paths
    - no `mutation_overrides_plan` or mutation creation-family fields remain
    - no split `override_no_mutation_*` / `override_mutation_*` runtime payload
      remains
    - the dead `GraphMutator` helper and its dedicated tests are gone
    The only remaining mutation concept is the stored payload on `Spell` and
    the normal override use in meld front doors.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/socket_kind.py:1-19
  - src/melder/aether/spellbook/spell_compiler/symbolic_graph/spell_symbolic_dependency.py:1-242
  - src/melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py:1-140
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:97-177
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:528-556
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:280-312
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-159
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-172
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1370
  - src/melder/aether/conduit/meld/conduit_meld.py:216-220
  - src/melder/aether/conduit/meld/spellspace_meld.py:222-226
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-214
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:1-154
  IMPACT: The mutation cleanup objective is satisfied on the requested
    surfaces. Remaining work is no longer semantic cleanup; it is lane closure,
    broader optional sanity runs, and any repo areas outside the requested
    compiler/creation-context scope.
  NEXT: decide whether to run a broader repo sanity suite or move this lane
    toward cleanup/closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T16:26:28Z
  TYPE: FACT
  CLAIM: The remaining overbuild is not "mutation compatibility" anymore. It
    is that `CreationContext` still owns too much spell-static override
    machinery. Current phase-11 output already gives it a direct
    `no_overrides_executor`, but the override side still passes a structural
    ingredient bag (`override_targeting`, route config fields, baseline
    executor, path registry, plan rows, spell lookup). `CreationContext` then
    turns that into a runtime specialization subsystem with:
    - shape caches
    - emitted-source cache
    - code-object cache
    - grouped-target preprocessing
    - override executor compilation on cache miss
    Hooks are a separate concern: the hook/no-hook split is chosen outside
    `CreationContext` by meld-front-door orchestration, so hooks should not be
    part of the phase-11 output contract.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:229-288
  - src/melder/aether/conduit/meld/spellspace_meld.py:238-297
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:166-190
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:272-345
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:571-740
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:98-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:47-99
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:51-109
  IMPACT: The next architecture refactor is clear. Phase 11 should output only
    `no_overrides` and `overrides` runtime doors. Hooks remain outer meld
    orchestration. The heavy override specialization/caching logic should move
    out of `CreationContext` and into the phase-11-produced override runtime
    pack itself.
  NEXT: define the minimal phase-11 output contract as two runtime doors plus
    any hidden closed-over runtime pack needed to execute them, with no
    plan-row/path-registry/spell-lookup ingredient bag exposed to
    `CreationContext`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:00:34Z
  TYPE: PLAN
  CLAIM: The implementation path is now narrow enough to code directly. Add one
    new fat phase-11 strategy `general_creation_context_codegen_creation`
    without deleting the existing strategy files. That new strategy should:
    - build the current no-overrides executor
    - build one private override runtime pack owning the current
      `CreationContext` override specialization machinery
    - expose only two final runtime doors on `SpellCodegenCreation`:
      `no_overrides_executor` and `overrides_executor`
    The two executors should return `(instance, created)` so meld can keep
    activation-hook behavior outside phase 11 while `CreationContext` becomes a
    thin dispatcher.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:658-695
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:568-619
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:4-192
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:571-977
  IMPACT: We can now do the phase-11 convergence as one deliberate shove
    instead of another mapping pass. The resulting runtime contract will match
    the desired end shape even if the internal implementation is still fat.
  NEXT: implement the new fat phase-11 strategy, remodel
    `SpellCodegenCreation`, simplify `CreationContextBuilder` /
    `CreationContext`, and update the directly coupled tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:35:40Z
  TYPE: MEASURE
  CLAIM: The phase-11 extension is landed the way the user asked for it:
    generalized phase-11 discovery now extends the existing chain with
    `general_creation_context_codegen_creation` as the finalizer instead of
    replacing the older generalized strategies. The earlier setup,
    no-overrides, and overrides strategies still run, but they now feed scratch
    state into the new finalizer through `SpellCodegenCreation.metadata`. The
    new finalizer builds the final runtime doors:
    - `no_overrides_executor`
    - `overrides_executor`
    Then `CreationContextBuilder` passes only those doors into a thin
    `CreationContext`, and meld front doors now call
    `creation_context.execute(...)` / `execute_no_hooks(...)` instead of
    reaching into internal compiled-door fields.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-55
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-109
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:1-95
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:1-132
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:1-210
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-370
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-62
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-108
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-138
  - src/melder/aether/conduit/meld/conduit_meld.py:229-279
  - src/melder/aether/conduit/meld/spellspace_meld.py:238-288
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-411
  - tests/unit/melder/spellbook/spell_compiler/test_creation_context_core.py:1-223
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-124
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-145
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-206
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-176
  IMPACT: Phase 11 now owns the final runtime handoff shape the user wanted,
    and `CreationContext` is no longer a mini compiler for override execution.
    Remaining work is optional broader validation and later breakup of the fat
    finalizer into smaller strategies if desired.
  NEXT: decide whether to run a broader compiler/runtime sanity pass or begin
    cleanup/closure for this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:42:12Z
  TYPE: MEASURE
  CLAIM: The extended phase-11 chain plus the thin `CreationContext`
    dispatcher are green on the focused runtime/compiler surface after the
    last implementation fixes. The key fix after the first pass was to stop
    closing over `spell._owner_creations` too early inside phase 11. The new
    finalizer now emits runtime closures that read owner-creations from the
    live spell at call time, so shared-lineage no-overrides/overrides routes
    no longer dereference `None` owner storage. Meld test stubs and direct
    creation-context tests were also updated to the new public
    `execute(...)` / `execute_no_hooks(...)` contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-370
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-138
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-108
  - src/melder/aether/conduit/meld/conduit_meld.py:229-279
  - src/melder/aether/conduit/meld/spellspace_meld.py:238-288
  - tests/unit/melder/aether/conduit/meld/test_meld.py:620-718
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:51-151
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-411
  - tests/unit/melder/spellbook/spell_compiler/test_creation_context_core.py:1-223
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-124
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-145
  IMPACT: The requested phase-11 extension is now stable on the focused suite.
    Remaining work is only broader optional repo validation or lane
    cleanup/closure.
  NEXT: decide whether to run a broader repo sanity pass or start closing the
    mutation convergence lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:47:34Z
  TYPE: DECISION
  CLAIM: The user explicitly wants continued cleanup on non-DevOps fallout, so
    the lane is staying open for broader spell-compiler / meld / conduit test
    repair. DevOps-specific failures are out of scope for this tranche.
  EVIDENCE:
  - codex/context_compass/attention_board.md:24-33
  IMPACT: Validation scope is now broader than the tightly focused phase-11
    suites, but still bounded away from the DevOps lane.
  NEXT: iterate on broader non-DevOps failing tests from the repo suite and
    repair the remaining runtime/compiler fallout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-06T17:57:08Z
  TYPE: FACT
  CLAIM: The likely hot-path regression vector is now explicit in the new
    phase-11 finalizer. The current
    `general_creation_context_codegen_creation` strategy does not hand through
    the old runtime doors 1:1. Instead it wraps the no-overrides executor and
    the override runtime in new closures, does per-call
    `get_creation(...)` probes through `_will_create_instance(...)` to recover
    the `created` flag, and then routes meld through the new public
    `CreationContext.execute(...)` / `execute_no_hooks(...)` dispatcher.
    That means the runtime surface is architecturally converged, but the hot
    path is no longer a direct transplant of the previous execution shape.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:150-231
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:300-516
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:82-147
  - src/melder/aether/conduit/meld/conduit_meld.py:218-256
  - src/melder/aether/conduit/meld/spellspace_meld.py:224-265
  IMPACT: The current code can be structurally cleaner while still being
    slower. If we want the old hot-path profile back, phase 11 likely needs to
    emit the final direct executors again instead of wrapping them just to
    synthesize `created` and then dispatching through another layer.
  NEXT: compare the old direct CreationContext executor shape against the new
    finalizer wrappers and decide whether `created` needs to move back into the
    emitted executors instead of being recovered by wrapper probes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:58:22Z
  TYPE: FACT
  CLAIM: The previous runtime path already encoded `created` directly inside
    the emitted route bodies. The old `creation_context_codegen` templates
    return `(instance, created)` inline for each route, and the older
    `CreationContext` owned the override specialization caches plus the direct
    compiled doors that consumed those emitted semantics. So the new phase-11
    finalizer is not preserving old behavior by necessity; it is re-deriving
    route-created status in wrapper code that the generated runtime already
    knew how to emit.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:4-199
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:512-883
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:899-906
  - src/melder/aether/conduit/meld/creation_context/old_creation_context.py:293-342
  - src/melder/aether/conduit/meld/creation_context/old_creation_context.py:410-740
  IMPACT: The clean fix path is now much clearer. We do not need to keep
    wrapper-level `created` probes around the final runtime doors if we are
    willing to let the emitted route bodies remain the owner of
    `created=True/False` semantics.
  NEXT: inspect the remaining phase-11 export surfaces that still assume the
    old artifact shape, then decide whether to revert to direct emitted doors
    or rebuild the new finalizer so it emits those semantics instead of
    probing for them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T17:58:54Z
  TYPE: FACT
  CLAIM: The phase-11 remodel is still carrying stale export-shape residue.
    `SpellCodegenCreation` now stores only the two final runtime doors plus
    metadata, but `SharedCompilerExecutions.capture_phase8_11_codegen_ir(...)`
    still dereferences removed top-level fields like `resolve_route_key`,
    `fast_transient_no_overrides_enabled`, and
    `no_overrides_executor_signature`. The generalized setup/no-overrides/
    overrides strategies are compensating by stuffing old scratch fields into
    `spell_codegen_creation.metadata`, and the new finalizer is then reading
    and popping those metadata keys. So the phase-11 chain is currently split
    between the new final door contract and an old compatibility-shaped export
    and scratch-data story.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:8-69
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:35-67
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:57-91
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:64-111
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:96-137
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1331-1410
  IMPACT: Even if we fix the runtime hot path, the phase-11 remodel is still
    paying for an unfinished compatibility layer. Cleaning that residue is part
    of finishing the new output model and will also reduce confusion about what
    phase 11 actually owns now.
  NEXT: finish tracing the live runtime door path through meld and then decide
    whether to first remove the wrapper/probe overhead or first clean the stale
    phase-11 export/scratch surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T18:14:49Z
  TYPE: MEASURE
  CLAIM: The hot-path restore slice is landed and the direct runtime surface is
    green again. The phase-11 finalizer no longer wraps the base no-overrides
    and override runtime callables just to probe `created`. Instead it now
    hands `CreationContext` the underlying spell-static executor inputs
    directly. `CreationContext` is no longer the thin `_dispatch(...)` shell;
    it once again compiles and owns the direct hooks/no-hooks doors using the
    old `creation_context_codegen` route templates, while the heavy override
    specialization work stays moved out into the phase-11-provided override
    runtime callable. The stale phase-11 IR export also now reads creation
    metadata instead of dereferencing removed top-level fields on
    `SpellCodegenCreation`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-533
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-280
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-117
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-69
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1331-1415
  IMPACT: The worst self-inflicted wrapper/probe overhead is gone, and the
    runtime shape now matches the old direct CreationContext door model much
    more closely without pulling the override specialization caches back into
    the runtime object.
  NEXT: if we want more confidence, run a broader non-DevOps repo sweep next
    instead of only the targeted creation-context / meld / compiler tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T18:14:49Z
  TYPE: MEASURE
  CLAIM: Focused validation is green on the restored runtime surface when run
    under the repo's `.venv_new` interpreter. The system `python` executable
    is not a trustworthy validation surface here because it trips eager
    annotation evaluation on files that rely on the repo's 3.14 deferred-
    annotation contract. Using `.venv_new\\Scripts\\python.exe` the touched
    unit/component slice passes:
    - `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
    - `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py`
    - `tests/unit/melder/spellbook/spell_compiler/test_creation_context_core.py`
    - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py`
    - `tests/unit/melder/aether/conduit/meld/test_meld.py`
    - `tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py`
    - `tests/component/melder/spellbook/test_spell_compiler_component_system.py`
    - `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-154
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-138
  - tests/unit/melder/spellbook/spell_compiler/test_creation_context_core.py:1-224
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-503
  - tests/unit/melder/aether/conduit/meld/test_meld.py:620-718
  - tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py:51-151
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py:689-703
  - tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:474-489
  IMPACT: The local hot-path restore did not break the directly coupled
    runtime/compiler surfaces, and the interpreter mismatch is now explicit
    instead of looking like a random regression in this slice.
  NEXT: decide whether to widen into a broader non-DevOps repo suite or stop
    after the targeted passing surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T18:18:17Z
  TYPE: MEASURE
  CLAIM: The broader non-DevOps repo sweep is now effectively clean for this
    lane. After the hot-path restore and the stale `contract_late_binding`
    test cleanup, rerunning
    `.venv_new\\Scripts\\python.exe -m pytest -q --ignore-glob=\"*dev_ops*\"`
    leaves only five failures, all in
    `tests/integration/melder/aether/test_aether_integration_change_control_transactions.py`.
    Those remaining failures are all the same transaction-mediator
    `configure(change_control_mode=...)` signature mismatch, which is the
    change-control / transaction lane the user explicitly wanted ignored for
    this pass. The two ConduitWard stale tests are fixed, and the conduit
    cluster concurrency test passes again in isolation and no longer fails in
    the broader rerun.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:2370-2516
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:960-1005
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:324-665
  IMPACT: The mutation/compiler hot-path lane is no longer carrying hidden
    fallout outside the explicitly ignored change-control lane. We can stop
    here cleanly unless the user wants to reopen the mediator tests too.
  NEXT: keep the lane scoped away from the ignored change-control tests unless
    the user explicitly redirects back into them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the downstream mutation convergence map. The current evidence
now says phases 9-10 are cleaned: the processor no longer carries mutation
targeting and the planner no longer emits a third mutation lane. Phase 11
creation and `CreationContext` are now also collapsed to one normal override
family. The phase-11 generalized chain is now extended with a fat finalizer
strategy rather than replaced. `SpellCodegenCreation` now carries only the two
final runtime doors, and meld uses the thin `CreationContext` public surface.
Remaining work is broader optional sanity validation or later breakup of the
fat finalizer.
