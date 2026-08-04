# Task: Investigate PhaseScheduler and Spell Compiler Pipeline

## Metadata
- Task ID: TASK-2026-05-24-investigate-phase-scheduler-and-spell-compiler-pipeline
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T18:17:03Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Map the current `PhaseScheduler` system, the extracted spell-compiler
directory, and the practical Phase 1-12 runtime/compiler flow so we can talk
about where scheduling, compilation, and execution actually live today instead
of guessing from older `SpellCrafter` mental models.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a fresh investigation of the phase
  scheduler, spell-compiler directory, and Phases 1-12 execution stack.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/synchronization/phase_scheduler.py`
  - `src/melder/spellbook/spell_compiler/**`
  - directly implicated phase-entry runtime callsites in:
    - `src/melder/spellbook/spellbook.py`
    - `src/melder/spellbook/spellbook_creation_system.py`
    - `src/melder/aether/conduit/meld/meld.py`
    - `src/melder/aether/conduit/meld/creation_context/**`
  - existing compiler/phase context in current system docs and directly
    relevant completed tickets only when needed for comparison
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/epics/2026-05-24_melder_runtime_performance_optimization_epic.md`
  - `tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md`
  - `tickets/tasks/completed/2026-05-20_lay_spell_compiler_foundation_task.md`
- EXIT_GATE: the current scheduler/compiler ownership model, phase entrypoints,
  and 1-12 phase split are summarized with direct source evidence and one
  bounded recommendation for the next deep dive.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation boundary
  grows beyond the current scheduler/compiler path into a broader architecture
  rewrite.

## Scope Boundaries
- In scope:
  - current `PhaseScheduler` ownership and execution model
  - current `spell_compiler` directory ownership and runtime entrypoints
  - practical Phase 1-12 split across Spellbook, compiler, and runtime
  - exact runtime/compiler seams where phase work is entered
- Out of scope:
  - implementing scheduler/compiler changes
  - broad performance rewrites
  - unrelated benchmark or dev-ops work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a bounded investigation of
  the scheduler, spell compiler, and the Phase 1-12 flow.

## Steps / Checklist
- [ ] Read `PhaseScheduler` and map its execution/lifecycle model.
- [ ] Read the `spell_compiler` directory shape and identify the current front
      door surfaces.
- [ ] Reconstruct the practical Phase 1-12 flow from active runtime entrypoints.
- [ ] Summarize which parts are scheduler-owned, compiler-owned, and still
      runtime-owned.
- [ ] Recommend the next bounded slice if we want to go deeper.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- one evidence-backed scheduler/compiler ownership map
- one evidence-backed Phase 1-12 flow summary
- one bounded recommendation for the next deeper slice

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-24_investigate_phase_scheduler_and_spell_compiler_pipeline_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "run_phase_|run_all_phases|PhaseScheduler|SpellCompiler" src/melder`

## Risks / Rollback Notes
- Risk: the current runtime/compiler split may differ materially from older
  completed tickets and cached assumptions.
  Rollback: keep the investigation source-first and mark historical drift
  explicitly instead of forcing old conclusions onto current code.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: scheduler/compiler ownership findings, exact phase boundaries,
  and one-step continuation.
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
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: PLAN
  CLAIM: The user wants a fresh source-backed read of the scheduler and the
    extracted compiler stack, not another recycled summary from older
    `SpellCrafter` work. The correct cut is to start from the live scheduler
    file and current `spell_compiler` entrypoints, then rebuild the 1-12 phase
    story from current runtime callsites.
  EVIDENCE:
  - user_instruction
  IMPACT: The first step is a bounded source read, not implementation or
    speculation.
  NEXT: inspect the current `spell_compiler` tree and the scheduler entry file,
    then record the first concrete ownership finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: The current scheduler/compiler split is already narrower than the old
    `SpellCrafter` story. `PhaseScheduler` is a generic, one-shot UnitOfWork
    barrier runner with worker-count and timeout config, explicit cancellation,
    and no knowledge of spells or DAGs beyond scheduling work factories.
    Separately, the live runtime/compiler seam is a lazy
    `Meld._get_spell_compiler_system()` helper that creates exactly one
    `SpellCompilerSystem` per `Meld` instance on first need. So the scheduler
    is not the compiler front door; `Meld` is still one current front door for
    compiler-backed runtime work.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:38-85
  - src/melder/aether/conduit/meld/meld.py:1370-1394
  IMPACT: The next investigation step should not treat `PhaseScheduler` and
    the extracted compiler stack as one subsystem. We need to read the compiler
    tree separately and then map which phase entrypoints still come from
    `Spellbook`, `SpellbookCreationSystem`, and `Meld`.
  NEXT: inspect `spell_compiler_system.py`, `spell_compiler.py`, and the
    `phases/` directory entrypoints, then build the current 1-12 ownership map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: The extracted compiler front surface is still intentionally thick.
    `SpellCompilerSystem` declares itself as the compiler-owned orchestration
    surface for Phases 1-12, owns one `SpellCompiler` plus one
    `SpellValidationSystem`, and exposes convenience runners like
    `run_structural_phases(...)` and `run_all_phases(...)`. Under that,
    `SpellCompiler` owns instantiated phase objects `_phase_1` through
    `_phase_12`. The phase split is also slightly asymmetric at the front door:
    `run_phase_execution_plan(...)` is documented as Phase 11, but it
    immediately compiles the Phase 12 no-overrides executor before returning.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:23-39
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:797-850
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:65-80
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:720-801
  IMPACT: We cannot describe the current system as a pure “one phase file per
    phase and nothing else” design. There is still a large orchestrator/facade
    layer above the phase modules, and the Phase 11/12 boundary is merged at
    the front-facing execution-plan entrypoint even though it stays split
    internally.
  NEXT: read the phase module entrypoints and the live runtime callers so the
    practical Phase 1-12 map shows where this fat facade is actually entered.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: The current Phase 1-4 split is already fairly clean at the phase-file
    level. Phase 1 only extracts requirements into the spell-owned compiler
    artifact. Phase 2 only builds the symbolic graph from those requirements.
    The first materially stateful phase is Phase 3: it resolves visible spells
    directly from `spellbook._spell_id_pool`, builds the local DAG, and then
    publishes direct dependency ids plus local topology into
    `SpellSystemStates`. Phase 4 then uses `SpellValidationSystem` to validate
    the Phase 1-3 artifacts and pushes structural validity back into the
    lineage state.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:19-68
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:30-171
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:118-137
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:557-674
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:34-157
  IMPACT: The practical boundary is not “validation starts in Phase 4.”
    Runtime-facing shared state mutation already starts in Phase 3 through
    `SpellSystemStates.update_dependencies(...)` and
    `register_local_topology(...)`. That matters for any performance or
    ownership discussion because Phase 3 is where the compiler first writes
    into frame-owned control-plane state.
  NEXT: read Phases 5-7 to see how rooted blueprints, system validation, and
    change-control wiring extend that shared-state story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: Phases 5-7 are where the compiler stops being just “per spell” and
    becomes conduit-scoped runtime infrastructure. Phase 5 builds a frame-wide
    adjacency snapshot from `SpellSystemStates`, filters it to the current
    `spellbook._spell_id_pool`, constructs rooted blueprints plus a
    `SpellSystemIndex`, and then rebuilds the change-control component-of map
    from **owned roots only**. Phase 6 validates that rooted graph with a large
    system-validation strategy stack and writes per-conduit validation state
    back across the visible spell artifacts. Phase 7 is not another compile
    step so much as runtime wiring: it rebuilds or upserts change-control
    component-of state and installs a dirty-root revalidator that spins up a
    fresh `SpellCompilerSystem` and reruns `run_all_phases(...)` for each dirty
    root.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:448-583
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:416-446
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:286-385
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:387-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:55-185
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:187-235
  IMPACT: The true compiler/runtime pivot is Phase 5, not Phase 8. By the time
    we reach 8-12, the compiler has already crossed into frame-visible,
    conduit-scoped, change-control-aware runtime state. That means any
    scheduler or performance discussion that ignores 5-7 is skipping the first
    heavy shared-state boundary.
  NEXT: read Phases 8-12 and the remaining shared helpers so the planning and
    executor layers can be compared against this earlier conduit-scoped pivot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: Phases 8-12 are currently dominated by cache-shape and handoff work.
    Phase 8 fingerprints blueprint, visible spell, topology, and contracted
    routing inputs so it can reuse occurrence-plan work on warm runs. Phase 11
    is the heaviest planning facade: it builds deterministic signatures for
    no-overrides inputs, caches execution-plan variants, stores the phase11 ->
    phase12 handoff on the artifact, and treats the front-facing execution-plan
    run as “execution-ready” by immediately compiling the Phase 12 no-overrides
    executor in the `SpellCompiler` facade. Phase 12 itself is not the runtime
    executor path; it is the compiler wrapper around
    `phase12_no_overrides_executor` codegen that either compiles from the
    cached plan handoff or falls back to exported payload IR.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:90-228
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:383-432
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:281-425
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:660-765
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:23-107
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:109-222
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:720-801
  IMPACT: The practical “phase 12” discussion needs to stay split between
    compile time and runtime. The phase file is about compiling and caching the
    callable executor, while the actual hot runtime execution path still lives
    later under `CreationContext` and the generated executor modules.
  NEXT: read the live callers in `SpellbookCreationSystem`, `Spellbook`, and
    `Meld` so the front-door orchestration over these phase surfaces is
    explicit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: The current caller topology splits cleanly across three layers. The
    `Spellbook` methods are thin wrappers that preserve the `PhaseScheduler`
    patch point and delegate all orchestration to `SpellbookCreationSystem`.
    `SpellbookCreationSystem` is the real phase orchestrator: it creates a
    fresh `SpellCompilerSystem`, creates a fresh `PhaseScheduler`, registers
    either per-spell or lead-spell `UnitOfWork` factories, runs the scheduler,
    and then cleans both objects. `Meld` is outside the scheduler path; it
    lazily keeps one `SpellCompilerSystem` and only calls it for structural
    reruns and root-vs-spell validity checks during runtime gating.
  EVIDENCE:
  - src/melder\aether\spellbook\spellbook.py:3728-3867
  - src/melder\aether\spellbook\spellbook_creation_system.py:771-815
  - src/melder\aether\spellbook\spellbook_creation_system.py:1256-1287
  - src/melder\aether\spellbook\spellbook_creation_system.py:1556-1685
  - src/melder\aether\spellbook\spellbook_creation_system.py:2024-2245
  - src/melder\aether\conduit\meld\meld.py:724-744
  - src/melder\aether\conduit\meld\meld.py:1328-1368
  - src/melder\aether\conduit\meld\meld.py:1370-1394
  IMPACT: The scheduler is mainly a conjure/revalidation orchestration tool
    owned by `SpellbookCreationSystem`, not a universal phase runtime. The
    runtime hot path only dips into the compiler system selectively through
    `Meld`, and it does so without going through `PhaseScheduler`.
  NEXT: inspect the actual `PhaseScheduler` worker/barrier implementation so we
    can explain how those registered phase factories are really executed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: `PhaseScheduler` itself is simple but strict. It is a one-shot,
    future-backed barrier runner: phase factories register by name, each phase
    factory must build `UnitOfWork` objects through the scheduler so they share
    one cancellation event, workers are started lazily once, `_run_single_phase`
    enqueues all work for a phase, waits with `FIRST_EXCEPTION`, and then
    either raises `PhaseExecutionError`, raises `PhaseTimeoutError`, or moves
    to the next phase in registration order. The scheduler never knows spell or
    DAG semantics; all spell/compiler meaning is outside it in the registered
    factories.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:301-384
  - src/melder/utilities/synchronization/phase_scheduler.py:390-487
  - src/melder/utilities/synchronization/phase_scheduler.py:491-611
  - src/melder/utilities/synchronization/phase_scheduler.py:618-673
  IMPACT: The scheduler is not where phase-specific complexity hides. If we
    want to optimize or rethink the phase stack, the likely leverage is in the
    phase factory topology and the compiler/runtime handoffs, not in the
    scheduler’s barrier mechanics themselves.
  NEXT: summarize the full scheduler/compiler/phase model for the user and
    recommend the next deeper read target inside the compiler stack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T18:17:03Z
  TYPE: FACT
  CLAIM: The main parallelism limit is structural work shaping, not a hidden
    scheduler bug. `SpellbookCreationSystem` builds one `UnitOfWork` per spell
    for Phases 1-4 and again for Phases 8-11, so those phases can fan out
    across workers. But the conduit-scoped middle is intentionally narrow:
    Phase 5 root-blueprints, Phase 6 system validation, and Phase 7
    change-control each emit exactly **one** lead-spell `UnitOfWork` for the
    whole conduit. On top of that, `PhaseScheduler` enforces a hard barrier
    between every registered phase. So even with many workers, the run keeps
    collapsing back to one active worker during 5-7, and local target reruns
    do the same thing with one target-specific unit per phase.
  EVIDENCE:
  - src/melder\aether\spellbook\spellbook_creation_system.py:1816-1870
  - src/melder\aether\spellbook\spellbook_creation_system.py:1873-1994
  - src/melder\aether\spellbook\spellbook_creation_system.py:1997-2036
  - src/melder\aether\spellbook\spellbook_creation_system.py:2166-2245
  - src/melder\aether\spellbook\spellbook_creation_system.py:1556-1588
  - src/melder\utilities\synchronization\phase_scheduler.py:491-611
  - src/melder\utilities\synchronization\phase_scheduler.py:618-663
  IMPACT: If we want more real parallelism, optimizing the worker loop alone
    will not move much. The real leverage is deciding whether 5-7 can be
    subdivided safely or whether the barrier topology can be relaxed without
    breaking rooted validation and change-control correctness.
  NEXT: recommend the next deep dive on Phase 5-7 decomposition and
    dependency constraints, because that is where worker starvation is being
    structurally introduced.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to rebuild the current scheduler/compiler mental model from
live source. It should stay on ownership, phase boundaries, and entrypoints
until the first concrete findings are documented.

