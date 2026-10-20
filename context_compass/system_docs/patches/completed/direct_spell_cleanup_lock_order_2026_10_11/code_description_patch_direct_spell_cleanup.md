# Code description patch: direct Spell.cleanup (direct_spell_cleanup_lock_order_2026_10_11)

## Control flow
1. `Spell.cleanup()`: `if self._cleaned: return`. `route = self._direct_removal_route()`.
2. `_direct_removal_route()`: `with self._lock:` return None if `_cleaned` or `_spellbook_cleanup`; else
   `removal_lock = self._removal_lock`, create an RLock into the slot when None; return `(self._spellbook,
   removal_lock)`.
3. With a route: `with removal_lock:` if not `_cleaned`: `spellbook.cleanup_and_remove_spell(self)`; then return.
4. Without one: `with self._lock:` return if `_cleaned`; the unchanged teardown, plus `del self._removal_lock`.
5. `Spellbook.cleanup_and_remove_spell(spell)`: `check_cleaned()`; `with self._lock:` if `_cleaned`: return when
   `spell` is a Spell and `spell._cleaned`, else `check_cleaned()` (raises); then the unchanged resolution,
   unregistration, emits and pops; the rest unchanged.

## Edge semantics
- A second direct call while the first removal runs waits on the removal lock and returns; one arriving after
  `_cleaned` flips returns at once (as before, through the lock-free check).
- A direct call that finds `_spellbook_cleanup` already set (a teardown on another thread is about to clean the spell)
  runs the local teardown itself; the teardown's own call then returns. The Book has already dropped the spell.
- A Book teardown racing a direct call: the call returns if the teardown cleaned the spell before it took the removal
  lock or while it waited for the Book lock; raises the cleaned-Book RuntimeError if it reached `check_cleaned()`
  after the teardown began; never hangs.
- A failed removal leaves `_cleaned` False and releases the removal lock, so a retry runs.

## Invariants / idempotency
`cleanup()` stays idempotent. `_removal_lock` is read and created only under `_lock`, held only by `cleanup()`, and
deleted with the other fields at teardown (a waiter holds its own reference).

## Non-goals
No change to Book teardown, to `_dispose_spell`'s disposal, to the parked-spell or multi-member behaviour (F2, F3), to
meld, or to any cache or record format.
