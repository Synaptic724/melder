# Architecture Patch: Codegen System Root Foundation

## Objective
Land the first real codegen runtime slice by adding the root `codegen_system/`
foundation and wiring the room/facade to delegate into it without widening the
public room command surface.

## Non-Goals
- No validation strategy implementation.
- No namespace strategy implementation.
- No compile/exec engine implementation.
- No new public room commands beyond the existing helper set plus
  `validate_codegen(...)` / `execute_codegen(...)`.

## Changed Components
- `codegen_system/` root package
- `CodegenRiftSpace`
- `CodegenCommandSystem`

## Invariants
- `CodegenCommandSystem` remains the public room-facing facade.
- `CodegenRiftSpace` owns the internal `CodegenSystem`.
- The public placeholder payload shape remains stable while internals move to
  the new engine.
- Validation result and execution result remain separate types.
- Namespace configuration and live namespace remain separate types.

## Interface Deltas
- Add `CodegenSystem` and `CodegenTransactionContext`.
- Add `CodegenValidationResult` and `CodegenExecutionResult`.
- Add `CodegenNamespaceConfiguration` and `CodegenNamespace`.
- Extend `CodegenRiftSpace` to own a private `CodegenSystem`.
- Extend `CodegenCommandSystem` so `validate_codegen(...)` and
  `execute_codegen(...)` delegate into the owned `CodegenSystem`.

## Migration Order
1. Add root patch artifacts.
2. Add root foundation files under `codegen_system/`.
3. Wire `CodegenRiftSpace` ownership.
4. Wire `CodegenCommandSystem` delegation.
5. Update focused tests.

## Rollback
If the root delegation proves too early, keep the new foundation files and
revert only the room/facade delegation while preserving the package layout.

