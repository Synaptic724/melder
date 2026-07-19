# component_patch_rift

## Component purpose and boundary in current architecture
`Rift` is the live runtime object created by `Nexus`. It owns the immediate
runtime/config/frame-assignment state it needs and is the first AR layer that
actually touches `Aether` for operational frame access.

## Before/after behavior summary
- Before:
  `AethericRift` was treated as a shell bound to separate canonical
  `AethericRiftState`.
- After:
  `Rift` owns its own live state directly and does not require a separate
  public state object.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  finalized per-Rift configuration, assigned frame-name grants/defaults, space
  or workstation creation requests
- Outputs:
  live runtime behavior, room/workspace registration, object creation/query
  access against allowed frames
- Error semantics:
  operations fail fast when required config/frame assignments are missing or
  when Nexus has not created the Rift coherently

## State and lifecycle deltas
- Owns:
  - id/name
  - finalized Rift config snapshot
  - assigned system-frame names/default
  - assigned target-frame names/default
  - live spaces/workstation/workspace refs as they emerge
- Does not own:
  - the global Rift registry
  - Nexus-wide config
  - actual `AethericFrame` ownership

## Failure mode deltas
- The older shell/state split becomes unnecessary ceremony unless true
  persistence or rehydration is later required
- Pushing registry/config state down into `Rift` would weaken the Nexus root

## Dependency and ordering constraints
- Created only through `Nexus`
- Targets `Aether` operationally only after Nexus assigns frame names/defaults
- Future workstation/workspace layers sit below `Rift`, not above Nexus

## Validation expectations
- No separate public `RiftState` remains in the active model
- `Rift` stores the frame/config state it actually needs
- `Rift` is the first layer that resolves named frames through hidden Aether

## Unknowns and open decisions
- Exact workstation/workspace field set remains a later slice
