# Component Patch: Codegen Namespace

## Before
- `CodegenNamespaceConfiguration` and `CodegenNamespace` exist.
- No builder exists.
- `CodegenSystem` manufactures a placeholder namespace directly.
- No namespace strategy files exist.

## After
- `CodegenNamespaceBuilder` owns live namespace assembly.
- Namespace exposure is split across four minimal strategy files:
  - room objects
  - workstation
  - command
  - target
- `CodegenSystem` consumes the builder instead of building the namespace itself.

## Validation Expectations
- The built namespace exposes the agreed stable names.
- When no target is selected, `target` is present and `None`.
- When a target is selected, `target` reflects the workstation target.

