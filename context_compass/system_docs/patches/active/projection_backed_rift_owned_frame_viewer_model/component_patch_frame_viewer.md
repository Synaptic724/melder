# Component Patch: FrameViewer Ownership Cut

## Before
- `FrameViewer` owns local descriptor/config/surface maps.
- `FrameViewer` owns an active-profile registry plus per-frame selected bound
  profiles.
- `sync_from_projection_sets(...)` clones ACL configs and compiled surfaces
  out of `ViewProjection` into viewer-owned state.

## After
- `FrameViewer` stays durable but no longer owns duplicate descriptor/config/
  surface maps.
- `FrameViewer` keeps only viewer-local state plus the selected viewer-profile
  choice and current frame/default metadata.
- Host methods resolve through projection-owned state.
- Selected profile behavior binds from projection-owned state rather than from
  viewer-owned copies.

## Validation Expectation
- Focused viewer tests prove host methods, selected profile behavior, and clone
  semantics under the new ownership model.
