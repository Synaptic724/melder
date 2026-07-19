# Patch Architecture: Rift Cleanup Protocol Hardening

## Objective
Harden the Rift-side cleanup chain so top-level owners actually cleanup their
owned AR objects before dropping references.

## Non-Goals
- Lower Melder runtime cleanup redesign.
- Codegen execution behavior.
- Broad repo-wide cleanup refactor.

## Boundary
- In scope:
  - `Rift`
  - room stack immediately owned by `Rift`
  - touched AR managers only if code proves a teardown gap
- Out of scope:
  - `Conduit`, `Meld`, and lower runtime cleanup except as already used
    transitively by AR-owned objects

## Invariants
- Owned children cleanup before parent references are dropped.
- Cleanup remains idempotent.
- Touched cleanup methods use their instance lock.
- No `hasattr`/`getattr` probing in owned cleanup paths.

## Required Deltas
- `Rift.cleanup()` must cleanup owned spaces before clearing registries.
- `Rift.cleanup()` must cleanup the owned per-Rift configuration snapshot.
- Touched cleanup docstrings must describe the real ordering.
