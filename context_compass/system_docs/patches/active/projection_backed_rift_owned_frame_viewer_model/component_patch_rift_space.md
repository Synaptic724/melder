# Component Patch: RiftSpace Viewer Construction Seam

## Before
- `RiftSpace` owns the durable viewer asset, but the viewer constructor still
  follows the older snapshot-host contract.

## After
- `RiftSpace` still owns the durable viewer asset.
- Viewer construction is adjusted only as needed for the new projection-owner
  seam and no longer assumes the viewer will own copied descriptor/config/surface
  maps.

## Validation Expectation
- Focused RiftSpace/static-room tests prove viewer construction still works
  with the new ownership model.
