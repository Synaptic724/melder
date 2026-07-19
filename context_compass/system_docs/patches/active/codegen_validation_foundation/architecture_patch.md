# Architecture Patch: Codegen Validation Foundation

## Objective
Land the next bounded codegen slice by turning validation into a real internal
subsystem and wiring the root codegen engine to consume it before any execution
work happens.

## Non-Goals
- No validation strategy files yet.
- No namespace strategy files yet.
- No compile/exec engine implementation yet.
- No observability implementation yet.

## Changed Components
- `codegen_system/validation/`
- `CodegenSystem`
- `CodegenCommandSystem`

## Invariants
- Validation remains separate from execution.
- Validation reporting remains separate from validation enforcement.
- The public room validate payload stays stable for valid placeholder cases.
- `execute_codegen(...)` may now surface validation failures before execution,
  but still returns not-implemented for valid code.

## Interface Deltas
- Add `CodegenValidator`.
- Add `CodegenValidationReporter`.
- Extend `CodegenSystem` to own and consume them.
- Extend `CodegenCommandSystem.validate_codegen(...)` to use the reporter path.

## Migration Order
1. Add validation patch artifacts.
2. Implement validator and validation reporter.
3. Wire `CodegenSystem` to use them.
4. Adjust `CodegenCommandSystem` validate path.
5. Add focused tests.

## Rollback
If syntax-aware validation proves too early, keep the validator/reporter files
and revert only the syntax-failure execution behavior while preserving the
subsystem boundary.

