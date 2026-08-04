# Task: AethericRift Facade and RiftContext

## Metadata
- Task ID: TASK-2026-02-25-facade-and-riftcontext
- Story: STORY-2026-02-25-aethericrift-implementation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-25T10:57:22Z
- Updated: 2026-03-15T22:05:00Z
- Created By: e3098096-e1f8-4279-b98f-082737b2cca9

## Objective
Implement the AethericRift facade (entry point for agents) and the
frame-bound RiftContext that manages per-frame AI Profile registries,
CapabilityManifest compilation, and ExecutionContext namespaces.

## Ticket Contract
- ENTRY_GATE: TASK-2026-02-25-riftengine-and-codegen-pipeline complete
- EXECUTION_BOUNDARY: AethericRift facade and RiftContext modules only
- DEPENDENCIES: RiftEngine task, facade/profile design artifact (Sections 2-3)
- EXIT_GATE: facade creates workspaces and RiftContext compiles manifests
- FAILURE_ESCALATION: raise DECISION_REQUEST if frame targeting or
  manifest compilation logic is ambiguous

## Scope Boundaries
- In scope:
  - AethericRift facade class (wire into Aether, target frame, create workspaces)
  - RiftContext on AethericFrame (AI Profile registry, manifest compilation)
  - ExecutionContext (controlled namespace for exec)
  - Frame targeting and discovery
  - Facade lifecycle (cleanup tears down workspaces, not frame)
- Out of scope:
  - FrameProfile/ConduitProfile governance (Profiles task)
  - Workspace execution loop (Workspace task)
  - Policy middleware (Profiles task)

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: design artifacts approved and dependency task identified.

## Steps / Checklist
- [ ] Create `AethericRift` facade class with frame targeting.
- [ ] Create `RiftContext` class on AethericFrame.
- [ ] Implement `CapabilityManifest` compilation from conduit profiles.
- [ ] Implement `ExecutionContext` controlled namespace.
- [ ] Implement workspace registry on facade.
- [ ] Wire RiftContext into AethericFrame initialization.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `AethericRift` facade class.
- `RiftContext` class.
- `CapabilityManifest` compilation logic.
- `ExecutionContext` namespace manager.

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/facade.py (new)
- src/melder/aether/aetheric_rift/rift_context.py (new)
- src/melder/aether/aetheric_rift/execution_context.py (new)
- src/melder/aether/aetheric_frame.py (RiftContext wiring)

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/aetheric_rift/test_facade.py -v`
  - `pytest tests/aetheric_rift/test_rift_context.py -v`

## Risks / Rollback Notes
- Risk: manifest compilation is slow for large frames.
  Rollback: add caching in follow-up.

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
  CLAIM: This task implements the facade and context layers from the architecture design artifact. The facade is the single entry point for agents; RiftContext is the frame-bound service that compiles manifests and manages execution namespaces.
  EVIDENCE:
  - tickets/artifacts/aethericrift_facade_and_profile_architecture.md:53-87
  - tickets/artifacts/aethericrift_facade_and_profile_architecture.md:90-113
  - tickets/artifacts/ai_profile_and_policy_middleware_design.md:30-46
  IMPACT: Completing this task provides the user-facing surface and frame-scoped context for workspace creation.
  NEXT: begin after RiftEngine task completes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Second implementation task. Depends on RiftEngine task. Creates the AethericRift facade and RiftContext that agents interact with to create workspaces and discover capabilities.


## Completion Summary
- Completed: 2026-03-15T22:05:00Z
- Summary: Superseded or completed during AR packaging cleanup; retained for historical reference.

