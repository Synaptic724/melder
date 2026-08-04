# Epic: Build Role-Local Workflow System
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after role-local workflow manifests, folders, templates,
  policy docs, and the first general workflow set were landed.

## Metadata
- Epic ID: EPIC-2026-04-26-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:22:01Z
- Updated: 2026-04-26T15:08:08Z
- Target Window: 2026-Q2
- Related Program/Initiative: context_compass workflow primitives

## Problem / Opportunity
Context Compass has strong skill and role primitives, but no first-class,
role-local workflow system. Workflow is currently a concept in prose rather
than a stored artifact shape.

The desired model is:
- no top-level workflow registry
- workflows live inside roles or classes
- workflows are user-generated and user-approved, not agent-created at
  discretion
- roles may inherit workflow availability the same way they inherit skills

## MRP Alignment (Most Reasonable Product)
This epic adds the smallest coherent workflow system:
- role-local `WORKFLOWS.MD`
- role-local `workflows/` folders
- simple and advanced workflow templates
- policy text that workflows are user-owned and role-bound

## Ticket Contract
- ENTRY_GATE: current role structure, class-creation docs, and template
  surfaces are investigated and patch artifacts exist before implementation.
- EXECUTION_BOUNDARY:
  - `context_compass/templates/**`
  - `context_compass/PROFILE_CLASS_CREATION_GUIDE.md`
  - selected role folders under `agent_onboarding/default/**`
  - selected role folders under `agent_onboarding/user_defined/**`
  - workflow-system tickets and patch docs
- DEPENDENCIES:
  - profile class creation guide
  - current role layout
  - current templates
- EXIT_GATE: role-local workflow support exists, templates exist, and the new
  docs are reread and summarized.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementing role-local
  workflows requires a hidden top-level registry or breaks current role wiring.

## Goals (Outcomes)
- Add role-local `WORKFLOWS.MD` support.
- Add role-local `workflows/` folders.
- Add simple and advanced workflow templates.
- Add policy text that workflows are user-generated/user-approved only.
- Update role/class creation guidance to include workflows.

## Non-Goals (Explicit Exclusions)
- Creating a top-level `context_compass/workflows/` registry.
- Adding any real workflow definitions by default beyond placeholders.
- Changing current role resolution from `SKILLS.MD` to a new config system.

## Scope Boundaries
- In scope:
  - workflow storage model
  - workflow templates
  - role-local workflow placeholders and guidance
- Out of scope:
  - concrete reusable workflows
  - runtime code changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested immediate implementation of the
  role-local workflow system after correcting the earlier drift.

## Success Metrics
- `WORKFLOWS.MD` exists where needed.
- role-local `workflows/` folders exist where needed.
- simple and advanced templates exist.
- policy and guide docs reflect the role-local workflow model.

## Requirements (Functional + Non-Functional)
- Functional:
  - workflow manifests
  - workflow folders
  - templates
  - guide updates
- Non-functional:
  - user-owned workflow policy
  - no top-level workflow registry
  - minimal but coherent inheritance model

## Constraints / Assumptions
- Agents may suggest or scaffold workflows only when asked.
- General skills are assumed by default; advanced workflows may rely on them.
- Role-local workflows should follow parent-first inheritance conceptually.

## Dependencies / External References
- `PROFILE_CLASS_CREATION_GUIDE.md`
- `agent_onboarding/default/general/SKILLS.MD`
- `agent_onboarding/default/engineer/SKILLS.MD`
- `templates/`

## Milestones (Track Progress)
- [ ] Milestone 1: Investigation and patch contracts are explicit.
- [ ] Milestone 2: Role-local workflow support exists.
- [ ] Milestone 3: Templates and guide docs are landed.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-26-investigate-role-local-workflow-system
- [ ] Story: STORY-2026-04-26-implement-role-local-workflow-system

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete the investigation story and capture the workflow model.
- [ ] Task: Complete the implementation story and child tasks.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- There is no top-level workflow registry.
- Role-local workflow manifests and folders exist.
- Simple and advanced templates exist.
- Role/class creation guidance explains the new workflow model.

## Risks / Mitigations
- Risk: workflow storage drifts into a second hidden registry.
  Mitigation: keep actual workflows role-local and templates global only.
- Risk: too much boilerplate for roles with no workflows.
  Mitigation: keep manifests lightweight and allow empty/no-active-workflow
  states.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Re-read the changed role-local workflow docs and templates.
- Not run:
  - no runtime tests unless later requested

## Rollout / Adoption Plan
- Use the new templates when a user asks to create workflows.
- Keep workflows role-local by default.

## Open Questions
- Should future roles always include `WORKFLOWS.MD`, or only when workflows are
  needed?

## Decision Log
- Workflow templates may be top-level; workflow instances should be role-local.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/role_local_workflow_system/architecture_patch.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_role_local_workflow_manifests.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_workflow_templates.md
  - system_docs/patches/active/role_local_workflow_system/component_patch_profile_creation_guide.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decide after the workflow system is accepted.

## Notes
- DATETIME: 2026-04-26T11:22:01Z
  TYPE: DECISION
  CLAIM: The workflow system should be role-local, not top-level. Templates can
    be global, but actual workflow definitions should live inside the role
    folders and be user-generated/user-approved only.
  EVIDENCE:
  - user_decision: keep workflows in roles/classes
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:121-159
  IMPACT: The implementation should avoid any top-level workflow registry.
  NEXT: create the investigation story/task and the workflow-system patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the role-local workflow system: manifests, folders, templates,
and user-ownership policy.
