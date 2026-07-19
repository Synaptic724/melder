Completed: 2026-05-23T19:26:44Z
Summary: Ran the five-thread spellspace experiment and established the actual cross-thread
scope behavior instead of relying on theory.
Summary: Closed by user cleanup request after the measured result had already informed the
transaction redesign notes.

# Task: Experiment SpellSpace Cross-Thread Scope Behavior

## Metadata
- Task ID: TASK-2026-05-22-experiment-spellspace-cross-thread-scope-behavior
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-22T15:52:00Z
- Updated: 2026-05-23T19:26:44Z

## Objective
Empirically validate how one `SpellSpace` behaves when five threads attempt to
use the same scope, both without context propagation and with forced shared
activation.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an experiment under
  `tests/experimentation` to prove the spellspace theory.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/*spellspace*`
  - directly related spellspace setup helpers only when needed
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_investigate_spellindex_transfer_semantic_drift_task.md`
- EXIT_GATE: an executable experiment exists, it has been run, and the result
  clearly shows what happens across five threads in both tested cases.
- FAILURE_ESCALATION: raise `BLOCKER` if the experiment cannot be made stable
  enough to produce a trustworthy result.

## Scope Boundaries
- In scope:
  - spellspace cross-thread experiment
  - focused runtime setup inside experimentation
  - targeted pytest execution
- Out of scope:
  - transaction implementation changes
  - spellspace production behavior changes
  - broader transfer work

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user explicitly asked for proof by experiment instead
  of continued discussion.

## Steps / Checklist
- [x] Add a spellspace cross-thread experiment under `tests/experimentation`.
- [x] Cover the no-context-propagation case across five threads.
- [x] Cover the forced shared-activation case across five threads.
- [x] Run the experiment with pytest and record the result.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- executable experiment file
- measured result for both thread cases

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_experiment_spellspace_cross_thread_scope_behavior_task.md`
- `codex/context_compass/attention_board.md`
- `tests/experimentation/test_spellspace_cross_thread_scope_experiment.py`

## Validation
- Ran:
  - `pytest -q tests/experimentation/test_spellspace_cross_thread_scope_experiment.py`

## Risks / Rollback Notes
- Risk: thread scheduling can make the forced-shared case flaky if the setup is
  not synchronized.
  Rollback: use barriers/events to synchronize worker start and keep the
  experiment deterministic enough to draw conclusions.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into production transaction changes from the experiment file.

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
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-22T15:52:00Z
  TYPE: PLAN
  CLAIM: The experiment needs to distinguish two different cross-thread
    situations cleanly: workers that never receive the active spellspace in
    their own context, and workers that are deliberately forced to treat the
    same spellspace as active by setting the conduit-owned context-local stack
    in each thread before meld.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:246-247
  - src/melder/aether/conduit/conduit.py:663-695
  - src/melder/aether/conduit/spell_space/spell_space.py:135-170
  - src/melder/aether/conduit/creations/creations.py:581-587
  IMPACT: Without both cases, we cannot separate "not shared by default" from
    "not protected if deliberately shared."
  NEXT: add the two-case experiment file and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T15:58:00Z
  TYPE: MEASURE
  CLAIM: The five-thread experiment overturned the earlier assumption. One
    unactivated `SpellSpace` fails across threads as expected, but worker
    threads spawned while the main thread is inside `conduit.enter_spellspace()`
    inherit that active spellspace context and all successfully meld through
    the same scope. Forcing the same spellspace active explicitly in each
    worker thread also succeeds, and in both success cases the returned object
    identity collapses to one shared instance for `Existence.unique_per_spell_space`.
  EVIDENCE:
  - tests/experimentation/test_spellspace_cross_thread_scope_experiment.py:1-190
  - src/melder/aether/conduit/conduit.py:246-247
  - src/melder/aether/conduit/conduit.py:663-695
  - src/melder/aether/conduit/spell_space/spell_space.py:135-170
  - src/melder/aether/conduit/creations/creations.py:581-587
  IMPACT: `SpellSpace` is not a one-thread-only ownership model today. In the
    current runtime, active spellspace context can flow into spawned threads
    and the same spellspace can be used concurrently if those threads carry the
    same context. That makes it a useful recursion-stack pattern, but not a
    safe ownership/exclusion model for transactions by itself.
  NEXT: use this result to separate "context-local stack model" from
    "thread-exclusive transaction ownership" in the transaction redesign.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This is a narrow proof-oriented experiment slice requested by the user to settle
spellspace cross-thread behavior empirically before continuing transaction
design.
