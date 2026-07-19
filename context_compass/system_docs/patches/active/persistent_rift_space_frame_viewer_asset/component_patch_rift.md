# Component Patch: Rift Durable Viewer Sync Orchestration

## Before
- `Rift.target_frame(...)` and `Rift.refresh_runtime_projections(...)` update
  projections and then rebuild the room viewer.
- `Rift.get_frame_viewer()` can fail when no viewer is attached.

## After
- `Rift` updates room projections and then syncs the existing room viewer.
- `Rift.get_frame_viewer()` is stable because the room always owns a viewer
  asset while active.

## Validation Expectation
- Focused Rift tests prove stable viewer identity across target/refresh
  operations and no-viewer failure paths are gone.
