# Component Patch: FrameACLBuilder

## Before
- one draft session cloned from the container's frame-global current bundle

## After
- one draft session targets one config family and one contract name
- draft clone source is the current config of that family/name chain
- commit inserts into that family/name chain

## Interface Deltas
- `begin_change(...)` becomes family/name aware
- `commit_change(...)` commits into the targeted family/name chain

## Non-Goals
- no reusable precision-builder surface yet
