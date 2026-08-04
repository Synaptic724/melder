# Story: AethericRift V1 Workspace Runtime Implementation

## Metadata
- Story ID: STORY-2026-03-15-aethericrift-v1-workspace-runtime
- Epic: EPIC-2026-02-18-aethericrift-discovery-design
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-03-15T11:59:14Z
- Updated: 2026-03-15T11:59:14Z

## User Narrative
As the project owner, I want the current AR v1 model converted into a clean
implementation story and ready tasks so engineering can build from the active
workspace-runtime design instead of the stale February decomposition.

## Value / MRP Alignment
This story makes the implementation lane match the architecture we actually
settled on:
- `AethericRiftSystem` owns canonical Rift state
- public `AethericRift` objects begin as shells and hydrate against that state
- `AethericRift` owns the AR-local substrate
- `FrameExaminer` gathers configured-frame truth for room population
- `RiftSpace` is the base room contract
- `StaticRiftSpace` and `DynamicRiftSpace` are the real room surfaces
- `RiftAttribute` / `RiftMethod` are the target model
- static and dynamic are expressed as concrete room types

That is the minimum coherent handoff needed before engineering starts writing
runtime code.

## Ticket Contract
- ENTRY_GATE: the unified AR architecture ticket and the AR v1 patch contracts
  exist and are stable enough to drive task decomposition.
- EXECUTION_BOUNDARY: implementation handoff documentation only; no runtime code
  and no MutationResearch implementation work.
- DEPENDENCIES: the unified AR architecture ticket, AR v1 object-model note,
  and active AR patch docs under
  `system_docs/patches/active/aethericrift_v1_workspace_runtime/`.
- EXIT_GATE: a patch-driven AR implementation story and ready task set exist,
  and active implementation routing no longer points at the stale February
  story.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the AR v1 object model shifts
  again before the engineer lane starts.

## Requirements (Functional)
- Replace the stale February implementation decomposition with tasks that match
  the active AR object model and patch contracts.
- Cover the current build order:
  - `AethericRiftSystem` / `AethericRiftState` / `AethericRift` core shell-to-live model
  - `FrameExaminer`
  - `RiftSpace` / `StaticRiftSpace`
  - `RiftAttribute` / `RiftMethod`
  - `RiftValidationSystem`
  - profile stack
  - `DynamicRiftSpace` local construction
- Keep `StaticRiftSpace` versus `DynamicRiftSpace` explicit in the task set.

## Requirements (Non-Functional)
- Tasks must be small enough for focused engineer execution windows.
- Task boundaries must follow the patch contracts, not the old RiftEngine
  vocabulary.
- Story language must stay aligned with the long-form unified architecture
  ticket.

## Scope Boundaries
- In scope:
  - patch-driven AR implementation story
  - ready implementation tasks for AR v1
  - implementation handoff routing update
- Out of scope:
  - runtime code edits
  - MutationResearch implementation
  - transport/server adapters

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the patch contracts now define the active AR component
  boundaries clearly enough that the stale February implementation story can be
  replaced with a patch-driven implementation stack.

## Dependencies / Related Work
- utilized_ticket_artifacts/Ticket - AethericRift and MutationResearch Unified Current Architecture.md
- codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_aetheric_rift_core.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_validation_system.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-03-15-aethericrift-runtime-core - implement
      `AethericRiftSystem`, `AethericRiftState`, and the shell-to-live Rift core
      ownership of AR-local Spellbook, root conduit, and configuration
- [ ] Task: TASK-2026-03-15-rift-space-and-target-model - implement the room,
      base room contract, target registries, cleanup model, and
      `StaticRiftSpace` declared-target surface
- [ ] Task: TASK-2026-03-15-rift-profile-stack - implement the AR profile
      layering plus `FrameExaminer`-driven exposure gathering
- [ ] Task: TASK-2026-03-15-rift-validation-system - implement AST parsing,
      target/member validation, and request classification
- [ ] Task: TASK-2026-03-15-rift-dynamic-local-construction - implement the
      `DynamicRiftSpace` conduit-backed local construction path
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A new AR implementation story exists and reflects the active AR v1 model.
- Ready tasks exist for each current AR patch component area.
- The implementation handoff route points to this story instead of the stale
  February story.
- Task language no longer centers `RiftEngine`, `ObjectRef`, `RefAttr`,
  `RefMethod`, `ConduitProfile`, or the older facade/context split.

## Validation / Test Plan
- Validate the task set against the active AR patch docs.
- Validate the new task order against the architecture patch rollout order.
- Validate that the handoff row in `attention_board.md` routes to this story.

## UX / API / Data Notes
- This story is still a design-to-engineer handoff layer.
- Runtime interface details remain governed by the patch docs and future
  implementation notes.

## Risks / Mitigations
- Risk: the AR object model shifts again before implementation starts.
  Mitigation: patch docs remain the authoritative engineer contract and can be
  revised before code begins.
- Risk: old February tickets continue to confuse later readers.
  Mitigation: active routing is moved to this story and the new tasks.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Exact merge semantics inside the profile stack may still refine during
  implementation, but the active profile-layer object set is now fixed enough
  for tasking.

## Decision Log
- 2026-03-15: The AR implementation lane is now patch-driven and no longer
  anchored to the stale February RiftEngine/facade/profile/workspace split.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-03-15T11:59:14Z
  TYPE: FACT
  CLAIM: The unified AR architecture ticket plus the AR v1 patch docs now
    define a coherent implementation model, while the old February
    implementation story/task set still routes through the earlier RiftEngine
    and workspace-object language.
  EVIDENCE:
  - utilized_ticket_artifacts/Ticket - AethericRift and MutationResearch Unified Current Architecture.md:1-1575
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md:1-58
  - codex/context_compass/tickets/stories/2026-02-25_aethericrift_implementation_story.md:1-118
  IMPACT: Engineering needs a new story/task stack that follows the current AR
    patch contracts instead of the stale February decomposition.
  NEXT: create the ready AR v1 implementation tasks from the patch set and
    reroute the active implementation handoff row to this story.
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
This story replaces the stale February AR implementation handoff with a
patch-driven task set based on the current AR v1 model. The next step is to
execute the five ready tasks in order, starting with the core `AethericRift`
runtime object and local substrate ownership.
