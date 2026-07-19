# Task: Reduce Lesser Conduit Pooled Cycle Cost

## Metadata
- Task ID: TASK-2026-06-07-reduce-lesser-conduit-pooled-cycle-cost
- Story: none
- Epic: EPIC-2026-06-07-optimize-meld-hotpath
- Status: in_progress
- Owner: codex
- Agent Name: tester_0
- Priority: p0
- Created: 2026-06-07T12:32:49Z
- Updated: 2026-06-07T12:32:49Z

## Objective
Map and reduce the steady-state pooled lesser-conduit cycle cost that the
real-world gauntlet pays on every outer-scope iteration.

## Ticket Contract
- ENTRY_GATE: the gauntlet baseline and cycle-cost map now show that steady-state
  pooled lesser reset/reattach is the first concrete optimization target.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/conduit_pool.py`
  - `src/melder/aether/conduit/conduit_ward/`
  - `benchmarks/testing_other_di/test_melder_gauntlet.py`
  - `benchmarks/testing_other_di/test_real_world_gauntlet.py`
  - `codex/context_compass/tickets/tasks/2026-06-07_reduce_lesser_conduit_pooled_cycle_cost_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`
  - `tickets/tasks/2026-06-07_run_real_world_gauntlet_baseline_task.md`
  - `tickets/tasks/2026-06-07_run_meld_hotpath_harness_baseline_task.md`
- EXIT_GATE:
  - the pooled lesser steady-state path is decomposed into concrete sub-steps,
  - the first optimization edit boundary is explicit,
  - baseline-vs-target measurement plan is recorded before implementation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first meaningful reduction
  would require widening scope into spellspace or meld before lesser-cycle
  evidence is complete.

## Scope Boundaries
- In scope:
  - `create_lesser_conduit(...)` pooled acquire/reuse path
  - `_prepare_for_pool()` and `_cleanup_spellspaces_for_pool()`
  - `ConduitPool.return_lesser_conduit(...)`
  - lesser reattach/link path costs
- Out of scope:
  - spellspace optimization itself
  - meld front-door optimization itself
  - unrelated benchmark suites

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the gauntlet map identified pooled lesser reset/reattach
  as the first optimization target in the measured cycle path.

## Steps / Checklist
- [ ] Decompose the steady-state pooled lesser cycle into concrete sub-steps.
- [ ] Identify which sub-steps are guaranteed on every gauntlet outer cycle.
- [ ] Define the first bounded implementation target and measurement check.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one decomposition of pooled lesser cycle cost
- one first bounded optimization target

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-06-07_reduce_lesser_conduit_pooled_cycle_cost_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks/testing_other_di/test_real_world_gauntlet.py`

## Risks / Rollback Notes
- Risk: attribute outer-cycle cost to fresh lesser creation when the pool means
  the steady state is mostly reuse/reset/reattach.
- Risk: drift into spellspace or meld cost before lesser-cycle evidence is
  fully mapped.
- Rollback: keep this task on lesser pooled lifecycle only.

## Applicable Anti-Patterns
- [ ] No optimization assumptions without steady-state path evidence.
- [ ] No scope jump into spellspace or meld before lesser-cycle map is explicit.
- [ ] No validation claims without an actual run.

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

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - pooled lesser reset
  - pooled lesser reattach
  - outer-scope create/cleanup gauntlet cost
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-07T12:32:49Z
  TYPE: PLAN
  CLAIM: The gauntlet map says the first optimization slice should start with
    pooled lesser reset/reattach, because in steady state the benchmark is
    mostly not paying fresh lesser allocation. The immediate job is to break
    that steady-state cycle into hard sub-steps before any code edit.
  EVIDENCE:
  - tickets/tasks/2026-06-07_run_real_world_gauntlet_baseline_task.md:1-218
  - src/melder/aether/conduit/conduit.py:336-379
  - src/melder/aether/conduit/conduit.py:1632-1765
  - src/melder/aether/conduit/conduit_pool.py:1-115
  IMPACT: This keeps the first optimization slice targeted on the real outer
    cycle cost instead of hand-waving about fresh lesser construction.
  NEXT: map the steady-state pooled lesser cycle step by step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the first successor slice from the gauntlet mapping. It focuses on
steady-state pooled lesser-conduit cost, not spellspace or meld yet.
