# Component Patch: StaticFrameViewer Projection-Owned Filtering

## Before
- `StaticFrameViewer` depends on the base viewer's copied compiled-surface maps
  and keeps its own base compiled-surface overlay on top.

## After
- `StaticFrameViewer` keeps the live-only spell filtering behavior without
  depending on the old viewer-owned second median layer.
- Any retained overlay state stays strictly about static filtering, not about
  reintroducing projection-owned descriptor/config/surface copies into the base
  viewer.

## Validation Expectation
- Focused static viewer tests prove live-only spell filtering still works after
  the ownership cut.
