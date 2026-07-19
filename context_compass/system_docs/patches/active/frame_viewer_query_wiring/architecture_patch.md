# Frame Viewer Query Wiring Architecture Patch

## Objective
Give `FrameViewer` its first real query/helper surface over projected
`FrameView` objects after the `FrameLink` / `FrameView` contract bridge.

## Non-Goals
- do not implement a full search DSL
- do not implement the Nexus holding zone
- do not add binding or execution behavior
- do not add event/update streaming

## Changed Components
- `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`

## Boundary Rules
- `FrameViewer` consumes projected `FrameView` objects only.
- `FrameViewer` must not evaluate ACLs or own raw runtime objects.
- Helper/query methods should stay narrow, deterministic, and view-local.

## Migration Order
1. define the smallest real read/query helper surface
2. implement the helper methods on top of existing view/link data
3. add focused tests
4. validate the viewer slice
