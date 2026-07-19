# Patch Architecture: Rename AR Dynamic Room To Codegen

## Objective
Rename the AR room/type layer from `dynamic` to `codegen` while preserving the
lower Melder runtime convention that still uses `SystemState.dynamic`.

## Non-Goals
- Rename lower `SystemState.dynamic`.
- Rename conduit dynamic-environment semantics.
- Change lower runtime policy about when dynamic substrate behavior is allowed.

## Boundary
- In scope:
  - `RiftSpaceType`
  - AR room classes and room-specific command classes
  - AR-facing interfaces
  - Nexus/Rift room creation and target-frame gating language
  - AR docs/tests
  - compatibility handling for legacy AR `dynamic` inputs
- Out of scope:
  - lower Conduit/Aether/Spellbook dynamic mode naming
  - mutationresearch semantics

## Invariants
- Target-frame codegen room still requires:
  - `rift_enabled=True`
  - `ai_native_enabled=True`
  - `system_state == dynamic`
- `capability` remains the broad manual non-codegen room.
- Lower Melder `dynamic` continues to mean substrate/runtime posture.

## Required Deltas
- AR room/type names become `codegen`.
- Legacy AR config input `"dynamic"` must still normalize to the new codegen
  room type during transition.
- Source/docs/tests must stop implying that the AR room name and the lower
  runtime posture name are the same concept.

## Migration Order
1. Rename AR enum/member and room classes.
2. Update Nexus/Rift selection logic and room construction.
3. Update interfaces.
4. Update docs/tests.
5. Preserve AR config compatibility for legacy `"dynamic"` input.

## Rollback
- Revert AR room/type names to `dynamic`.
- Keep lower runtime posture untouched throughout either direction.
