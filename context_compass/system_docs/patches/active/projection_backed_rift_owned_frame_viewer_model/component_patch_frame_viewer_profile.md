# Component Patch: FrameViewerProfile Projection Binding

## Before
- `FrameViewerProfile.bind_to_frame(...)` binds to decomposed
  descriptor/config/surface arguments sourced from viewer-owned maps.

## After
- `FrameViewerProfile` binds from projection-owned state directly, either via
  `ViewProjection` or the same borrowed references pulled from the live
  projection bundle.
- The profile remains a borrowed-reference binder and does not become a new
  owner of projection state.

## Validation Expectation
- Focused profile/helper tests prove the bound helper surfaces still behave the
  same when fed from projection-owned state.
