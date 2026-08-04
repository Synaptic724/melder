# Task: Investigate Role-Local Workflow Touchpoints
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the workflow-system touchpoints across roles,
  templates, guide docs, and routing surfaces were inventoried.

## Metadata
- Task ID: TASK-2026-04-26-investigate-role-local-workflow-touchpoints
- Story: STORY-2026-04-26-investigate-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:22:01Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Map the current role/class and template surfaces so the new workflow system can
land role-local and user-owned.

## Ticket Contract
- ENTRY_GATE: epic and investigation story exist and the current docs are readable.
- EXECUTION_BOUNDARY:
  - `PROFILE_CLASS_CREATION_GUIDE.md`
  - selected role `SKILLS.MD` files
  - `templates/`
  - this task ticket
- DEPENDENCIES:
  - current role layout
  - current profile guide
- EXIT_GATE: the role-local implementation split is explicit.
- FAILURE_ESCALATION: raise `BLOCKER` if the current layout cannot support
  role-local workflow manifests cleanly.

## Scope Boundaries
- In scope:
  - role-local manifest placement
  - template placement
  - policy insertion points
- Out of scope:
  - concrete workflow examples

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested implementation and the role-local
  touchpoints needed one bounded discovery pass first.

## Steps / Checklist
- [ ] Read the profile creation guide and current role files.
- [ ] Record the first evidence-backed role-local workflow model.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed workflow storage model
- evidence-backed template placement model

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_investigate_role_local_workflow_touchpoints_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/PROFILE_CLASS_CREATION_GUIDE.md`
  - `Get-ChildItem codex/context_compass/templates`

## Risks / Rollback Notes
- Risk: we overbuild support before proving the minimal model.
  Rollback: land the minimum manifests, folders, and templates only.

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
  TYPE: FACT
  CLAIM: The clean split is: global templates, role-local manifests and
    workflow folders. That preserves user ownership while avoiding a top-level
    workflow registry.
  EVIDENCE:
  - user_decision: workflows should live in roles/classes
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:121-159
  - context_compass/templates: `epic_template.md`, `story_template.md`, `task_template.md`
  IMPACT: The implementation should create `WORKFLOWS.MD` and `workflows/`
    under roles and only add templates at the top level.
  NEXT: create the patch docs and implement the role-local workflow structure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task pins down the role-local workflow model before implementation.
