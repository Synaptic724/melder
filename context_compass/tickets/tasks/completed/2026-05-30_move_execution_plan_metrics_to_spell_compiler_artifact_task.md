# Task: Move execution plan metrics to spell compiler artifact

## Metadata
- Task ID: TASK-2026-05-30-move-execution-plan-metrics-to-spell-compiler-artifact
- Story: none
- Status: done
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T14:39:36Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Move the Phase 11 execution-plan metric fields off `Spell` and into
`SpellCompilerArtifact`, while intentionally leaving
`requires_spellspace_request` and `execution_plan_dispatch_route` on `Spell`.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the metric ownership move, the
  board routes to this task before edits begin, and the narrow patch lane for
  this ownership change exists before code changes.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
- EXIT_GATE: all execution-plan metric fields except `execution_plan_dispatch_route`
  are removed from `Spell`, added to `SpellCompilerArtifact`, Phase 11 writes
  the artifact-owned fields, and narrow syntax validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this ownership move widens
  into broader runtime strategy refactors beyond the declared seam.

## Scope Boundaries
- In scope:
  - moving execution-plan metrics off `Spell`
  - adding those metrics to `SpellCompilerArtifact`
  - redirecting Phase 11 writes to artifact-owned fields
- Out of scope:
  - moving `requires_spellspace_request`
  - moving `execution_plan_dispatch_route`
  - adding a new strategy phase
  - broader runtime strategy consumption changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the ownership migration as
  the first step before larger strategy work.

## Steps / Checklist
- [ ] Add a narrow task/patch lane for the metric ownership move.
- [ ] Move execution-plan metric fields from `Spell` to `SpellCompilerArtifact`.
- [ ] Redirect Phase 11 metric writes to the artifact-owned fields.
- [ ] Keep `requires_spellspace_request` and `execution_plan_dispatch_route` on `Spell`.
- [ ] Run narrow syntax validation on touched files.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one bounded ownership migration for execution-plan metrics
- one narrow validation result

## Files / Paths Impacted
- `src/melder/aether/spellbook/spell.py`
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
- `codex/context_compass/tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/spellbook/spell.py src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`

## Risks / Rollback Notes
- Risk: tests or stale internal expectations may still read the old `Spell`
  fields even though `src/` no longer does.
- Rollback: restore the removed `Spell` fields and revert Phase 11 writes only.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into strategy-phase redesign in this slice.
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
  - `system_docs/patches/active/execution_plan_metric_artifact_ownership/architecture_patch.md`
  - `system_docs/patches/active/execution_plan_metric_artifact_ownership/component_patch_spell.md`
  - `system_docs/patches/active/execution_plan_metric_artifact_ownership/component_patch_spell_compiler_artifact.md`
  - `system_docs/patches/active/execution_plan_metric_artifact_ownership/component_patch_phase11.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: user-directed after review

## Noting Behavior
- Note focus: exact producer/consumer ownership, concrete patch impact, and one-step continuation.
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
- DATETIME: 2026-05-30T14:42:47Z
  TYPE: MEASURE
  CLAIM: The narrow ownership move is landed. `Spell` no longer owns the
    Phase 11 execution-plan metric fields except
    `execution_plan_dispatch_route`, `SpellCompilerArtifact` now owns the moved
    metrics as `_..._phase11` fields, and `CompilerPhase11` now writes those
    artifact-owned fields while continuing to write `dispatch_route` onto
    `Spell`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:223-226
  - src/melder/aether/spellbook/spell.py:357-359
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:79-85
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:140-146
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:541-547
  IMPACT: Compiler-owned execution-plan shape data now lives on the compiler
    artifact instead of being stranded on `Spell`, while the current runtime
    consumer path for `dispatch_route` stays unchanged.
  NEXT: if the next slice is approved, trace or migrate the runtime consumer of
    `dispatch_route` or introduce the richer strategy artifact above it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T14:42:47Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the ownership-move slice.
    `python -m py_compile
    src/melder/aether/spellbook/spell.py
    src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py
    src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py`
    completed successfully.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:223-226
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:79-85
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:541-547
  IMPACT: The bounded ownership move parses cleanly. Broader tests were not
    run in this slice.
  NEXT: review the landed ownership move and decide whether the next compiler
    slice should target `dispatch_route` or a proper strategy artifact above it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T14:39:36Z
  TYPE: PLAN
  CLAIM: Patch consumption mapping for this slice is now explicit.
    `architecture_patch.md` sets the ownership target and non-goals,
    `component_patch_spell.md` removes the metric fields from `Spell`,
    `component_patch_spell_compiler_artifact.md` adds the destination fields
    and reset/cleanup ownership to `SpellCompilerArtifact`, and
    `component_patch_phase11.md` redirects the Phase 11 writes while keeping
    `execution_plan_dispatch_route` on `Spell`.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/execution_plan_metric_artifact_ownership/architecture_patch.md:1-24
  - codex/context_compass/system_docs/patches/active/execution_plan_metric_artifact_ownership/component_patch_spell.md:1-21
  - codex/context_compass/system_docs/patches/active/execution_plan_metric_artifact_ownership/component_patch_spell_compiler_artifact.md:1-19
  - codex/context_compass/system_docs/patches/active/execution_plan_metric_artifact_ownership/component_patch_phase11.md:1-15
  IMPACT: The implementation can stay tight to the declared ownership move with
    no strategy-phase widening.
  NEXT: patch the three production files and run narrow syntax validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T14:39:36Z
  TYPE: FACT
  CLAIM: The execution-plan metric fields are compiler-owned outputs today.
    Phase 11 writes all of them, `src/` only consumes `execution_plan_dispatch_route`,
    and the other metrics are stranded on `Spell` rather than being consumed
    from compiler-owned artifact state.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:225-233
  - src/melder/aether/spellbook/spell.py:357-365
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:540-547
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:166-170
  IMPACT: The ownership move is narrow and justified: move the unused
    compiler-output metrics off `Spell`, leave `dispatch_route` where runtime
    currently reads it, and do not widen into strategy redesign in this slice.
  NEXT: create the patch artifacts, then patch `spell.py`,
    `spell_compiler_artifact.py`, and `compiler_phase_11.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to move compiler-owned execution-plan metric outputs off
`Spell` and into `SpellCompilerArtifact` before larger strategy-phase work.

