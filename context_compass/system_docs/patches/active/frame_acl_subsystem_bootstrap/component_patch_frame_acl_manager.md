# component_patch_frame_acl_manager

## Component purpose and boundary in current architecture
`FrameACLManager` is the Nexus-owned coordinator for frame-scoped ACL
containers. It is not the public Nexus root and it is not yet the full
propagation engine.

## Before/after behavior summary
- Before:
  The ACL lane had design docs but no concrete frame-scoped runtime object.
- After:
  One placeholder manager exists on `Nexus` and owns per-frame ACL containers
  keyed by frame name.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  descriptor-owned frame context and future ACL operations
- Outputs:
  access to the unique container and its placeholder ACL objects
- Error semantics:
  placeholder slice should fail fast on invalid construction rather than hiding
  ownership mistakes

## State and lifecycle deltas
- manager owns per-frame containers keyed by frame name
- manager is thread-safe
- manager does not pretend to solve full ACL propagation in this slice

## Validation expectations
- manager exists under `Nexus`
- manager owns one container per frame target by name
- builder is not recreated ad hoc
