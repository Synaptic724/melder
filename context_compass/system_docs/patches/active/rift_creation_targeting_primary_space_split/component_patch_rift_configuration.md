# Component Patch: RiftConfiguration

## Before
- `RiftConfiguration` carries both `target_frame_name` and `space_type`.

## After
- `RiftConfiguration` carries Rift-level identity/room-mode choices only.
- `space_type` remains.
- `target_frame_name` is removed.
- Frame targeting happens later through Rift operations.
