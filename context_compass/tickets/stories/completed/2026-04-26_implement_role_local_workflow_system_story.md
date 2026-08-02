# Story: Implement Role-Local Workflow System
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the role-local workflow system landed with manifests,
  templates, guide updates, and the general workflow catalog.

## Metadata
- Story ID: STORY-2026-04-26-implement-role-local-workflow-system
- Epic: EPIC-2026-04-26-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:22:01Z
- Updated: 2026-04-26T15:08:08Z

## User Narrative
As the user, I want workflows to live inside roles or classes, so that they
are role-bound, user-generated, and not hidden top-level behavior.

## Value / MRP Alignment
This story lands the actual role-local workflow system: manifests, role folders,
templates, and the user-ownership policy.

## Ticket Contract
- ENTRY_GATE: investigation findings are explicit and the patch-doc set exists.
- EXECUTION_BOUNDARY:
  - `PROFILE_CLASS_CREATION_GUIDE.md`
  - `templates/**`
  - selected role folders under `agent_onboarding/default/**`
  - selected role folders under `agent_onboarding/user_defined/**`
  - this story and linked child tasks
- DEPENDENCIES:
  - investigation story/task
  - workflow-system patch docs
- EXIT_GATE: role-local workflow manifests and folders exist, templates exist,
  and the changed docs are reread.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the role-local workflow model
  cannot be expressed cleanly without a top-level registry.

## Requirements (Functional)
- Add `WORKFLOWS.MD` support for roles.
- Add role-local `workflows/` folders.
- Add simple and advanced workflow templates.
- Add policy text that workflows are user-generated/user-approved only.

## Requirements (Non-Functional)
- Keep workflows role-local.
- Keep templates global.
- Keep the model additive.

## Scope Boundaries
- In scope:
  - manifests
  - folders
  - templates
  - guide/policy docs
- Out of scope:
  - real workflow definitions
  - top-level workflow registry

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: role-local workflow manifests, folders, templates, and
  guide updates are landed and reread.

## Dependencies / Related Work
- STORY-2026-04-26-investigate-role-local-workflow-system
- TASK-2026-04-26-implement-role-local-workflow-manifests
- TASK-2026-04-26-implement-workflow-templates-and-guide-updates
- TASK-2026-04-26-author-cleanup-context-compass-workflow
- TASK-2026-04-26-author-general-workflow-catalog

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-26-implement-role-local-workflow-manifests
- [x] Task: TASK-2026-04-26-implement-workflow-templates-and-guide-updates
- [x] Task: TASK-2026-04-26-author-cleanup-context-compass-workflow
- [x] Task: TASK-2026-04-26-author-general-workflow-catalog
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- role-local `WORKFLOWS.MD` support exists
- role-local `workflows/` folders exist
- simple and advanced workflow templates exist
- policy/guide docs reflect user-owned, role-local workflows
- `general` ships one real starter workflow: `cleanup_context_compass`
- `general` ships the requested active workflow set and the optional on-demand
  workflow set

## Validation / Test Plan
- Re-read manifests, templates, and guide docs.
- Not run:
  - no runtime tests unless later requested

## UX / API / Data Notes
- This is a role-system and documentation-structure change, not runtime code.

## Risks / Mitigations
- Risk: role-local workflow support becomes noisy boilerplate.
  Mitigation: keep manifests lightweight and allow no-active-workflow states.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should all roles eventually get explicit starter workflow examples, or only
  when the user asks?

## Decision Log
- No top-level workflow registry.
- Templates stay top-level.
- Workflow definitions stay role-local.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/role_local_workflow_system/architecture_patch.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_role_local_workflow_manifests.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_workflow_templates.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_profile_creation_guide.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_general_workflow_catalog.md
  - tickets/tasks/2026-04-26_author_cleanup_context_compass_workflow_task.md
  - tickets/tasks/2026-04-26_author_general_workflow_catalog_task.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decide after the workflow system is accepted.

## Notes
- DATETIME: 2026-04-26T11:22:01Z
  TYPE: DECISION
  CLAIM: The implementation should create role-local `WORKFLOWS.MD` and
    `workflows/` support, not a top-level workflow registry. Templates should
    be global because they are scaffolding, not workflow instances.
  EVIDENCE:
  - user_decision: workflows in roles/classes
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:121-159
  - context_compass/templates: current top-level template placement
  IMPACT: The system stays user-owned and role-bound instead of drifting into
    hidden global automation.
  NEXT: create the patch docs and implement the two slices: manifests/folders
    and templates/guide docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T11:31:44Z
  TYPE: FACT
  CLAIM: The role-local workflow system is landed. Selected roles now have
    `WORKFLOWS.MD` manifests and role-local `workflows/` folders, the general
    baseline now defines the role-local workflow policy, simple and advanced
    workflow templates exist under `templates/`, and the profile creation guide
    documents the model explicitly.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/role_local_workflows.md:1-28
  - context_compass/agent_onboarding/default/general/WORKFLOWS.MD:1-15
  - context_compass/agent_onboarding/default/engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/design_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/default/qa_engineer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/WORKFLOWS.MD:1-14
  - context_compass/agent_onboarding/user_defined/data_engineer/WORKFLOWS.MD:1-14
  - context_compass/templates/workflow_simple_template.md:1-40
  - context_compass/templates/workflow_advanced_template.md:1-73
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:96-236
  - context_compass/agent_onboarding/default/general/workflows/cleanup_context_compass.md:1-95
  - context_compass/agent_onboarding/default/general/workflows/start_context_compass_work.md:1-78
  - context_compass/agent_onboarding/default/general/workflows/turn_in_selected_tickets.md:1-72
  - context_compass/agent_onboarding/default/general/workflows/sync_attention_board.md:1-71
  - context_compass/agent_onboarding/default/general/workflows/role_creation.md:1-31
  - context_compass/agent_onboarding/default/general/workflows/workflow_creation.md:1-31
  IMPACT: Workflows are now first-class role artifacts without introducing a
    top-level workflow registry.
  NEXT: present the landed model and call out that there was no top-level
    workflow system to remove.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T12:32:40Z
  TYPE: FACT
  CLAIM: The `general` workflow catalog now matches the requested split:
    active `cleanup_context_compass`, `start_context_compass_work`,
    `turn_in_selected_tickets`, and `sync_attention_board`, plus on-demand
    `role_creation` and `workflow_creation`.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/WORKFLOWS.MD:11-19
  - context_compass/agent_onboarding/default/general/workflows/start_context_compass_work.md:1-77
  - context_compass/agent_onboarding/default/general/workflows/turn_in_selected_tickets.md:1-71
  - context_compass/agent_onboarding/default/general/workflows/sync_attention_board.md:1-71
  - context_compass/agent_onboarding/default/general/workflows/role_creation.md:1-31
  - context_compass/agent_onboarding/default/general/workflows/workflow_creation.md:1-31
  IMPACT: The role-local workflow system now includes both starter workflows and
    discoverable optional scaffolds under the same manifest model.
  NEXT: present the full workflow set and call out which ones are optional.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T12:31:03Z
  TYPE: FACT
  CLAIM: The `general` workflow catalog now matches the requested split:
    active workflows for day-to-day routing and cleanup, plus on-demand
    scaffolding workflows that agents can know exist without reading them by
    default.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/WORKFLOWS.MD:11-19
  - context_compass/agent_onboarding/default/general/skills/role_local_workflows.md:15-25
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:144-160
  IMPACT: The role-local workflow model now supports both baseline workflows
    and discoverable optional scaffolds without collapsing them into one list.
  NEXT: present the full workflow set and call out which ones are optional.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the actual role-local workflow system.
