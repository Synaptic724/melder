# Component Patch: FrameACLContainer

## Before
- one frame-local bundle chain
- one sidecar named configuration registry
- `"default"` mirrors the current frame-global chain node

## After
- one frame-local registry of named view chains
- one frame-local registry of named command chains
- one frame-local registry of named codegen chains
- current/head/history/rollback semantics are per family chain

## Interface Deltas
- family-aware accessors for:
  - current configuration
  - head configuration
  - history/configuration listing
  - named chain registration/lookup
- builder-facing family + contract selection for draft sessions

## State / Failure Deltas
- duplicate family-chain names still fail fast within each family registry
- unknown family-chain names fail fast
- family-chain history operations fail fast when the target family/name is unknown
