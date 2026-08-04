# Story: Implement Persistent RiftSpace FrameViewer Asset
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-19-implement-persistent-rift-space-frame-viewer-asset
- Epic: EPIC-2026-04-19-persistent-rift-space-frame-viewer-asset-lifecycle
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T11:25:38Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a Rift runtime maintainer, I want `frame_viewer` to be a durable room-owned
asset that exists from room init onward, so projection changes update the
viewer in place instead of rebuilding and replacing it.

## Value / MRP Alignment
The room already owns durable assets like `command_system` and `workstation`.
Making `frame_viewer` durable aligns the room lifecycle with that same model
and removes the last fake detach/replace viewer choreography from the runtime.

## Ticket Contract
- ENTRY_GATE: the discovery task proved the viewer constructor already supports
  empty state and the user explicitly approved implementation.
- EXECUTION_BOUNDARY: `RiftSpace`, `Rift`, `FrameViewer`, `StaticFrameViewer`,
  focused tests, matching AR docs, and the required patch-doc set only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-19_implement_persistent_rift_space_frame_viewer_asset_task.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/architecture_patch.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_rift_space.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_frame_viewer.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_static_frame_viewer.md
  - system_docs/patches/active/persistent_rift_space_frame_viewer_asset/component_patch_rift.md
- EXIT_GATE: the room owns one durable viewer asset from init onward, refresh
  syncs it in place, focused tests are green, and docs/tickets are synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the durable-viewer model
  forces a broader viewer API or explicit-frame redesign.

## Requirements (Functional)
- `RiftSpace` creates a viewer asset during init.
- `FrameViewer` gains one in-place sync/update path from projection sets.
- Static rooms keep static overlay semantics under the durable-asset model.
- `Rift` updates projections and syncs the existing viewer instead of
  rebuilding it.
- Replace/clear/rebuild viewer lifecycle seams are removed.

## Requirements (Non-Functional)
- No return to Nexus-owned viewer lifecycle.
- No second room/viewer coordination layer.
- Keep changes bounded to viewer lifecycle and directly affected tests/docs.

## Scope Boundaries
- In scope:
  - durable viewer init
  - in-place viewer sync
  - static viewer durable-asset behavior
  - Rift refresh orchestration update
  - focused tests/docs
- Out of scope:
  - command/codegen redesign
  - broad viewer helper redesign
  - explicit frame-target enforcement lane

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the durable-viewer lifecycle implementation is landed and
  the focused validation ring is green.

## Dependencies / Related Work
- room-owned viewer ownership epic
- atomic ACL batch refresh implementation

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-19-implement-persistent-rift-space-frame-viewer-asset
- [ ] Enforce Ticket Microcycle across linked implementation work.
- [ ] Keep patch-doc consumption mapped in task notes before edits.

## Acceptance Criteria
- The room always owns a viewer asset from init onward.
- Empty rooms can host a viewer before any projection exists.
- Projection refresh updates one existing viewer object in place.
- Static rooms keep filtered viewer behavior without rebuilding a new viewer.
- Focused tests pass.

## Validation / Test Plan
- Focused room/viewer unit tests.
- Focused Rift tests for stable viewer identity.
- Focused refresh tests for in-place sync behavior.

## Risks / Mitigations
- Risk: `FrameViewer` sync could accidentally drop selected-profile state.
  Mitigation: preserve previous per-frame selection by default and test it.
- Risk: static viewer overlay may need its own sync override.
  Mitigation: treat static sync as a first-class part of the implementation
  rather than assuming base behavior is enough.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No cross-task synthesis claims without task-note evidence pointers.
- [ ] No closure while the implementation task remains active or unrouted.

## Open Questions
- Whether the in-place sync path should be public, protected, or purely
  internal to the room lifecycle.

## Decision Log
- Pending implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T11:25:38Z
  TYPE: PLAN
  CLAIM: The implementation split is:
    1. base room creates a durable empty viewer,
    2. base viewer gains an in-place sync/update path from projection sets,
    3. static viewer overrides the sync path as needed,
    4. Rift refresh switches from rebuild to sync,
    5. focused tests/doc contracts flip from replacement behavior to stable
       asset behavior.
  EVIDENCE:
  - tickets/epics/2026-04-19_persistent_rift_space_frame_viewer_asset_lifecycle_epic.md:1-152
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:152-177
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:83-212
  IMPACT: The task can stay bounded to the viewer lifecycle and does not need
    to reopen ownership or ACL batching.
  NEXT: land the linked task and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:50:05Z
  TYPE: FACT
  CLAIM: The child task landed the durable-viewer lifecycle cut. The room now
    owns a viewer asset from init onward, projection refresh syncs it in place,
    static rooms keep filtered viewer behavior on the same object, and the
    broader viewer/rift ring is green.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_persistent_rift_space_frame_viewer_asset_task.md:1-186
  - codex/context_compass/system_docs/src_architecture.md:474-538
  - codex/context_compass/system_docs/src_components.md:1920-2050
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: hold for acceptance or one more bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when sync semantics, static behavior, or lifecycle seam removal
  order changes.
- Reference child-task notes for tactical evidence instead of duplicating them.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story implements the durable viewer-asset model on top of the already
landed room-owned viewer ownership change.