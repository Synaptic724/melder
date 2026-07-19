# component_patch_frame_descriptor_manager

## Component purpose and boundary in current architecture
`FrameDescriptorManager` owns the frame-scoped Nexus state surface:
- descriptor lookup/create
- frame posture refresh and publishability checks
- passive frame/conduit/spell record publication/removal
- Nexus-managed frame-record lookup/create/list/count

It is not the public Rift root and does not own Rift registry/configuration.

## Before/after behavior summary
- Before:
  This frame-scoped subsystem lived directly inside `Nexus`.
- After:
  It lives in one dedicated thread-safe manager owned by `Nexus`.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  frame names, spellbooks, conduits, spells, and Rift-owned frame-record
  requests delegated from `Nexus`
- Outputs:
  descriptor-owned frame records, conduit records, spell records, and
  Nexus-managed frame records
- Error semantics:
  fail fast on frame-store invariant breaks and malformed frame-scoped state

## State and lifecycle deltas
- Owns descriptor dictionary
- Owns manager-level `RLock`
- Owns frame-scoped state mutation helpers
- Does not own `Nexus` config or Rift registry state

## Failure mode deltas
- Multi-step state mutations cannot rely on container-level behavior alone.
- Partial migration must not leave dual source of truth.

## Dependency and ordering constraints
- Manager depends on `Nexus` for semantic façade entrypoints and may depend on
  `Aether` access passed in at construction time.
- Descriptor-owned nested state remains inside `FrameDescriptor`.

## Validation expectations
- The manager is explicitly thread-safe for multi-step mutations.
- Descriptor/store mutation paths live in the manager.
- `Nexus` delegates instead of mutating descriptor-store state directly.

## Unknowns and open decisions
- Whether a target-frame onboarding façade should later delegate into this
  manager
