# Component Patch: Rift Cleanup

## Before
- `Rift.cleanup()` clears room registries and drops `_configuration`, but it
  does not cleanup owned rooms or the owned configuration object first.

## After
- `Rift.cleanup()` cleans owned rooms deterministically.
- `Rift.cleanup()` cleans the owned configuration snapshot.
- Registry/data references are dropped only after owned cleanup runs.

## Validation Expectation
- Focused AR unit tests still pass.
