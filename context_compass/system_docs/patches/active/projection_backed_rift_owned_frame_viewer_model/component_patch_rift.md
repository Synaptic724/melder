# Component Patch: Rift Projection-Owned Viewer Sync

## Before
- `Rift` owns the live projection registry, but the viewer profile default is
  hard-coded in `refresh_runtime_projections(...)`.
- `Rift` syncs the viewer by handing it projection sets plus metadata, while
  the viewer rebuilds a second snapshot layer from those bundles.

## After
- `Rift` still owns the live projection registry and still drives sync.
- `Rift` chooses the default viewer profile from `RiftConfiguration`.
- `Rift` continues to build viewer metadata, but the viewer consumes the live
  projection bundle directly instead of decomposing it into viewer-owned
  descriptor/config/surface maps.

## Validation Expectation
- Focused Rift runtime tests prove config-driven profile selection and
  projection-owned viewer sync behavior.
