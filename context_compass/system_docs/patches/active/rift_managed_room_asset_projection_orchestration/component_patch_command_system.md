# Component Patch: CommandSystem Rift-Owned Projection Access

## Before
- CommandSystem reads command projection truth from `space`.

## After
- CommandSystem reads command projection truth from `Rift`.
- Space remains only the host for room-local memory/gate/workstation assets.

## Validation Expectation
- Focused command-system tests prove direct command lookup still works through
  Rift-owned command projection state.
