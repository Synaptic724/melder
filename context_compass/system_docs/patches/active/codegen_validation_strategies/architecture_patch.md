# Architecture Patch: Codegen Validation Strategies

## Objective
Land the next governance slice by turning the validator from syntax-only into a
real strategy-driven policy subsystem across structure, imports, builtins, name
resolution, and attribute access.

## Non-Goals
- No observability implementation.
- No builtins namespace strategy.
- No compile/exec changes beyond consuming the strengthened validator.

## Changed Components
- `codegen_system/validation/strategies/`
- `CodegenValidator`
- focused codegen tests

## Invariants
- Validation remains separate from execution.
- Strategy files own rule families, not reporting.
- Namespace policy and validator strategy checks must stay aligned.
- Syntax still fails first.

## Interface Deltas
- Add five validation strategy files.
- Extend `CodegenValidator` to compose them.
- Valid code may still return not-implemented until deeper features are added.
- Invalid policy violations return validation-failure payloads before execution.

## Migration Order
1. Add validation-strategy patch artifacts.
2. Implement strategy files.
3. Wire `CodegenValidator` to consume them.
4. Add focused tests for each rule family.

## Rollback
If a strategy boundary proves wrong, keep the file set and collapse only the
internal delegation while preserving the validator-facing result contract.

