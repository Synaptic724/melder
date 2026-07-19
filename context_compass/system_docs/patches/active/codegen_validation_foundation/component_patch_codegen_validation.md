# Component Patch: Codegen Validation

## Before
- Validation result type exists.
- No validator object exists.
- No validation reporter exists.
- `CodegenSystem` manufactures placeholder validation results directly.

## After
- `CodegenValidator` owns validation orchestration.
- `CodegenValidationReporter` owns payload shaping for validation responses.
- `CodegenSystem` consumes both instead of manufacturing validation payloads
  directly.
- Basic syntax failure reporting is allowed in this slice.

## Validation Expectations
- Valid code still returns the current not-implemented validation payload.
- Invalid syntax returns a validation-failure payload with issue details.
- Focused unit tests cover validator ownership and syntax failure behavior.

