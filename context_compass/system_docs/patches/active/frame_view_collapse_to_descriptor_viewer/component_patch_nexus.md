# Component Patch: Nexus

## Before
- `create_frame_view(...)` produced one `FrameView`
- `create_frame_viewer(...)` built one or more `FrameView` objects, then
  wrapped them in `FrameViewer`
- frame-view cache and viewer cache both existed

## After
- `create_frame_view(...)` is removed from the runtime path
- `create_frame_viewer(...)` projects descriptor truth plus compiled ACL output
  directly into `FrameViewer`
- cache keys remain driven by frame name, ACL configuration id, and viewer
  posture inputs, but the cached object is the viewer only

## Invariants
- Viewer creation still validates descriptor<->ACL payload compatibility first
- Cached objects returned to callers remain detached clones

## Risks
- Viewer build code may become too heavy if projection helpers are not split
  cleanly
- Old tests may still assume `FrameView` exists
