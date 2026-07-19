# component_patch_frame_acl_builder

## Component purpose and boundary in current architecture
`FrameACLBuilder` is the mutable frame-scoped ACL authoring object returned by
the container. In this placeholder slice it should exist as structure, not as
the full ACL mutation engine.

## Before/after behavior summary
- Before:
  Builder semantics existed only in design notes.
- After:
  One frame-scoped builder object exists per container.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  manager/container-owned ACL state
- Outputs:
  placeholder builder object for future ACL authoring flow
- Error semantics:
  invalid creation or detached ownership should fail fast

## State and lifecycle deltas
- builder is object-singleton per frame container
- builder should be created through the container, not ad hoc by callers

## Validation expectations
- repeated container builder access returns the same object
