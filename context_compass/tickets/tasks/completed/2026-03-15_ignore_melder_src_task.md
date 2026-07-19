# Task: Ignore Melder Src Tree

## Metadata
- Task ID: TASK-2026-03-15-ignore-melder-src
- Story: none
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-03-15T12:10:30Z
- Updated: 2026-03-15T22:05:00Z

## Objective
Add the newly introduced `src/` tree to repository ignore rules so the local
Melder source copy does not get tracked by git.

## Ticket Contract
- ENTRY_GATE: user explicitly requested that the added `src/` tree be ignored.
- EXECUTION_BOUNDARY: root `.gitignore`, this task, and attention-board routing
  only.
- DEPENDENCIES: repo root contains `src/melder` and currently has no root
  `.gitignore`.
- EXIT_GATE: `.gitignore` exists at repo root and ignores `/src/`.
- FAILURE_ESCALATION: raise `BLOCKER` if ignore rules already exist elsewhere
  and conflict with a root-level ignore entry.

## Scope Boundaries
- In scope:
  - create or update root `.gitignore`
  - ignore the `src/` tree
  - route and document the change in `context_compass`
- Out of scope:
  - broader ignore cleanup
  - AR architecture or code implementation changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested that the added Melder `src/` tree be kept
  out of git tracking.

## Steps / Checklist
- [x] Verify whether a root `.gitignore` already exists.
- [x] Add a root ignore entry for `/src/`.
- [ ] Validate the ignore file state and update task notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Root `.gitignore` file with `/src/` ignored.

## Files / Paths Impacted
- .gitignore
- codex/context_compass/tickets/tasks/2026-03-15_ignore_melder_src_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content .gitignore`
  - `git status --short`

## Risks / Rollback Notes
- Risk: ignoring the whole `src/` tree may hide future repo-root source work.
  Rollback: narrow the ignore path later if the user decides some of `src/`
  should be tracked.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
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
- DATETIME: 2026-03-15T12:10:30Z
  TYPE: FACT
  CLAIM: The repo root currently has a `src/melder` tree but no root
    `.gitignore`, so an explicit ignore entry is needed if that local source
    copy should stay untracked.
  EVIDENCE:
  - .gitignore:1-1
  IMPACT: Adding `/src/` at the root ignore layer is the smallest change that
    satisfies the request without touching broader repo behavior.
  NEXT: validate the new ignore file and then ask whether this task should be
    closed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task captures the small repo housekeeping change to keep the new local
Melder `src/` tree out of git tracking. The next step is validation and user
acceptance.


## Completion Summary
- Completed: 2026-03-15T22:05:00Z
- Summary: Superseded or completed during AR packaging cleanup; retained for historical reference.

