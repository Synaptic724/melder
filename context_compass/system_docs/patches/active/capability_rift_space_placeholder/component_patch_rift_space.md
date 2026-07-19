# Component Patch: RiftSpace

## Before
- Only `StaticRiftSpace` and `DynamicRiftSpace` exist as concrete room types.

## After
- `CapabilityRiftSpace` exists as a third concrete placeholder room type.
- It inherits the same base room behavior as the other two and fixes `space_kind`
  to `capability`.
