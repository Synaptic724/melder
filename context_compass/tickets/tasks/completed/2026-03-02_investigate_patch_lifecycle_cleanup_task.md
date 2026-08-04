# Task: Investigate Patch Lifecycle and Cleanup Contract

Completed: 2026-03-05T00:20:03Z
Summary: Lifecycle and cleanup rules were integrated into patch-framework policies and active-lane template guidance.

## Metadata
- Task ID: TASK-2026-03-02-investigate-patch-lifecycle-cleanup
- Story: STORY-2026-03-02-patch-framework-skill-investigation
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-03-03T01:03:46Z
- Updated: 2026-03-05T00:20:03Z

## Objective
Define lifecycle rules for temporary patch artifacts, including merge-to-canonical
transition and deletion policy after closure.

## Ticket Contract
- ENTRY_GATE: patch artifact taxonomy is defined in prior investigation tasks.
- EXECUTION_BOUNDARY: lifecycle and cleanup policy only.
- DEPENDENCIES: framework artifact and ticket closure policies.
- EXIT_GATE: lifecycle stages and closure checks are explicit and enforceable.
- FAILURE_ESCALATION: raise DECISION_REQUEST if lifecycle conflicts with audit traceability expectations.

## Scope Boundaries
- In scope:
  - active patch folder structure;
  - closure transition to canonical docs;
  - deletion and retention policy by artifact type.
- Out of scope:
  - scripting implementation for automation.
  - runtime feature implementation.

## State Transition Event
- from_state: ready
- to_state: done
- transition_reason: investigation lane is closed after patch-framework implementation and user-accepted closure routing.

## Steps / Checklist
- [x] Define active patch path convention and naming.
- [x] Define closure gate requiring canonical architecture and component updates before deletion.
- [x] Define exceptions where retention is needed instead of deletion.
- [x] Define board and artifact-board synchronization checkpoints on closure.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Lifecycle state model for patch docs.
- Deletion and retention decision policy.

## Files / Paths Impacted
- artifacts/2026-03-02_patch_framework_skill_system.md (reference)
- context_compass/agent_onboarding/default/general/skills/ticket_closure_attention_sync.md (reference)
- context_compass/agent_onboarding/default/general/skills/ticketing.md (reference)

## Validation
- Not run.
- Recommended commands:
  - `rg -n "Lifecycle Model|closure" context_compass/artifacts/2026-03-02_patch_framework_skill_system.md`
  - `rg -n "closure|sync" context_compass/agent_onboarding/default/general/skills/ticketing.md context_compass/agent_onboarding/default/general/skills/ticket_closure_attention_sync.md`

## Risks / Rollback Notes
- Risk: deleting patch docs too early loses design rationale.
  Rollback: require ticket and ADR evidence pointers before deletion.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-03-02_patch_framework_skill_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: when framework investigation story closes.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-03T01:03:46Z
  TYPE: PLAN
  CLAIM: Patch docs must be temporary and deleted after canonical architecture and component docs are updated, with closure checkpoints to preserve auditability.
  EVIDENCE:
  - artifacts/2026-03-02_patch_framework_skill_system.md:74-80
  - context_compass/agent_onboarding/default/general/skills/ticket_closure_attention_sync.md:1-44
  IMPACT: This keeps temporary amendment artifacts from becoming stale parallel documentation.
  NEXT: finalize lifecycle states and closure gates for the framework.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-03-05T00:20:03Z
  TYPE: DECISION
  CLAIM: Task is closed as completed/superseded by delivered patch-framework skill implementation, with findings retained for traceability.
  EVIDENCE:
  - context_compass/tickets/stories/2026-03-02_patch_framework_skill_investigation_story.md:60-90
  - context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:1-75
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:1-70
  IMPACT: Investigation outputs remain captured while active lane tracking can close cleanly.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task defines when patch documents are active, when they are merged into
canonical docs, and when they are deleted or retained by exception.


