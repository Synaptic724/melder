# Component Patch: RiftSpace Durable Viewer Asset

## Before
- `RiftSpace` starts with no viewer.
- Viewer construction requires installed projections.
- Projection refresh rebuilds and replaces the viewer.
- Replace/clear/rebuild viewer lifecycle seams exist on the room.

## After
- `RiftSpace` creates one durable viewer asset during init.
- Empty rooms keep an empty viewer asset.
- The room syncs the existing viewer from current projections.
- Replace/clear/rebuild seams are removed from the room lifecycle.

## Validation Expectation
- Focused room tests prove:
  - viewer exists immediately after room init
  - projection sync updates the same viewer object
  - cleanup cleans the owned viewer asset normally
