# Component Patch: FrameViewer

## Before
- Hosts `available_views_by_frame_name: Dict[str, FrameView]`
- Delegates:
  - target ordering
  - target descriptions
  - local view-profile selection
  to the selected `FrameView`

## After
- Hosts descriptor-driven frame surfaces directly, keyed by frame name
- Owns:
  - available target lookup
  - target grouping/filtering
  - target descriptions
  - frame summaries
- `FrameViewerProfile` continues to map tool ids to host handler names

## Interface Deltas
- Remove `available_views_by_frame_name` runtime dependence
- Remove `get_available_view(...)` / `get_default_view()` dependence on
  `FrameView`
- Keep externally useful viewer methods stable where possible, but rebase them
  onto descriptor truth plus compiled ACL output

## State Deltas
- Replace hosted view objects with hosted per-frame descriptor/ACL consumer data
- Keep default frame selection at viewer level
- Keep active viewer profiles at viewer level

## Failure Rules
- Missing frame remains a fail-fast error
- Missing visible target remains a fail-fast error
- Viewer methods must continue to reject targets/fields hidden by ACL output
