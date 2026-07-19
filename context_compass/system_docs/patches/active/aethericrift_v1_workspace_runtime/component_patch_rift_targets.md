# component_patch_rift_targets

## Component purpose and boundary in current architecture
`RiftAttribute` and `RiftMethod` define the declared workspace target model.
They are the named target universe codegen and validation reason over.

## Before/after behavior summary
- Before:
  The design drifted between older `RefAttr` / `RefMethod`, raw object access,
  and other target-model names.
- After:
  `RiftAttribute` and `RiftMethod` are the active canonical names and the room’s
  declared target language.

## Interface deltas (inputs, outputs, error semantics)
- Inputs:
  names, bound objects/callables, metadata
- Outputs:
  named targets visible to codegen and direct room operations
- Error semantics:
  name collisions, invalid replacement, or invalid target metadata should be
  explicit room-level registration errors

## State and lifecycle deltas
- Targets carry metadata
- Targets are clearable/replacable by explicit room operations
- Targets do not become canonical mutation by default

## Failure mode deltas
- Missing or sloppy target metadata erodes room legibility
- Unclear local/imported/promoted state makes cleanup and promotion ambiguous

## Dependency and ordering constraints
- Depends on `RiftSpace`
- Feeds directly into `RiftValidationSystem`

## Validation expectations
- Codegen target names match the declared registries
- The room can inspect and clear targets explicitly
- The room does not collapse into ambient anonymous locals

## Unknowns and open decisions
- Exact minimal metadata fields can still be refined during implementation
