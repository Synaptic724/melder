# Component Patch: FrameACLCompiler

## Before
- compiler resolves only the base view/codegen profile names
- effective access is compiled from:
  - base profile
  - overrides

## After
- compiler resolves:
  - base profile
  - precision profile
- effective access is compiled from:
  - base profile
  - precision profile
  - overrides

## Interface Deltas
- family configs become the source of precision-profile identity
- compiler merge order is explicit and matches validator compatibility logic

## State / Failure Deltas
- missing precision profile names fail during profile resolution
- compiled access surfaces reflect precision policy without adding a fourth ACL
  configuration family
