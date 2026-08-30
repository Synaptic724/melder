# component_patch_nexus

## Component purpose and boundary in current architecture
`Nexus` should remain the process-wide façade/root for Rift-domain behavior:
- configuration
- enablement
- Rift registry
- profile templates
- topology decisions

It should stop directly owning frame-scoped descriptor/store state.

## Before/after behavior summary
- Before:
  `Nexus` directly owned the descriptor dictionary plus the frame-scoped
  posture refresh, passive publication/removal, and Nexus-managed frame-record
  helpers.
- After:
  `Nexus` delegates those frame-scoped mechanics to
  `FrameDescriptorManager` and keeps façade/root semantics.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  same façade-level frame and Rift operations as before
- Outputs:
  delegated frame-scoped behavior through the manager
- Error semantics:
  `Nexus` should continue surfacing semantic root-level failures while the
  manager handles low-level frame-store invariant failures

## State and lifecycle deltas
- Removes direct ownership of `_frame_descriptors_by_name`
- Adds owned manager reference
- Keeps Rift registry/config/topology state in `Nexus`

## Failure mode deltas
- Keeping direct frame-state mutation in `Nexus` would preserve the current
  god-object pressure.
- Leaving alias methods behind would recreate dual ownership.

## Dependency and ordering constraints
- `FrameDescriptorManager` must be created before frame-scoped delegation paths
  are used.
- `Nexus` should not mutate manager-owned frame-state directly after migration.

## Validation expectations
- `Nexus` remains the semantic façade/root.
- Frame-scoped state ownership leaves `Nexus`.
- No old direct descriptor-store paths remain.

## Unknowns and open decisions
- Exact façade docstring depth on delegated methods
