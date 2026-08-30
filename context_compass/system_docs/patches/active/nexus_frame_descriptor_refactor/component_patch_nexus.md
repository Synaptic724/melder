# component_patch_nexus

## Component purpose and boundary in current architecture
`Nexus` should remain the singleton root, but frame-scoped state should stop
living in scattered flat fields and instead be organized under one
`FrameDescriptor` per frame.

## Before/after behavior summary
- Before:
  Frame-scoped state is split across flat store fields, frame posture cache,
  frame records, and Nexus-managed frame records.
- After:
  Frame-scoped state migrates under one descriptor aggregate, while `Nexus`
  remains the registry/root owner.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  existing frame publication/update/remove calls
- Outputs:
  descriptor-owned frame state instead of flat parallel fields
- Error semantics:
  malformed or partial descriptor state should fail fast inside Nexus

## State and lifecycle deltas
- Add `_frame_descriptors_by_name`
- Move frame posture and frame overview under the descriptor
- Later move frame-local entry sets and ACL containers under the descriptor

## Failure mode deltas
- Continuing the flat shape will harden the wrong internal model for viewer/ACL
  work.
- Collapsing everything in one pass would create avoidable migration risk.

## Dependency and ordering constraints
- Depends on the completed passive-ingest slice
- Must preserve current behavior while migrating in stages

## Validation expectations
- One descriptor per frame name
- No ambiguous dual source of truth after each migration slice

## Unknowns and open decisions
- Exact first-slice descriptor contents
