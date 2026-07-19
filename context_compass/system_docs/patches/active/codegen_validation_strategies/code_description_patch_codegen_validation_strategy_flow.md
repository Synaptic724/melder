# Code Description Patch: Codegen Validation Strategy Flow

## Control Flow
1. `CodegenValidator.validate(...)`
   - parses the code with `ast.parse`
   - returns syntax failure immediately on parse error
   - iterates the strategy family in fixed order
2. Each strategy
   - receives `CodegenTransactionContext`
   - returns either `None` or a `CodegenValidationResult`
3. Validator
   - returns the first failure result
   - otherwise returns the current not-implemented result

## Edge / Error Semantics
- Syntax errors still win over policy errors.
- Name-resolution checks are based on namespace configuration, not the live
  namespace globals dict.
- Attribute-access checks are pattern-based in this slice, not full runtime
  reflection.

## Idempotency / Lifecycle
- Strategy objects are owned by `CodegenValidator`.
- Validator cleanup remains unnecessary because strategies are stateless in this slice.

## Non-Goals
- No strategy-specific reporting objects.
- No per-strategy metrics/history yet.

