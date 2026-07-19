# Component Patch: Rift Multi-Frame Projection Refresh

## Before
- `Rift.refresh_runtime_projections(...)` only supports one optional
  `frame_name`.
- One single-frame refresh asks Nexus for one projection subset, merges it, and
  rebuilds the viewer immediately.

## After
- `Rift.refresh_runtime_projections(...)` supports one explicit multi-frame
  scope.
- One impacted Rift asks Nexus for one multi-frame projection subset, merges
  once into the room, and rebuilds the viewer once.
- Current viewer profile-selection state is preserved across the batch rebuild.

## Validation Expectation
- Focused Rift tests prove:
  - one multi-frame projection-builder call per batch
  - one room merge per batch
  - one viewer rebuild per batch
