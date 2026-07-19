# Component Patch: RiftSpace

## Before
- RiftSpace already owns the attached viewer and selected-target state, but is not created as part of a primary-space lifecycle.

## After
- RiftSpace is created as the primary room/workspace from the chosen Rift `space_type`.
- The primary space exists before frame targeting and may initially have no attached viewer.
- Viewer attachment becomes a consequence of successful frame targeting.
