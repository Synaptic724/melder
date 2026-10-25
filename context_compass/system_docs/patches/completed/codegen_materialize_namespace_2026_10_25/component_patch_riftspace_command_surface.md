# component_patch_riftspace_command_surface

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
- RiftSpace Workstation And Command Surface: `CodegenCommandSystem.materialize_codegen`, the enforcement point.

## Before/After Behavior Summary
- Before: any dotted-legal name published over whatever held it; failure cleanup lost a displaced module.
- After: validation, then the six refusals (architecture_patch), then the room's builtins merged into the module,
  then materialize; on failure the module and the parent shells this call created are cleaned, deepest first.

## Interface Deltas
- Payload key `refusal` (str) when a policy refusal answers; `materialized` False; `validation` as before.

## State and Lifecycle Deltas
- None held; the verb reads the projection's compiled surface from the transaction context.

## Failure Mode Deltas
- Exec errors still propagate after the restoring cleanup; illegal names still raise ValueError.

## Dependency and Ordering Constraints
- Policy after validation (needs the frame's surface) and before SyntheticModule construction.

## Validation Expectations
- Unit (mocked engine) and integration (real rooms) per refusal; failure path; builtins.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION: rule narrows, no fail-closed default (the owner, chat 2026-10-25).

## Context / Handoff Summary
The verb refuses live, core, stdlib, installed and out-of-namespace names.
