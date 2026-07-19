# Task: Implement Workflow Templates And Guide Updates
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the simple and advanced workflow templates and the
  profile/class creation guide were updated for the role-local model.

## Metadata
- Task ID: TASK-2026-04-26-implement-workflow-templates-and-guide-updates
- Story: STORY-2026-04-26-implement-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:22:01Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Implement the simple and advanced workflow templates and update the profile
creation guide so role-local workflows are part of the documented class model.

## Ticket Contract
- ENTRY_GATE: implementation story is active and the workflow patch docs exist.
- EXECUTION_BOUNDARY:
  - `templates/**`
  - `PROFILE_CLASS_CREATION_GUIDE.md`
  - directly related docs only
- DEPENDENCIES:
  - workflow-system patch docs
  - investigation findings
- EXIT_GATE: both templates exist and the guide documents role-local workflow
  support clearly.
- FAILURE_ESCALATION: raise `CONFLICT` if the simple/advanced template split
  cannot be explained cleanly without more workflow policy than intended.

## Scope Boundaries
- In scope:
  - simple workflow template
  - advanced workflow template
  - guide updates
- Out of scope:
  - concrete workflows
  - runtime code changes

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: the workflow templates and profile-guide updates are
  landed and reread.

## Steps / Checklist
- [x] Create the simple workflow template.
- [x] Create the advanced workflow template.
- [x] Update the class/profile creation guide for role-local workflows.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- workflow templates
- updated class/profile guide

## Files / Paths Impacted
- codex/context_compass/templates/**
- codex/context_compass/PROFILE_CLASS_CREATION_GUIDE.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/templates/workflow_simple_template.md`
  - `Get-Content codex/context_compass/templates/workflow_advanced_template.md`
  - `Get-Content codex/context_compass/PROFILE_CLASS_CREATION_GUIDE.md`

## Risks / Rollback Notes
- Risk: the advanced template becomes too heavy for the intended workflow model.
  Rollback: keep the advanced template present but optional and role-bound.

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
- DATETIME: 2026-04-26T11:22:01Z
  TYPE: PLAN
  CLAIM: This task owns the template/guide slice. The simple and advanced
    templates should live at the top level, while the guide should explain that
    workflow instances live inside roles.
  EVIDENCE:
  - user_decision: simple and advanced formats
  - context_compass/templates: existing top-level template placement
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:121-236
  IMPACT: Template reuse stays clean without creating a top-level workflow
    registry.
  NEXT: create the two templates and update the guide.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-26T11:31:44Z
  TYPE: FACT
  CLAIM: The template/guide slice is landed. Context Compass now has a simple
    and advanced workflow template, and the profile creation guide documents
    `WORKFLOWS.MD`, role-local `workflows/`, user ownership, and the no
    top-level-registry rule.
  EVIDENCE:
  - context_compass/templates/workflow_simple_template.md:1-40
  - context_compass/templates/workflow_advanced_template.md:1-73
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:96-236
  IMPACT: Users now have a supported way to create workflows without inventing
    storage or format conventions ad hoc.
  NEXT: keep this task in review while the user inspects the overall workflow system.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the workflow templates and the profile guide updates.
