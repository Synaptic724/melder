# Patch Architecture: Projection-Backed Rift-Owned FrameViewer Model

## Objective
Implement the settled ownership cut so `FrameViewer` stops rehosting
descriptor/ACL/surface copies and instead consumes projection-owned state from
the live `Rift` projection registry.

## Non-Goals
- Redesigning `Nexus` ACL compilation or projection generation.
- Normalizing the duplication between view/command/codegen projection families.
- Redesigning `CommandSystem` or codegen systems.

## Boundary
- In scope:
  - Rift-level viewer-profile configuration
  - Rift sync ownership and metadata update
  - FrameViewer ownership/state cut
  - StaticFrameViewer adaptation
  - FrameViewerProfile binding update
  - focused tests/docs
- Out of scope:
  - projection-family redesign
  - unrelated room/workstation changes
  - broader AR architecture work

## Invariants
- `Nexus` remains the compiler/assembler of `FrameProjectionSet`.
- `Rift` remains the owner of the live projection registry.
- `RiftSpace` remains the durable asset host.
- `CompiledFrameACLAccessSurface` remains projection-owned.
- `FrameViewer` remains a durable asset, but not a second snapshot host.

## Required Deltas
- Add `viewer_profile_name` to `RiftConfiguration`.
- Make `Rift.refresh_runtime_projections(...)` default to the configured
  viewer profile instead of hard-coded `"general"`.
- Remove viewer-owned duplicate descriptor/config/surface maps.
- Rebind selected profile behavior from projection-owned state.
- Preserve static live-only filtering under the new ownership model.
