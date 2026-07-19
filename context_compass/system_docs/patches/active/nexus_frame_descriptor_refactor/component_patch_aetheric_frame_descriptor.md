# component_patch_frame_descriptor

## Component purpose and boundary in current architecture
`FrameDescriptor` is the Nexus-side aggregate for one frame. It is not
the runtime `AethericFrame`; it is the Nexus-owned descriptive container for
frame-scoped state.

## Before/after behavior summary
- Before:
  No single Nexus-side frame aggregate exists.
- After:
  One descriptor can host frame posture, frame overview, Nexus-managed frame
  metadata, frame-local records, and later ACL containers.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  frame publication/update paths from Nexus
- Outputs:
  nested frame-scoped state
- Error semantics:
  descriptor invariants should fail fast if nested state becomes contradictory

## State and lifecycle deltas
- Likely nested fields:
  - frame handle
  - frame configuration
  - frame overview
  - nexus frame record
  - frame-local entries/indexes
  - future ACL containers

## Failure mode deltas
- Treating the descriptor as a runtime frame replacement would blur ownership
  badly.
- Making it a dumping ground would just recreate the current problem under a
  different name.

## Dependency and ordering constraints
- Descriptor is owned only by Nexus
- Descriptor should remain frame-scoped, not process-global

## Validation expectations
- Descriptor contents remain clearly separated internally
- Descriptor can grow later without re-fragmenting frame-scoped state

## Unknowns and open decisions
- Exact nested object names (`FrameOverview`, entry containers, ACL containers)
