# Frame Viewer Multi-View Helper Architecture Patch

## Objective
Expand `FrameViewer` with richer deterministic multi-view helper methods over
attached projected views and links.

## Non-Goals
- no fuzzy search
- no subscriptions/update model
- no raw runtime-object access
- no binding or execution behavior

## Changed Components
- `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`

## Boundary Rules
- helpers must stay view-local and deterministic
- helper output must be derived entirely from attached `FrameView` / `FrameLink`
  objects
- no ACL evaluation logic
- no new manager or cache

## Migration Order
1. define grouped/count/summarizing helpers
2. implement them on the existing projected-view surface
3. add focused tests
4. validate the viewer slice
