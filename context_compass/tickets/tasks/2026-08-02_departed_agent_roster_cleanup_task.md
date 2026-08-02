# Task: Retire departed agents helper_f and mediator_0 and unassign their lanes

## Metadata
- Task ID: TASK-2026-08-02-departed-agent-roster-cleanup
- Story: none (standalone board/roster hygiene task)
- Status: review
- Owner: cowork
- Agent Name: tester_0
- Priority: p1
- Created: 2026-08-02T18:32:37Z
- Updated: 2026-08-02T18:42:00Z

## Objective
Retire `helper_f` and `mediator_0` under owner directive: remove both roster rows
from `mailbox_board.md`, unassign every active ticket they hold, clear their
routing identity from `attention_board.md`, and dispose of the one undeliverable
mailbox message addressed to `helper_f` without destroying its content.

Explicitly NOT a closure pass. The owner directed that the lanes stay ACTIVE and
merely become unowned. No ticket moves to `completed/`, no acceptance is claimed,
no `## Recently Closed Anchors` row is added.

## Ticket Contract
- ENTRY_GATE: explicit owner directive naming both agents as departed, plus an
  active `attention_board.md` row routing to this task.
- EXECUTION_BOUNDARY: `mailbox_board.md`, `attention_board.md`, and the
  `- Agent Name:` metadata line of active tickets held by the two departed
  agents. NO edits to ticket scope, status, acceptance criteria, notes, or any
  `Owner:` field. No source files.
- DEPENDENCIES: `agent_onboarding/default/general/skills/mailbox_protocol.md`,
  `active_pointerboard.md`, `agent_identity.md`, `ticket_closure_attention_sync.md`.
- EXIT_GATE: zero `helper_f` / `mediator_0` occurrences remain as LIVE routing or
  assignment identity across both boards and all active tickets; historical
  mentions in notes and anchors are preserved verbatim; the owner confirms the
  three open decisions below.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` rather than guessing whenever a
  lane could reasonably transfer to a live agent instead of going unowned.

## Scope Boundaries
- In scope:
  - `mailbox_board.md` `## Checked-In Agents` roster rows for both agents
  - `mailbox_board.md` `## Messages` entry addressed to `helper_f`
  - `attention_board.md` `## Message Alerts` line naming `helper_f`
  - `attention_board.md` `## Active Items` `agent_name` cells only
  - `- Agent Name:` metadata line in active tickets held by `helper_f`
- Out of scope:
  - ticket `Status`, `next`, `outcome`, `exit_signal`, scope, or acceptance text
  - the `Owner:` field on any ticket or board row (`owner` is executor identity,
    `agent_name` is assignment identity; conflating them is the anti-pattern named
    at `cleanup_context_compass.md:200`)
  - tickets already in `completed/` or `archive/`
  - authorship credit inside existing notes and anchors - it stays verbatim

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner issued an explicit departure directive for both agents
  and authorised unassignment; the readset needed to execute it is already read
  under this session's certified onboarding.
- from_state: in_progress
- to_state: review
- transition_reason: every deliverable is on disk and mechanically verified (see
  the MEASURE note); what remains is three decisions that are the owner's to make,
  not work. Held at `review` rather than `done` because `ticketing.md:61-63`
  requires acceptance confirmation before closure, and because two of the three
  open questions concern lanes owned by a LIVE agent and by the owner.

## Scope Expansion (owner-directed, mid-flight)
- from: departure cleanup only (roster, unassignment, mail)
- to: plus a general `attention_board.md` prune
- authorised_by: explicit owner instruction at 2026-08-02T18:38Z, "clean up old
  shit from the attention board and manage some of the old shit out"
- recorded here rather than absorbed silently, per
  `context_window_budget.md:26-30` and this ticket's own EXECUTION_BOUNDARY, which
  named only `agent_name` cells on this board. The boundary is now widened to the
  board's USER-DEFINED regions. Still excluded and still untouched: any other
  agent's active rows, and any ticket status or content.

## Steps / Checklist
- [x] Enumerate what each departed agent actually holds, from disk not from claims
- [x] Unassign `- Agent Name:` on every active ticket held by `helper_f` (14)
- [x] Clear `agent_name` on every `attention_board.md` active row they hold (7)
- [x] Preserve the undeliverable message content into the ticket it concerns
- [x] Delete the consumed message and clear its `## Message Alerts` line
- [x] Remove both roster rows with an owner-directive note recording the basis
- [x] Verify: zero live assignment/routing occurrences remain
- [x] OWNER-ADDED: prune stale content from `attention_board.md`
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `helper_f` and `mediator_0` retired from the roster with the directive recorded
- 14 active tickets carrying `UNASSIGNED` instead of a departed agent's name
- 7 attention-board rows routable by any agent who wants to pick them up
- the undeliverable message's actionable content landed in a durable ticket

## Files / Paths Impacted
- context_compass/mailbox_board.md
- context_compass/attention_board.md
- context_compass/tickets/epics/2026-07-18_parallel_restore_ulid_identity_epic.md
- context_compass/tickets/epics/2026-07-27_transactional_structure_unwind_epic.md
- context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md
- context_compass/tickets/stories/2026-07-18_cohort_aware_load_gate_story.md
- context_compass/tickets/stories/2026-07-18_link_identity_journal_rows_story.md
- context_compass/tickets/stories/2026-07-18_loadplan_phase_compiler_story.md
- context_compass/tickets/stories/2026-07-18_phase_scheduler_config_seam_story.md
- context_compass/tickets/stories/2026-07-19_bind_kwargs_transplant_story.md
- context_compass/tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md
- context_compass/tickets/stories/2026-07-19_melder_init_composition_story.md
- context_compass/tickets/stories/2026-07-31_aetheric_mediator_core_story.md
- context_compass/tickets/tasks/2026-07-19_crystallizer_analysis_io_storm_task.md
- context_compass/tickets/tasks/2026-07-19_melder_init_composition_and_wheel_strategy_task.md
- context_compass/tickets/tasks/2026-08-02_stale_source_docstrings_task.md

## Validation
- RUN, and these are measured results, not claims. No test suite was executed -
  this pass touches no source - so "Not run." applies to `pytest` and coverage.
- Verified 2026-08-02T18:41:00Z:
  - `| cowork | helper_f |` in `attention_board.md`: **0**
  - `^- Agent Name: helper_f$` across active tickets: **0**
  - departed roster rows in `mailbox_board.md`: **0**
  - tickets carrying the new UNASSIGNED stamp: **14** (expected 14)
  - live messages in the mailbox `## Messages` region: **0** (the two remaining
    `- TO:` lines are the format template, one inside an HTML comment)
  - MANAGED/USER-DEFINED region markers: **12** in `attention_board.md`, **10** in
    `mailbox_board.md` - all balanced, none damaged by the prune
  - line endings: **0 CRLF** in both boards, still uniform LF
  - sizes after prune: `attention_board.md` 221 -> 211 lines,
    `mailbox_board.md` 184 -> 166 lines
- Not run: `pytest`, `pytest --cov`. Out of scope; no source touched.

## Risks / Rollback Notes
- RISK: unassigning a lane that should have transferred to a LIVE agent silently
  orphans work someone was ready to own. Mitigated by raising each such case as a
  `DECISION_REQUEST` instead of deciding it here.
- RISK: deleting the mailbox message destroys the only copy of a request another
  agent made. Mitigated by copying its actionable content into the story it
  concerns BEFORE deletion, per `mailbox_protocol.md:59-61`.
- ROLLBACK: every edit is a single metadata line or table cell; git carries the
  prior state. No ticket content, status, or history is rewritten.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] Do not treat `owner` as the assigned agent identity instead of `agent_name`
      (`cleanup_context_compass.md:200`).
- [ ] Do not edit another agent's check-in row absent an owner directive
      (`mailbox_protocol.md:76-77`) - this pass rests on one and says so.

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

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-08-02T18:32:37Z
  TYPE: FACT
  CLAIM: THE ATTENTION BOARD UNDERCOUNTS helper_f's OWNERSHIP BY HALF. The board
    routes SEVEN rows under `agent_name` helper_f, but a disk sweep of the
    `- Agent Name:` metadata line across every ACTIVE ticket returns FOURTEEN
    tickets held by them - 3 epics, 8 stories, 3 tasks. The seven with no board
    row are child tickets of routed parents plus two orphans:
    `2026-07-31_aetheric_mediator_subsystem_epic.md` (the PARENT epic of a routed
    story, itself unrouted) and
    `2026-07-19_melder_init_composition_and_wheel_strategy_task.md`. Cleaning up
    from the board alone - the obvious approach, and the one the owner's wording
    naturally suggests - would have left seven active tickets stamped with a
    departed agent's name and no signal anywhere that they were unowned.
  EVIDENCE:
  - context_compass/attention_board.md:124-135
  - context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md:7-7
  - context_compass/tickets/tasks/2026-07-19_melder_init_composition_and_wheel_strategy_task.md:7-7
  - context_compass/tickets/stories/2026-07-18_cohort_aware_load_gate_story.md:8-8
  IMPACT: The board is a ROUTING surface, not an ownership index. Any future
    departure cleanup must sweep ticket metadata, not board rows, or it will
    under-clean by the same ratio. This is the durable lesson of this pass.
  NEXT: Unassign all 14 ticket metadata lines, then the 7 board cells.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T18:32:37Z
  TYPE: FACT
  CLAIM: mediator_0's self-report is TRUE and was verified independently rather
    than accepted. Their roster row claims "NO LANE CLAIMED, no ticket opened, no
    board row added, nothing edited outside this row". A sweep across both boards,
    the context board, the artifact board, and every active ticket returns exactly
    ONE occurrence of the name: their own check-in row. Their retirement is a
    single-row deletion with no lane consequences.
  EVIDENCE:
  - context_compass/mailbox_board.md:76-76
  IMPACT: mediator_0 needs no unassignment work at all, which means the entire
    lane-bearing half of this task belongs to helper_f alone.
  NEXT: Proceed with helper_f's 14 tickets; mediator_0 is roster-only.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-08-02T18:38:00Z
  TYPE: DECISION
  CLAIM: PRESERVE-THEN-DELETE on the undeliverable mail, rather than a clean
    delete. bootstrap_0's NOTICE to helper_f could never be consumed by its
    recipient, and `mailbox_protocol.md:76-77` makes deleting another agent's
    message an illegal write absent the owner directive I have. But a clean delete
    would have destroyed the only copy of a live review request: bootstrap_0
    authored 38 graph nodes describing the aetheric_mediator's design intent FROM
    DOCSTRINGS ALONE and named three specific assertions they wanted the lane owner
    to check. `mailbox_protocol.md:59-61` already prescribes the answer - copy
    anything actionable into the ticket first, because tickets are the durable
    truth and the mailbox never is. So the content landed in
    `2026-07-31_aetheric_mediator_core_story.md` `## Notes` as a RISK note before
    the message was removed.
  EVIDENCE:
  - context_compass/tickets/stories/2026-07-31_aetheric_mediator_core_story.md
  - context_compass/agent_onboarding/default/general/skills/mailbox_protocol.md:59-61
  IMPACT: The review debt survives its requester AND its intended reviewer. Without
    this it would have died with the roster row, and 38 nodes of confident graph
    prose about an unsettled design would read as verified to everyone downstream.
  NEXT: Whoever claims the aetheric_mediator lane checks the three assertions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T18:40:00Z
  TYPE: RISK
  CLAIM: SIX CLOSED EPICS CARRY AN OWNER SUITE RUN THAT WAS NEVER MADE, and the
    board was one compression away from losing the fact entirely. Five anchor-cap
    bookkeeping blocks recorded which anchors had been pruned to hold the 12-row
    cap. Buried in three of them was a different kind of statement: several pruned
    rows were `done_pending_owner_run`, so their outstanding 3.14t runs became
    "recorded ONLY in the ticket". Compressing those blocks as pure bookkeeping -
    which is what they look like - would have deleted the last board-level trace
    of six accepted-but-unverified epics. They are now named explicitly in the
    surviving anchor note. Which THREE of the four in melder_1's group were
    pending is UNKNOWN: their block said "three were" without naming them, and I
    did not guess.
  EVIDENCE:
  - context_compass/attention_board.md (Recently Closed Anchors, surviving note)
  IMPACT: Six epics were accepted on the strength of a validation run with no
    recorded result. That is an acceptance-integrity gap, not a hygiene one.
  NEXT: Owner either runs the suite or rules the six accepted without it; resolve
    the UNKNOWN three by reading the four tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T18:41:00Z
  TYPE: MEASURE
  CLAIM: Cleanup verified mechanically, not asserted. Zero live
    `| cowork | helper_f |` routing cells; zero exact `- Agent Name: helper_f`
    lines across active tickets; zero departed roster rows; 14 tickets carrying the
    new UNASSIGNED stamp against an expected 14; zero live mailbox messages; all 22
    MANAGED/USER-DEFINED region markers balanced across both boards; both boards
    still uniform LF at 0 CRLF. Boards shrank 221->211 and 184->166 lines.
  EVIDENCE:
  - context_compass/attention_board.md
  - context_compass/mailbox_board.md
  IMPACT: The expected-14 match is the load-bearing check: it proves the ticket
    sweep caught the seven lanes the board never routed, which was the whole risk.
  NEXT: Owner rules the three open questions.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T18:42:00Z
  TYPE: DECISION_REQUEST
  CLAIM: THREE decisions are the owner's and I deliberately made none of them.
    (1) `ux_aix_experiences` routes a story that was helper_f's and is now
    unassigned, while examples_0 - who is LIVE - holds the four sibling UX/AIX
    epics. Transfer it or leave it claimable? Handing a live agent a lane without
    their knowledge is the mirror of the rule that stopped me removing their rows.
    (2) bootstrap_0's `graph_semantics_authoring` and
    `crystallizer_transactional_survey` rows are `status: completed` routing
    tickets already in `completed/`, which breaks the invariant at
    `ticket_closure_attention_sync.md:33-34`. bootstrap_0 is ACTIVE; this board
    twice established that a live agent clears their own rows. Flagged, untouched.
    (3) The six unrecorded suite runs above.
  EVIDENCE:
  - context_compass/attention_board.md
  - context_compass/agent_onboarding/default/general/skills/ticket_closure_attention_sync.md:33-34
  IMPACT: Deciding any of these unilaterally would either orphan work someone was
    ready to own, or perform a closure act on a live agent's lane.
  NEXT: Owner answers; this ticket then closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T18:46:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: THE OWNER ASKED ME TO "MOVE ALL COMPLETEDS INTO COMPLETED", AND THE SET IS
    EMPTY. A status sweep of all 32 active tickets returns NOT ONE with
    `Status: done` or `Status: completed` - the live values are active, blocked,
    in_progress, pending, ready and review. There was nothing to move. What
    actually existed was FOUR board-versus-ticket disagreements wearing the same
    clothes, and they do not resolve the same way:
    (1) `graph_semantics_authoring` and (2) `crystallizer_transactional_survey` -
    rows marked `completed` whose tickets were ALREADY in `completed/`. Pure
    closure-sync that was never run. FIXED: rows retired to anchors claiming no
    acceptance their author had not already claimed.
    (3) `configuration_surface_uniformity_REMOVED` - a `done` row routing
    `tickets/stories/2026-08-01_config_foundation_base_story.md`, WHICH DOES NOT
    EXIST anywhere under `tickets/`. FIXED: removed, with the substance redirected
    to the live epic that owns the lane. Its claim of "9 STORIES OPENED" is false -
    none are on disk.
    (4) `bind_guard_sentinel_vs_set` and `conjure_boot_melds` - NOT FIXED, and
    deliberately. Each has an external source asserting a closure the TICKET
    denies. The benchmark task reads `Status: in_progress` in the ACTIVE tasks dir
    while a board anchor calls it `done`; melder_1 flagged that three-way
    disagreement on 2026-07-25 and it is unchanged. The boot-melds epic reads
    `Status: active (idea captured; NOT designed)` while bootstrap_0's roster row
    claims "CLOSED NOT-DOING under owner ruling" - a ruling that appears NOWHERE in
    the epic itself.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-23_bind_guard_sentinel_vs_set_benchmark_task.md:8-8
  - context_compass/tickets/epics/2026-07-20_conjure_boot_melds_epic.md:5-7
  - context_compass/attention_board.md
  IMPACT: `active_pointerboard.md:43` is explicit that the pointer board never
    overrides ticket truth. Moving either of the last two would have used a board
    row or a roster claim to overwrite the ticket that outranks it - manufacturing
    a closure record rather than syncing one. That is the difference between
    cleaning up and falsifying, and it is invisible if you only read the board.
  NEXT: Owner rules on (4): is the benchmark task done, and was boot-melds really
    closed not-doing? Either answer makes the move a one-line operation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner-directed retirement of two agents. mediator_0 is a one-line roster delete.
helper_f holds 14 active tickets and 7 board rows, all of which go UNASSIGNED
while staying ACTIVE - this is deliberately not a closure pass and claims no
acceptance on any of their work. Their authored notes and anchors stay verbatim
as the record of who did the work.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
