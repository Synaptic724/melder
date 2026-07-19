# Code Description Patch: Codegen Validation Flow

## Control Flow
1. `CodegenCommandSystem.validate_codegen(...)`
   - validates non-empty public inputs
   - delegates into `CodegenSystem.validate_codegen(...)`
   - asks `CodegenSystem` to report the validation result payload
2. `CodegenSystem.validate_codegen(...)`
   - builds one `CodegenTransactionContext`
   - delegates to `CodegenValidator`
3. `CodegenValidator`
   - parses the code with `ast.parse(...)`
   - returns syntax failure when parsing fails
   - otherwise returns the current not-implemented validation result
4. `CodegenValidationReporter`
   - converts `CodegenValidationResult` into the public payload shape
5. `CodegenSystem.execute_codegen(...)`
   - validates first
   - returns an execution validation failure result when syntax is invalid
   - otherwise returns the current not-implemented execution result

## Edge / Error Semantics
- Empty `code` and empty `frame_name` still fail at the command-surface entry.
- Syntax errors now surface as validation failures.
- Successful syntax parse does not imply execution support yet.

## Idempotency / Lifecycle
- Validator and reporter are owned by `CodegenSystem`.
- Cleanup drops those owned references with the rest of the root codegen state.

## Non-Goals
- No strategy family yet.
- No compile/exec yet.
- No namespace builder yet.

