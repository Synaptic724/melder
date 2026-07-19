# Component Patch: StaticRiftSpace

## Before
- `StaticRiftSpace` composed `StaticCommandSystem` only.
- Attached viewers stayed generic.

## After
- `StaticRiftSpace` composes the static viewer variant when a viewer is
  attached.

## Contract
- Static rooms keep the same viewer access pattern (`space.frame_viewer`).
- The difference is behavioral: spell-facing viewer output is live-only.

## Validation Expectations
- Focused room tests should prove attached viewers become static viewers in
  static rooms.
