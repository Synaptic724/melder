# component_patch_rift_validation_system

## Component purpose and boundary in current architecture
`RiftValidationSystem` parses, validates, and classifies submitted codegen for
the room.

## Before/after behavior summary
- Before:
  Validation was described at a philosophy level and drifted between older
  target-language names.
- After:
  `RiftValidationSystem` explicitly validates against the active room target
  model and mode semantics.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  code string, configuration, room target registries
- Outputs:
  parse result, validation result, classification result, hook outcomes
- Error semantics:
  invalid syntax, invalid targets, invalid member paths, or disallowed mode use
  should fail before execution

## State and lifecycle deltas
- Validation itself is stateless enough to be reused per code submission
- It depends on the current room target model and current configuration

## Failure mode deltas
- Validation against stale names or stale room assumptions would break operator
  expectations quickly
- Weak validation would collapse the declared target universe back into ambient
  Python access

## Dependency and ordering constraints
- Depends on `RiftSpace`
- Depends on current profile/config picture
- Must exist before meaningful `simple` or `dynamic` execution can work

## Validation expectations
- Names and member paths must be checked against the declared room targets
- `StaticRiftSpace` and `DynamicRiftSpace` must differ in what construction
  paths are allowed
- Hook execution should remain configuration-driven and explicit
- Validation should not pretend to be stronger than the room surface actually is:
  static is enforced through the static room surface, dynamic is governed mainly
  through AST preflight and hooks

## Unknowns and open decisions
- The exact syntax allowlist can still be refined during implementation
