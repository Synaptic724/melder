# Component Patch: Room Type And Configuration

## Components
- `RiftSpaceType`
- `RiftConfiguration`
- `Nexus`

## Before
- AR room type uses `dynamic`.
- Target-frame gating says "dynamic AR" requires AI-native + dynamic system state.
- Config/tests/docs speak in terms of `dynamic` room type.

## After
- AR room type uses `codegen`.
- Target-frame gating continues to enforce the same lower-frame requirements,
  but the room-facing language becomes "codegen room" instead of "dynamic room".
- Legacy AR input `"dynamic"` remains accepted and maps to the `codegen` room.

## Key Constraint
- Do not rename lower `SystemState.dynamic`.

## Validation Expectation
- Rift configuration can still be built from legacy `"dynamic"` AR input.
- New canonical AR room type/value is `codegen`.
