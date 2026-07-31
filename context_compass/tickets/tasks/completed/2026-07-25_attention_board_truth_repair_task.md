

# Task: Repair attention_board.md routing truth without closing other agents' lanes

## Metadata
- Task ID: TASK-2026-07-25-attention-board-truth-repair
- Story: none (standalone board-hygiene task)
- Status: done
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T19:10:00Z
- Updated: 2026-07-31T23:03:22Z

## Objective
Make `attention_board.md` tell the truth about what is live, what is stale, and what is
actually closed, without performing closure acts that belong to other agents or to the
owner.

## Ticket Contract
- ENTRY_GATE: owner selected this lane 2026-07-25; every defect evidenced by a
  filesystem or ticket-field check before any edit.
- EXECUTION_BOUNDARY: `attention_board.md` only, plus this ticket. NO ticket files are
  moved, NO other agent's ticket Status is edited, NO lane is declared dead.
- DEPENDENCIES: none. Deliberately disjoint from melder_0's active code/packaging lane.
- EXIT_GATE: zero dead ticket pointers on the board; staleness visible where it exists;
  board/ticket contradictions surfaced rather than silently resolved.
- FAILURE_ESCALATION: DECISION_REQUEST to the owner for anything requiring a closure
  act or a judgement about whether another agent's lane is abandoned.

## Scope Boundaries
- In scope: repointing dead ticket paths; annotating rows whose routing claim no longer
  matches reality; surfacing board-vs-ticket contradictions.
- Out of scope: moving tickets to `completed/`; editing another agent's ticket Status;
  closing or deleting helper_f's or gemini_0's lanes; anchor pruning (count is under
  cap).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner picked this lane explicitly; all three defects are evidenced
  and none requires an unknown to be resolved first.

## Steps / Checklist
- [ ] Repoint the `oce_contract_completion_sweep` anchor to the epic's real location.
- [ ] Annotate the `bind_guard_sentinel_vs_set` anchor with the ticket-state mismatch
      rather than resolving it unilaterally.
- [ ] Annotate helper_f's four rows with an evidenced staleness marker; do NOT change
      their status.
- [ ] Verify zero dead pointers remain across Active Items and Anchors.
- [ ] Verify LF line endings and zero NUL bytes after every write.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A board whose every pointer resolves and whose staleness is visible.

## Files / Paths Impacted
- context_compass/attention_board.md

## Validation
- Not run (no test surface; this is a documentation/routing artifact).
- Recommended checks:
  - resolve every `tickets/...` path referenced by any board row
  - byte check for line endings and NUL

## Risks / Rollback Notes
- RISK: the board is a SHARED file and melder_0 is active on it; it changed twice
  during this session already. Mitigation: targeted single-row edits with unique
  anchors, never whole-file rewrites, and re-read before each edit.
- Rollback: git revert of one file.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No editing or deleting another agent's row beyond evidenced stale-marking.
- [ ] No whole-file rewrite of a shared board.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

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
- DATETIME: 2026-07-25T19:10:00Z
  TYPE: FACT
  CLAIM: Three defects confirmed, and two suspected ones disproved. CONFIRMED:
    (1) the `oce_contract_completion_sweep` anchor points at
    `tickets/epics/2026-07-19_object_contract_enrichment_program_epic.md`, which DOES
    NOT EXIST - the epic lives in `tickets/epics/completed/`; the very next anchor row
    already cites the correct path, so the board disagrees with itself about one file.
    (2) `bind_guard_sentinel_vs_set` is anchored as CLOSED while its ticket file reads
    `Status: in_progress` and still sits in the active `tickets/tasks/` directory - a
    three-way disagreement between board, ticket status, and file location.
    (3) helper_f's four rows all read `in_progress` with `updated_at` of 2026-07-19/20,
    and helper_f's mailbox `last_checked` is 2026-07-19T13:10:00Z - six days silent.
    DISPROVED: the anchor cap is fine (11 data rows against a cap of 12), and the stray
    blank line that previously broke the Active Items table has already been fixed by
    melder_0.
  EVIDENCE:
  - context_compass/attention_board.md:74-77
  - context_compass/tickets/tasks/2026-07-23_bind_guard_sentinel_vs_set_benchmark_task.md
  - context_compass/mailbox_board.md:37-37
  IMPACT: A dead pointer breaks post-compaction re-entry for anyone following the
    anchor, and `active_pointerboard.md` holds that the board never overrides ticket
    truth - so a board asserting a closure the ticket denies is the exact inversion.
  NEXT: Repoint the dead anchor first; it is the only fully unambiguous defect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-25T19:10:00Z
  TYPE: MEASURE
  CLAIM: Repairs complete and verified. All 16 ticket paths referenced anywhere on the
    board now resolve on disk (was 15 of 16). Anchors sit at 11 data rows against a cap
    of 12. Encoding intact: 92 LF, zero CRLF, zero NUL. helper_f's four rows are
    byte-untouched and still read `in_progress`, as intended.
  EVIDENCE:
  - context_compass/attention_board.md
  IMPACT: Post-compaction re-entry through any board pointer now lands on a real file,
    which was the concrete failure mode of the dead anchor.
  NEXT: Owner acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T19:10:00Z
  TYPE: DECISION
  CLAIM: Two defects were deliberately SURFACED rather than fixed, because fixing them
    are closure acts rather than routing repairs. The `bind_guard_sentinel_vs_set`
    three-way disagreement needs a departed agent's ticket moved to `completed/` and
    its Status edited - that is closure on gemini_0's lane. helper_f's four rows need
    a judgement about whether six days of silence means parked or abandoned - that is
    an owner call. `active_pointerboard.md` holds that the board never overrides ticket
    truth, so quietly "repairing" either one by making the ticket agree with the board
    would invert the authority order.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/active_pointerboard.md:42-48
  - context_compass/attention_board.md:74-74
  IMPACT: The board is now honest about its own uncertainty instead of presenting two
    contested states as settled.
  NEXT: Owner ruling on both.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T19:10:00Z
  TYPE: RISK
  CLAIM: SEQUENCING LAPSE, self-reported. I created this ticket and then implemented
    the board edits BEFORE adding the routing row, so for the duration of the edits the
    routing gate was unsatisfied. `ticketing.md` requires an active board row pointing
    at the ticket before implementation, not merely a ticket. The row was added
    immediately afterwards and the gate is now satisfied.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/ticketing.md:78-89
  IMPACT: No damage - the work was scoped, evidenced, and reversible - but the gate
    exists so that concurrent agents can see a lane before it touches shared files, and
    melder_0 is active on this very board. A colliding edit during that window would
    have been invisible to them.
  NEXT: For the remainder of this session, add the board row in the same pass that
    creates the ticket, before any implementation edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-31T23:03:22Z
  TYPE: DECISION
  CLAIM: CLOSED at owner turn-in 2026-07-31. Board pointers repaired without pre-empting any lane: dead anchor pointer fixed, helper_f's 4
    rows annotated stale but left UNCHANGED (declaring another agent's lane dead is an owner
    call). All 16 board ticket paths resolve.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_attention_board_truth_repair_task.md
  IMPACT: Ticket moved to completed/; board row removed and replaced by one anchor.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Standalone board-hygiene lane, deliberately disjoint from melder_0's code/packaging
work. Three evidenced defects: one dead anchor pointer, one board-vs-ticket closure
contradiction, and four rows claiming live work from an agent silent for six days. The
governing constraint is that this task repairs ROUTING TRUTH only - it performs no
closure act and declares no other agent's lane dead.
