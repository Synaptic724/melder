# Component Patch: RiftSpace Generic Viewer Builder

## Before
- `RiftSpace` stores the attached viewer and post-binds the `RiftGate`.
- The room already owns installed projection sets but does not assemble the
  generic viewer from them.

## After
- `RiftSpace` builds the generic `FrameViewer` from installed `ViewProjection`
  objects.
- The room passes `rift_gate` into `FrameViewer(...)` at construction time.
- Viewer replacement remains internal room lifecycle, not a public seam.

## Validation Expectation
- Focused room/viewer tests prove the room can rebuild and replace the viewer
  from installed projections.
