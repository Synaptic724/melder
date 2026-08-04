# Task: Investigate Meld, CreationContext, and Phase 10-12 Creation Runtime

## Metadata
- Task ID: TASK-2026-05-26-investigate-meld-creation-context-phase10-12-creation-runtime
- Story: none
- Status: done
- Owner: codex
- Agent Name: guard_check_0
- Priority: p0
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Read the live `Meld`, `CreationContext`, Phase 10-12 spell-compiler seam, and
the `Creations` / `Creation` runtime so we can explain where time is being
spent, where work is being saved already, and where the next bounded hot-path
cuts actually are.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a source-first investigation of
  `meld`, `creation_context`, compiler phases `10-12`, `creations`, and
  `creation`.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - directly required nearby creation-context files only when the call/ownership
    claim cannot be resolved from `creation_context.py` alone:
    - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
    - `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
    - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
  - directly required nearby compiler artifacts only when a phase claim cannot
    be resolved locally
  - `src/melder/aether/conduit/creations/creations.py`
  - `src/melder/aether/conduit/creations/creation.py`
  - `codex/context_compass/tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_investigate_phase_scheduler_and_spell_compiler_pipeline_task.md`
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
  - `tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md`
- EXIT_GATE: the investigation produces one evidence-backed ownership and hot
  path map across `Meld`, `CreationContext`, phases `10-12`, `Creations`, and
  `Creation`, plus one bounded recommendation for the next savings cut.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation must widen
  beyond this runtime/compiler seam into broader scheduler or transaction
  redesign work.

## Scope Boundaries
- In scope:
  - `Meld` runtime ownership and lookup/reuse flow
  - `CreationContext` ownership, dispatch, and compiled-executor seam
  - what phases `10-12` actually own today
  - `Creations` and `Creation` storage/disposal/runtime responsibilities
  - explicit current sources of saved work or repeated work
- Out of scope:
  - runtime edits before the investigation result is reviewed
  - benchmark runs
  - broad scheduler redesign
  - broad transaction/dev-ops redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a bounded read of the meld,
  creation-context, phase `10-12`, and creations runtime seam.

## Steps / Checklist
- [ ] Count and read the target files in bounded chunks.
- [ ] Map `Meld` ownership, lookup, reuse, and gating responsibilities.
- [ ] Map `CreationContext` runtime ownership and execution dispatch.
- [ ] Map what phases `10-12` actually prepare, cache, or compile for the
      creation/runtime path.
- [ ] Map `Creations` and `Creation` storage, lock, and disposal cost surfaces.
- [ ] Summarize one bounded hot-path savings target with direct evidence.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- one evidence-backed map of the current creation/runtime seam
- one bounded recommendation for the next time-saving cut

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "CreationContext|ExecutionPlan|OverridePatchMap|MutationPatchMap|compile_no_overrides_executor|Creations|Creation" src/melder/aether`

## Risks / Rollback Notes
- Risk: the creation/runtime seam crosses more files than the top-level names
  imply, especially once `creation_context.py` hands off into builder/codegen
  helpers. The investigation has to widen only when the local file cannot prove
  the claim by itself.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No broader scheduler or transaction claims without direct source evidence.
- [ ] No cleanup recommendations framed as fact until the current ownership map
      is explicit.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: runtime/compiler ownership, saved-work seams, repeated-work
  seams, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

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
- DATETIME: 2026-05-30T14:11:03Z
  TYPE: FACT
  CLAIM: The current `8-12` runtime codegen is partially shaped, not fully
    flattened by whole-plan outcome size. `CreationContext` already removes
    some generic branches by selecting one of four front-door families
    (hooks/no-hooks x overrides/no-overrides) and then one route-specific body
    (`existing_creation`, `many`, `unique_per_conduit`, `spellspace`,
    `shared`). Phase 12 no-overrides also tries to emit a fully unrolled
    transient executor when the plan supports that shape, and otherwise emits a
    step-plan executor instead of falling back to a Python loop interpreter.
    But the emitted bodies still retain generic branch structure inside the
    chosen route or specialization: existence-target handling, creation reuse
    checks, lock paths, registration decisions, contract payload behavior, and
    per-step override target count/shape logic are still represented as
    conditional code in the emitted result.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:54-191
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:497-609
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:45-161
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:201-259
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:19-71
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:212-251
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:2354-2460
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py:2727-2860
  IMPACT: The current system does compile away some high-level genericity, but
    it does not yet use a whole-plan sizing/shaping model that strips most
    internal conditional structure from the final emitted program.
  NEXT: explain to the user where shaping already exists, where genericity still
    survives in emitted code, and what a stronger sizing-model compiler would
    probably target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T12:54:31Z
  TYPE: FACT
  CLAIM: `Meld` and `CreationContext` divide the runtime seam cleanly but not
    lightly. `Meld` is the front-door policy and identity layer: it resolves
    spell identity, normalizes override payloads, probes live creations,
    enforces structural validity, contract validity, per-conduit resolution
    validity, and deferred runtime-resolution readiness, and lazily creates the
    `SpellCompilerSystem` helper it needs for those gates. `CreationContext`
    is the spell-bound hot executor cache: it owns the compiled hook/no-hook
    entry doors, the prebound Phase 12 no-overrides executor, the Phase 10
    override patch map bridge, the override route configs, and the
    specialization caches/source/code-object caches that let override calls
    reuse shape-compiled executors instead of recompiling each call.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:43-170
  - src/melder/aether/conduit/meld/meld.py:481-579
  - src/melder/aether/conduit/meld/meld.py:747-1057
  - src/melder/aether/conduit/meld/meld.py:1080-1439
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:38-121
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-429
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:431-558
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:585-1338
  IMPACT: The current hot path is already optimized around spell-bound caches.
    The likely remaining cost is not “Phase 12 compiles every meld”; it is
    front-door gating/revalidation work in `Meld`, plus override specialization
    misses in `CreationContext` when the socket shape changes.
  NEXT: summarize the full execution model to the user: phases stage the
    runtime artifacts, `Meld` decides whether a call may proceed, and
    `CreationContext` is the reusable spell-bound executor/cache surface that
    actually runs the call.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T12:53:21Z
  TYPE: FACT
  CLAIM: The live `1-12` compiler pipeline is structurally split into three
    layers. Phases `1-4` are spell-local artifact extraction and structural
    validation. Phase `5` builds the rooted system index and root blueprints
    for visible spells, Phase `6` validates that rooted graph, and Phase `7`
    wires change-control revalidation. Then Phase `8` compiles occurrence
    plans, Phase `9` compiles injection plans, Phase `10` builds override and
    mutation patch maps, Phase `11` builds the execution plans and caches the
    no-overrides `11 -> 12` handoff, and Phase `12` only compiles the cached
    no-overrides executor from the Phase `11` plan or exported payload.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:19-71
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:29-171
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:43-674
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:31-157
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:36-607
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:90-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:18-235
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:23-432
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:21-142
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:18-149
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:24-750
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:20-222
  IMPACT: The runtime hot path is already heavily staged before `Meld` gets
    involved. The real planning weight sits in Phase `5`, `8`, and `11`, while
    Phase `12` is a compile/cache edge over already-built no-overrides plan
    state.
  NEXT: read `meld.py` and `creation_context.py` fully, then map exactly how
    those runtime layers consume the staged phase artifacts and where runtime
    gates still repeat work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T12:51:43Z
  TYPE: FACT
  CLAIM: The live readset for the requested compiler/runtime seam is now
    explicit. Phase `1-12` currently spans twelve files under
    `src/melder/aether/spellbook/spell_compiler/phases/`, and five of the
    requested runtime files exceed the `500`-line manual-read cap:
    `compiler_phase_3.py`, `compiler_phase_5.py`, `compiler_phase_11.py`,
    `meld.py`, and `creation_context.py`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:1-71
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:1-171
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1-500
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:1-157
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:1-500
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:1-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:1-235
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-432
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-142
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-149
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-500
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-222
  - src/melder/aether/conduit/meld/meld.py:1-500
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-500
  IMPACT: The next read tranche can stay compliant and deterministic: read the
    smaller phase files whole, then chunk the oversized phase/runtime files in
    sequential `<=500`-line passes.
  NEXT: read Phase `1-12` in order, then finish `meld.py` and
    `creation_context.py` in sequential chunks before summarizing the execution
    model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T12:51:43Z
  TYPE: FACT
  CLAIM: The old task wording still points at a stale phase location. The live
    compiler phases no longer sit under `spell_crafter/blueprints`; the current
    runtime tree is `src/melder/aether/spellbook/spell_compiler/phases/`, and
    this task's next read tranche needs to use that live path for Phase `1-12`
    instead of the older blueprints wording.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md:21-33
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-1
  IMPACT: Further phase inventory and read work should route through the live
    `spell_compiler/phases` tree or the investigation will drift against the
    current source layout.
  NEXT: inventory `compiler_phase_1.py` through `compiler_phase_12.py`, count
    lines, and read them in order with `meld.py` and `creation_context.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-26T22:36:42Z
  TYPE: PLAN
  CLAIM: The user wants a direct hot-path investigation, not another broad
    scheduler story. The bounded target is the runtime creation seam:
    `Meld`, `CreationContext`, compiler phases `10-12`, `Creations`, and
    `Creation`.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is to count and read the exact files first, then record
    the first ownership or repeated-work finding before widening into nearby
    helpers.
  NEXT: count the target files and start with `meld.py` plus
    `creation_context.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-26T22:36:42Z
  TYPE: FACT
  CLAIM: The first hot seam is already clear before phases `10-12` enter the
    picture. `Meld` is not a thin resolver: it owns front-door input caching,
    lookup normalization, structural/resolution gating, lazy compiler-system
    ownership, and the final direct jump into `CreationContext` compiled call
    lanes. `CreationContext` is not a transient builder product either; it is
    a spell-owned runtime cache object that prebinds four compiled entry doors,
    stores the prebound Phase 12 no-overrides executor, stores the Phase 10
    override patch map, and owns multiple override specialization caches plus
    the dynamic-mode `CreationGate` admission path.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:134-171
  - src/melder/aether/conduit/meld/meld.py:328-442
  - src/melder/aether/conduit/meld/meld.py:1370-1394
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-180
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:182-344
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:431-559
  IMPACT: The actual runtime cost and saved-work discussion is centered on the
    `Meld -> CreationContext` seam, not on a generic scheduler story. If we
    want time savings, the next evidence has to show what Phase `10-12`
    artifacts and `Creations` interactions are still being re-read or
    duplicated across that seam.
  NEXT: read compiler phases `10-12` and `Creations` / `Creation`, then map
    exactly which artifacts are prebound once versus recomputed or rechecked at
    runtime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-26T22:36:42Z
  TYPE: FACT
  CLAIM: The current Phase `10-12` creation path is already much more
    ahead-of-time than the old “phase 12 is the runtime executor” story. Phase
    10 fingerprints root-blueprint shape and skips patch-map rebuild when the
    signature and both patch maps are already present. Phase 11 is the heavy
    reuse stage: it fingerprints no-overrides inputs, reuses cached execution
    plans when signatures hold, and stores the `11 -> 12` no-overrides handoff
    directly on the compiler artifact. Phase 12 is compile-only: it either
    consumes that stored plan handoff or falls back to exported payload IR and
    only refreshes the cached no-overrides executor when the signature drifts.
    `CreationContext` then captures those artifact outputs once into
    spell-owned fields, while `creation_context_codegen.py` prebuilds the route
    template families at module load and only binds spell-specific callables on
    context construction. By contrast, `Creations` is still a narrower backend:
    one shared map, one lock, disposal stacks, spellspace buckets, and pool
    reset helpers; `Creation` is only the disposal-metadata wrapper.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:49-172
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:281-308
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:587-808
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:41-244
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:152-178
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:233-359
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:54-177
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:980-1177
  - src/melder/aether/conduit/creations/creations.py:38-87
  - src/melder/aether/conduit/creations/creations.py:307-381
  - src/melder/aether/conduit/creations/creations.py:590-749
  - src/melder/aether/conduit/creations/creation.py:8-82
  IMPACT: The next savings target is probably not “make phases `10-12` exist.”
    That work is already cached and staged. The more likely remaining waste is
    in how often `CreationContext` itself gets rebuilt, how often override
    specialization misses force compilation, and how much front-door lock or
    lookup work `Meld` still repeats before it reaches those cached lanes.
  NEXT: read `CreationContextBuilder` and `CreationContextFactory` to pin down
    context-construction frequency and what still rebuilds when a spell’s
    runtime context is refreshed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T23:30:47Z
  TYPE: FACT
  CLAIM: The live runtime seam is slightly wider than the original top-level
    task wording implied. The current compiler phases live under
    `src/melder/aether/spellbook/spell_compiler/phases/`, and the runtime
    creation path now clearly depends on `CreationContextBuilder`,
    `CreationContextFactory`, and `creation_context_codegen.py` in addition to
    `CreationContext`, `Meld`, and `Creations`.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md:28-33
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:27-432
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:20-142
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:18-149
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:32-750
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:23-222
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:19-251
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:19-255
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-1253
  - src/melder/aether/conduit/creations/creations.py:13-519
  IMPACT: The next useful read is the spell-owned artifact and spell surfaces,
    because the hot path is already staged around spell-owned artifact/context
    caches rather than a direct `Meld -> phase12` jump.
  NEXT: read `spell_compiler_artifact.py` and `spell.py`, then separate which
    cached runtime fields live on the artifact versus directly on `Spell`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T23:30:47Z
  TYPE: FACT
  CLAIM: `SpellCompilerArtifact` is the spell-owned compiler/cache container,
    while `Spell` owns the runtime-entry surface that decides when those caches
    are usable. The artifact holds structural and plan artifacts through Phase
    12, their reuse signatures, exported IR, and phase-reset helpers. `Spell`
    then owns the spell-bound `CreationContextFactory`, the spell-bound
    `CreationContext`, the selector latch used to publish that context,
    runtime resolution flags, conduit-ownership state, and the execution-plan
    metrics that later runtime paths inspect.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:37-92
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:259-395
  - src/melder/aether/spellbook/spell.py:51-383
  - src/melder/aether/spellbook/spell.py:665-665
  - src/melder/aether/spellbook/spell.py:935-1037
  - src/melder/aether/spellbook/spell.py:1163-1235
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:19-101
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:19-255
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-559
  IMPACT: The remaining hot-path questions are now narrower. If runtime work
    still feels heavy, the pressure is less about phase ownership and more
    about when `Spell` invalidates/rebuilds its spell-owned context/factory,
    how often `Meld` has to cross those runtime gates, and how much artifact
    state is still read before it can hit the cached execution doors.
  NEXT: summarize the artifact-versus-spell ownership split for the user, then
    decide whether the next read should focus on artifact invalidation paths or
    on `Meld` front-door cache/gate repetition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-27T23:40:00Z
  TYPE: FACT
  CLAIM: The compiler already has one specialization strategy, but it fires too
    late to save the main planning cost for small spells. `ExecutionPlanBuilder`
    always walks the full Phase 8 occurrence order and Phase 9 injection state
    to build generic Phase 11 steps first, and only inside the
    `NO_OVERRIDES_FAST` variant does it derive the `fast_plan_data` and optional
    `fast_transient_plan`. Later, Phase 11 writes plan-shape metrics like step
    count, max depth, dependency count, and dispatch route back onto `Spell`,
    and `CreationContextBuilder` consumes those spell-level metrics only after
    the generic plan already exists.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1043-1335
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1764-1954
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:405-519
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:486-591
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:540-547
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:76-101
  IMPACT: The current system does have a strategy-style fast lane, but it is a
    post-plan specialization layered on top of the generic compiler instead of
    a pre-plan strategy map that can bypass most of Phase 8-11 work for small
    simple spells.
  NEXT: explain this late-specialization shape to the user and decide whether
    the next investigation should target an early spell-shape strategy map or
    the invalidation paths that currently force full generic rebuilds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-28T11:04:17Z
  TYPE: MEASURE
  CLAIM: The narrow owner-creations cleanup is landed. The live-creation status
    probe in `Meld._describe_spell_live_creation_status(...)` now uses
    `owner_creations.get_creation(spell_id)` instead of reaching directly into
    `owner_creations._creations`, so the shared-lifetime probe path is aligned
    with the existing retrieval helper used elsewhere in `Meld`.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:924-944
  IMPACT: This does not change runtime semantics, but it removes one
    inconsistent raw-store access and keeps the owner-creations path uniform.
  NEXT: continue the runtime/compiler investigation or, if you want another
    cleanup slice, audit other direct `_creations` accesses for the same kind
    of inconsistency.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-28T11:04:17Z
  TYPE: MEASURE
  CLAIM: Narrow validation passed for the touched file. `python -m py_compile
    src/melder/aether/conduit/meld/meld.py` completed successfully after the
    owner-creations helper cleanup.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:924-944
  IMPACT: The small consistency patch is syntactically sound. Broader runtime
    or behavior validation has not been run yet.
  NEXT: if stronger validation is wanted, run the directly implicated meld
    unit surface next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-28T11:18:48Z
  TYPE: FACT
  CLAIM: In the current tree state, external runtime callers are no longer
    reaching directly into `Creations._creations`. The direct raw-dict access
    sites now live only inside `creations.py` itself. The active runtime call
    paths through `Meld`, `CreationContext`, `creation_context_codegen`, and
    the Phase 12 executors are using helper methods like `get_creation(...)`
    and `get_spellspace_creation(...)` rather than bypassing into the backing
    dict.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:212-214
  - src/melder/aether/conduit/creations/creations.py:251-271
  - src/melder/aether/conduit/creations/creations.py:286-325
  - src/melder/aether/conduit/creations/creations.py:434-470
  - src/melder/aether/conduit/meld/meld.py:540-573
  - src/melder/aether/conduit/meld/meld.py:890-944
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:538-609
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:825-866
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1343-1368
  IMPACT: The current problem boundary is narrower than "find every raw
    `_creations` bypass." On the current runtime path, the remaining issue is
    more about owner-creations pointer selection and generic planning cost than
    direct backing-dict access outside `Creations`.
  NEXT: answer the user with the current exact result: no remaining external
    raw `_creations` dict reads are present in the live runtime path, only
    internal ones inside `creations.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-28T22:01:12Z
  TYPE: FACT
  CLAIM: A broader-lived spell is supposed to be blocked from depending on a
    `unique_per_spell_space` spell by Phase 6 system validation before runtime.
    `ScopeOrderingStrategy` ranks `unique_per_spell_space` as narrower than
    `unique`, `unique_per_conduit_cluster`, `unique_per_conduit_lineage`, and
    `unique_per_conduit`, and emits `scope_ordering_violation` when a broader
    node depends on that narrower scope. If such a graph still reached runtime,
    the spellspace step would hard-fail because the `CreationContext` and Phase
    12 spellspace lanes require an active spellspace on the caller creations.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:69-114
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1133-1134
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:565-580
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1369-1380
  IMPACT: The current contract is "block broad-to-spellspace dependencies at
    validation, then hard-gate spellspace runtime if one slips through." The
    `requires_spellspace` and `owner_conduit_required` plan-step fields are
    metadata, not the primary enforcement point.
  NEXT: explain the validation-first and runtime-fallback behavior to the
    user, including the exception that `many` is skipped by the ordering
    strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-28T22:56:35Z
  TYPE: MEASURE
  CLAIM: A direct runtime probe for `unique` depending on
    `unique_per_spell_space` showed that current behavior is not a clean
    Phase-6-at-conjure rejection. `conjure()` succeeded, but the first
    `meld(UniqueRoot)` failed later with `SpellbookValidationError` during the
    meld-time resolution-validity gate for the root spell.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:373-373
  - src/melder/aether/conduit/meld/meld.py:1140-1160
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:69-114
  IMPACT: The current question is now empirical instead of theoretical. The
    next step is to codify this exact behavior in `tests/experimentation` so we
    stop arguing from intent and can rerun the same repro cheaply.
  NEXT: add a focused experimentation test where a `unique` root depends on a
    `unique_per_spell_space` dependency, then run that file with `.venv_new`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-28T22:57:42Z
  TYPE: MEASURE
  CLAIM: The focused experimentation file is landed and green. The current
    runtime behavior is now pinned down in `tests/experimentation`:
    a `unique` root depending on a `unique_per_spell_space` dependency
    successfully conjures, but `meld(_UniqueRoot)` raises
    `SpellbookValidationError` both without an active spellspace and with one
    active on the caller conduit.
  EVIDENCE:
  - tests/experimentation/test_unique_depends_on_spellspace_experiment.py:1-132
  IMPACT: We now have a direct repro for the mismatch between intended
    scope-ordering policy and the observed runtime behavior, and we can rerun
    it cheaply while tracing why Phase 6 does not stop this at conjure time.
  NEXT: summarize the experiment result to the user and, if they want the next
    slice, trace why the scope-ordering violation does not surface during
    conjure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-28T22:57:42Z
  TYPE: MEASURE
  CLAIM: Focused validation passed for the new experimentation surface:
    `.\.venv_new\Scripts\python.exe -m pytest -q
    tests\experimentation\test_unique_depends_on_spellspace_experiment.py`
    completed with `2 passed, 1 warning`.
  EVIDENCE:
  - tests/experimentation/test_unique_depends_on_spellspace_experiment.py:1-132
  IMPACT: The experiment is runnable and stable enough to use as a follow-up
    probe while investigating the conjure-vs-meld validation gap.
  NEXT: if deeper validation is needed, expand from the experiment into the
    directly implicated spell-compiler or meld unit surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-28T23:01:13Z
  TYPE: FACT
  CLAIM: The `unique`-depends-on-`unique_per_spell_space` repro breaks during
    meld-time local resolution validation, not because the spellspace is absent
    at the final execution door. `Meld._ensure_resolution_resolvable(...)`
    reruns target-local resolution phases when conduit validity is unknown or
    gated, and local Phase 6 includes `ScopeOrderingStrategy`, which marks
    broader-lived nodes invalid when they depend on narrower-lived nodes like
    `unique_per_spell_space`. That invalid conduit-resolution state is what
    turns into the generic `SpellbookValidationError`, so even an active
    spellspace does not help: the graph is rejected before runtime spellspace
    execution matters.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1140-1186
  - src/melder/aether/spellbook/spellbook_creation_system.py:1570-1640
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:430-483
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:69-114
  IMPACT: The current failure is a scope-ordering validation failure surfaced
    late, not a direct spellspace-runtime absence failure. If this behavior is
    undesirable, the next cut is to decide whether Phase 6 should reject it
    earlier at conjure time, or whether this dependency shape should become
    legal.
  NEXT: explain the actual break point to the user and, if requested, isolate
    why the validation result is surfacing as a generic spellbook failure
    without a more explicit phase-6 diagnostic in the raised exception text.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-28T23:37:51Z
  TYPE: MEASURE
  CLAIM: The first narrow spellspace-request binding slice is landed. `Spell`
    now exposes a runtime bool `requires_spellspace_request`, and Phase 5
    computes/binds that value from the rooted blueprint by checking whether any
    reachable spell in `ordered_node_ids` uses
    `Existence.unique_per_spell_space`. The compiler artifact still keeps its
    existing `_requires_spellspace_request_phase5` field, but the runtime-facing
    source of truth now also lives on `Spell`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:225-383
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:161-210
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:282-335
  IMPACT: The compiler-derived request fact is now available on the live spell
    object without forcing runtime callers to reason about the artifact
    directly. No meld/runtime consumer was added in this slice yet.
  NEXT: if the next step is approved, wire `Meld` to read
    `requires_spellspace_request` and fail early before deeper resolution work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-28T23:37:51Z
  TYPE: MEASURE
  CLAIM: Focused validation passed for the narrow binding slice.
    `python -m py_compile` succeeded for the touched files, and
    `.\.venv_new\Scripts\python.exe -m pytest -q
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5.py`
    passed with `10 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:282-335
  IMPACT: The bool binding is syntactically and locally behaviorally sound.
  NEXT: keep the next slice narrow and wire only the front-door meld check if
    requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-29T00:25:10Z
  TYPE: MEASURE
  CLAIM: The approved attach-seam implementation is landed. Phase 5 now scans
    `blueprint.ordered_node_ids` inside `_attach_phase5_artifacts_for_snapshot(...)`,
    flips `requires_spellspace_request` when any node in that rooted request
    has `Existence.unique_per_spell_space`, and passes that bool into
    `_set_root_blueprint_phase5(...)`, which binds it onto both the artifact
    and the live `Spell` field.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:161-182
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:348-363
  - src/melder/aether/spellbook/spell.py:225-383
  IMPACT: The bool is now derived at the Phase 5 attach seam with no pool
    lookup, no builder widening, and no detached helper reconstruction pass.
  NEXT: if the next slice is approved, read `spell.requires_spellspace_request`
    in `Meld` and fail before deeper resolution work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T00:25:10Z
  TYPE: MEASURE
  CLAIM: Focused validation passed after fixing the local root-blueprint test
    stub to expose `ordered_node_ids`. `python -m py_compile` succeeded for
    the touched files, and
    `.\.venv_new\Scripts\python.exe -m pytest -q
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5.py`
    passed with `10 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:70-82
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:258-320
  IMPACT: The attach-seam slice is locally green and the test harness now
    matches the real blueprint contract.
  NEXT: keep any follow-up restricted to the meld front door unless a broader
    validation/reporting improvement is explicitly requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-29T10:46:14Z
  TYPE: MEASURE
  CLAIM: The attach-seam extra loop has been removed. Phase 5 now derives
    spellspace-request truth without a new pass by reusing two existing loops:
    `_build_system_index_for_snapshot(...)` collects one
    `spellspace_scoped_spell_ids` set while it already has
    `spell_instance.existence`, and
    `SpellSystemRootBlueprintBuilder._compute_reachable_by_id(...)` propagates
    `requires_spellspace_request_by_id` while it already computes dependency
    closure. `build_root_blueprints(...)` / `build_blueprint_for_spell_id(...)`
    copy that precomputed bool into `RootResolutionBlueprint`, and Phase 5
    attach binds it onto both the artifact and `Spell`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:161-186
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:275-301
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:338-356
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:55-167
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:292-317
  - src/melder/aether/spellbook/spell_compiler/blueprints/root_resolution_blueprint.py:33-94
  - src/melder/aether/spellbook/spell.py:225-389
  IMPACT: The bool is now built from a spell and its dependency closure with
    no post-blueprint re-loop and no spellbook pool lookup.
  NEXT: if you want the next narrow slice, wire `Meld` to read
    `spell.requires_spellspace_request` and fail before deeper resolution work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T10:46:14Z
  TYPE: MEASURE
  CLAIM: Focused validation is green after the no-extra-pass refactor.
    `.\.venv_new\Scripts\python.exe -m pytest -q
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5.py
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5_local.py`
    passed with `15 passed, 1 warning`, and `python -m py_compile` succeeded
    for the touched production and test files.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:79-153
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:282-335
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5_local.py:68-114
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5_local.py:263-296
  IMPACT: The no-extra-pass implementation is locally stable and the test
    stubs now match the live blueprint contract.
  NEXT: keep any follow-up restricted to the meld front door unless you want
    to widen into validation/reporting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-29T11:09:35Z
  TYPE: MEASURE
  CLAIM: The spell-level bool now stays in sync when Phase 5 artifacts are
    explicitly cleared. `SpellCompilerSystem.clear_phase5_artifacts(...)`
    resets `spell.requires_spellspace_request = False` after clearing the
    artifact, and the two direct production transfer-of-ownership call sites
    that still invoke `spell._compiler_artifact.clear_phase5_artifacts()`
    directly now also reset the spell field immediately afterward.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:804-831
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:836-845
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1368-1377
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_system.py:217-231
  IMPACT: The compiler-derived bool is no longer only a one-way Phase 5 attach.
    It now clears with the Phase 5 artifact lifecycle instead of leaving stale
    spell-level runtime state behind.
  NEXT: if the next slice is approved, wire `Meld` to consume the spell-level
    bool and fail before deeper runtime resolution work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-29T11:09:35Z
  TYPE: MEASURE
  CLAIM: Focused validation passed for the bool-sync fix.
    `python -m py_compile` succeeded for the touched production and test files,
    and `.\.venv_new\Scripts\python.exe -m pytest -q
    tests\unit\melder\spellbook\spell_compiler\test_spell_compiler_system.py`
    passed with `16 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_system.py:217-231
  IMPACT: The spell/artifact sync path is locally green.
  NEXT: keep the next follow-up narrow and wire only the meld front-door check
    unless a broader lifecycle change is explicitly requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-29T11:33:28Z
  TYPE: FACT
  CLAIM: `Meld` is only partially lineage-scoped today. It already uses
    `_resolution_conduit_id` as a root-lineage key for conduit-scoped
    resolution validity and change-control lookups, but it still owns
    conduit-local state that directly affects runtime semantics:
    `_conduit_id`, `_creations`, `_input_resolution_cache`, and the active
    meld hook surface. The execution hot path passes `self._creations` into
    `CreationContext`, and `CreationContext` / generated code rely on that
    caller-creations object for `unique_per_conduit`, `many`, and
    `unique_per_spell_space` behavior, including active spellspace lookup.
    Shared owner-root existences (`unique`, cluster, lineage) already bypass
    caller storage by using `spell._owner_creations`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:285-317
  - src/melder/aether/conduit/conduit.py:1693-1749
  - src/melder/aether/conduit/conduit.py:1515-1544
  - src/melder/aether/conduit/meld/meld.py:78-170
  - src/melder/aether/conduit/meld/meld.py:373-438
  - src/melder/aether/conduit/meld/meld.py:532-573
  - src/melder/aether/conduit/meld/meld.py:838-945
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:28-108
  IMPACT: Sharing one `Meld` per lineage would not be a free cache win. It
    would either break per-conduit/per-spellspace semantics or force `Meld`
    to take caller-conduit state (`creations`, query identity, maybe hooks)
    as per-call inputs. The current code already uses lineage scoping where it
    matters for validity (`_resolution_conduit_id`) while keeping hot
    storage/scope behavior conduit-local.
  NEXT: explain the partial lineage/conduit split to the user and separate
    real wins (sharing caches keyed only by root/lineage) from risky state that
    should stay caller-conduit-local.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to rebuild the current creation/runtime hot-path mental model
from live source before any optimization or cleanup claim is made.

