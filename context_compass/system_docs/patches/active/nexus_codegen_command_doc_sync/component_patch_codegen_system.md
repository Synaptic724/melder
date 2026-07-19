# Component Patch: CodegenSystem

## Component Purpose and Boundary in Current Architecture
`CodegenSystem` is the internal codegen-engine root owned by one
`CodegenRiftSpace`. It owns per-call transaction construction plus validator,
namespace-builder, compiler, executor, reporter, and monitor collaborators.

## Before/After Behavior Summary
Before:
- canonical docs described codegen mostly as a thin command seam and did not
  name the internal engine package

After:
- canonical docs explicitly describe `CodegenSystem` as the root internal
  engine beneath `CodegenCommandSystem`
- docs name the owned validation, namespace, execution, and observability
  collaborators and the transaction-context flow

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - generated Python `code`
  - target `frame_name`
  - optional `CodegenProjection` resolved through the owning `Rift`
- Outputs:
  - `ICodegenValidationResult`
  - `ICodegenExecutionResult`
  - shared `ICodegenTransactionContext`
  - public validation payloads through the reporter
- Error semantics:
  - `ValueError` for empty code or frame name
  - best-effort projection resolution that tolerates missing projection seams

## State and Lifecycle Deltas
- owned state includes validator, validation reporter, namespace builder,
  compiler, executor, and monitor
- cleanup MUST describe collaborator cleanup/nulling and lock-disciplined
  teardown
- docs MUST separate room-memory emission from engine ownership

## Failure Mode Deltas
- validation failure returns a validation-failed execution result instead of
  executing compiled code
- missing projection support does not hard-fail transaction construction

## Dependency and Ordering Constraints
- architecture/components docs MUST show:
  - `CodegenRiftSpace` owns `CodegenSystem`
  - `CodegenSystem` borrows `Rift` and room
  - `CodegenCommandSystem` delegates into `CodegenSystem`
- graph update MUST add node and edge coverage for the internal engine files

## Validation Expectations
- architecture/components docs include explicit `CodegenSystem` ownership and
  transaction flow
- graph includes nodes and semantic edges for the internal engine root and its
  core collaborators where warranted by the source review
- readable graph regeneration is required if canonical graph storage changes

## Unknowns and Open Decisions
- UNKNOWN: how granular the first-pass graph expansion should be for the
  internal validation strategy files versus grouped validator ownership
