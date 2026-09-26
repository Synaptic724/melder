# Task: Clean the shared boards and the mailbox of stale messages, alerts and roster rows

## Metadata
- Task ID: TASK-2026-09-26-cleanup-shared-boards-and-mailbox
- Story: none
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-26T13:42:06Z
- Updated: 2026-09-26T13:45:56Z

## Objective
Under the owner's request ("cleanup attention board and cleanup all that jazz and mailbox shit of old messages"),
retire stale coordination history from the shared boards while preserving every live route: mailbox messages
and alert lines addressed to agents whose check-in is older than a day, stale roster marks, and the
cleared-artifact history older than today, all archived verbatim first.

## Ticket Contract
- ENTRY_GATE: Owner request 2026-09-26; roster, alerts, messages and cleared history read before any write.
- EXECUTION_BOUNDARY: `mailbox_board.md` (messages to dormant agents; stale marks; own row), `attention_board.md`
  (alert lines to dormant agents; this task's row), `artifact_board.md` (cleared history compaction; one archive
  row; one note), the archive artifact. No ticket of another agent is closed or edited; active items, attention
  details, closed anchors and standing notes are untouched unless the owner selects tickets to turn in (below).
- DEPENDENCIES: precedent tickets/tasks/completed/2026-09-21_cleanup_shared_context_compass_boards_task.md
  (same rule set: archive verbatim, mark stale, keep live routes).
- EXIT_GATE: archive written; mailbox holds only messages for active agents; alerts match; roster marks applied;
  cleared history compacted; owner reviews and decides on the stale active rows.
- FAILURE_ESCALATION: DECISION_REQUEST for closing other agents' review tickets (the cleanup workflow requires
  the owner's explicit selection); CONFLICT on a concurrent board edit (re-read and retry).

## Scope Boundaries
- In scope: mailbox messages/alerts for dormant agents, stale roster marks, cleared-artifact compaction, archive.
- Out of scope: closing other agents' tickets without the owner's selection; the context board (empty).

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: Hygiene pass complete and archived (2026-09-26T13:42:06Z); the stale active rows need the
  owner's turn-in selection before anything else changes.

## Steps / Checklist
- [x] C1: read the four boards; classify messages, alerts and roster rows by recipient activity (one-day rule).
- [x] C2: archive retired records verbatim under artifacts/shared_boards_cleanup_20260926/.
- [x] C3: delete the retired messages and alert lines; mark stale roster rows; compact cleared history.
- [x] C4: owner selected "All 13 dormant rows"; closed with closure sync and artifact dispositions (2026-09-26T13:45:56Z).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Clean mailbox, alert region and cleared-artifact list; the verbatim archive.

## Files / Paths Impacted
- mailbox_board.md
- attention_board.md
- artifact_board.md
- artifacts/shared_boards_cleanup_20260926/retired_board_history.md

## Validation
- Not run (board files only). Post-edit checks: 1 message left (F0-14, melder_0); 1 alert line (same); 4 rows
  marked stale; 16 cleared rows kept, 68 archived.

## Risks / Rollback Notes
- A dormant agent returning will not find its old notices on the mailbox; they are in the archive and their
  content lives in the cited tickets.
- Rollback: restore the three boards from git; the archive is additive.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No deletion of another agent's record without a verbatim archive.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off (C4 waits on the owner)
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/shared_boards_cleanup_20260926/retired_board_history.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none (historical evidence).

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - shared-board hygiene
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T13:42:06Z
  TYPE: FACT
  CLAIM: State before cleanup: 14 mailbox messages, 13 of them NOTICEs addressed to workflows_0, updater_0,
    updater_1 and muse (last check-ins 2026-09-24T11:53Z, 22:50Z, 22:48Z and 2026-09-21T00:16Z), one to melder_0
    (F0-14, 13:33Z); 14 alert lines mirroring them; 68 cleared-artifact rows over 52 tickets back to 2026-09-19.
    Applied: the 13 messages and 13 alerts retired to the archive and deleted; the four dormant roster rows
    marked stale (codex_1 and knowledge_expert_0 were already stale); the cleared list keeps the 16 rows closed
    on 2026-09-26 with the full 68 archived. Not changed: the 13 active rows of other agents (in review since
    2026-09-06..24 for the owner) and their attention details - the cleanup workflow requires the owner to
    select which tickets to turn in; DECISION_REQUEST raised in the report.
  EVIDENCE:
  - artifacts/shared_boards_cleanup_20260926/retired_board_history.md:1-243
  - mailbox_board.md:82-95
  - attention_board.md:76-78
  - tickets/tasks/completed/2026-09-21_cleanup_shared_context_compass_boards_task.md:16-24
  IMPACT: The boards route only live coordination; nothing of another agent is lost.
  NEXT: Owner selects the stale active rows to turn in (all, a subset, or none); fable_0 closes them with
    closure sync, or closes this task as is.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T13:45:56Z
  TYPE: FACT
  CLAIM: Owner selected "All 13 dormant rows". Closed and moved to completed/: ten tasks (workflows_0 x1,
    updater_0 x2, updater_1 x5, codex_1 x2), muse's two probes and the unassigned stateful-recovery epic; each
    carries Completed, a Summary taken from its own board `outcome`, Status done and a transition line. Board:
    the 13 rows and their attention details removed (8 active rows remain: melder_0 x4, melder_1 x3, this task);
    ONE batch anchor row added instead of thirteen - the 12-row cap would otherwise have evicted every anchor
    from today's fable_0 closures, so the per-ticket record lives in the archive artifact (disclosed
    deviation from the one-anchor-per-ticket rule). Artifact board: ten rows moved to cleared - seven
    investigation artifacts retain_as_reference as declared; the two codex_1 artifacts declared
    delete_on_close were KEPT (deletion not performed at a bulk turn-in); the readme_coverage_badges patch
    folder was archived to system_docs/patches/completed/ WITHOUT promotion (declared
    promote_to_documentation) - the owner can ask for that promotion separately. Parent tickets of the
    override discovery tasks (the 2026-09-24 override epic, melder_0's lane) were not edited; their task links
    now resolve under completed/ by filename.
  EVIDENCE:
  - artifacts/shared_boards_cleanup_20260926/retired_board_history.md:245-315
  - attention_board.md:84-100
  - artifact_board.md:100-127
  IMPACT: The board routes only live lanes; nothing of another agent is lost (archive + completed/).
  NEXT: Owner closes this task ("close it") or names anything to restore.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-26T13:42:06Z: REVIEW. Hygiene pass done and archived. Open: the owner's selection of other agents'
stale review rows to turn in (C4); then close this task.
STATE 2026-09-26T13:45:56Z: REVIEW. All 13 dormant rows turned in (owner selection); boards and artifact board synced; archive
complete. Waiting on the owner's "close it".

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
