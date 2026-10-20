# Code description patch: ManagedSpellQuantity._rebind_spell (managed_settings_spell_id_2026_10_17)

## Metadata
- Patch ID: managed_settings_spell_id_2026_10_17
- Component: Managed Spell Pools - `ManagedSpellQuantity._rebind_spell`, `Creations.ensure_managed_quantity`
- Status: archived at the story's closure (2026-10-18T11:45:58Z): landed at 0.2.8254 and promoted to the system
  documents and the graph
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T00:10:00Z
- Updated: 2026-10-18T11:45:58Z

## Trigger Justification
- Concurrency: the policy of a live pool changes while plans pop its idle deque, `reserve()` raises its count, queue
  waiters sleep on its condition and releases append - all without the store lock and mostly without the pool lock.

## Control-Flow Description (Pseudocode Level)
1. `Creations.ensure_managed_quantity(spell)`: under the store lock - check cleaned, read the pool under
   `spell.spell_id`, compose and store one when absent; release the store lock. When a pool was found, call
   `pool._rebind_spell(spell)`. Then `ReleaseManagedSpell().register(pool, root_conduit_id=...)` as today.
2. `_rebind_spell(spell)`: read the four settings from the Spell (no lock; the Spell is the caller's, under its lock).
3. Take the pool's condition (its lock). Re-point `_spell`, `_managed_class`, `_disposal_method_names`.
4. If mode, limit, timeout and reset names all equal the pool's: return (nothing else changes).
5. Otherwise set the four settings and `_notify_on_return`; size the base pool as `__init__` does; set `_target_idle`
   to the new baseline and `_decay_step` from it; `notify_all()` so each queue waiter re-checks under the new policy.
6. Release the lock. Nothing is destroyed here: surplus idle objects leave at later releases (outside every lock).

## Edge/Error and Rollback Semantics
- A plan's lock-free idle pop racing step 5 takes an idle object or not; either way the object was built for this
  spell_id and is valid under both policies.
- `reserve()` reads `_mode` once before its lock: a lease racing the rebind takes the old mode's path once, under the
  pool lock, against the limit in force when it takes the lock.
- `put_back` reads the reset names once: a release racing the rebind runs the old or the new names, never a mix.
- A queue waiter woken by step 5 re-checks: cleaned, a free place under the new limit, an idle object, its own
  deadline (taken at its call, from the old timeout) - then waits again or proceeds.
- A pool whose store was cleaned is never rebound: `ensure_managed_quantity` checks the store first, and a live store
  never holds a torn-down pool.
- No rollback: the rebind is the last step of owner stamping for a Spell that is already published; if stamping later
  fails, the next stamp of the same spell_id re-composes again.

## Invariants and Idempotency Expectations
- `count` stays the number of objects alive; a rebind never changes it.
- A rebind with equal settings is a pure re-point (idempotent; a transfer's restamp keeps the elastic band's state).
- The store lock is never held while the pool lock is taken; the pool lock is held only for field writes and the
  notify; no user code runs under it.

## Explicit Non-Goals
- Destroying idle objects above a smaller new limit at rebind time (disposal never runs under a Melder lock).
- Tracking which objects were built under which settings.

## Validation Focus Points
- The rebind ordering against the store lock (lock probe in the Creations unit test).
- Queue waiters after a mode or limit change; the count invariant under concurrent leases and releases.

## Context / Handoff Summary
- What changed: nothing yet (prototype only, outside the repo).
- Remaining unknowns: none.
- Next entrypoint: `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity._rebind_spell`.
