# Component Patch: Codegen System Validation Wiring

## Before
- `CodegenSystem` creates placeholder validation/execution results directly.
- `CodegenCommandSystem.validate_codegen(...)` returns `result.to_payload()`
  from the placeholder result type.

## After
- `CodegenSystem` owns one validator and one validation reporter.
- `CodegenSystem.validate_codegen(...)` delegates into the validator.
- `CodegenSystem.report_validation_result(...)` delegates into the reporter.
- `CodegenSystem.execute_codegen(...)` checks validation first:
  - syntax failure becomes an execution-layer validation failure result
  - valid code still returns the current not-implemented execution result

## Validation Expectations
- Existing codegen placeholder tests stay green.
- New syntax-failure tests prove the validation boundary is live.

