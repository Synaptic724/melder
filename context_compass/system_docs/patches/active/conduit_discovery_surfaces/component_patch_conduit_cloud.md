# Component Patch: ConduitCloud

## Before
- `ConduitCloud` only supported `get_conduit(name)` plus internal register and
  unregister.

## After
- `ConduitCloud` exposes the frame-local discovery mesh helpers:
  - list ids
  - list names
  - count
  - has by id
  - has by name
  - find id by name
  - get by id
  - get by name

## Contract
- `ConduitCloud` remains a discovery facade over frame-local named conduits.
- It does not become a cluster API.
- It does not own conduit lifecycle.

## Validation Expectations
- Focused `ConduitCloud` tests should prove mesh-discovery behavior and error
  paths.
