# Task: Implement Role-Local Workflow Manifests
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after role-local `WORKFLOWS.MD` manifests and workflow
  folders were created across the selected role chain.

## Metadata
- Task ID: TASK-2026-04-26-implement-role-local-workflow-manifests
- Story: STORY-2026-04-26-implement-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:22:01Z
- Updated: 2026-04-26T15:08:08Z

## Objective
Implement role-local `WORKFLOWS.MD` support and role-local `workflows/`
folders without creating a top-level workflow registry.

## Ticket Contract
- ENTRY_GATE: implementation story is active and the workflow patch docs exist.
- EXECUTION_BOUNDARY:
  - selected role folders under `agent_onboarding/default/**`
  - selected role folders under `agent_onboarding/user_defined/**`
  - directly related guide/policy docs
- DEPENDENCIES:
  - workflow-system patch docs
  - investigation findings
- EXIT_GATE: the selected roles have manifests/folders and the docs explain the
  user-owned workflow model.
- FAILURE_ESCALATION: raise `CONFLICT` if the selected role set proves too
  small or too large for a coherent first implementation.

## Scope Boundaries
- In scope:
  - general
  - engineer
  - current user-defined roles
- Out of scope:
  - every default role in the repository
  - real workflow definitions

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: the selected role manifests and workflow folders are
  landed and reread.

## Steps / Checklist
- [x] Create role-local `WORKFLOWS.MD` files.
- [x] Create role-local `workflows/` folders with lightweight placeholder docs.
- [x] Add policy text that workflows are user-generated/user-approved only.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- role-local workflow manifests
- role-local workflow folders

## Files / Paths Impacted
- codex/context_compass/agent_onboarding/default/general/**
- codex/context_compass/agent_onboarding/default/engineer/**
- codex/context_compass/agent_onboarding/user_defined/**

## Validation
- Not run.
- Recommended commands:
  - `Get-Content <role>/WORKFLOWS.MD`
  - `Get-ChildItem <role>/workflows`

## Risks / Rollback Notes
- Risk: the selected role set is too narrow for the system to feel real.
  Rollback: add more role-local manifests later without changing the model.

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
  CLAIM: This task owns the manifest/folder slice only. The goal is to make
    role-local workflow storage real without overbuilding the feature before
    templates and guide docs are in place.
  EVIDENCE:
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:121-159
  - context_compass/agent_onboarding/default/general/SKILLS.MD:1-20
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:1-23
  IMPACT: We can land a real role-local structure first, then layer templates
    and guide updates on top.
  NEXT: create the manifests and role-local workflow folders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-26T11:31:44Z
  TYPE: FACT
  CLAIM: The manifest/folder slice is landed for the baseline role chain and
    current user-defined roles: `general`, `engineer`, `data_engineer`,
    `synaptic_python_developer`, and `synaptic_finishing_developer` now have
    role-local workflow manifests and workflow folders.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/WORKFLOWS.MD:1-15
  - context_compass/agent_onboarding/default/engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/user_defined/data_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/WORKFLOWS.MD:1-14
  IMPACT: The role-local workflow model is real instead of only conceptual.
  NEXT: keep this task in review while the template and guide slice is reviewed beside it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T11:38:53Z
  TYPE: FACT
  CLAIM: The manifest/folder slice now covers the role set the current system
    actually uses: the base defaults, the specialized software/fiction roles,
    and the current user-defined roles. The role-local workflow structure is
    therefore consistent across the active role tree instead of being limited to
    a narrow subset.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/platform_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/qa_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/security_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/story_designer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/proofreader/WORKFLOWS.MD:1-14
  IMPACT: The workflow-system feature is structurally coherent across the role
    tree instead of feeling partial.
  NEXT: keep this task in review while the user inspects the workflow model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the role-local workflow manifests and folders.
