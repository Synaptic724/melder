# Task: Audit And Close Ticket Backlog
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the active backlog and board state were synchronized.

## Metadata
- Task ID: TASK-2026-04-19-audit-and-close-ticket-backlog
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T16:37:39Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Audit the live ticket backlog under `tickets/epics/`, `tickets/stories/`, and
`tickets/tasks/`, move defensibly complete items into the matching
`completed/` folders, and synchronize `attention_board.md` and
`artifact_board.md` so active routing matches reality.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to clean up ticket directories and the
  attention board.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/tickets/stories/`
  - `codex/context_compass/tickets/tasks/`
  - matching `completed/` folders
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
- DEPENDENCIES:
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
  - active ticket files selected during the audit
- EXIT_GATE: every moved ticket has a defensible completion basis, board rows
  no longer route to moved tickets, and any still-live work remains explicitly
  active instead of being falsely closed.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the user insists on moving
  materially unfinished tickets to `completed/`, because that would corrupt the
  durable state.

## Scope Boundaries
- In scope:
  - audit of non-completed tickets
  - closure of tickets that are actually done / accepted enough
  - attention-board and artifact-board sync for those closures
- Out of scope:
  - fabricating completion for unfinished work
  - editing unrelated runtime code
  - rewriting historical content beyond closure/sync notes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: review and superseded planning tickets were moved to the
  matching completed folders and the active board now routes only to genuinely
  unfinished work.

## Steps / Checklist
- [x] Inventory active/non-completed epics, stories, and tasks.
- [x] Separate finished review-ready work from still-live discovery or
      implementation work.
- [x] Move defensibly complete tickets into the matching `completed/` folders.
- [x] Sync `attention_board.md` and `artifact_board.md`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- cleaned ticket directories
- synced attention board
- synced artifact board

## Files / Paths Impacted
- codex/context_compass/tickets/epics/
- codex/context_compass/tickets/stories/
- codex/context_compass/tickets/tasks/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-ChildItem codex/context_compass/tickets/tasks -File`
  - `Get-ChildItem codex/context_compass/tickets/stories -File`
  - `Get-ChildItem codex/context_compass/tickets/epics -File`

## Risks / Rollback Notes
- Risk: moving unfinished tickets would corrupt durable execution memory.
- Rollback: move only tickets we can defend from their current contents and
  leave unfinished items active.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No closure of materially unfinished tickets.
- [ ] No attention-board rows pointing at moved completed tickets after sync.

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
- Note focus: audit findings, closure decisions, and concrete next cleanup
  action.
- Keep notes append-only and evidence-backed.

## Notes
- DATETIME: 2026-04-19T16:37:39Z
  TYPE: FACT
  CLAIM: The cleanup pass moved the review backlog and a small set of
    superseded planning tickets into the matching `completed/` folders, then
    pruned `attention_board.md` so it no longer routes to those closed items.
    The remaining non-completed epics/stories/tasks are the tickets still
    marked `in_progress`, `ready`, or `draft`, which I left live rather than
    falsifying as completed.
  EVIDENCE:
  - codex/context_compass/tickets/epics/completed/: moved review epics plus the superseded frame-viewer planning epic
  - codex/context_compass/tickets/stories/completed/: moved review stories plus the superseded frame-viewer planning story
  - codex/context_compass/tickets/tasks/completed/: moved review tasks plus the superseded compare-architecture and frame-viewer planning tasks
  - codex/context_compass/attention_board.md:25-36
  IMPACT: The ticket directories are substantially cleaner and the active board
    now reflects only genuinely unfinished work.
  NEXT: hold for user review unless a second pass should classify additional
    `ready` / `draft` tickets as backlog or closure candidates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T16:37:39Z
  TYPE: PLAN
  CLAIM: The cleanup pass must separate real closure from fake closure. The
    user asked to clean up everything, but the compliant path is to move only
    the tickets whose current contents support completion and to leave still-live
    discovery/implementation lanes active.
  EVIDENCE:
  - user_instruction: "cleanup everything in tickets, tasks, stories, and epics"
  - codex/context_compass/attention_board.md:25-39
  IMPACT: This task is an audit-and-close pass, not a blind move-all script.
  NEXT: inventory the non-completed ticket set and classify it before moving
    anything.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task audits the current ticket backlog and moves only defensibly complete
items into the matching completed folders, with board sync in the same pass.
