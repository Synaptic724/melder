# Component Patch: StaticFrameViewer Durable Asset Behavior

## Before
- Static rooms build a new generic viewer and then clone it into
  `StaticFrameViewer`.
- Static viewer lifecycle therefore still depends on rebuild/replacement.

## After
- Static rooms own one durable static viewer asset.
- Static viewer participates in the same in-place sync lifecycle while
  preserving live-only spell filtering.

## Validation Expectation
- Focused static viewer/room tests prove filtered behavior survives sync
  without rebuilding a new viewer object.
