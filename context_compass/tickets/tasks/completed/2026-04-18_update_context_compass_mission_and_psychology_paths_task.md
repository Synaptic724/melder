# Task: Update Context Compass Mission And Psychology Paths
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-update-context-compass-mission-and-psychology-paths
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T00:00:00Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Update live `context_compass` policy references now that `mission.md` and
`psychology.md` live directly under `codex/context_compass/`.

## Ticket Contract
- ENTRY_GATE: the user explicitly moved the two docs and requested live
  reference updates under `codex/context_compass`.
- EXECUTION_BOUNDARY: patch live `context_compass` references only; do not
  rewrite completed ticket history.
- DEPENDENCIES:
  - codex/context_compass/AGENTS.MD
  - codex/context_compass/mission.md
  - codex/context_compass/psychology.md
- EXIT_GATE: live `context_compass` references point at the new locations and
  the board routes this task accurately.
- FAILURE_ESCALATION: raise `BLOCKER` if another live context-compass doc still
  points at the old locations after the search pass.

## Scope Boundaries
- In scope:
  - live `codex/context_compass` references to `mission.md` and `psychology.md`
  - board routing for this task
- Out of scope:
  - completed ticket history
  - non-`context_compass` references elsewhere in the repo

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the live references are patched and the verification
  search now shows only historical completed-ticket references using the old
  paths.

## Steps / Checklist
- [ ] Confirm all live `context_compass` references to the old paths.
- [ ] Patch the live references to the new `context_compass` paths.
- [ ] Re-run the search to verify no live path drift remains.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated live `context_compass` path references
- verification search result

## Files / Paths Impacted
- codex/context_compass/AGENTS.MD
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/tasks/2026-04-18_update_context_compass_mission_and_psychology_paths_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-ChildItem codex\\context_compass -Recurse -File | Select-String -Pattern 'codex/mission\\.md|codex\\\\mission\\.md|codex/psychology\\.md|codex\\\\psychology\\.md'`

## Risks / Rollback Notes
- Risk: rewriting completed ticket history would distort historical evidence.
  Rollback: patch only live docs and leave completed tickets as historical artifacts.

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
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T00:00:00Z
  TYPE: FACT
  CLAIM: The live path drift is confined to `codex/context_compass/AGENTS.MD`.
    The broader search under `codex/context_compass` only found the old
    parent-folder mission/psychology references in that live file; the
    remaining hits are completed ticket history that should stay unchanged.
  EVIDENCE:
  - codex/context_compass/AGENTS.MD:75-77
  - codex/context_compass/AGENTS.MD:114-115
  - codex/context_compass/AGENTS.MD:140-141
  - codex/context_compass/AGENTS.MD:183-183
  IMPACT: The fix is narrow and safe. We only need to patch the canonical live
    policy doc instead of rewriting history across completed tickets.
  NEXT: update the live references in `AGENTS.MD`, then rerun the search to
    confirm the drift is gone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T10:19:44Z
  TYPE: MEASURE
  CLAIM: The live path correction is complete. `AGENTS.MD` now points at
    `context_compass/mission.md` and `context_compass/psychology.md`, and the
    old-path search under `codex/context_compass` only returns completed-ticket
    history.
  EVIDENCE:
  - codex/context_compass/AGENTS.MD:75-77
  - codex/context_compass/AGENTS.MD:114-115
  - codex/context_compass/AGENTS.MD:140-141
  - codex/context_compass/AGENTS.MD:183-183
  - validation_result: `Get-ChildItem codex\\context_compass -Recurse -File | Select-String -Pattern 'codex/mission\\.md|codex\\\\mission\\.md|codex/psychology\\.md|codex\\\\psychology\\.md'` -> completed-ticket references only
  IMPACT: The live context-compass policy surface is aligned with the moved
    mission/psychology docs.
  NEXT: return the path-fix task for review/acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the live `context_compass` path correction for `mission.md` and
`psychology.md`.