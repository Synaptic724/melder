# Task: Cleanup spellspace conduit lane and scaffold execution strategy epic

## Metadata
- Task ID: TASK-2026-05-30-cleanup-spellspace-conduit-lane-and-scaffold-execution-strategy-epic
- Story: none
- Status: done
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T14:58:15Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Create the new execution-strategy compiler epic plus its spirit-capturing
artifact, then park the older spellspace/conduit lane tickets so the next
compiler work starts from one clean umbrella instead of a stale runtime-ownership
branch pile.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the new epic/artifact and a cleanup
  pass over the older spellspace/conduit epics, stories, and tasks before new
  work begins.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/tickets/stories/`
  - `codex/context_compass/tickets/tasks/`
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
  - `codex/context_compass/artifacts/`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
  - `tickets/tasks/2026-05-26_investigate_meld_creation_context_phase10_12_creation_runtime_task.md`
- EXIT_GATE:
  - new execution-strategy epic exists
  - one supporting artifact captures the spirit/direction in detail
  - old spellspace/conduit epic/story/task set is moved out of the active lane
  - attention board routes cleanly to the new direction
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any old ticket should remain
  active because it is still directly on the path for the new compiler-strategy
  work.

## Scope Boundaries
- In scope:
  - new compiler strategy epic
  - one design artifact
  - backlog cleanup for old spellspace/conduit planning tickets
  - active board and artifact-board sync
- Out of scope:
  - source-code changes
  - test execution
  - implementing the new strategy phase

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested planning scaffolding first,
  then cleanup of the older spellspace/conduit lane.

## Steps / Checklist
- [ ] Create the new execution-strategy compiler epic.
- [ ] Create one artifact capturing the spirit and investigation direction.
- [ ] Decide which old spellspace/conduit epic/story/task files should be
      parked into backlog.
- [ ] Move the parked tickets and update their metadata for backlog parking.
- [ ] Sync attention-board routing to the new active lane.
- [ ] Sync artifact_board for the new artifact.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further cleanup.

## Deliverables
- one new execution-strategy compiler epic
- one supporting artifact
- one cleaned spellspace/conduit backlog set
- one cleaned board route

## Files / Paths Impacted
- `codex/context_compass/tickets/epics/`
- `codex/context_compass/tickets/stories/`
- `codex/context_compass/tickets/tasks/`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/artifact_board.md`
- `codex/context_compass/artifacts/`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "spellspace|conduit|strategy|phase12|phase 12" codex/context_compass/attention_board.md`

## Risks / Rollback Notes
- Risk: parking too much could hide still-relevant spellspace work from the new
  compiler lane.
- Rollback: move a parked ticket back out of backlog and restore a board row if
  the cleanup proves too aggressive.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No completion-folder moves without explicit acceptance.
- [ ] No stale board rows pointing at parked tickets.

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
- CLEANUP_TRIGGER: user-directed after the new epic direction is accepted

## Noting Behavior
- Note focus: parking decisions, epic direction, and board-routing cleanup.
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
- DATETIME: 2026-05-30T18:20:04Z
  TYPE: MEASURE
  CLAIM: The older spellspace/conduit runtime lane has now been converted from
    backlog parking into explicit completed tickets, as requested. The parked
    spellspace/conduit epics, story, and tasks were stamped with
    `Completed: 2026-05-30T15:06:13Z`, marked `Status: done`, given a
    superseded summary referencing the new compiler-strategy direction, and
    moved into the matching `completed/` folders. The active board no longer
    routes to those files.
  EVIDENCE:
  - codex/context_compass/tickets/epics/completed/2026-05-27_spellspace_sharded_runtime_ownership_epic.md:1-8
  - codex/context_compass/tickets/epics/completed/2026-05-24_reusable_lesser_runtime_pooling_epic.md:1-8
  - codex/context_compass/tickets/stories/completed/2026-05-24_flatten_spellspace_warm_path_story.md:1-8
  - codex/context_compass/tickets/tasks/completed/2026-05-30_start_spellspace_meld_split_task.md:1-8
  - codex/context_compass/attention_board.md:21-82
  IMPACT: The old spellspace/conduit lane is now explicitly closed rather than
    merely parked, and the next planning/implementation work can start from the
    new compiler-strategy umbrella without active-lane ambiguity.
  NEXT: let the user review the cleanup result, then continue from the new epic
    when they want the first execution-strategy implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T15:06:13Z
  TYPE: MEASURE
  CLAIM: The new compiler-strategy umbrella and spirit artifact are now in
    place, and the older spellspace/conduit runtime lane has been parked into
    backlog. Parked epics:
    `2026-05-27_spellspace_sharded_runtime_ownership_epic.md`,
    `2026-05-24_reusable_lesser_runtime_pooling_epic.md`. Parked story:
    `2026-05-24_flatten_spellspace_warm_path_story.md`. Parked tasks:
    `2026-05-27_investigate_spellspace_owned_creations_and_meld_lane_task.md`,
    `2026-05-29_investigate_conduit_and_spellspace_pool_reset_cost_task.md`,
    `2026-05-30_start_spellspace_meld_split_task.md`,
    `2026-05-30_fix_spellspace_pool_cleanup_order_task.md`,
    `2026-05-24_prepare_spellspace_for_pooling_task.md`,
    `2026-05-24_start_conduit_pool_task.md`,
    `2026-05-24_hoist_spellspace_active_lookup_once_per_executor_run_task.md`,
    `2026-05-23_replace_spellspace_contextvar_with_single_active_thread_scope_task.md`,
    and `2026-05-26_investigate_conduit_spellspace_spellbook_guard_and_lock_bloat_task.md`.
    Their active board rows/details were removed in the same pass, and the new
    artifact was indexed on `artifact_board.md`.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md
  - codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md
  - codex/context_compass/attention_board.md:21-82
  - codex/context_compass/artifact_board.md:21-33
  IMPACT: The next compiler work can start from one clean umbrella instead of
    dragging the older spellspace/conduit runtime-ownership and pooling lane
    along as active routing noise.
  NEXT: let the user review the cleanup result, then continue from the new epic
    when they want the first execution-strategy implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T14:58:15Z
  TYPE: PLAN
  CLAIM: The user wants the compiler-strategy direction scaffolded first, then
    the older spellspace/conduit runtime-ownership lane cleaned out of active
    routing so the next phase of work has one clean umbrella and one spirit
    artifact instead of multiple stale active tickets.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/attention_board.md:26-62
  IMPACT: The next step is to create the new epic and artifact immediately,
    then park the older spellspace/conduit planning set into backlog and strip
    their active board rows.
  NEXT: create the new epic and artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to scaffold the new execution-strategy compiler direction and
to clean the older spellspace/conduit runtime lane out of active routing first.

