# Story: Investigate Multi-Contract Frame Policy Model

## Metadata
- Story ID: STORY-2026-04-11-investigate-multi-contract-frame-policy-model
- Epic: EPIC-2026-04-11-frame-scoped-contract-registries-and-rift-binding
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-11T00:12:09Z
- Updated: 2026-04-11T00:12:09Z

## User Narrative
As the Rift runtime designer, I want the current ACL model audited and the
target multi-contract frame policy model defined, so that implementation can
start from one explicit contract instead of conflicting assumptions.

## Value / MRP Alignment
This story prevents us from implementing the wrong permission model. It keeps
descriptor truth stable while letting many policy lenses exist per frame.

## Ticket Contract
- ENTRY_GATE: the new epic exists and the user explicitly asked for discovery
  plus a proposal before runtime edits begin.
- EXECUTION_BOUNDARY: discovery and proposal only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_frame_scoped_contract_registries_and_rift_binding_epic.md
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md
  - tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md
  - tickets/tasks/2026-04-11_propose_multi_contract_frame_policy_implementation_plan.md
- EXIT_GATE: the current model is audited, the target model is defined, and a
  concrete implementation proposal is ready for user review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation still leaves
  multiple materially different implementation paths plausible.

## Requirements (Functional)
- audit the current Nexus/frame ACL model
- define the target multi-contract frame model
- define the Rift binding shape
- produce one implementation proposal

## Requirements (Non-Functional)
- evidence-first
- no runtime edits
- no policy drift

## Scope Boundaries
- In scope:
  - ACL contract multiplicity per frame
  - codegen contract multiplicity per frame
  - `FrameLinkContract` selected binding role
  - migration sequencing
- Out of scope:
  - runtime implementation
  - UI endpoint work
  - CommandOps ownership changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the first audit task is complete enough that the target-model
  definition task can now become the active discovery lane.

## Dependencies / Related Work
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-11-audit-current-nexus-acl-model-and-migration-seams
- [ ] Task: TASK-2026-04-11-define-frame-scoped-contract-registry-and-rift-binding-model
- [ ] Task: TASK-2026-04-11-propose-multi-contract-frame-policy-implementation-plan
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The current ACL model and seams are documented with evidence.
- The target multi-contract frame model is explicit.
- One implementation proposal is ready for review before code work starts.

## Validation / Test Plan
- Discovery/proposal only in this story.

## UX / API / Data Notes
- Descriptor stays canonical frame truth.
- ACL/codegen contracts become registrable per-frame policy lenses.
- Rift binds to selected contracts, not one universal frame ACL.

## Risks / Mitigations
- Risk: the story drifts into runtime edits before the contract is stable.
  Mitigation: keep the child tasks discovery/proposal-only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should contract registries be owned directly by `FrameDescriptor` or by a
  sibling Nexus manager keyed by frame?

## Decision Log
- Created after the user explicitly redirected the policy model away from
  one-universal-ACL-per-frame.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: The story is intentionally a discovery/proposal story. The user wants
    the lane staged and the plan brought back before implementation starts.
  EVIDENCE:
  - user_instruction: "lay out an epic, to run discovery on how to implement this"
  - user_instruction: "then propose your plan to me before you begin"
  IMPACT: Runtime edits are out of bounds until the proposal task is done and
    reviewed.
  NEXT: start by auditing the current single-current-ACL seams in Nexus and Rift.
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
This story stages the discovery and proposal lane for the new multi-contract
frame policy model before any runtime implementation starts.
