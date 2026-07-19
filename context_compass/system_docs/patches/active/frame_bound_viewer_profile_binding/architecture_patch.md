# Patch Architecture: Frame-Bound Viewer Profile Binding

## Metadata
- Patch ID: `frame_bound_viewer_profile_binding`
- Status: active
- Updated: 2026-04-06T18:41:02Z

## Objective
Bind selected `FrameViewerProfile` instances to single-frame descriptor + ACL
state and make the frame-specific viewer creation transaction start from
`Rift`.

## Core Decision
- Reusable `FrameViewerProfile` templates stay builder-owned.
- `FrameViewer` holds selected profile instances per frame.
- Each selected instance is bound by reference to:
  - one `FrameDescriptor`
  - one `FrameACLConfiguration`
  - one `CompiledFrameACLAccessSurface`
- `Rift` checks `FrameLinkContract` and then creates the frame-specific viewer
  transaction.

## Non-Goals
- new snapshot/view layer
- codegen execution
- mutation work
