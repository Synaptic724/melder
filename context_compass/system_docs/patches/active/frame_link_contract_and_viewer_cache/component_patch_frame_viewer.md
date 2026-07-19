# Frame Viewer Component Patch

## Before
- `FrameViewer` had no clone support for safe cache returns.

## After
- `FrameViewer` supports detached cloning of projected views and metadata.

## Invariants
- cloned viewers must own detached cloned views
- cleanup stays idempotent
