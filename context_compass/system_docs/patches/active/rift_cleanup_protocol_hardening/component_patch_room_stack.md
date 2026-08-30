# Component Patch: Room Stack Cleanup

## Components
- `RiftSpace`
- `Workstation`
- `CommandSystem`
- `FrameViewer`
- `FrameLinkContract`

## Goal
Confirm the existing room-stack cleanup ordering is coherent and only patch it
if the source proves a real ownership gap.

## Validation Expectation
- Room-owned cleanup stays deterministic and idempotent.
- No unnecessary behavior change if the current room-stack cleanup is already valid.
