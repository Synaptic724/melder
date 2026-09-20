# Creations and SpellSpace purge contract

## Purpose and boundary
Creations owns one scoped live/disposal registry. SpellSpace owns its local store and Meld door.

## Before and after
Before: whole-store clear and transfer extraction. After: additionally retire one Spell's stored
singleton or many bucket through native purge; SpellSpace exposes that operation for its own store.

## Interface deltas
Creations.purge(spell: Spell) -> int, receiving Meld's normal internal discovery result.
Scope authority is already checked by Meld, never by this store.
SpellSpace.purge mirrors meld selectors without overrides. Wrong lifetime/scope raises RuntimeError.
Empty entry returns zero. Disposal failure raises ExceptionGroup after all selected objects are tried.

## State and lifecycle
Pop the selected key from both maps. Retain detached object references until locks are released,
then dispose newest-first using established method lists. Preserve unrelated keys, ids, contexts,
thread stacks and pool state. Never infer many from the application's return type.

## Failures
Removed entries remain removed on disposal failure. A concurrent replacement must never be removed
after detachment. Supplied objects remain referenced by the Spell under the unchanged binding model.

## Dependencies and ordering
Use Existence and typing-only concrete Spell. For unique take Spell._lock before Creations._lock.
All other modes take only Creations._lock. Disposal runs after both are released.

## Validation
Ordered cleanup, counted removals, idempotence, unrelated slots, lock selection/order, callbacks
outside locks, replacement retention, and direct/nested/shared SpellSpace calls.

## Unknowns
None for this bounded contract. Pool misuse and concurrent terminal destruction retain their
existing caller-lifecycle constraints.
