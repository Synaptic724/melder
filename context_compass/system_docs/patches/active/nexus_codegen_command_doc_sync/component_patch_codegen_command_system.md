# Component Patch: CodegenCommandSystem

## Component Purpose and Boundary in Current Architecture
`CodegenCommandSystem` is the room-facing command facade for codegen rooms. It
inherits shared command/workstation behavior from `CommandSystem`, owns the
selected runtime-helper subset for codegen rooms, and delegates validate/execute
operations into the attached `CodegenSystem`.

## Before/After Behavior Summary
Before:
- canonical docs described a slim helper surface and placeholders, but did not
  document engine attachment or codegen-specific room-memory behavior

After:
- canonical docs describe `attach_codegen_system(...)`
- docs show validate/execute delegation into `CodegenSystem`
- docs show codegen-specific room-memory emission with full source/hash
  metadata

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - attached `ICodegenSystem`
  - generated Python `code`
  - target `frame_name`
- Outputs:
  - public validation payload dictionaries
  - public execution payload dictionaries
  - full-source room-memory records through the room memory system
- Error semantics:
  - `RuntimeError` when no codegen system is attached
  - `ValueError` for empty code or frame name

## State and Lifecycle Deltas
- command-system-owned state includes one attached `_codegen_system` reference
- cleanup MUST clear the attached engine reference before delegating to base
  cleanup
- docs MUST preserve the boundary that room-memory emission belongs to the
  command facade, not the engine root

## Failure Mode Deltas
- top-level validation/execution still unregister RiftGate tickets even on
  failure
- memory emission is skipped when room memory is unavailable or disabled

## Dependency and Ordering Constraints
- architecture/components docs MUST place `CodegenCommandSystem` between
  `CodegenRiftSpace` and `CodegenSystem`
- method-level flow updates MUST align with the code-description patch for
  validate/execute delegation

## Validation Expectations
- components docs explicitly mention engine attachment and full-source memory
  emission
- call-flow sections mention `validate_codegen(...)` /
  `execute_codegen(...)` -> `CodegenSystem` delegation -> memory emission
- graph update should add or adjust edges if delegation/ownership edges are
  currently missing

## Unknowns and Open Decisions
- UNKNOWN: whether the first doc pass should enumerate the full selected
  runtime-helper method set or keep it summarized as a selected helper subset
