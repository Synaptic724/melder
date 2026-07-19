<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Departed-agent cleanup executed: 18 sole-owned tickets (2 epics, 3 stories, 13 tasks) turned in; mailbox + attention + artifact boards synced; 3 keep-open tickets unassigned. Acceptance per-ticket not re-verified (state preserved in-file).

# Task: turn_in_departed_agents_optimizer0_hope0

## Metadata
- Type: task
- Status: done
- Updated: 2026-06-30T23:04:50Z
- Agent Name: mutation_0
- Owner: cowork

## Problem / Opportunity
Agents `optimizer_0` and `hope_0` have departed (user-confirmed: "completely
gone"). Their footprint remains on `mailbox_board.md`, `attention_board.md`,
`artifact_board.md`, and across active epics/stories/tasks they solely owned.
Stale routing for departed owners breaks the board invariant that active rows
map to live, owned work.

## Context
- User directive: remove them from the mailbox and attention board, close their
  epics, and turn in their docs.
- Ownership was verified via the `Agent Name` metadata field, not incidental
  mentions, to avoid closing tickets co-owned or owned by still-active agents
  (`general_0`, `crystal_0`, `compiler_strategy_0`, `mediator_builder_0`).

## MRP Alignment
Board/ticket truth is the durable, resumable system of record. Keeping it
coherent (no orphaned active routing) is part of the minimum trustworthy
operability bar for Context Compass.

## Ticket Contract
- ENTRY_GATE: explicit user cleanup directive for the two departed agents.
- EXECUTION_BOUNDARY: only tickets whose `Agent Name` is solely `hope_0` or
  `optimizer_0`; shared/foreign-owned tickets are unassign-only or untouched.
- DEPENDENCIES: none (no code changes).
- EXIT_GATE: departed agents absent from mailbox + attention board; their epics
  and docs moved to completed/ with completion banners; artifact board synced.
- FAILURE_ESCALATION: if any board write conflicts (concurrent edit by another
  agent), re-read and retry; if a ticket's ownership is ambiguous, leave it and
  raise to the user.

## Goals / Non-goals
- Goal: remove `optimizer_0` + `hope_0` presence and turn in their sole-owned
  epics/stories/docs tasks.
- Non-goal: closing tickets owned/co-owned by active agents; re-verifying the
  acceptance criteria of each turned-in ticket (state is preserved in-file).

## Scope
Close (move to completed/ with banner):
- hope_0 epic: tickets/epics/2026-06-12_investigate_source_system_doc_drift_excluding_mutation_and_crystallizer_epic.md
- hope_0 stories: tickets/stories/2026-06-12_investigate_{aether,nexus,utilities}_directory_doc_drift_story.md
- hope_0 docs tasks (6): the 2026-06-12 / 2026-06-13 investigate_*_doc_drift tasks
- optimizer_0 epic: tickets/epics/2026-06-20_adaptive_pgo_di_optimizer_epic.md
- optimizer_0 tasks (7): 2026-06-20 generalized_* (4), 2026-06-21 many_only_port,
  2026-06-22 deep_map_phase8_11, 2026-06-22 scope_ordering_spellspace_captive

Unassign only (leave open):
- tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md
  (shared with compiler_strategy_0 -> keep compiler_strategy_0)
- tickets/tasks/2026-06-07_reduce_spellspace_pooled_cycle_cost_task.md (hope_0, hotpath)
- tickets/tasks/2026-06-09_return_to_meld_hotpath_frontdoor_task.md (hope_0, hotpath)

## Acceptance Criteria
- `optimizer_0` row gone from mailbox `## Checked-In Agents`; message to `hope_0`
  deleted; `hope_0` alert line removed from `attention_board.md`.
- The 8 departed-owner rows removed from `## Active Items`; compact anchors added.
- All in-scope epics/stories/tasks live under their matching completed/ folders
  with a completion banner.
- `artifact_board.md` rows for the closed source-doc-drift task moved to
  Recently Cleared with `retain_as_reference` (patch files retained on disk).

## Risks / Mitigations
- Risk: closing mid-flight work. Mitigation: hotpath tasks unassign-only +
  flagged; completion banners preserve prior Notes verbatim.
- Risk: concurrent board edits. Mitigation: re-read boards immediately before
  editing.

## Validation Plan
- `git status` shows the expected moves into completed/ folders.
- grep confirms `optimizer_0` / `hope_0` no longer appear as active owners on the
  boards. Tests: Not run (no code change).

## Decision Log
- DECISION 2026-06-30T23:04:50Z: scope limited to sole-owned tickets; hotpath +
  shared-backlog tickets are unassign-only, not closed.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user-directed departed-agent cleanup started.

## Applicable Anti-Patterns
- Closing tickets without explicit user selection: mitigated (explicit directive).
- Wiping unrelated rows: mitigated (ownership verified via Agent Name).

## Noting Behavior
- Task notes: tactical closure actions + immediate next step.

## Notes
- DATETIME: 2026-06-30T23:04:50Z
  TYPE: PLAN
  CLAIM: Verified sole ownership for 18 closures + 3 unassign-only tickets via the
    Agent Name field; ready to stamp completion banners, move to completed/, and
    run mailbox/attention/artifact board sync.
  EVIDENCE:
    - tickets/epics/2026-06-12_investigate_source_system_doc_drift_excluding_mutation_and_crystallizer_epic.md:7-7
    - tickets/epics/2026-06-20_adaptive_pgo_di_optimizer_epic.md:7-7
  IMPACT: Prevents over-closing active agents' co-owned work.
  NEXT: Execute the closure + board sync pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Cleanup of departed `optimizer_0` and `hope_0`. Sole-owned epics/stories/docs
turned in; boards synced; hotpath + shared-backlog tickets unassign-only and
flagged for the user.
