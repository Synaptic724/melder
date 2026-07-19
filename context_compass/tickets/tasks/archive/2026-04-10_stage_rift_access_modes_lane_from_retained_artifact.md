# Task: Stage Rift Access Modes Lane From Retained Artifact

## Metadata
- Task ID: TASK-2026-04-10-stage-rift-access-modes-lane-from-retained-artifact
- Story: STORY-2026-04-10-define-rift-access-modes-and-space-semantics
- Status: draft
- Owner: codex
- Priority: p1
- Created: 2026-04-10T00:50:25Z
- Updated: 2026-04-10T00:50:25Z

## Objective
Create the dedicated access-mode epic/story/task lane and re-home the retained
Rift access-mode artifact under it.

## Ticket Contract
- ENTRY_GATE: the retained access-mode artifact exists and the user explicitly
  asked whether the static/capability/dynamic split should get its own epic.
- EXECUTION_BOUNDARY: ticket/artifact staging only.
- DEPENDENCIES:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - tickets/epics/completed/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md
- EXIT_GATE: the new epic/story/task exist and the retained artifact points at
  the new lane instead of the closed lifecycle epic.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the retained artifact is too
  incomplete to stage a real lane.

## Scope Boundaries
- In scope:
  - new epic/story/task files
  - retained artifact re-homing
  - artifact-board sync
- Out of scope:
  - runtime implementation
  - board activation
  - tests

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as the bounded staging task for the new access-mode lane.

## Steps / Checklist
- [ ] Create the epic.
- [ ] Create the story.
- [ ] Create this staging task.
- [ ] Re-home the retained artifact under the new lane.
- [ ] Sync artifact-board references.

## Deliverables
- new access-mode epic/story/task lane
- retained artifact association under the new lane

## Files / Paths Impacted
- codex/context_compass/tickets/epics/
- codex/context_compass/tickets/stories/
- codex/context_compass/tickets/tasks/
- codex/context_compass/tickets/artifacts/
- codex/context_compass/artifact_board.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: the new lane duplicates the closed lifecycle epic instead of isolating
  the access-mode problem.
  Rollback: keep the new lane explicitly about mode semantics and not lifecycle.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the access-mode lane is either implemented or retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-10T00:50:25Z
  TYPE: PLAN
  CLAIM: The retained access-mode artifact has outlived the lifecycle epic that
    originally hosted it. The clean fix is to stage a new dedicated lane rather
    than keep static/capability/dynamic semantics attached to a completed parent.
  EVIDENCE:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:1-202
  - tickets/epics/completed/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md:1-187
  IMPACT: Future access-mode work can now start from a clean lane instead of
    reopening the wrong completed epic.
  NEXT: update the retained artifact metadata and artifact-board row to point at
    the new epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task stages the new access-mode lane only. It does not activate the lane
or implement runtime behavior yet.
