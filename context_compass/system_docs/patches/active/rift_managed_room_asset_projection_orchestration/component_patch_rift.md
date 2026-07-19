# Component Patch: Rift-Owned Projection Registry And Asset Application

## Before
- Rift orchestrates refresh but stores no projection registry of its own.
- RiftSpace stores projection sets and asset sync helpers.

## After
- Rift owns the current frame projection registry.
- Rift merges/replaces projection updates internally.
- Rift applies view projections to the viewer asset and exposes command/codegen
  projection truth internally for other assets.

## Validation Expectation
- Focused Rift tests prove projection refresh still works and room assets stay
  in sync.
