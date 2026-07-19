# Conduit Discovery Surfaces Architecture Patch

## Objective
Add one coherent conduit-discovery surface across backend runtime ownership,
dynamic discovery mesh access, and agent-facing access.

## Non-Goals
- No cluster redesign.
- No spell or meld redesign.
- No capability-handle redesign.
- No viewer redesign.

## Changed Components
- `Aether`
- `ConduitCloud`
- `Rift`
- `CommandSystem`

## Boundary Contract
- `Aether` owns the generic frame-scoped conduit-discovery logic.
- `ConduitCloud` facades that logic as the frame-local discovery mesh.
- `Rift` facades the same logic for agent/runtime use.
- `CommandSystem` exposes query helpers and conduit getters over the same
  owned discovery truth.
- `Conduit` does not receive these cloud/discovery methods.

## Interface Deltas
- Add generic conduit-discovery methods to `Aether`.
- Add matching discovery helpers to `ConduitCloud`.
- Add matching discovery helpers to `Rift`.
- Add command query helpers plus shorter conduit getter names
  (`get_conduit_by_id`, `get_conduit_by_name`) to `CommandSystem`.

## Invariants
- `Aether` remains the owner of frame/root conduit topology.
- `ConduitCloud` remains the discovery mesh, not the owner of runtime topology.
- `Rift` and `CommandSystem` remain facades, not owners.

## Migration Order
1. Add backend methods to `Aether`.
2. Add cloud facade methods to `ConduitCloud`.
3. Add Rift facade methods.
4. Add command query helpers and renamed conduit getter names.
5. Update focused tests.

## Rollback
If the new surface creates drift, remove facade methods from `Rift` and
`CommandSystem` first and keep `Aether` plus `ConduitCloud` as the stable base.
