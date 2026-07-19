# Architecture Patch: Codegen Execution Foundation

## Objective
Land the next bounded codegen slice by replacing the execution placeholder with
the real internal compile/exec path while preserving the existing room-facing
execution contract shape.

## Non-Goals
- No validation strategy implementation.
- No observability implementation.
- No builtins strategy yet.
- No direct workstation-binding-local expansion.

## Changed Components
- `codegen_system/execution/`
- `CodegenSystem`

## Invariants
- `CodegenCompiler` remains an internal stage.
- `CodegenExecutor` remains the owner of actual execution.
- `CodegenExecutionResult` remains separate from validation results.
- Validation still runs before execution.
- `execute_codegen(...)` now executes valid code against the built namespace.

## Interface Deltas
- Add `CodegenCompiler`.
- Add `CodegenExecutor`.
- Extend `CodegenSystem.execute_codegen(...)` to use compile/exec instead of
  returning the placeholder path for valid code.

## Migration Order
1. Add execution patch artifacts.
2. Implement compiler and executor.
3. Wire `CodegenSystem.execute_codegen(...)` to consume them.
4. Update focused tests for real execution behavior.

## Rollback
If real execution proves too early, keep compiler/executor files and revert only
the `CodegenSystem.execute_codegen(...)` wiring while preserving the package
boundary.

