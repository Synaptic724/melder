# Architecture Patch: Room Command Surface Ownership Refactor

## Objective
Refactor room command ownership so the shared `CommandSystem` owns only shared
infrastructure and truly shared public helpers, while room-specific public
commands move into the room-specific command classes.

## Non-Goals
- No codegen ownership changes in this patch.
- No lower Melder conduit/spell API redesign.
- No viewer/workstation ownership changes.

## Changed Components
- `CommandSystem`
- `CapabilityCommandSystem`
- `StaticCommandSystem`
- directly affected command-system interfaces
- focused room-command tests

## Invariants
- Capability keeps the broad manual-runtime command surface.
- Static keeps live-only/static-safe spell access and status behavior.
- Static no longer relies on inherited topology/activation methods that it then
  denies at runtime.
- Command discovery output must match actual room-owned public surfaces.

## Interface Deltas
- Shared base command discovery shrinks.
- Capability command discovery expands to own topology mutation and direct
  activation/reuse helpers.
- Static discovery reflects its true room-owned surface, including static-only
  status helpers.

## Migration Order
1. Define the placement matrix.
2. Move topology mutation and activation methods out of the base.
3. Add moved methods to capability.
4. Remove now-obsolete static deny-list reliance for moved methods.
5. Align interfaces and tests.

## Rollback
If the room-specific move breaks typing or discovery semantics, restore the
previous placement and keep the notes/task state explicit about the blocker.
