# Task: Define execution strategy phase 12

## Metadata
- Task ID: TASK-2026-05-30-define-execution-strategy-phase-12
- Story: none
- Status: in_progress
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T18:24:53Z
- Updated: 2026-05-30T20:29:29Z

## Objective
Define the new compiler-owned Phase 12 strategy/right-sizing stage that should
sit between current Phase 11 raw execution-plan truth and the future final
executor emission phase, then map how that stage should wire into artifact
state and `CreationContext`.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested focus on the new Phase 12 design
  after the compiler-strategy epic and direction artifact were created.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_no_overrides_executor.py`
  - `src/melder/aether/spellbook/spell_compiler/blueprints/phase13_overrides_executor.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
- EXIT_GATE:
  - the new Phase 12 responsibility is explicit
  - its exact inputs and outputs are explicit
  - the current Phase 13 role is explicit
  - the `CreationContext` consequence/wiring map is explicit
  - the first bounded implementation order is explicit
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the design implies replacing
  current Phase 11 plan truth instead of extending it.

## Scope Boundaries
- In scope:
  - defining the new strategy/right-sizing stage
  - mapping artifact-owned inputs/outputs
  - mapping how the new Phase 12 sits above current Phase 13
  - mapping `CreationContext` consequences
- Out of scope:
  - source-code implementation
  - test execution
  - broad compiler rewrite

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the active lane to the new
  Phase 12 strategy-stage design.

## Steps / Checklist
- [ ] Reconfirm current Phase 10-12 and `CreationContext` responsibilities.
- [ ] Define the exact responsibility of the new Phase 12 strategy stage.
- [ ] Define the exact artifact it should produce.
- [ ] Define the current Phase 13 emitter role.
- [ ] Define the `CreationContext` and `CreationContextBuilder` consequence map.
- [ ] Define the first bounded implementation order.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further design expansion.

## Deliverables
- one explicit new Phase 12 role
- one explicit strategy artifact outline
- one explicit current Phase 13 role
- one explicit `CreationContext` consequence map

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-30_define_execution_strategy_phase12_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "phase12|dispatch_route|creation_context|execution_plan" src/melder/aether`

## Risks / Rollback Notes
- Risk: the design could drift into “replace the compiler” instead of
  “right-size and extend the current compiler”.
- Rollback: keep the lane descriptive only and do not turn design claims into
  code changes until a later implementation slice.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No compiler-rewrite claims without source-backed producer/consumer mapping.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after direction acceptance

## Noting Behavior
- Note focus: phase role clarity, artifact ownership, and wiring order.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: The earlier Phase 12 summary was too narrow because it treated the new
    shape profiles as the primary inputs and underplayed the richer artifact
    surfaces already present. The real Phase 12 input set is broader:
    structural artifacts (`_requirements`, `_symbolic_graph`,
    `_resolution_frame`, `_validation_result_phase4`, `_validation_result_phase6`),
    rooted artifacts (`_root_blueprint_phase5`, `_spell_system_index_phase5`,
    `_entire_dag_blueprint_phase5`), planning artifacts
    (`_occurrence_plan_phase8`, `_injection_plan_phase9`,
    `_override_patch_map_phase10`, `_mutation_patch_map_phase10`,
    `_execution_plan_phase11*`), exported IR state (`_codegen_ir`,
    `_phase8_11_codegen_ir_dirty`, `_phase11_no_overrides_plan_signature`,
    `_phase11_no_overrides_transient_schema`), and the newer shape profiles.
    The shape profiles are strategy-friendly summaries, but they are not the
    whole Phase 12 truth surface.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:58-101
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:124-167
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:373-431
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:435-474
  IMPACT: The first Phase 12 scaffold should model examination inputs as a
    full compiler artifact view, not just a profile bag. Strategies can choose
    summarized facts when they are enough, but the system should still have
    access to the richer rooted/plan/IR artifacts when needed.
  NEXT: Define `SpellExaminationInput` so it exposes both the profile layer and
    the richer artifact layer, with the strategies deciding how deep they need
    to read.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: `Spell` and `SpellCompilerArtifact` already expose the clean ownership
    seam Phase 12 needs. `Spell` is the spell-owned runtime holder for
    `CreationContext`, `CreationContextFactory`, the publication switch,
    mutation overlay state, conduit ownership, and the one remaining runtime
    dispatch hint on the spell itself (`execution_plan_dispatch_route`). In
    contrast, `SpellCompilerArtifact` is already the compiler-owned phase cache
    surface for Phase 1 shape, Phase 5 rooted artifacts, Phases 8-11 plans and
    shape profiles, the Phase 11 -> 13 no-overrides handoff, and exported
    codegen IR. That means the new Phase 12 output should live on
    `SpellCompilerArtifact` as the next compiler-owned artifact layer instead
    of being smeared back onto `Spell`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:194-228
  - src/melder/aether/spellbook/spell.py:353-377
  - src/melder/aether/spellbook/spell.py:566-679
  - src/melder/aether/spellbook/spell.py:947-983
  - src/melder/aether/spellbook/spell.py:991-1037
  - src/melder/aether/spellbook/spell.py:1151-1222
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:37-98
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:125-164
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:373-431
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:435-473
  IMPACT: We do not need another ownership debate for the Phase 12 plan. The
    compiler-owned result belongs on the artifact; `Spell` should keep only the
    runtime-owned state that binds or reacts to that result.
  NEXT: Define the first `SpellCodegenPlan` fields directly on
    `SpellCompilerArtifact` and keep only the spell-facing runtime bind hooks on
    `Spell`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: The recent epics line up cleanly into the current Phase 12/13
    direction. The older AOT/override-free compiler epic already established
    that the real runtime split is Phase 11 plan truth + late `CreationContext`
    specialization + a dedicated no-overrides compiled lane, while the old
    spellspace ownership epic established that route/storage ownership is
    already a real seam and not just a bucket detail. The current active epic
    is the first umbrella that correctly combines those two truths into one new
    compiler stage: Phase 12 must examine and shape, not just forward existing
    plan artifacts, and Phase 13 must emit from that shaped plan instead of
    rediscovering route/override/storage shape late.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-05-11_investigate_aot_creation_context_override_disable_and_no_overrides_compiler_path_epic.md:70-76
  - codex/context_compass/tickets/epics/2026-05-11_investigate_aot_creation_context_override_disable_and_no_overrides_compiler_path_epic.md:249-300
  - codex/context_compass/tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md:217-258
  - codex/context_compass/tickets/epics/completed/2026-05-27_spellspace_sharded_runtime_ownership_epic.md:112-182
  - codex/context_compass/tickets/epics/completed/2026-05-27_spellspace_sharded_runtime_ownership_epic.md:428-500
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md:174-242
  IMPACT: We do not need another design reset. The current Phase 12 scaffold
    can proceed directly from the active epic, with the older epics treated as
    supporting evidence for why examination, plan-shaping, and route-aware
    output families belong there.
  NEXT: Start the Phase 12 scaffold from the active epic contract and avoid
    reopening the old "just skip overrides" or "just split spellspace storage"
    ideas as separate design umbrellas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: The current Phase 11 -> 12 -> 13 seam is now explicit in source.
    Phase 11 already computes and stores the no-overrides handoff signature and
    transient schema for Phase 13, Phase 12 is still a true no-op placeholder,
    Phase 13 currently only compiles the no-overrides executor from plan or IR
    payload, and `CreationContext` still owns the heavy late-stage route
    selection plus override specialization caches and override-executor compile
    machinery. That means the new Phase 12 has to absorb real examination and
    codegen-plan shaping work instead of just selecting a label.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:657-710
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:730-880
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:11-55
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:23-245
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:161-325
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:585-708
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1171-1331
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:115-189
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:228-289
  IMPACT: If Phase 12 does not take over the examination and codegen-plan
    shaping burden, Phase 13 and `CreationContext` will keep rediscovering
    shape too late and the new phase will collapse into another generic pass.
  NEXT: Scaffold the Phase 12 class set and the first `SpellCodegenPlan`
    artifact so the examination and plan-shaping work has a real home.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: The meld and creations runtime split is also explicit now. `Meld` is
    an abstract shared resolution core, `ConduitMeld` and `SpellSpaceMeld` are
    the concrete front doors, `CreationContextBuilder` chooses route families
    from existence, `Creations` is the slim scoped live-object registry, and
    `ConduitCreations` is currently only a conduit/root override seam on top of
    the base scoped store. That means future Phase 12 codegen families should
    target these concrete route/storage boundaries directly rather than assume
    one generic caller-creations model.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:42-92
  - src/melder/aether/conduit/meld/meld.py:215-500
  - src/melder/aether/conduit/meld/conduit_meld.py:13-515
  - src/melder/aether/conduit/meld/spellspace_meld.py:15-527
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:115-151
  - src/melder/aether/conduit/creations/creations.py:1-366
  - src/melder/aether/conduit/creations/conduit_creations.py:9-73
  IMPACT: The right-sized compiler families can and should be route-aware:
    shared, conduit-local, spellspace-local, transient-many, and
    existing-creation all already exist as real runtime seams.
  NEXT: Use these route/storage seams when defining the first `SpellExamination`
    and `SpellCodegenPlanStrategy` contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: DECISION
  CLAIM: The active investigation pass is intentionally expanding beyond the
    default five-file microcycle gate because the user explicitly requested a
    full source read of Phases 1-13, the full creation-context subtree, meld,
    conduit meld, spellspace meld, creations, and conduit creations before the
    next Phase 12 implementation slice.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/config/context_compass_config.yaml:76-90
  IMPACT: This pass is a deliberate source-grounding tranche for the Phase 12
    lane rather than an opportunistic repo scan, so the expanded read boundary
    is accepted and should be summarized back into notes before implementation
    begins.
  NEXT: Read the requested compiler, creation-context, meld, and creations
    files in full, then append one source-backed summary note for the current
    Phase 12 handoff seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:29:29Z
  TYPE: FACT
  CLAIM: The Phase 12 direction is now captured in the spirit artifact at the
    concrete class level instead of only at the abstract strategy-stage level.
    The documented model is: Phase 12 owns `SpellExaminationBuilder`,
    `SpellExaminationStrategy`, `SpellExaminationSystem`,
    `SpellCodegenPlanStrategyBuilder`, and `SpellCodegenPlanStrategy`; Phase
    13 owns `SpellCodegenStrategy`, `SpellCodegenBuilder`, and
    `SpellCodegenCreatorSystem`.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md
  IMPACT: The task can now move from design-only clarification into the Phase
    12 scaffold without relying on chat-only memory for the target class map.
  NEXT: scaffold the Phase 12 classes and the first `SpellCodegenPlan`
    artifact surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T18:24:53Z
  TYPE: FACT
  CLAIM: The current `phase 11 -> 12 -> CreationContext` seam is split in the
    wrong place. Phase 11 already builds the raw execution-plan truth and shape
    metrics, current Phase 13 mostly compiles the no-overrides backend from the
    Phase 11 handoff or exported payload, and `CreationContext` still owns too
    much late strategy/customization pressure through route-family binding,
    fast-transient eligibility checks, patch-map binding, and override
    specialization machinery. That means the missing piece is not more raw plan
    generation; it is a compiler-owned strategy/right-sizing stage between raw
    plan truth and final backend emission.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:660-809
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:41-222
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:62-99
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-429
  IMPACT: The new Phase 12 should consume current Phase 11 truth and produce a
    compiler-owned strategy artifact, while current Phase 13 should stay the
    backend emitter role and `CreationContext` should thin into a
    binder of chosen outputs.
  NEXT: define the exact inputs, outputs, and artifact fields for the new
    strategy phase before discussing concrete strategy families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T18:24:53Z
  TYPE: PLAN
  CLAIM: The user wants to focus next on the new Phase 12 itself: what it
    consumes, what it outputs, how it changes current Phase 12, and what
    `CreationContext` should become as a result. This task is the narrow design
    lane for that question.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md
  IMPACT: The next step is to define the strategy-stage contract precisely
    enough that implementation can be sliced cleanly later.
  NEXT: map the new Phase 12 inputs and outputs directly against current Phase
    10-12 and `CreationContext`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to define the new compiler-owned strategy/right-sizing phase
and its exact relationship to current Phase 10-13 and `CreationContext`.
