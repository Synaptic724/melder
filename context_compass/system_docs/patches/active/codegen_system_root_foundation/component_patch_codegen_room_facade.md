# Component Patch: Codegen Room Facade

## Before
- `CodegenRiftSpace` only composes `CodegenCommandSystem`.
- `CodegenCommandSystem` owns placeholder validate/execute logic directly.

## After
- `CodegenRiftSpace` owns one private `CodegenSystem`.
- `CodegenCommandSystem` receives that system and delegates
  `validate_codegen(...)` / `execute_codegen(...)` into it.
- The selected helper surface remains unchanged.

## Validation Expectations
- Existing codegen room composition tests still pass.
- Placeholder payload tests still pass.
- New delegation tests prove the room/facade wiring.

