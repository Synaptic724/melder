# Component Patch: Aether

## Before
- `Aether` already owned frame/root conduit registries and point lookups.
- Generic list/count/has/find discovery helpers were missing.

## After
- `Aether` owns the generic frame-scoped conduit-discovery methods:
  - list ids
  - list names
  - count
  - has by id
  - has by name
  - find id by name
  - get by id
  - get by name

## Contract
- These methods operate on one frame at a time.
- They return live conduit objects or snapshot scalar/query results.
- They do not widen ownership beyond existing frame/root conduit state.

## Validation Expectations
- Focused `Aether` unit tests should prove ids/names/count/lookup behavior.
