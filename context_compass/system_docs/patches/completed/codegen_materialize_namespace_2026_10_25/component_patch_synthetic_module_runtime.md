# component_patch_synthetic_module_runtime

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
- SyntheticModule Runtime: publication and parent attachment become reversible for what they displace.

## Before/After Behavior Summary
- Before: publish assigned `sys.modules[name]` and the parent attribute unconditionally; cleanup deleted its own
  entry, so a displaced original was lost.
- After: publish records a displaced non-synthetic module, attach a displaced non-synthetic parent attribute;
  unpublish, detach and cleanup restore them when this object still holds the slot.

## Interface Deltas
- None public; two private fields with a module-level sentinel.

## State and Lifecycle Deltas
- Records are cleared on restore; cleanup deletes them.

## Failure Mode Deltas
- A displaced SyntheticModule is not restored (it may be cleaned); the slot is removed as before.

## Dependency and Ordering Constraints
- Restore, rebuild and graft lanes never displace a real module (rebuild skips live files, restore skips loaded
  names), so their behaviour is unchanged.

## Validation Expectations
- Unit: publish/cleanup and unpublish restore a module; detach restores an attribute; a synthetic is not restored.

## Unknowns and Open Decisions
- UNKNOWN: none.

## Context / Handoff Summary
Whatever a SyntheticModule displaces, it gives back.
