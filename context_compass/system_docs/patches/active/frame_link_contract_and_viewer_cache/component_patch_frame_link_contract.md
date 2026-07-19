# Frame Link Contract Component Patch

## Before
- `FrameLinkContract` mostly exposed raw tuples and metadata.

## After
- `FrameLinkContract` exposes stable helper APIs for:
  - kind/command allow checks
  - frame payload fields
  - conduit payload sections by id
  - spell payload sections by key
  - contract summaries

## Invariants
- helper outputs remain detached
- helper methods must not mutate contract state
