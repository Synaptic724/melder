# Component Patch: Nexus Atomic ACL Projection Refresh Barrier

## Before
- `Nexus` only owns `_refresh_rift_projection_sets_for_frame(frame_name)`.
- The single-frame helper freezes impacted Rifts, drains, refreshes one frame,
  and reopens.
- `create_frame_projection_sets_for_rift(...)` only supports one optional
  `frame_name`.

## After
- `Nexus` owns one batch helper for changed frame-name sequences.
- The batch helper dedupes changed frame names, computes the union of impacted
  Rifts, disables/drains each impacted Rift once, dispatches one refresh call
  per impacted Rift, and then reopens once.
- The single-frame helper and `_on_frame_acl_changed(frame_name)` become thin
  delegates to the batch helper.
- `create_frame_projection_sets_for_rift(...)` supports a multi-frame scope for
  one Rift.

## Validation Expectation
- Focused Nexus tests prove:
  - overlapping frame batches disable/drain/refresh/open once per impacted Rift
  - the single-frame helper delegates to the batch path
  - ungated config still refreshes directly
