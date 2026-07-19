# Code Description Patch: Codegen System Root

## Control Flow
1. `CodegenRiftSpace.__init__(...)`
   - creates the room-local `CodegenSystem`
   - composes `CodegenCommandSystem` with that engine
2. `CodegenCommandSystem.validate_codegen(...)`
   - validates public inputs
   - delegates into `CodegenSystem.validate_codegen(...)`
   - returns the public payload form
3. `CodegenCommandSystem.execute_codegen(...)`
   - validates public inputs
   - delegates into `CodegenSystem.execute_codegen(...)`
   - returns the public payload form
4. `CodegenSystem`
   - creates one `CodegenTransactionContext`
   - returns placeholder validation/execution result objects for now

## Edge / Error Semantics
- Empty `code` and empty `frame_name` still fail at the command-surface entry.
- The new engine does not yet parse or execute code.
- Placeholder reasons remain:
  - `codegen_validation_not_implemented`
  - `codegen_execution_not_implemented`

## Idempotency / Lifecycle
- `CodegenSystem.cleanup()` is idempotent.
- `CodegenRiftSpace.cleanup()` cleans the owned `CodegenSystem` before room
  teardown drops local references.

## Non-Goals
- No AST validation yet.
- No namespace build yet.
- No compile/exec yet.
- No history/log/monitor implementation yet.

