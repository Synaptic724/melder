# Component Patch: FrameViewer In-Place Projection Sync

## Before
- `FrameViewer` can be constructed empty, but there is no explicit sync/update
  contract.
- The room rebuilds a new viewer from projections instead of updating the
  existing one.

## After
- `FrameViewer` owns one explicit in-place sync/update path from projection
  state.
- Sync preserves prior selected-profile state where frame membership still
  exists.
- Sync recalculates default-frame state coherently as frames are added or
  removed.

## Validation Expectation
- Focused viewer tests prove empty-init plus in-place sync behavior.
