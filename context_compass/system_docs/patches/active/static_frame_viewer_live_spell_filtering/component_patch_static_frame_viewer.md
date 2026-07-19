# Component Patch: StaticFrameViewer

## Before
- Static rooms used the generic `FrameViewer`.
- Spell-facing viewer methods and target projection still surfaced published
  spells regardless of liveness.

## After
- `StaticFrameViewer` filters spell-facing viewer surfaces to already-live
  spells only.
- Filtering is an overlay; it does not mutate descriptor publication.

## Contract
- Frame and conduit queries stay structural.
- Spell lists, spell record resolution, and spell target projection are
  live-only.
- No-create live checks use existing runtime truth only.

## Validation Expectations
- Focused static viewer tests should prove non-live spells disappear from
  spell-facing queries and target projection.
