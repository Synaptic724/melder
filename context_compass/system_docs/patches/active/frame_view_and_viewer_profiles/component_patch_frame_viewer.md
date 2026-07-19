# Frame Viewer Component Patch

## Before
- `FrameViewer` had behavior but no profile foundation.

## After
- `FrameViewer` can optionally carry a viewer profile identity/default posture.
- one seeded `general` viewer profile exists through a small builder/catalog path.

## Invariants
- profiles modify defaults and enabled helper sets only
- profiles do not redefine permissions
