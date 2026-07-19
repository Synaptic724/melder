# Component Patch: FrameView Removal

## Decision
`FrameView` is removed from the runtime path in this patch.

## Why
- It currently owns target ordering/description behavior and local profile
  runtime that can live directly on `FrameViewer`
- Keeping it forces an extra projection/snapshot layer while the user wants the
  viewer to act directly on descriptor-organized data

## Removal Conditions
- No runtime code path in `Nexus` should construct `FrameView`
- `FrameViewer` should not import or reference `FrameView`
- `FrameViewProfile` and `FrameViewProfileBuilder` should also be removed from
  runtime usage

## Residual Constraint
If a hidden intermediate aggregate is still needed after implementation, that
must be raised as a design conflict rather than silently recreating `FrameView`
under a different name
