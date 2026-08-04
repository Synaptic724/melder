# Task: Propose Multi-Contract Frame Policy Implementation Plan

## Metadata
- Task ID: TASK-2026-04-11-propose-multi-contract-frame-policy-implementation-plan
- Story: STORY-2026-04-11-investigate-multi-contract-frame-policy-model
- Status: draft
- Owner: codex
- Priority: p0
- Created: 2026-04-11T00:12:09Z
- Updated: 2026-04-11T00:12:09Z

## Objective
Turn the current-model audit and the target-model definition into one concrete
implementation proposal for user review before runtime work starts.

## Ticket Contract
- ENTRY_GATE: the current-model audit and target-model definition are both in place.
- EXECUTION_BOUNDARY: proposal only; no runtime edits.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md
  - tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md
- EXIT_GATE: one evidence-backed implementation proposal exists for user review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the audit and target-model task
  still leave incompatible migration strategies unresolved.

## Scope Boundaries
- In scope:
  - implementation sequencing
  - migration order
  - validation strategy
  - risks/tradeoffs
- Out of scope:
  - runtime implementation
  - board activation of implementation work

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as the proposal lane the user explicitly requested
  before implementation starts.

## Steps / Checklist
- [ ] Read the audit and target-model tasks.
- [ ] Write one concrete implementation proposal.
- [ ] Record tradeoffs, risks, and recommended first cut.

## Deliverables
- one implementation proposal for user review

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-11_propose_multi_contract_frame_policy_implementation_plan.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: this task starts implementing by stealth instead of proposing.
  Rollback: keep it design/proposal-only.

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
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: This task is the explicit pause point before implementation. The user
    asked for the plan to come back after discovery and before code changes.
  EVIDENCE:
  - user_instruction: "then propose your plan to me before you begin"
  IMPACT: The lane now has a formal review gate before any runtime edits can start.
  NEXT: wait for the first two discovery tasks, then synthesize one implementation proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: The first implementation proposal should stay narrower than a full ACL
    rewrite. Based on the current-model audit and the target-model decision, the
    most reasonable sequence is:
    1) add a per-frame named `FrameACLConfiguration` dictionary to `FrameACLContainer`
       and seed `"default"` from the existing current configuration
    2) add manager/Nexus facade methods for register/get/list by frame + name
    3) add selected contract name state to `FrameLinkContract`
    4) extend `Rift.target_frame(...)` to accept a contract name (default `"default"`)
    5) switch viewer projection to resolve the selected named config instead of
       always pulling the frame's current selected configuration
    6) keep the existing configuration chain in place during the first cut to
       avoid coupling the registry change to a larger ACL-history rewrite
  EVIDENCE:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md:1-170
  - tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md:1-122
  IMPACT: We can implement the new frame-scoped contract selection model as one
    incremental seam over the existing typed ACL system instead of replacing the
    whole ACL subsystem at once.
  NEXT: present this implementation plan to the user for review before code work starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the explicit proposal gate before runtime implementation begins.
