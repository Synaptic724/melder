# Task: Profiles, Policy Middleware, and AI Exposure

## Metadata
- Task ID: TASK-2026-02-25-profiles-and-policy
- Story: STORY-2026-02-25-aethericrift-implementation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-25T10:57:22Z
- Updated: 2026-03-15T22:05:00Z
- Created By: e3098096-e1f8-4279-b98f-082737b2cca9

## Objective
Implement FrameProfile, ConduitProfile, AI Profile schema
(ObjectProfile/MethodProfile/AttrProfile), Configuration-driven AI
exposure, and the live Policy Middleware that gates workspace access.

## Ticket Contract
- ENTRY_GATE: TASK-2026-02-25-facade-and-riftcontext complete
- EXECUTION_BOUNDARY: profile models, policy middleware, and
  Configuration extension only
- DEPENDENCIES: facade/riftcontext task, profile architecture artifact
  (Sections 4-5), AI profile/policy artifact (Sections 2-5)
- EXIT_GATE: profiles enforce thread limits and policy middleware
  correctly filters manifest views and gates operations
- FAILURE_ESCALATION: raise DECISION_REQUEST if profile inheritance
  or policy override resolution rules are ambiguous

## Scope Boundaries
- In scope:
  - FrameProfile model (thread limits, embargo timeout, auth policy, mutation toggle)
  - ConduitProfile model (per-conduit thread cap, allow_mutations, allow_transfers)
  - AI Profile schema (ObjectProfile, MethodProfile, AttrProfile)
  - AIExposureConfig on Configuration with per-spell overrides at bind time
  - Profile compilation chain (Configuration → Conduit → Frame → Middleware)
  - Policy Middleware (describe, validate, classify, execute, return filtering)
  - Live policy fetch (per-execution, not cached snapshot)
- Out of scope:
  - Workspace execution loop (Workspace task)
  - Embargo mechanism implementation (uses existing MeldGate)
  - Iris logging tier (deferred)

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: design artifacts approved and dependency tasks identified.

## Steps / Checklist
- [ ] Create `FrameProfile` and `ConduitProfile` models.
- [ ] Create AI Profile models (ObjectProfile, MethodProfile, AttrProfile).
- [ ] Extend Configuration with `AIExposureConfig` and per-spell `ai_override`.
- [ ] Implement profile compilation chain.
- [ ] Implement Policy Middleware with describe/validate/classify/execute/return phases.
- [ ] Wire live policy fetch into RiftContext.
- [ ] Ensure conduit profiles cannot exceed frame profile limits.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `FrameProfile` and `ConduitProfile` models.
- AI Profile models.
- `AIExposureConfig` Configuration extension.
- Policy Middleware class.

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/profiles.py (new)
- src/melder/aether/aetheric_rift/ai_profile.py (new)
- src/melder/aether/aetheric_rift/policy.py (new)
- src/melder/spellbook/configuration/configuration.py (AIExposureConfig extension)
- src/melder/spellbook/spellbook.py (ai_override on bind)

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/aetheric_rift/test_profiles.py -v`
  - `pytest tests/aetheric_rift/test_policy_middleware.py -v`

## Risks / Rollback Notes
- Risk: policy middleware per-execution fetch adds latency.
  Rollback: add optional caching with invalidation hook.
- Risk: profile override resolution ambiguity (local vs conduit vs frame).
  Rollback: document explicit merge rules with test coverage.

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
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-25T10:57:22Z
  TYPE: PLAN
  CLAIM: This task implements the governance layer from two design artifacts: FrameProfile/ConduitProfile from the facade architecture artifact and AI Profile/Policy Middleware from the AI profile artifact. The key design decision is that AI exposure is Configuration-driven and policy is live (not cached).
  EVIDENCE:
  - tickets/artifacts/aethericrift_facade_and_profile_architecture.md:115-175
  - tickets/artifacts/ai_profile_and_policy_middleware_design.md:50-151
  - tickets/artifacts/ai_profile_and_policy_middleware_design.md:176-186
  IMPACT: Completing this task provides the governance layer that workspaces depend on for access control and lane routing.
  NEXT: begin after facade/riftcontext task completes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Third implementation task. Depends on facade/riftcontext task. Creates the governance and access control layer (profiles, AI exposure, policy middleware) that workspaces consume at execution time.


## Completion Summary
- Completed: 2026-03-15T22:05:00Z
- Summary: Superseded or completed during AR packaging cleanup; retained for historical reference.

