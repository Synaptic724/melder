# Patch Architecture: Persistent RiftSpace FrameViewer Asset

## Objective
Turn `FrameViewer` from a rebuilt room-owned snapshot into a durable room-owned
asset that exists from room init onward and syncs in place to current
projection targets.

## Non-Goals
- Moving viewer ownership back into `Nexus`.
- Redesigning command or workstation assets.
- Redesigning viewer helper APIs.

## Boundary
- In scope:
  - `RiftSpace` durable viewer lifecycle
  - `FrameViewer` in-place sync/update
  - `StaticFrameViewer` durable sync behavior
  - `Rift` refresh orchestration update
  - focused tests/docs
- Out of scope:
  - ACL model changes
  - explicit `frame_name` enforcement
  - command/codegen redesign

## Invariants
- The room always owns a viewer asset when active.
- Empty rooms can host an empty viewer.
- Projection updates sync the existing viewer instead of rebuilding a new one.
- Cleanup is ordinary owned-asset cleanup, not detach/replace choreography.
- Static rooms keep filtered viewer semantics.

## Required Deltas
- Create the viewer asset during room init.
- Add one in-place sync contract from projections to viewer state.
- Remove room viewer replace/clear/rebuild seams.
- Update Rift refresh to call sync instead of rebuild.
