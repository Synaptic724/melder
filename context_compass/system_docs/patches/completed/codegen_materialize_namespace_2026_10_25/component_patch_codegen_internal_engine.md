# component_patch_codegen_internal_engine

## Metadata
- Patch ID: codegen_materialize_namespace_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T11:34:22Z
- Updated: 2026-10-25T11:34:22Z
- Ticket: TASK-2026-10-10-refuse-materializing-over-live-modules (D-20), parent
  EPIC-2026-10-25-codegen_room_policy_defects

## Component Purpose and Boundary
- Codegen Internal Engine: exposes the room's filtered builtins mapping for one accepted transaction.

## Before/After Behavior Summary
- Before: only `execute_codegen` gets the filtered builtins; materialized code got the interpreter's.
- After: `build_materialize_builtins(context)` returns the same mapping (denied builtins stripped, D-11 import
  guard installed) from the context's namespace configuration, building the default when absent.

## Interface Deltas
- `CodegenSystem.build_materialize_builtins`; `CodegenNamespaceBuilder.build_builtins(configuration)`.

## State and Lifecycle Deltas
- None; a fresh dict per call.

## Failure Mode Deltas
- A None context raises TypeError, as `_build_namespace` does.

## Dependency and Ordering Constraints
- Called only after accepted validation.

## Validation Expectations
- Unit: the mapping lacks a denied name and carries the import guard under hybrid.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION: materialized code gets room builtins (the owner, chat 2026-10-25).

## Context / Handoff Summary
One mapping for room code, executed or materialized.
