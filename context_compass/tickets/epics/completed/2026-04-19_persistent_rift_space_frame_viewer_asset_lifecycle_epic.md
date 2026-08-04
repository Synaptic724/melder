# Epic: Persistent RiftSpace FrameViewer Asset Lifecycle
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-19-persistent-rift-space-frame-viewer-asset-lifecycle
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-19T11:25:38Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-04-19
- Related Program/Initiative: AetherRift room asset lifecycle cleanup

## Problem / Opportunity
The runtime already moved viewer construction into `RiftSpace`, but it still
treated the viewer as a rebuilt snapshot instead of a durable room asset.

Before this slice:
- rooms started with no viewer
- viewer construction required installed projections
- target-frame and projection refresh rebuilt/replaced the viewer
- static rooms rebuilt a generic viewer and then cloned it into a static
  wrapper

That conflicted with the intended room asset model where:
- `command_system` exists as a durable room asset
- `workstation` exists as a durable room asset
- `frame_viewer` should also exist as a durable room asset

## MRP Alignment (Most Reasonable Product)
The most reasonable product was:
- create the viewer asset during room init
- allow it to exist empty before any projection exists
- add one in-place sync/update path from projections into the existing viewer
- remove replace/detach/rebuild lifecycle seams
- keep static viewer semantics under the same durable-asset model

## Ticket Contract
- ENTRY_GATE: source-backed discovery proved the current limitation was a room
  lifecycle choice, not a viewer constructor requirement, and the user
  explicitly approved implementation.
- EXECUTION_BOUNDARY: `RiftSpace`, `Rift`, `FrameViewer`,
  `StaticFrameViewer`, focused tests, matching AR docs, and directly related
  interfaces only.
- DEPENDENCIES:
  - tickets/stories/2026-04-19_implement_persistent_rift_space_frame_viewer_asset_story.md
  - tickets/tasks/2026-04-19_implement_persistent_rift_space_frame_viewer_asset_task.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- EXIT_GATE: the room owns a durable viewer asset from init onward, syncs it
  in place from projections, focused tests/docs are updated, and no
  replace/detach/rebuild lifecycle seams remain.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the sync model forces a
  broader viewer API or explicit-frame redesign.

## Goals (Outcomes)
- Make `FrameViewer` a durable room-owned asset from room construction onward.
- Allow empty rooms to host an empty viewer.
- Sync projection changes into the existing viewer in place.
- Remove room-level replace/clear/rebuild viewer lifecycle seams.
- Keep static viewer behavior under the durable-asset model.
- Make `Rift.get_frame_viewer()` stable while the room is active.

## Non-Goals (Explicit Exclusions)
- Do not move viewer ownership back into `Nexus`.
- Do not redesign `CommandSystem` or `Workstation`.
- Do not reopen full explicit `frame_name` enforcement in this epic.
- Do not widen into unrelated viewer helper redesign.

## Scope Boundaries
- In scope:
  - durable viewer init
  - in-place viewer sync
  - static viewer durable behavior
  - Rift refresh orchestration update
  - focused tests/docs
- Out of scope:
  - command/codegen redesign
  - ACL model changes
  - broad viewer API redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the durable-viewer lifecycle implementation is landed and
  the broader viewer/rift validation ring is green.

## Success Metrics
- Rooms always own a viewer asset while active.
- Empty rooms can hold a viewer before any projection exists.
- Projection updates keep viewer identity stable.
- Replace/clear/rebuild lifecycle seams are removed.
- Static rooms keep filtered viewer behavior without rebuilding wrapper
  objects.

## Requirements (Functional + Non-Functional)
- `RiftSpace` creates a viewer during init.
- `FrameViewer` supports one in-place sync/update contract from projections.
- Static viewers preserve live-only filtering under sync.
- `Rift` updates projections and syncs the existing viewer instead of
  rebuilding it.
- Public/runtime contracts no longer rely on â€œno attached viewerâ€ state for
  active rooms.

## Constraints / Assumptions
- `FrameViewer.__init__(...)` already supports empty descriptor/ACL/compiled
  maps.
- The viewer data model is snapshot-oriented, so the durable model required an
  explicit sync contract rather than just earlier construction.
- Static viewer behavior depends on a filtered overlay over compiled access
  surfaces, so static needed a distinct sync path.

## Dependencies / External References
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- the earlier viewer-ownership epic from 2026-04-18

## Milestones (Track Progress)
- [x] Milestone 1: Discovery and plan complete
      Durable viewer-asset implications, risks, and implementation order are
      explicit.
- [x] Milestone 2: Base room creates a durable empty viewer
      `RiftSpace` starts with a live viewer asset instead of `None`.
- [x] Milestone 3: In-place viewer sync lands
      Projection refresh updates the existing viewer instead of rebuilding.
- [x] Milestone 4: Replace/clear/rebuild seams removed
      The room cleanup path uses only normal owned-asset cleanup.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-19-implement-persistent-rift-space-frame-viewer-asset -
      implement durable empty viewer asset and in-place sync

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-04-19-implement-persistent-rift-space-frame-viewer-asset
- [ ] Task: Verify Ticket Microcycle enforcement across staged tickets.

## Acceptance Criteria (Epic Done)
- The room always owns a viewer asset from init onward.
- Empty rooms can host a viewer before any projection exists.
- Projection refresh updates one existing viewer object in place.
- The replace/clear/rebuild room-viewer lifecycle seams are gone.
- Static rooms keep their filtered viewer semantics under the durable-asset
  model.
- Focused tests and AR docs match the landed lifecycle model.

## Risks / Mitigations
- Risk: selected-profile/default-frame state could be lost during sync.
  Mitigation: preserve prior state by default and cover it with focused tests.
- Risk: static filtering could regress under sync.
  Mitigation: give `StaticFrameViewer` its own durable sync behavior and test
  it directly.

## Applicable Anti-Patterns
- [ ] No claim that the viewer must have projections when the constructor
      already supports empty state.
- [ ] No new lifecycle seam that just renames replace/detach behavior instead
      of removing it.
- [ ] No widening into unrelated command/codegen or explicit-frame work without
      a documented decision.

## Validation / Test Approach
- Focused room/viewer unit tests for empty-init behavior.
- Focused Rift tests for stable viewer identity.
- Focused refresh tests for in-place sync behavior.
- Broader viewer/rift ring for profile and integration surfaces.

## Rollout / Adoption Plan
1. Land durable empty viewer init on the room.
2. Land in-place sync on base viewer and static viewer.
3. Switch Rift refresh from rebuild to sync.
4. Rewrite focused tests/docs to the stable-viewer model.

## Open Questions
- Whether the in-place sync contract should remain internal forever or later be
  promoted to a formal public asset lifecycle API.

## Decision Log
- Pending user review of the landed lifecycle slice.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-19T11:25:38Z
  TYPE: FACT
  CLAIM: The current runtime already moved viewer construction into
    `RiftSpace`, but the room still started with no viewer, required installed
    projection sets to build one, and rebuilt/replaced it after target-frame
    and refresh operations.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:152-177
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:373-582
  - src/melder/aether/nexus/rift/rift.py:361-542
  IMPACT: The viewer was room-built, but not yet a durable room asset.
  NEXT: prove why the constructor could already support empty state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-19T11:25:38Z
  TYPE: FACT
  CLAIM: `FrameViewer.__init__(...)` already supports empty descriptor, ACL,
    and compiled-surface maps. The â€œviewer requires projectionsâ€ rule was a
    room lifecycle choice, not a viewer constructor requirement.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:83-212
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:414-415
  IMPACT: A durable empty viewer asset was architecturally valid.
  NEXT: land the sync-based lifecycle instead of the rebuild-based lifecycle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T11:50:05Z
  TYPE: FACT
  CLAIM: The durable-viewer lifecycle slice is landed. `RiftSpace` now owns
    one viewer asset from init onward, `FrameViewer` and `StaticFrameViewer`
    sync in place from current projection targets, and the old
    replace/clear/rebuild room seams are gone.
  EVIDENCE:
  - tickets/tasks/2026-04-19_implement_persistent_rift_space_frame_viewer_asset_task.md:1-186
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:152-491
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:83-585
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:15-335
  IMPACT: The viewer now behaves like the other long-lived room assets.
  NEXT: hold for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level lifecycle direction, cross-story sequencing, and
  cleanup/ownership boundaries.
- Add notes when the sync model, static strategy, or follow-on scope changes.
- Reference child story/task evidence instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic tracks the follow-on cleanup that turned `FrameViewer` from a rebuilt
room-owned snapshot into a durable room-owned asset that can exist empty and
sync to current projection targets.