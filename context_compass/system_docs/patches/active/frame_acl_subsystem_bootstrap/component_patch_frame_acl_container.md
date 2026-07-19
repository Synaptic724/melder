# component_patch_frame_acl_container

## Component purpose and boundary in current architecture
`FrameACLContainer` is the holder for the unique frame-scoped ACL objects for
one frame.

## Before/after behavior summary
- Before:
  The ACL lane had no concrete place to keep the unique builder/config/validator
  objects for one frame.
- After:
  One container owns those objects under the Nexus-owned manager.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  frame identity and manager-owned construction flow
- Outputs:
  access to the unique builder object, current config placeholder, validator,
  and history holder
- Error semantics:
  invalid ownership wiring should fail fast

## State and lifecycle deltas
- container owns:
  - current configuration placeholder
  - bounded history placeholder
  - one builder object
  - one validator object
- container is created with defaults when the matching descriptor is first
  created

## Validation expectations
- repeated builder access returns the same builder object
- configuration/history/validator live under the same container
