# Component Patch: Codegen System Namespace Wiring

## Before
- `CodegenSystem.execute_codegen(...)` calls `_build_placeholder_namespace(...)`.
- No builder object exists in the root engine.

## After
- `CodegenSystem` owns one `CodegenNamespaceBuilder`.
- `CodegenSystem.execute_codegen(...)` and any later execution path use
  `_build_namespace(...)`.
- The root engine no longer manufactures namespace globals/locals itself.

## Validation Expectations
- Focused codegen tests prove:
  - builder ownership
  - stable namespace names
  - selected target reflection

