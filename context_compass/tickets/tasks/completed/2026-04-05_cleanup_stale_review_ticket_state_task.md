# Task: Cleanup Stale Review Ticket State
- Completed: 2026-04-05T19:35:48Z
- Summary: Closed the stale review-only tasks, reduced the active board to the
  real live lanes, and synchronized retained artifact links to the moved task
  paths.

## Metadata
- Task ID: TASK-2026-04-05-cleanup-stale-review-ticket-state
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T17:48:04Z
- Updated: 2026-04-05T19:35:48Z

## Objective
Clean up the active ticket/board state before more SpellExaminer work by:
- closing review-only tickets that are already done
- syncing `attention_board.md`
- syncing `artifact_board.md`
- leaving only the genuinely live lanes active

## Ticket Contract
- ENTRY_GATE: the user explicitly requested ticket cleanup before returning to
  SpellExaminer work.
- EXECUTION_BOUNDARY: ticket files, `attention_board.md`, and
  `artifact_board.md` only.
- DEPENDENCIES:
  - codex/context_compass/attention_board.md
  - codex/context_compass/artifact_board.md
  - active review tickets already reflecting completed work
- EXIT_GATE: stale review-only tickets are moved to completed folders where
  appropriate and the board/artifact state matches the remaining live work.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any review ticket still has
  unresolved acceptance or if a move would hide still-live work.

## Scope Boundaries
- In scope:
  - stale review ticket cleanup
  - active board pruning and rerouting
  - artifact-board cleanup for moved tickets
- Out of scope:
  - SpellExaminer implementation
  - ACL/runtime code changes
  - new architecture/design work

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the user approved moving on from the cleanup pass and the
  board/artifact state is synchronized.

## Steps / Checklist
- [ ] Identify review-only tickets that are already done and no longer need to
      stay active.
- [ ] Move those tickets into the matching completed folders with completion
      summaries.
- [ ] Sync `attention_board.md` active rows/details and closed anchors.
- [ ] Sync `artifact_board.md` active links/details for any moved tickets.
- [ ] Reassess the live SpellExaminer lane after cleanup.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- cleaned active ticket set
- synchronized `attention_board.md`
- synchronized `artifact_board.md`

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/
- codex/context_compass/tickets/tasks/completed/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/attention_board.md`
  - `Get-Content codex/context_compass/artifact_board.md`

## Risks / Rollback Notes
- Risk: moving a ticket too early hides still-live follow-up work.
  Rollback: keep uncertain tickets active and document the reason explicitly.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T17:48:04Z
  TYPE: PLAN
  CLAIM: The active board is carrying a large number of review-only rows from
    already-landed slices, and the user explicitly wants the stale ticket state
    cleaned before we go back into SpellExaminer. The immediate job is to
    separate still-live discovery/blocker lanes from already-done review lanes,
    then move the done tickets and sync the boards accordingly.
  EVIDENCE:
  - user_instruction: "go cleanup all the tickets we don't need first anything we already did deal with that first"
  IMPACT: We need one explicit cleanup lane first so the next SpellExaminer pass
    starts from accurate routing state instead of a board full of stale review
    rows.
  NEXT: inspect the active review rows and decide which tickets are genuinely
    complete versus still-live.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:48:04Z
  TYPE: FACT
  CLAIM: The current active set splits cleanly into two groups. The genuinely
    live lanes are:
    - cleanup itself
    - SpellExaminer rebuild review/rework
    - blocked mutation publication
    - frame-surface HLD design
    - profile/ACL design
    - MutationResearch interview
    The obvious cleanup candidates are the review-only tickets whose own state
    transition reasons already say their work is landed/written and waiting only
    on user review. That safe review-only set is:
    - default class/callable AI profile
    - ACL profile placeholders
    - ACL chain test expansion
    - Nexus logger metadata
    - Nexus/ACL docstring cleanup
    - ACL configuration chain
    - ACL subsystem placeholders
    - frame descriptor manager extraction
    - MRP policy wording
    - source-doc sync
    - psychology doc
    - mission doc
    - Nexus singleton public-root refactor
  EVIDENCE:
  - codex/context_compass/attention_board.md:29-46
  - codex/context_compass/tickets/tasks/2026-04-05_default_class_and_callable_profiles_in_ai_profile_task.md:6-43
  - codex/context_compass/tickets/tasks/2026-04-05_scaffold_frame_acl_profile_placeholders_task.md:6-47
  - codex/context_compass/tickets/tasks/2026-04-05_expand_frame_acl_chain_test_surface_task.md:6-52
  - codex/context_compass/tickets/tasks/2026-04-05_tighten_nexus_logger_metadata_task.md:6-41
  - codex/context_compass/tickets/tasks/2026-04-05_improve_recent_nexus_acl_docstrings_and_cleanup_order_task.md:6-48
  - codex/context_compass/tickets/tasks/2026-04-05_implement_frame_acl_configuration_chain_task.md:6-41
  - codex/context_compass/tickets/tasks/2026-04-04_scaffold_frame_acl_subsystem_placeholders_task.md:6-52
  - codex/context_compass/tickets/tasks/2026-04-04_migrate_nexus_frame_state_into_frame_descriptor_manager_task.md:6-51
  - codex/context_compass/tickets/tasks/2026-04-02_harden_mrp_policy_definition_task.md:6-41
  - codex/context_compass/tickets/tasks/2026-04-02_sync_core_architecture_and_components_docs_task.md:6-52
  - codex/context_compass/tickets/tasks/2026-04-02_write_project_psychology_doc_task.md:6-45
  - codex/context_compass/tickets/tasks/2026-04-02_write_project_mission_doc_task.md:6-43
  - codex/context_compass/tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md:6-51
  IMPACT: We can shrink the active board materially before reopening the
    reverted SpellExaminer work, while leaving the still-live design/blocker
    lanes untouched.
  NEXT: close the safe review-only ticket set, move those files into completed
    folders, and sync the board/artifact state in the same pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T17:50:09Z
  TYPE: MEASURE
  CLAIM: The cleanup pass is landed. Thirteen stale review-only tasks were
    stamped `done` and moved into `tickets/tasks/completed/`, the active board
    was reduced to the six genuinely live lanes, the review-only rows/details
    were pruned into closed anchors, and the retained patch-doc rows for the
    moved chain/bootstrap/manager/Nexus tasks now point at completed ticket
    paths instead of stale active-task paths.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/completed/2026-04-05_tighten_nexus_logger_metadata_task.md:1-10
  - codex/context_compass/attention_board.md:28-33
  - codex/context_compass/attention_board.md:132-143
  - codex/context_compass/artifact_board.md:28-42
  IMPACT: The board is no longer carrying a pile of already-landed review rows,
    and the next SpellExaminer pass can start from a materially cleaner routed
    state.
  NEXT: re-read the live SpellExaminer code and patch docs, then re-baseline
    the rebuild task against the current reverted checkout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:35:48Z
  TYPE: DECISION
  CLAIM: The cleanup pass is complete and accepted for closure. The user
    explicitly directed us to close the SpellExaminer-related tickets and swap
    focus back to ACL work, which means this cleanup helper task no longer needs
    to stay active.
  EVIDENCE:
  - user_instruction: "go ahead and close the tickets for the mods in spell and the spell examiner and I think its time to move on"
  IMPACT: This task should leave the active lane and become a completed anchor
    so the board routes directly into the remaining ACL/design work.
  NEXT: move this task to `tickets/tasks/completed/` and sync the board in the
    same pass.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task exists to clean the active ticket/board state before more
SpellExaminer work starts.
