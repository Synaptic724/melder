# Task: Investigate Conduit Same-Frame Link Guard

- Completed: 2026-03-28T21:38:03Z
- Summary: Verified that conduits already carry frame identity locally and that
  the current public link path did not enforce same-frame-only peer contracts.
  The investigation directly fed the follow-up runtime guard task.

## Metadata
- Task ID: TASK-2026-03-28-investigate-conduit-same-frame-link-guard
- Story: STORY-2026-03-16-aethericrift-system-bootstrap
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-28T14:55:48Z
- Updated: 2026-03-28T21:38:03Z

## Objective
Investigate whether the current conduit link path explicitly forbids
cross-frame conduit linking, document the actual behavior with evidence, and
capture whether a dedicated runtime invariant/task is needed before AR frame
topology decisions continue.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a focused ticketed investigation
  before any code change.
- EXECUTION_BOUNDARY: read-only investigation plus ticket/board updates only.
- DEPENDENCIES:
  - STORY-2026-03-16-aethericrift-system-bootstrap
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py
- EXIT_GATE: the ticket notes capture whether same-frame enforcement exists
  today, whether conduits already know their frame, and whether a dedicated
  change task should follow.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the relevant link path cannot
  be resolved from current source evidence.

## Scope Boundaries
- In scope:
  - conduit public link/sever path
  - ward `_link` / contract-creation path
  - conduit frame identity fields relevant to same-frame enforcement
  - ticket/board documentation of findings
- Out of scope:
  - code changes to enforce the invariant
  - test implementation
  - broader ARS configuration changes

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the investigation completed and the resulting evidence was
  used to drive the follow-up implementation task.

## Steps / Checklist
- [x] Create a focused investigation task and route the board to it.
- [x] Inspect the public conduit link/sever path.
- [x] Inspect the lower-level ward contract-creation path.
- [x] Confirm whether conduits already carry frame identity locally.
- [x] Record findings and impact in ticket notes.
- [x] Decide with the user whether to create a follow-up implementation task
      for same-frame enforcement.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Evidence-backed answer on whether same-frame conduit linking is currently
  enforced
- Evidence-backed answer on whether conduits already carry frame identity
- Recommendation on whether a dedicated runtime guard task should follow

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-03-28_investigate_conduit_same_frame_link_guard_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/stories/2026-03-16_aethericrift_system_bootstrap_story.md

## Validation
- Not run.
- Read-only source investigation only.
- Recommended commands:
  - `Select-String -Path src/melder/aether/conduit/conduit.py -Pattern "def link|def sever_link" -Context 0,40`
  - `Select-String -Path src/melder/aether/conduit/conduit_ward/conduit_ward.py -Pattern "def _link|def _create_new_contract" -Context 0,60`

## Risks / Rollback Notes
- Risk: AR topology decisions accidentally assume a same-frame invariant that
  is not actually enforced by the runtime.
  Rollback: treat cross-frame-link prevention as `UNKNOWN` or `FACT` strictly
  from code evidence and add an explicit follow-up task before relying on it.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-03-28T14:55:48Z
  TYPE: FACT
  CLAIM: Conduits already carry their frame identity directly on the runtime
    object through `_aetheric_frame`, so a same-frame link guard would not need
    an `Aether` round-trip just to know whether two conduits belong to the same
    frame.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:112-129
  IMPACT: If we choose to enforce same-frame-only linking, the runtime already
    has the minimum local data needed to compare the two conduit frames.
  NEXT: inspect the public `link(...)` and ward `_link(...)` path to see
    whether that comparison already exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T14:55:48Z
  TYPE: FACT
  CLAIM: The current public conduit link path does not appear to enforce a
    same-frame hard-stop. `Conduit.link(...)` validates dynamic mode, target
    type, and target id presence, then delegates to `ConduitWard._link(...)`.
    The ward path checks lesser/self/dynamic/policy constraints and then creates
    the contract directly, but no `_aetheric_frame` equality check appears in
    that path.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2463-2500
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:573-652
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:652-698
  IMPACT: We should not assume cross-frame conduit linking is forbidden by the
    current runtime when making AR topology decisions.
  NEXT: decide whether to create a dedicated implementation task that enforces a
    same-frame invariant in `ConduitWard._link(...)`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task pinned down the runtime truth for same-frame linking: conduits already
carry frame identity locally, but the public link/ward path did not enforce
same-frame equality. That evidence directly fed the completed implementation
task.
