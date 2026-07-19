# Component Patch: Nexus Viewer Ownership Removal

## Before
- `Nexus` builds `FrameProjectionSet` objects and also assembles/caches
  `FrameViewer` objects.
- ACL-change handling invalidates viewer cache and then refreshes attached
  viewers through `Rift.attach_frame_viewer(...)`.

## After
- `Nexus` builds projection sets only.
- ACL-change handling refreshes projection sets for affected Rifts and lets the
  room rebuild its viewer from installed projections.
- Nexus-owned viewer cache fields/helpers are gone.

## Validation Expectation
- Focused Nexus/Rift projection tests pass without the removed viewer APIs.
