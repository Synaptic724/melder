# Component patch: AethericFrame Services (ConduitCloud Registry) - list_conduits (2026-09-27)

## Before
- The Cloud answered names, ids, counts and membership over its NAMED directory but returned no conduit objects.

## After
- `ConduitCloud.list_conduits() -> Tuple[Conduit, ...]`: a snapshot of the directory's values taken under the
  Cloud's leaf lock; same membership as `list_conduit_ids()` / `list_conduit_names()` at that moment.

## Interface / state / failure deltas
- Additive method; RuntimeError after cleanup like every Cloud read. No new state; references are borrowed.

## Dependency and ordering
- Independent; lands first.

## Validation expectations
- Unit: named roots and named lessers listed by identity; anonymous and returned scopes absent; cleaned Cloud raises.
