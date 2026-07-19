# Patch Architecture: FrameView Collapse To Descriptor-Driven FrameViewer

## Metadata
- Patch ID: `frame_view_collapse_to_descriptor_viewer`
- Status: active
- Updated: 2026-04-06T17:24:39Z

## Objective
Remove the `FrameView` runtime layer and make `FrameViewer` execute directly
against descriptor-organized frame/conduit/spell data after ACL filtering.

## Non-Goals
- codegen execution
- mutation work
- workspace redesign beyond the viewer path

## Boundary Change
Before:
- `Nexus` compiled ACL output -> `FrameView.from_compiled_access_surface(...)`
- `FrameViewer` hosted `FrameView` objects and delegated target/profile work
  into them

After:
- `Nexus` compiled ACL output + descriptor truth -> descriptor-driven
  `FrameViewer`
- `FrameViewer` owns the target-description, profile-ordering, and lookup logic
  directly
- `FrameView`, `FrameViewProfile`, and `FrameViewProfileBuilder` are removed
  from the runtime path

## Invariants
- Descriptor truth remains canonical.
- ACLs still define the visibility/filter layer.
- `FrameViewerProfile` continues to own exposed tool composition.
- `FrameLinkContract` remains the Rift frame-availability object only.
- Viewer methods must not bypass ACL-filtered visibility.

## Changed Components
- `FrameViewer`
- `Nexus`
- `FrameView` removal
- focused viewer/projection tests

## Migration Order
1. Route active work to the runtime-collapse task.
2. Move frame-local target/description logic onto `FrameViewer`.
3. Rewire `Nexus.create_frame_viewer(...)` and cache paths to stop building
   `FrameView`.
4. Delete `FrameView`, `FrameViewProfile`, and `FrameViewProfileBuilder`.
5. Realign focused tests.

## Rollback
- Restore the removed `FrameView` files and the old `Nexus.create_frame_view`
  path.
- Reattach viewer delegation to `FrameView` methods.

## Validation Expectations
- Focused viewer/projection unit tests must pass.
- Nexus frame-surface projection tests must pass.
- No remaining runtime imports of `FrameView` or its profile/builder layer.
