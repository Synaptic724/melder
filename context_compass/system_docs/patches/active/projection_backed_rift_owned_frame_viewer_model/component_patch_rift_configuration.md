# Component Patch: RiftConfiguration Viewer Profile Selection

## Before
- `RiftConfiguration` has no viewer-profile concept.
- `Rift.refresh_runtime_projections(...)` defaults the viewer profile to the
  hard-coded string `"general"`.

## After
- `RiftConfiguration` owns one `viewer_profile_name` property with the default
  `general`.
- The fluent API exposes one setter for that property.
- The live `Rift` sync path reads that property as the default viewer-profile
  choice.

## Validation Expectation
- Focused Rift configuration tests prove default loading, mutation, freeze, and
  clone behavior for `viewer_profile_name`.
