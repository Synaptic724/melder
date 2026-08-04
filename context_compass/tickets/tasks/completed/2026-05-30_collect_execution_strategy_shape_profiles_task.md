# Task: Collect execution strategy shape profiles

## Metadata
- Task ID: TASK-2026-05-30-collect-execution-strategy-shape-profiles
- Story: none
- Status: done
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T18:56:16Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Implement the Option 2 shape-data path by adding compiler-owned shape profiles
onto `SpellCompilerArtifact` and populating them incrementally in Phases 1, 8,
9, 10, and 11 without adding a new deep analysis pass.

## Ticket Contract
- ENTRY_GATE: the user explicitly chose Option 2, wants richer strategy-grade
  shape data with minimal added compile cost, and the active board routes this
  implementation slice before code edits begin.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `tickets/tasks/2026-05-30_define_execution_strategy_phase12_task.md`
  - `tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
- EXIT_GATE:
  - `SpellCompilerArtifact` owns phase shape profiles for 1/8/9/10/11
  - each target phase populates its profile at the cheapest existing hook point
  - no new deep analysis pass is introduced
  - narrow syntax validation passes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the useful data cannot be
  collected cheaply from the existing phase truth and would require a second
  heavy pass.

## Scope Boundaries
- In scope:
  - artifact-owned shape profile fields
  - incremental shape collection in phases 1/8/9/10/11
  - narrow syntax validation
- Out of scope:
  - strategy-selection phase implementation
  - CreationContext consumer changes
  - broad compiler rewrite

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly selected the Option 2 incremental
  profile path.

## Steps / Checklist
- [ ] Add phase shape profile fields to `SpellCompilerArtifact`.
- [ ] Populate low-cost signature/profile data in Phase 1.
- [ ] Populate occurrence/graph shape data in Phase 8.
- [ ] Populate injection shape data in Phase 9.
- [ ] Populate override targetability shape data in Phase 10.
- [ ] Populate final runtime-step shape data in Phase 11.
- [ ] Run narrow syntax validation on touched files.
- [ ] Document what new facts are now available for future strategy selection.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one artifact-owned shape profile surface
- one incremental phase data collection pass
- one narrow validation result

## Files / Paths Impacted
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
- `codex/context_compass/tickets/tasks/2026-05-30_collect_execution_strategy_shape_profiles_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`

## Risks / Rollback Notes
- Risk: profile collection could turn into a noisy metric dump that does not
  affect strategy choice.
- Rollback: remove the low-value profile fields and keep only the ones that
  come for near-zero cost from the current phase truth.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No second heavy analysis pass disguised as profile collection.
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
  - `system_docs/patches/active/execution_strategy_shape_profiles/architecture_patch.md`
  - `system_docs/patches/active/execution_strategy_shape_profiles/component_patch_spell_compiler_artifact.md`
  - `system_docs/patches/active/execution_strategy_shape_profiles/component_patch_phase_metrics_collection.md`
  - `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after the strategy-direction work is accepted

## Noting Behavior
- Note focus: cheap hook points, added facts, and compile-cost discipline.
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
- DATETIME: 2026-05-30T19:12:51Z
  TYPE: FACT
  CLAIM: One obvious duplicate loop is now gone. Phase 11 was still rewalking
    the occurrence graph to recover `max_occurrence_depth`, even though Phase 8
    now stores that exact fact on the artifact. Phase 11 now reads
    `artifact._occurrence_shape_profile_phase8["max_occurrence_depth"]` when
    available and only falls back to the old graph walk if the Phase 8 profile
    is absent.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:84-112
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:537-548
  IMPACT: The Option 2 slice now removes at least one clear duplicate pass and
    keeps the later strategy inputs more artifact-driven.
  NEXT: if we optimize collection further later, the remaining likely targets
    are Phase 9 and Phase 10 profile loops, but those need a more careful
    judgment because they currently reuse already-built maps instead of
    rewalking the whole compiler input stack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T19:03:45Z
  TYPE: MEASURE
  CLAIM: The Option 2 collection slice is landed. `SpellCompilerArtifact` now
    owns five grouped shape profiles:
    - `_requirements_shape_profile_phase1`
    - `_occurrence_shape_profile_phase8`
    - `_injection_shape_profile_phase9`
    - `_override_shape_profile_phase10`
    - `_execution_shape_profile_phase11`
    and the five target phases now populate them at cheap existing hook points.
    The new facts gathered are:
    - Phase 1: parameter count, optional count, DI-shape counts, plain vs
      annotation vs collection vs contract shape counts
    - Phase 8: execution-order count, unique spell count, shared spell count,
      max occurrence depth, width-by-depth, max width, solo/chain-like hints
    - Phase 9: runtime injection spec count, positional override count,
      contract payload count, list aggregation count, param-source kind counts,
      dependency-arity histogram
    - Phase 10: target-spec count, targeted socket count, targeted spell count,
      max targets per spec, single/multi-target spec counts, path-depth
      histogram, max target path depth
    - Phase 11: step count, unique spell count, max occurrence depth, max
      dependency count, contract/existing creation flags, shared-instance step
      count, spell-lock count, must-register count, spellspace/owner-conduit
      requirement counts, override-capable step count, creations-target-kind
      counts, existence counts, dependency-arity histogram, fast-plan and
      fast-transient availability, call-mode counts
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:59-90
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:33-154
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:45-521
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:40-238
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:30-242
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:500-607
  IMPACT: The compiler now gathers richer strategy-grade facts without adding a
    second deep analysis phase, which gives the future strategy selector real
    artifact-owned shape inputs to consume.
  NEXT: if approved, the next slice is to define the actual strategy artifact
    and new Phase 12 consumer path over these profiles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T19:03:45Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the Option 2 collection slice.
    `python -m py_compile
    src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py
    src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py
    src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py
    src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py
    src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py
    src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
    completed successfully.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:59-90
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:33-154
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:45-521
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:40-238
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:30-242
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:500-607
  IMPACT: The bounded profile-collection patch parses cleanly. Broader tests
    were not run in this slice.
  NEXT: review the new fact surface and decide whether the next implementation
    slice should be the strategy artifact itself or a narrower subset of it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T18:56:16Z
  TYPE: PLAN
  CLAIM: Patch consumption mapping for the Option 2 slice is now explicit.
    `architecture_patch.md` fixes the ownership and non-goals,
    `component_patch_spell_compiler_artifact.md` adds the new profile surface
    and cleanup/reset ownership, and
    `component_patch_phase_metrics_collection.md` defines the exact
    phase-by-phase collection points for Phases 1/8/9/10/11.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/execution_strategy_shape_profiles/architecture_patch.md:1-24
  - codex/context_compass/system_docs/patches/active/execution_strategy_shape_profiles/component_patch_spell_compiler_artifact.md:1-17
  - codex/context_compass/system_docs/patches/active/execution_strategy_shape_profiles/component_patch_phase_metrics_collection.md:1-21
  IMPACT: The implementation can stay bounded to cheap hook points and avoid
    drifting into strategy-selection logic or a second analysis pass.
  NEXT: patch the artifact and the five phase files only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T18:56:16Z
  TYPE: FACT
  CLAIM: The recommended Option 2 path is now concrete. Most useful raw shape
    truth already exists in the rooted blueprint, occurrence plan, injection
    plan, patch maps, and execution plan. So the cheapest correct move is to
    store incremental shape summaries on `SpellCompilerArtifact` and populate
    them where those structures are already being built, instead of adding a
    second deep analysis pass later.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/root_resolution_blueprint.py:36-95
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:146-246
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:120-205
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py:76-167
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:83-205
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:380-698
  IMPACT: This slice can gather more strategy-grade facts with low compile-cost
    overhead and without turning the new Phase 12 into another heavy analyzer.
  NEXT: add the profile fields and populate them in phases 1/8/9/10/11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to implement the Option 2 incremental shape-profile path so
future strategy selection has richer artifact-owned facts to consume.

