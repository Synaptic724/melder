# Component Patch: Static RiftSpace Viewer Composition

## Before
- `StaticRiftSpace` wraps a generic viewer into `StaticFrameViewer` only after
  the generic viewer is already built elsewhere.

## After
- Static viewer composition stays room-local while the generic builder moves
  into `RiftSpace`.
- `StaticRiftSpace` still guarantees a `StaticFrameViewer` is what the room
  stores live.

## Validation Expectation
- Static-room viewer behavior remains intact after the ownership move.
