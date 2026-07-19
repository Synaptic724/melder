# Component Patch: Codegen Execution

## Before
- `CodegenExecutionResult` exists.
- No compiler exists.
- No executor exists.
- `CodegenSystem.execute_codegen(...)` returns a placeholder result after
  namespace build when validation succeeds.

## After
- `CodegenCompiler` owns compile.
- `CodegenExecutor` owns `exec`.
- `CodegenSystem.execute_codegen(...)` validates, builds namespace, compiles,
  executes, and returns `CodegenExecutionResult`.

## Validation Expectations
- Valid code executes and can return `result`.
- Syntax failures still fail at validation before execution.
- Runtime errors surface through execution result payloads.

