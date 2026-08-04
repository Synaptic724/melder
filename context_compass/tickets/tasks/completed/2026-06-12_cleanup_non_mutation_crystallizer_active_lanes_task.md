Completed: 2026-06-12T12:32:32Z
Summary: Closed after retiring the stale non-mutation/non-crystallizer active
and graph-population lanes, then replacing them with a fresh doc-drift epic and
active investigation task.

# Task: Cleanup Non-Mutation Active Lanes

## Metadata
- Task ID: TASK-2026-06-12-cleanup-non-mutation-crystallizer-active-lanes
- Story: none
- Status: done
- Owner: codex
- Agent Name: hope_0
- Priority: p1
- Created: 2026-06-12T11:56:03Z
- Updated: 2026-06-12T12:32:32Z

## Objective
Close active Context Compass tickets that are unrelated to
`mutation_research` and `crystallizer`, then synchronize board and artifact
state so only the preserved lanes remain active.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested cleanup of old tickets/tasks
  unrelated to `mutation_research` and `crystallizer`, and the cleanup lane
  itself is now routed from `attention_board.md`.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
  - active tickets currently routed from `attention_board.md`
  - `codex/context_compass/tickets/tasks/2026-06-12_cleanup_non_mutation_crystallizer_active_lanes_task.md`
- DEPENDENCIES: none
- EXIT_GATE:
  - selected non-mutation/non-crystallizer active tickets are moved to their
    matching completed folders
  - `attention_board.md` no longer routes those closed tickets as active work
  - `artifact_board.md` reflects the closure/disposition outcomes for any
    selected tickets with artifacts
- FAILURE_ESCALATION: record `BLOCKER`, `DECISION_REQUEST`, or `CONFLICT` if
  any candidate ticket's relation to `mutation_research` / `crystallizer` is
  ambiguous or if closure would violate a live dependency/artifact contract.

## Scope Boundaries
- In scope:
  - classify current active-board tickets against the user filter
  - close the selected tickets
  - synchronize attention-board and artifact-board state
- Out of scope:
  - editing unrelated production code
  - changing mutation/crystallizer ticket contents
  - reopening or rewriting already completed tickets

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a cleanup pass scoped to
  active tickets unrelated to `mutation_research` and `crystallizer`.

## Steps / Checklist
- [x] Identify the active-board candidate tickets.
- [x] Mark which candidates are unrelated to `mutation_research` and
      `crystallizer`.
- [x] Move the selected tickets to completed with short completion summaries.
- [x] Synchronize `attention_board.md` active rows/details and recently closed
      anchors.
- [x] Synchronize `artifact_board.md` active/cleared artifact rows when
      selected tickets have artifacts.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- completed-ticket moves for the selected active lanes
- synchronized `attention_board.md`
- synchronized `artifact_board.md` where needed

## Files / Paths Impacted
- `codex/context_compass/attention_board.md`
- `codex/context_compass/artifact_board.md`
- `codex/context_compass/tickets/tasks/2026-06-12_cleanup_non_mutation_crystallizer_active_lanes_task.md`
- selected active tickets routed from `attention_board.md`

## Validation
- Ran:
  - `rg -n "^\| .*\| in_progress \|" codex/context_compass/attention_board.md`
  - `rg -n "2026-06-05_define_devops_transaction_control_plane_philosophy_story" codex/context_compass/artifact_board.md`
  - `Test-Path` over the nine completed-ticket destinations

## Risks / Rollback Notes
- Risk: one or more active tickets may still have live dependency value and
  should not be closed without a clearer filter.
- Risk: active artifacts may drift if ticket closure and artifact-board sync
  are separated.
- Rollback: restore only the moved tickets and board rows touched by this
  cleanup lane.

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
- CLEANUP_TRIGGER: selected closed tickets with active artifacts must be
  synchronized into `artifact_board.md`.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - active ticket cleanup
  - preserve mutation_research and crystallizer lanes
  - board and artifact synchronization
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-12T11:56:03Z
  TYPE: PLAN
  CLAIM: The cleanup selection rule is explicit: current active-board tickets
    unrelated to `mutation_research` and `crystallizer` should be closed,
    while any lane still tied to those topics should remain active.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/attention_board.md:1-171
  IMPACT: The first step is a board-driven candidate classification, not a
    blind mass move across the whole tickets tree.
  NEXT: identify the active-board candidates and mark which ones match the
    user filter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-12T11:58:04Z
  TYPE: FACT
  CLAIM: The active-board candidate set is the nine pre-existing active rows
    below the cleanup task itself, and none of those routed ticket files
    contain `mutation_research` or `crystallizer`. Under the user's filter,
    the selected closure set is therefore all nine old active lanes:
    `repair_compiler_test_drift`,
    `define_devops_transaction_control_plane_philosophy`,
    `decompose_phase10_phase11_strategy_groups`,
    `enforce_bind_time_disposal_signature`,
    `experiment_phase11_cache_rehydration_dynamic`,
    `add_aether_configuration_system_caching_flag`,
    `measure_set_vs_dictkeys_cache_membership`,
    `add_spellbook_creation_system_cache_paths`,
    and `remove_spellbook_conjure_automatic_alias`.
  EVIDENCE:
  - codex/context_compass/attention_board.md:26-35
  - codex/context_compass/tickets/tasks/2026-06-12_repair_compiler_test_drift_task.md
  - codex/context_compass/tickets/stories/2026-06-05_define_devops_transaction_control_plane_philosophy_story.md
  - codex/context_compass/tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md
  - codex/context_compass/tickets/tasks/2026-06-10_enforce_bind_time_disposal_signature_task.md
  - codex/context_compass/tickets/tasks/2026-06-06_experiment_phase11_cache_rehydration_dynamic_task.md
  - codex/context_compass/tickets/tasks/2026-06-06_add_aether_configuration_system_caching_flag_task.md
  - codex/context_compass/tickets/tasks/2026-06-06_measure_set_vs_dictkeys_cache_membership_task.md
  - codex/context_compass/tickets/tasks/2026-06-07_add_spellbook_creation_system_cache_paths_task.md
  - codex/context_compass/tickets/tasks/2026-06-08_remove_spellbook_conjure_automatic_alias_task.md
  IMPACT: The cleanup move can be executed as one bounded closure batch over
    the currently routed old active set without risking mutation/crystallizer
    lane loss.
  NEXT: add completion summaries to the selected tickets, move them to
    completed, then synchronize the board and artifact index.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-12T11:58:04Z
  TYPE: MEASURE
  CLAIM: The cleanup batch is complete. The selected nine non-mutation /
    non-crystallizer active tickets were stamped closed, moved into completed
    folders, removed from active routing, and reduced to recently closed
    anchors. The only remaining active row is the cleanup task itself, and the
    one matching active artifact row was converted into a retained cleared
    artifact row under the completed DevOps story path.
  EVIDENCE:
  - codex/context_compass/attention_board.md:26-45
  - codex/context_compass/artifact_board.md:116-118
  - codex/context_compass/tickets/tasks/completed/2026-06-12_repair_compiler_test_drift_task.md:1-12
  - codex/context_compass/tickets/stories/completed/2026-06-05_define_devops_transaction_control_plane_philosophy_story.md:1-12
  IMPACT: Context Compass active routing is now narrowed to the cleanup lane
    itself, and the old unrelated lanes are preserved as closed references
    instead of continuing to clutter the active board.
  NEXT: report the closed set to the user and ask whether to start a
    mutation/crystallizer-focused lane next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-12T12:29:40Z
  TYPE: FACT
  CLAIM: There is a second stale doc-lane cleanup set: the old open 2026-04-19
    source-graph population tickets. Ignoring mutation/crystallizer as the user
    requested, the stale non-crystallizer review set is:
    `2026-04-19_populate_src_graph_for_aether_directory_story.md`,
    `2026-04-19_populate_src_graph_for_spellbook_directory_story.md`,
    `2026-04-19_populate_src_graph_for_utilities_directory_story.md`,
    `2026-04-19_populate_src_graph_for_aether_first_tranche_task.md`,
    `2026-04-19_populate_src_graph_for_aether_second_tranche_task.md`,
    `2026-04-19_populate_src_graph_for_spellbook_first_tranche_task.md`,
    `2026-04-19_populate_src_graph_for_spellbook_second_tranche_task.md`,
    `2026-04-19_populate_src_graph_for_utilities_first_tranche_task.md`,
    and `2026-04-19_resume_src_graph_exhaustive_gap_fill_from_baseline_task.md`.
    Those tickets are old graph-population lanes, not the fresh drift-investigation
    lane we need now.
  EVIDENCE:
  - codex/context_compass/tickets/stories/2026-04-19_populate_src_graph_for_aether_directory_story.md:3-32
  - codex/context_compass/tickets/tasks/2026-04-19_resume_src_graph_exhaustive_gap_fill_from_baseline_task.md:3-34
  IMPACT: We should close this stale non-crystallizer graph set and replace it
    with one new epic for current documentation-drift investigation.
  NEXT: stamp and move the stale non-crystallizer 2026-04-19 graph tickets to
    completed, then create the new drift-investigation epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This lane exists to close old active work that the user no longer wants routed,
while preserving any mutation/crystallizer-specific work. The next reader
should start from the active-board candidate set and the notes in this task.
