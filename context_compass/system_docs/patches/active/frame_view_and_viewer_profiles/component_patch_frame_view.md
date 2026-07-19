# Frame View Component Patch

## Before
- `FrameView` had no profile concept.

## After
- `FrameView` can optionally carry a view profile identity/default posture.

## Invariants
- profile only shapes defaults/presentation posture
- profile does not change ACL-derived visibility
