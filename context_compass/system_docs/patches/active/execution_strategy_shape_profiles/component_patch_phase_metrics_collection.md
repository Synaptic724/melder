# Component Patch: Phase Metrics Collection

## Before
Useful raw shape truth exists inside the current phase artifacts, but it is not
normalized into one artifact-owned profile surface for later strategy
selection.

## After
Phases 1, 8, 9, 10, and 11 each emit a cheap shape profile at the point where
their truth is already available.

## Collection Plan
- Phase 1:
  - parameter and DI-shape counts
- Phase 8:
  - depth/width/shared occurrence shape
- Phase 9:
  - injection/override/contract shape
- Phase 10:
  - override targetability/path-depth shape
- Phase 11:
  - final step/runtime shape

## State / Failure Deltas
- No extra heavy pass should appear in later phases.
- New fields should be derived from already-built phase structures only.

## Validation Expectations
- The five phase files parse after profile writes are added.
