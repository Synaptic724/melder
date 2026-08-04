# Story: Investigate Role-Local Workflow System
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after workflow placement, ownership, and templating
  requirements were investigated and turned into the implementation basis.

## Metadata
- Story ID: STORY-2026-04-26-investigate-role-local-workflow-system
- Epic: EPIC-2026-04-26-role-local-workflow-system
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T11:22:01Z
- Updated: 2026-04-26T15:08:08Z

## User Narrative
As the workflow designer, I want the current role/class and template surfaces
mapped before implementation, so the new workflow system lands where the user
actually wants it.

## Value / MRP Alignment
This story keeps the workflow system from becoming another hidden registry or a
badly placed feature.

## Ticket Contract
- ENTRY_GATE: epic exists and the workflow-system lane is routed.
- EXECUTION_BOUNDARY:
  - current role and guide docs
  - current templates
  - this story and linked investigation task
- DEPENDENCIES:
  - current role layout
  - current class-creation guide
- EXIT_GATE: the role-local workflow shape is explicit enough to implement.
- FAILURE_ESCALATION: raise `BLOCKER` if the current role layout cannot express
  role-local workflow manifests cleanly.

## Requirements (Functional)
- Identify where `WORKFLOWS.MD` should live.
- Identify where `workflows/` folders should live.
- Identify where templates should live.
- Identify what policy text needs to change.

## Requirements (Non-Functional)
- Keep the change additive.
- Keep actual workflows role-local.

## Scope Boundaries
- In scope:
  - role folders
  - profile guide
  - templates
- Out of scope:
  - concrete workflow definitions

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested immediate implementation of the
  role-local workflow model after clarifying placement.

## Dependencies / Related Work
- TASK-2026-04-26-investigate-role-local-workflow-touchpoints

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-26-investigate-role-local-workflow-touchpoints
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The role-local workflow storage model is explicit.
- The template placement is explicit.
- The policy/guide insertion points are explicit.

## Validation / Test Plan
- Not run.
- Validation is document reread and evidence consistency only.

## UX / API / Data Notes
- This is a workflow-system doc/schema change, not a runtime code change.

## Risks / Mitigations
- Risk: the role-local model turns into duplicated boilerplate.
  Mitigation: keep manifests lightweight and use inheritance language.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should every future role always get a `WORKFLOWS.MD` by default?

## Decision Log
- Actual workflows are role-local; templates are global.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-26T11:22:01Z
  TYPE: FACT
  CLAIM: The current profile-creation guide already defines role-local folder
    creation and inheritance patterns, so workflow manifests fit naturally into
    the same role-local structure instead of needing a top-level registry.
  EVIDENCE:
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:121-159
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:183-236
  IMPACT: We can extend the role/class model instead of inventing a separate
    global workflow subsystem.
  NEXT: create the implementation story/tasks and workflow patch docs.
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
This story proves where the new workflow system belongs before implementation.
