# Code-description patch: ReleaseManagedSpell (managed_spell_quantity_2026_10_15, S4)

Read with component_patch_release_managed_spell.md. Triggers: concurrency (lock-free reads of a published map, a
singleton built under a class lock) and idempotency (register, unregister, lease release).

## State
- Class: `_instance`, `_singleton_lock` (RLock), `_initialized`.
- Instance: `_lock` (a leaf, held only to publish), `_pools_by_class: Dict[type, Tuple[pool, ...]]`,
  `_registrations: Dict[int, Tuple[type, str]]`. Neither map is ever mutated after it is published: a writer builds
  new dicts and stores `_registrations` first, then `_pools_by_class`.

## Control flow
- `release(obj)`: `pools = self._pools_by_class.get(type(obj))`; if `pools` is a one-pool tuple and no filter was
  given -> `pools[0].put_back(obj)`. Otherwise `_resolve_pool(obj, pools, spell_id, conduit).put_back(obj)`.
- `_resolve_pool`: `check_cleaned()`; validate the filters; no pools -> not managed; filter by spell id, then by the
  holding root id read from `_registrations` (the conduit's `_root_conduit_id`, after its own cleaned check); several
  left -> keep the selected versions (`Spell._spell_index_unless_cleaned()` then
  `SpellIndex._is_selected_unless_cleaned`); one left -> return it; else the ambiguity or no-match error.
- `register(pool, root)`: `check_cleaned()`; `key = pool.managed_class`; under `_lock` re-check cleaned; read the
  previous registration; same key and root -> return; build the new maps (remove from the old key's tuple when the
  key changed, append to the new key's tuple, write the registration) and publish.
- `unregister(pool)`: cleaned -> return; under `_lock` re-check; no registration -> return; build the maps without
  the pool (drop a key whose tuple empties) and publish.
- `cleanup()`: once, under `_lock`: mark cleaned, publish empty `_registrations` and `_pools_by_class` (tombstones:
  a lock-free reader racing the cleanup sees an empty registry, never a missing field); keep `_lock` (a racing
  register or unregister takes it and sees `_cleaned`); then reset `_instance` and `_initialized` under
  `_singleton_lock`. It never cleans a pool: pools belong to their stores. (As built; the first draft deleted
  `_registrations`.)
- `_reset_singleton_for_tests()`: under `_singleton_lock`, clean the instance (an AttributeError from a half-built
  husk is ignored) and clear the bookkeeping in a `finally`.

## Edge and error semantics
- A release racing an unregister: the fast path may still reach the pool (it read the older map); the pool is
  either live (the object is pooled; the store's teardown then disposes it as idle) or torn down (put_back raises the
  torn-down RuntimeError). A release racing a register misses at worst: not managed or ambiguous, raised plainly.
- A release of an object whose pool moved roots (a transfer, S6): the class key is unchanged, so it routes to the
  same pool object in its new store.
- `id(pool)` keys are safe: a registered pool is held by the published tuple, so its id cannot be reused while it is
  registered; register and unregister update both maps under one lock hold.

## Invariants and idempotency
- The registry holds exactly the pools live stores hold (architecture invariant 7).
- register(p) twice == once; unregister(p) twice == once; lease.release() twice == once.
- No lock is taken on the fast path; `_lock` is never held with another lock and runs no user code.

## Non-goals
- No identity tracking of objects that are out; no automatic return; no release through Aether; the registry never
  disposes or cleans a pool.
