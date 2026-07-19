# Task: Experiment Melder Bind With Dropped Synthetic Dependencies

## Metadata
- Task ID: TASK-2026-05-02-experiment-melder-bind-with-dropped-synthetic-dependencies
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: review
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-02T16:43:11Z
- Updated: 2026-05-02T16:50:27Z

## Objective
Build a bounded Melder integration experiment under `tests/experimentation/`
that answers one concrete question: what happens when a bound synthetic-module
object depends on another synthetic module that has already been removed from
`sys.modules` / normal history visibility before bind or before later object
creation.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a Melder integration experiment for
  synthetic-module dependency loss during bind and later object creation.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - existing synthetic-module experimentation benches
  - `src/melder/spellbook/bind/bind.py`
  - `src/melder/spellbook/spellbook.py`
- EXIT_GATE: one runnable experiment exists and records what happens in both:
  - bind time with the dependency dropped
  - later object creation / resolution with the dependency dropped
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the experiment requires a
  larger crystallizer/module-lifecycle harness than a bounded bench should own.

## Scope Boundaries
- In scope:
  - one Melder-facing synthetic-module dependency-loss bench
  - synthetic module `A -> B` dependency behavior
  - bind + later object creation behavior
- Out of scope:
  - production crystallizer implementation
  - broad policy changes
  - solving retention/lifecycle globally in this task

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a Melder integration test
  covering dropped synthetic-module dependencies during bind and later object
  creation.

## Steps / Checklist
- [ ] Inspect the existing synthetic-module bench and the relevant bind path.
- [ ] Build a bounded Melder integration experiment under `tests/experimentation/`.
- [ ] Run the experiment with a hard timeout.
- [ ] Record the result in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one bounded Melder integration experiment for dropped synthetic dependencies
- one concrete validation result

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-02_experiment_melder_bind_with_dropped_synthetic_dependencies_task.md
- codex/context_compass/attention_board.md
- tests/experimentation/

## Validation
- Executed:
  - `python -u tests/experimentation/melder_bind_dropped_synthetic_dependency_testbench.py`
- Result:
  - `OK_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_EAGER`
  - `OK_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_LAZY_MeldExecutionError`
  - `OK_MELDER_BIND_DROPPED_SYNTHETIC_DEPENDENCY_EXPERIMENT`

## Risks / Rollback Notes
- Risk: the experiment accidentally turns into a full crystallizer lifecycle
  prototype instead of a narrow bind/resolve proof.
  Rollback: keep it focused on one synthetic module `A` depending on one
  synthetic module `B` and observe bind/resolve outcomes only.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-02T16:43:11Z
  TYPE: PLAN
  CLAIM: The next crystallizer/codegen seam is a narrow Melder integration
    proof around synthetic dependency loss. We need to know what actually
    happens when module `A` is bindable but depends on synthetic module `B`
    after `B` has been removed from `sys.modules` / normal live visibility.
  EVIDENCE:
  - user_instruction: "can you make a melder integration test that will use a synthetic module that references another syntheticmodule"
  - user_instruction: "remove module B from sys.modules and make it go out of scope, what happens when we bind it and what happens if we try and make that object"
  IMPACT: The immediate move is an experiment, not more abstract retention
    design talk.
  NEXT: inspect the existing synthetic-module bench and the bind path, then add
    the new experiment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T16:50:27Z
  TYPE: MEASURE
  CLAIM: The dropped synthetic-dependency experiment is now green and it split
    the behavior cleanly. If module `A` eagerly captured its dependency from
    synthetic module `B` before `B` was removed from `sys.modules` and the
    loader registry, then bind and later meld still succeeded. If module `A`
    only imported `B` lazily inside `__init__`, then bind still succeeded, but
    later meld failed with `MeldExecutionError` wrapping the inner
    `ModuleNotFoundError`.
  EVIDENCE:
  - tests/experimentation/melder_bind_dropped_synthetic_dependency_testbench.py:1-415
  - validation_result: `python -u tests/experimentation/melder_bind_dropped_synthetic_dependency_testbench.py`
  IMPACT: Current Melder bind provenance does not require the dropped
    dependency to stay live at bind time if the root object already captured the
    imported symbol, but later object creation still fails when the dependency
    is only resolved lazily at runtime. That is the exact seam your retention
    model needs to care about.
  NEXT: review whether this eager-vs-lazy split is enough evidence to justify
    synthetic-module closure retention at bind time.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T23:09:39Z
  TYPE: FACT
  CLAIM: Ownership transfer currently leaves one lineage-side owner field stale.
    The transfer path updates `SpellIndex._owner_spellbook` and
    `SpellIndex._owner_spell` directly inside `_flip_registry_and_spellbooks(...)`,
    and then updates the spell-side conduit ownership through
    `spell_obj._add_owned_conduit(...)`, but it never updates
    `SpellIndex._owner_conduit_id`. The normal bind/conjure path does update
    that field through `SpellIndex._set_owner_conduit_id(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:772-812
  - src/melder/spellbook/spell.py:1241-1280
  - src/melder/spellbook/spellbook.py:2754-2767
  - src/melder/spellbook/spellbook_creation_system.py:494-506
  IMPACT: The best place to fix the stale lineage-side conduit owner is in the
    ownership-flip block, right after the new spellbook/owner spell is written
    onto `SpellIndex` and before or alongside the new spell-side owned-conduit
    stamp.
  NEXT: if we choose to patch it, update `SpellIndex._owner_conduit_id` in the
    same transfer block that sets the new owner spellbook/spell.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded Melder integration experiment for dropped synthetic
dependencies across bind and later object creation.
