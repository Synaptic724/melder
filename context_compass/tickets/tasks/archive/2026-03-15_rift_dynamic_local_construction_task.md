# Task: Rift Dynamic Local Construction

## Metadata
- Task ID: TASK-2026-03-15-rift-dynamic-local-construction
- Story: STORY-2026-03-15-aethericrift-v1-workspace-runtime
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-03-15T11:59:14Z
- Updated: 2026-03-15T11:59:14Z

## Objective
Implement `DynamicRiftSpace`, where the room can surface the backing
conduit as `RiftConduit` and use it to materialize local helpers, objects, and
methods without silently crossing into canonical MutationResearch behavior.

## Ticket Contract
- ENTRY_GATE: core runtime, room/target model, validation system, and profile
  stack are in place.
- EXECUTION_BOUNDARY: `DynamicRiftSpace` conduit exposure, local room construction,
  local binding/cleanup, and local-vs-canonical boundary enforcement.
- DEPENDENCIES:
  - TASK-2026-03-15-aethericrift-runtime-core
  - TASK-2026-03-15-rift-space-and-target-model
  - TASK-2026-03-15-rift-validation-system
  - TASK-2026-03-15-rift-profile-stack
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md
- EXIT_GATE: `DynamicRiftSpace` can surface the backing conduit for local room
  construction, bind resulting local helpers back into the room when allowed,
  and preserve the explicit boundary between local construction and canonical
  mutation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if `DynamicRiftSpace` forces
  MutationResearch semantics or breaks the `StaticRiftSpace` versus
  `DynamicRiftSpace` split.

## Scope Boundaries
- In scope:
  - `DynamicRiftSpace` conduit exposure through `RiftConduit`
  - local helper/object materialization in the room
  - local binding back into room targets when allowed
  - cleanup/discard semantics for local room construction
  - explicit local-vs-canonical mutation boundary enforcement
- Out of scope:
  - MutationResearch implementation
  - transport/server behavior

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the current AR v1 patch set leaves `DynamicRiftSpace`
  local construction as the final AR slice before MR integration, so it can now be
  isolated as its own engineer task.

## Steps / Checklist
- [ ] Implement `DynamicRiftSpace` as the dynamic room surface.
- [ ] Surface `RiftConduit` only in `DynamicRiftSpace`.
- [ ] Prefer `Aether._get_conduit_cloud(...)`, `_get_conduit_by_name(...)`, and
      `_get_conduit_by_id(...)` when exposing conduits from the configured frame.
- [ ] Implement local helper/object materialization against the backing conduit.
- [ ] Implement binding of allowed local outputs back into room targets.
- [ ] Implement cleanup/discard behavior for local room construction.
- [ ] Enforce the boundary between local room work and canonical mutation.
- [ ] Add tests proving the `StaticRiftSpace` versus `DynamicRiftSpace` split stays explicit.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `DynamicRiftSpace` room behavior
- `RiftConduit` exposure behavior
- local room-construction tests

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/
- tests/

## Validation
- Not run.
- Recommended commands:
  - `pytest tests -k rift_dynamic -v`
  - `pytest tests -k rift_conduit -v`

## Risks / Rollback Notes
- Risk: `DynamicRiftSpace` becomes indistinguishable from canonical mutation or
  from `StaticRiftSpace`.
  Rollback: tighten the mode boundary before widening local-construction
  behavior.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-15T11:59:14Z
  TYPE: PLAN
  CLAIM: This task implements the last AR-only slice before MR integration:
    implement `DynamicRiftSpace`, expose the backing conduit there, allow local
    room construction, and
    keep that local work distinct from canonical mutation.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md:42-47
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md:1-34
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:29-44
  IMPACT: Completing this task gives AR its full local room-construction path
    without dragging MR implementation into the base workspace runtime.
  NEXT: implement after the room, validation, and profile slices are in place,
    using the existing `Aether` conduit lookup surface for configured-frame
    exposure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Final AR-only implementation task in the patch-driven stack. It brings
`DynamicRiftSpace` online while preserving the explicit boundary between local
construction and canonical mutation.
