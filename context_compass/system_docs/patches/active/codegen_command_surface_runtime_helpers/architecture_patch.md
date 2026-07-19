# Architecture Patch: Codegen Command Surface Runtime Helpers

## Objective
Expand `CodegenCommandSystem` from placeholder-only codegen seams to the user-
selected slim runtime-helper surface without inheriting the full capability
command model.

## Non-Goals
- No AST validation implementation.
- No compile/exec implementation.
- No codegen history/logging implementation.
- No further base/capability/static ownership changes.

## Changed Components
- `CodegenCommandSystem`
- focused codegen command-surface tests

## Invariants
- `CodegenCommandSystem` stays separate from `CapabilityCommandSystem`.
- The codegen public surface remains smaller than capability.
- Selected helper methods are explicitly owned on the codegen class.
- Discovery output matches the actual codegen helper set.

## Interface Deltas
- Add the selected runtime-helper methods directly to `CodegenCommandSystem`.
- Keep `validate_codegen(...)` and `execute_codegen(...)` as placeholders.
- Do not widen codegen to the full capability surface.

## Migration Order
1. Lock the selected helper list.
2. Add the selected helper methods to `CodegenCommandSystem`.
3. Update supported-method discovery.
4. Update focused tests.

## Rollback
If the selected helper set proves too broad for the current codegen room, keep
the placeholder-only surface and record the exact blocker instead of widening
into capability inheritance.
