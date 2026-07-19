# Component Patch: RiftSpace And Command System

## Components
- `DynamicRiftSpace` -> `CodegenRiftSpace`
- `DynamicCommandSystem` -> `CodegenCommandSystem`
- `Rift`

## Before
- Final AR room is still named `dynamic`.
- It currently shares capability's broad manual-runtime posture.
- The class names imply runtime/substrate posture rather than the room's AR
  differentiator.

## After
- Final AR room is named `codegen`.
- The room still shares the same current manual-runtime posture unless and
  until later codegen-specific behavior is added.
- Naming now reflects the AR-layer differentiator, not the lower substrate
  posture.

## Constraint
- This rename must not imply a lower runtime semantic change.

## Validation Expectation
- Rift primary-space construction selects `CodegenRiftSpace`.
- Room-specific command system selection chooses `CodegenCommandSystem`.
