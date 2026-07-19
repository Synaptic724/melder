# Architecture Patch: Codegen Namespace Foundation

## Objective
Land the next bounded codegen slice by replacing the placeholder namespace path
with a real namespace builder and the minimal exposure strategies needed for
the stable namespace contract.

## Non-Goals
- No builtins strategy yet.
- No validation strategy files yet.
- No compile/exec engine implementation.
- No direct-local workstation binding expansion beyond the agreed stable names.

## Changed Components
- `codegen_system/namespace/`
- `codegen_system/namespace/strategies/`
- `CodegenSystem`

## Invariants
- `CodegenNamespaceConfiguration` remains separate from `CodegenNamespace`.
- The stable initial namespace names remain:
  - `rift`
  - `space`
  - `viewer`
  - `workstation`
  - `command`
  - `target`
  - `frame_name`
- `CodegenSystem` stops manufacturing the placeholder namespace directly.
- The builder consumes strategies instead of hand-building a giant dict.

## Interface Deltas
- Add `CodegenNamespaceBuilder`.
- Add namespace strategies:
  - room objects
  - workstation
  - command
  - target
- Extend `CodegenSystem` to own and consume the builder.

## Migration Order
1. Add namespace patch artifacts.
2. Implement the builder and minimal strategy files.
3. Wire `CodegenSystem` to consume the builder.
4. Add focused namespace tests.

## Rollback
If the strategy split proves too early, keep the builder and fold only the
strategy internals back into it while preserving the namespace boundary.

