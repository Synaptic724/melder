# Task: Owner-directed clean-slate archive of all active tickets + board/mailbox reset

- Completed: 2026-07-18T21:58:04Z
- Summary: Owner-accepted clean slate. 116 active tickets (32 epics / 26 stories / 58 tasks)
  archived byte-identical to `tickets/*/archive/`; attention board, mailbox, artifact board,
  and context board reset and integrity-verified (zero NULs); zero disk deletions; durable
  pointers (open MR decision, nexus 050/059 pending, dead-letter content) preserved in Notes.

## Metadata
- Task ID: TASK-2026-07-18-owner-cleanslate-archive
- Story: none (standalone owner-directed cleanup lane)
- Status: done
- Owner: cowork
- Agent Name: helper_f
- Priority: p0
- Created: 2026-07-18T21:22:55Z
- Updated: 2026-07-18T21:58:04Z

## Objective
Execute the owner's 2026-07-18 clean-slate directive: archive every active epic, story, and task
across all agent lanes into the (owner-created, empty) `tickets/*/archive/` folders, clear the
mailbox, and reset `attention_board.md` to a clean routing state.

## Ticket Contract
- ENTRY_GATE: owner directive of 2026-07-18 ("cleanup ALL the epics in all the agents and cleanup
  the mailbox and attentionboard cleanslate lets go archive all epics"); helper_f certified
  (`CERTIFY: APPROVED`, 2026-07-18) as synaptic_python_developer.
- EXECUTION_BOUNDARY: `tickets/epics/*.md`, `tickets/stories/*.md`, `tickets/tasks/*.md` (moves
  only, no content edits), `attention_board.md`, `mailbox_board.md`, `artifact_board.md`,
  `context_management/context_board.md`, `_stage_tmp_*` leftovers. No source code touched.
- DEPENDENCIES: `cleanup_context_compass` workflow (scope pre-answered: everything; selection: all).
- EXIT_GATE: all active tickets moved to `archive/`; boards rewritten clean; owner walkthrough
  of this ticket's acceptance criteria.
- FAILURE_ESCALATION: BLOCKER on any failed move/write; DECISION_REQUEST for artifact deletions.

## Scope Boundaries
- In scope: 32 active epics, 26 active stories, 58 active tasks (this ticket excluded), both
  boards, artifact/context board sync rows, `_stage_tmp_cbm_epic.md` + `_stage_tmp_mailbox.md`.
- Out of scope: `backlog/` (1 parked epic left parked), `completed/` history, `archive/` history,
  artifact files on disk (all retained; zero deletions), source code, system_docs.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: owner confirmed acceptance 2026-07-18 ("confirmed it all ... cleanup
  and turn in"); closure sync executed in the same pass.

## Steps / Checklist
- [x] Enumerate candidates (32 epics / 26 stories / 58 tasks; live counts 2026-07-18T21:22:55Z).
- [x] Move all active epics to `tickets/epics/archive/` (32/32).
- [x] Move all active stories to `tickets/stories/archive/` (26/26).
- [x] Move all active tasks to `tickets/tasks/archive/` (58/58, this ticket excluded).
- [x] Rewrite `attention_board.md`: clear alerts/details/rows; single row routes this lane.
- [x] Rewrite `mailbox_board.md`: helper_f sole check-in row; messages cleared.
- [x] Sync `artifact_board.md`: active links -> cleared (retain_as_reference; no disk deletions).
- [x] Sync `context_management/context_board.md`: active row -> cleared.
- [x] Move `_stage_tmp_*` leftovers to repo `_to_delete/` (folder recreated; 2 files moved).
- [x] Owner walkthrough + closure (owner-confirmed 2026-07-18T21:58:04Z).

## Deliverables
- Archived ticket tree under `tickets/*/archive/`; clean boards; this audit ticket.

## Files / Paths Impacted
- tickets/epics/ (32 moves), tickets/stories/ (26 moves), tickets/tasks/ (58 moves)
- attention_board.md, mailbox_board.md, artifact_board.md, context_management/context_board.md
- _stage_tmp_cbm_epic.md, _stage_tmp_mailbox.md -> ../_to_delete/

## Validation
- Not run. (No code changed; validation = post-move directory counts + board re-reads,
  recorded in Notes below.)

## Risks / Rollback Notes
- Archive is a move, not a close: ticket contents are byte-identical; rollback = `mv` back.
- No acceptance criteria are claimed met for archived tickets; they were archived mid-flight
  under owner directive, not completed.
- Board history (anchors, restoration notes) is superseded by this clean slate; durable
  pointers preserved in Notes below.

## Applicable Anti-Patterns
- [x] No closure of other agents' tickets without explicit owner selection (owner said: all).
- [x] No artifact deletion without explicit owner ruling (all retained on disk).
- [x] Board remains routing-only; this ticket holds the narrative.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded (MEASURE note, zero-NUL board verification + counts)
- [x] Acceptance criteria reviewed with user and confirmed (owner, 2026-07-18)
- [x] Board sync completed for closure anchor update (active row removed, anchor added)

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: n/a
- CLEANUP_TRIGGER: n/a

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Append-only; evidence ranges required.

## Notes
- DATETIME: 2026-07-18T21:22:55Z
  TYPE: FACT
  CLAIM: Repo layout moved since onboarding: context_compass now lives at repo root (the old
    `codex/` wrapper is gone). Empty `archive/` folders exist in all three ticket dirs -
    created by the owner as the destination for this directive.
  EVIDENCE:
  - context_compass/tickets/epics/archive:1-1
  - context_compass/tickets/stories/archive:1-1
  - context_compass/tickets/tasks/archive:1-1
  IMPACT: All paths in this lane use the new root-level context_compass location.
  NEXT: Execute the epic moves first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-18T21:22:55Z
  TYPE: FACT
  CLAIM: Durable pointers preserved before board wipe: (1) mr_salvage anchor carried the one
    open MR design decision (runtime recomposition A/B/C DECISION_REQUEST, recommendation A;
    ticket tickets/tasks/completed/2026-07-11_mr_salvage_lanes_and_qol_completion_task.md).
    (2) helper_1's nexus lane state: BUG-051+055 landed, 050/059 pending (epic now archived).
    (3) Two dead-letter mailbox messages TO departed helper_f2 (story-04 partition NOTICE
    17:15Z; owner-override NOTICE 20:50Z) - both void: f2 departed, story04 archived.
  EVIDENCE:
  - context_compass/attention_board.md:71-98
  - context_compass/mailbox_board.md:54-91
  IMPACT: Open decisions survive the clean slate through this note; nothing silently lost.
  NEXT: Wipe boards after moves complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T21:22:55Z
  TYPE: DECISION
  CLAIM: Archive semantics = park, not complete. Ticket files move byte-identical with no
    completion summaries appended, because acceptance criteria were not walked through for
    116 tickets; `completed/` remains reserved for accepted closures.
  EVIDENCE:
  - context_compass/tickets/epics/README.md:24-27
  IMPACT: History stays honest; any lane can be revived by moving its file back.
  NEXT: Run the moves.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T21:27:00Z
  TYPE: MEASURE
  CLAIM: Post-execution verification, all green: active epics 0 (archive 32, backlog 1,
    completed 101); active stories 0 (archive 26); active tasks 1 - this ticket only
    (archive 58). All four rewritten boards byte-verified with zero NUL bytes (the prior
    write-fault class), correct sole active row, and sole helper_f check-in. `_to_delete/`
    recreated at repo root (it did not survive the repo restructure); both `_stage_tmp_*`
    leftovers moved into it for owner deletion.
  EVIDENCE:
  - context_compass/attention_board.md:52-54
  - context_compass/mailbox_board.md:35-38
  - context_compass/artifact_board.md:37-39
  - context_compass/context_management/context_board.md:20-22
  IMPACT: Clean slate is physically in place and integrity-checked; nothing deleted from disk.
  NEXT: Owner confirms acceptance criteria; on confirm this ticket moves to completed/ and the
    board anchor updates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Owner-directed clean slate 2026-07-18: all active epics/stories/tasks -> `tickets/*/archive/`,
mailbox cleared to a single helper_f check-in row, attention board reset to this single lane,
artifact/context boards synced with zero disk deletions. Backlog (1 epic) left parked.
Open MR design decision pointer preserved in Notes. Next: owner confirms closure of this ticket.
