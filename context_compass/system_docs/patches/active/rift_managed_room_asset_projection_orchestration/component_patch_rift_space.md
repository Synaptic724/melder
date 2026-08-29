# Component Patch: RiftSpace Projection-Blind Asset Host

## Before
- RiftSpace stores `_projection_sets_by_frame_name`.
- RiftSpace exposes projection-management and projection-access methods.

## After
- RiftSpace no longer stores projection sets.
- RiftSpace hosts assets only.
- Projection apply/sync orchestration is no longer a room responsibility.

## Validation Expectation
- Focused room tests prove the room still exposes assets but no longer manages
  projection state.
