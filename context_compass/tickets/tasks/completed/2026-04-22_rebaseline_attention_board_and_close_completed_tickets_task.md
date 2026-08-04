# Task: Rebaseline Attention Board And Close Completed Tickets
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the fresh-baseline pass was accepted and superseded by later board maintenance.

## Metadata
- Task ID: TASK-2026-04-22-rebaseline-attention-board-and-close-completed-tickets
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-22T11:14:18Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Close the tickets that are actually complete, move them into their matching
`completed/` folders, and reset `attention_board.md` to a fresh baseline that
only routes genuinely active work.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a ticket/board cleanup pass and
  explicitly asked to move actually completed tickets into completed folders.
- EXECUTION_BOUNDARY: `codex/context_compass/attention_board.md`, the
  completed Apr 21-22 rooted-Nexus and Nexus-support tickets being closed in
  this pass, and this task file only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-21_audit_nexus_cleanup_and_locking_task.md
  - tickets/tasks/2026-04-21_constrain_nexus_frame_manager_creation_by_mode_task.md
  - tickets/tasks/2026-04-21_sync_primary_architecture_docs_from_codex_agent_2_task.md
  - tickets/tasks/2026-04-21_refactor_rift_frame_link_api_and_nexus_target_authorization_task.md
  - tickets/tasks/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md
  - tickets/tasks/2026-04-22_cleanup_rooted_nexus_creation_fallout_task.md
  - tickets/stories/2026-04-22_design_and_implement_rooted_spellbook_mediated_nexus_creation_story.md
  - tickets/stories/2026-04-22_audit_rooted_nexus_creation_fallout_story.md
  - tickets/epics/2026-04-21_refactor_nexus_frame_realization_into_spellbook_mediated_rooted_creation_epic.md
  - tickets/epics/2026-04-22_cleanup_stale_fallout_from_rooted_nexus_creation_refactor_epic.md
- EXIT_GATE: the completed ticket set is moved into matching completed folders,
  `attention_board.md` reflects only genuinely active work plus fresh closed
  anchors, and the board/ticket state is internally consistent.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the closure set becomes
  ambiguous enough that a broader portfolio audit would be required instead of
  this bounded rebaseline pass.

## Scope Boundaries
- In scope:
  - close actually completed Apr 21-22 review-state tickets
  - move them into matching completed folders
  - prune the board to a cleaner active baseline
- Out of scope:
  - changing source code behavior
  - broad historical ticket archaeology
  - closing ambiguous older lanes without evidence

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the bounded Apr 21-22 closure set is patched and moved,
  and `attention_board.md` now routes only the remaining live work plus this
  rebaseline review task.

## Steps / Checklist
- [ ] Inventory the live review-state rows and identify the definitely-completed closure set.
- [ ] Patch the closure set to `done` with completion summaries and acceptance markers.
- [ ] Move the completed ticket files into their matching completed folders.
- [ ] Rebuild `attention_board.md` so the closed items are removed from active routing and represented only by compact closed anchors.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- cleaned completed-ticket set in matching completed folders
- fresh-baseline `attention_board.md`

## Files / Paths Impacted
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/tasks/
- codex/context_compass/tickets/tasks/completed/
- codex/context_compass/tickets/stories/
- codex/context_compass/tickets/stories/completed/
- codex/context_compass/tickets/epics/
- codex/context_compass/tickets/epics/completed/

## Validation
- Not run.
- Validation for this pass is file-state consistency:
  - closed tickets are no longer routed from `## Active Items`
  - matching completed-folder files exist
  - `Recently Closed Anchors` reflects the new closure set cleanly

## Risks / Rollback Notes
- Risk: closing an actually-still-live lane would erase useful routing state.
  Rollback: keep the closure set bounded to the clearly complete Apr 21-22
  review items whose outcomes already landed and were explicitly accepted by
  the user through this cleanup request.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-22T11:14:18Z
  TYPE: PLAN
  CLAIM: This task exists to make the ticket cleanup itself explicit and auditable.
    The user asked for a fresh baseline and explicitly told me to move anything
    actually completed into the matching completed folders.
  EVIDENCE:
  - codex/context_compass/attention_board.md:28-37
  - user_instruction: "cleanup the attentionboard and all the tickets move anything youve' actually completed into the completed folders within each ticket type, and lets get a fresh baseline"
  IMPACT: The closure pass can stay bounded and evidence-backed instead of being
    another implicit board mutation.
  NEXT: patch `attention_board.md` with a routing row for this task, then close
    the definitely-completed Apr 21-22 review set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T11:14:18Z
  TYPE: FACT
  CLAIM: The bounded rebaseline pass is complete. The definitely-completed Apr
    21-22 Nexus/rooted-creation tickets are now in their matching completed
    folders, and `attention_board.md` no longer routes to those dead review rows.
  EVIDENCE:
  - codex/context_compass/attention_board.md:25-38
  - codex/context_compass/attention_board.md:43-54
  - codex/context_compass/attention_board.md:326-338
  - codex/context_compass/tickets/tasks/completed/2026-04-21_audit_nexus_cleanup_and_locking_task.md:1-12
  - codex/context_compass/tickets/tasks/completed/2026-04-22_implement_rooted_spellbook_mediated_nexus_creation_task.md:1-12
  - codex/context_compass/tickets/epics/completed/2026-04-21_refactor_nexus_frame_realization_into_spellbook_mediated_rooted_creation_epic.md:1-12
  IMPACT: The repo now has a cleaner live routing baseline and the closed Apr
    21-22 Nexus/rooted-creation work no longer pollutes active attention state.
  NEXT: review the fresh baseline and decide whether to stop here or run a
    second bounded closure pass on older review lanes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded rebaseline pass for ticket closure and board cleanup.
The Apr 21-22 Nexus/rooted-creation closure set is now moved and the board has
been reset around the remaining live work only.
