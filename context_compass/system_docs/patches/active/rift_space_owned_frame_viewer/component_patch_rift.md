# Component Patch: Rift Viewer Refresh Orchestration

## Before
- `Rift` delegates viewer creation to `Nexus` through `create_frame_viewer*`
  helpers and `attach_frame_viewer(...)`.
- `refresh_runtime_projections(...)` installs projection sets and then asks
  Nexus to rebuild a viewer from scratch.

## After
- `Rift` keeps contract/refresh orchestration only.
- `refresh_runtime_projections(...)` replaces projection sets on the room and
  tells the room to rebuild its viewer directly.
- Old Rift viewer-builder delegation helpers are removed.

## Validation Expectation
- Focused Rift runtime-contract tests pass through the room-owned viewer path.
