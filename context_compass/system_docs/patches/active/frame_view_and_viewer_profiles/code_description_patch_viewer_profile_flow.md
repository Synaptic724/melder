# Viewer Profile Flow Code Description Patch

## Control Flow
1. resolve the selected `FrameViewProfile` / `FrameViewerProfile`
2. attach the selected profile identity to the projected view/viewer
3. keep runtime behavior on the shared methods already implemented

## Error Semantics
- unknown profile names should fail fast
- invalid profile objects should fail fast
