# Story: Implement RiftSpace-Owned FrameViewer Migration
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-implement-rift-space-owned-frame-viewer-migration
- Epic: EPIC-2026-04-18-rehome-frame-viewer-ownership-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T23:05:00Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want `RiftSpace` to build and own the live
`FrameViewer`, so that `Nexus` stays limited to descriptor/ACL/projection truth
and the room owns the interaction surface built from those projections.

## Value / MRP Alignment
This lands the actual ownership correction instead of leaving the plan at
design stage. It removes duplicated projection/viewer work and makes the room
responsible for the viewer it already hosts.

## Ticket Contract
- ENTRY_GATE: user approved implementation of the planned ownership move.
- EXECUTION_BOUNDARY: viewer construction/removal seams, static wrapping,
  focused tests, and docs required by the ownership change only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_implement_rift_space_owned_frame_viewer_builder_and_remove_nexus_viewer_seams_task.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/architecture_patch.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_nexus.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_rift_space.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/component_patch_static_rift_space.md
  - system_docs/patches/active/rift_space_owned_frame_viewer/code_description_patch_viewer_refresh_flow.md
- EXIT_GATE: the room owns viewer assembly, old Nexus/Rift viewer-builder seams
  are gone, focused validation is green, and docs/tests match the new model.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if explicit-frame targeting
  redesign becomes inseparable from the ownership cut.

## Requirements (Functional)
- `RiftSpace` must build the generic `FrameViewer` from installed
  `ViewProjection` objects.
- `StaticRiftSpace` must preserve static overlay composition locally.
- `Rift.refresh_runtime_projections(...)` must rebuild the room viewer through
  the room-owned path after replacing projection sets.
- `Nexus.create_frame_viewer*` and cache seams must be removed.
- `Rift` viewer-builder delegation helpers must be removed.

## Requirements (Non-Functional)
- No backward-compat compatibility layer for removed viewer-builder methods.
- Keep code/doc changes tightly scoped to viewer ownership.
- Keep docstrings deep and contract-first on touched runtime methods.

## Scope Boundaries
- In scope:
  - `Nexus`, `Rift`, `RiftSpace`, `StaticRiftSpace`, viewer classes, focused
    tests/docs
- Out of scope:
  - command/codegen redesign
  - explicit `frame_name` migration
  - broader AR room API redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the ownership slice is implemented and the focused
  validation ring is green.

## Dependencies / Related Work
- STORY-2026-04-18-plan-rift-space-owned-frame-viewer-migration
- TASK-2026-04-18-investigate-and-plan-rift-space-owned-frame-viewer-migration

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-implement-rift-space-owned-frame-viewer-builder-and-remove-nexus-viewer-seams
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `RiftSpace` builds the generic viewer from installed projections.
- `StaticRiftSpace` still yields `StaticFrameViewer` behavior.
- `Nexus` no longer constructs or caches viewers.
- `Rift` no longer exposes the removed viewer-builder delegation family.
- Focused tests and AR docs match the new ownership model.

## Validation / Test Plan
- Focused Rift/Nexus/RiftSpace/viewer unit and integration rings after the code
  migration lands.

## UX / API / Data Notes
- The removed viewer-builder methods are intentionally not preserved.
- The room-owned builder is internal and should not become a new public seam.

## Risks / Mitigations
- Risk: current tests overfit to the removed builder APIs.
  Mitigation: port tests to projection refresh plus `rift.get_frame_viewer()`
  or direct room state checks.
- Risk: cache invalidation code may still be coupled to ACL-change callbacks.
  Mitigation: collapse ACL refresh onto projection refresh only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether any focused viewer tests should move from `Nexus` to `Rift`/room
  surfaces after the seam removal.

## Decision Log
- Pending implementation and validation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-18T23:27:29Z
  TYPE: FACT
  CLAIM: The child implementation task landed the room-owned viewer builder,
    removed the old Nexus/Rift builder and cache seams, and updated the focused
    docs/tests with a green validation ring.
  EVIDENCE:
  - tickets/tasks/2026-04-18_implement_rift_space_owned_frame_viewer_builder_and_remove_nexus_viewer_seams_task.md:1-174
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: hold for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T23:05:00Z
  TYPE: PLAN
  CLAIM: The implementation slice is bounded to room-owned viewer assembly,
    static wrapping, seam removal, and focused test/doc updates.
  EVIDENCE:
  - tickets/tasks/2026-04-18_implement_rift_space_owned_frame_viewer_builder_and_remove_nexus_viewer_seams_task.md:1-200
  IMPACT: The ownership fix stays reviewable and avoids widening into unrelated
    frame-target or command/codegen work.
  NEXT: land the linked task and validate the focused runtime rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
This story tracks the actual runtime ownership move after the approved plan. It
is now implemented and waiting on review.