# component_patch_frame_examiner

## Component purpose and boundary in current architecture
`FrameExaminer` is the read/inspection tool that gathers the configured target
frame's conduits, services, and profile truth for `AethericRiftSystem`.

## Before/after behavior summary
- Before:
  Frame inspection and exposure gathering were implied but not given a concrete
  object boundary.
- After:
  `FrameExaminer` is the explicit inspection layer instead of letting the public
  Rift or room absorb all discovery responsibilities.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  configured target frame, current profile state, available `Aether` accessors
- Outputs:
  gathered frame facts used for room population and profile aggregation
- Error semantics:
  missing frame, invalid conduit selection, or stale frame truth should surface
  as inspection/discovery errors rather than silently producing a bad room view

## State and lifecycle deltas
- Primarily read/inspection state only
- Does not own canonical Rift state
- Feeds `AethericRiftSystem`

## Failure mode deltas
- Overloading the public Rift with direct frame discovery responsibilities makes
  the architecture muddier
- Reaching through frame internals instead of using `Aether` accessors should be
  avoided when a clean accessor exists

## Dependency and ordering constraints
- Depends on `AethericRiftSystem`
- Depends on the configured target frame and available `Aether` accessors
- Should exist before room population is treated as complete

## Validation expectations
- `FrameExaminer` remains read/inspection only
- It gathers enough information to populate static and dynamic rooms
- It does not become a shadow manager or policy engine

## Unknowns and open decisions
- Exact method surface still depends on whether `_get_conduits_by_frame(...)`
  is added to `Aether`
