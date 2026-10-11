# Component patch: Binding Pipeline - Spell.cleanup lock order (direct_spell_cleanup_lock_order_2026_10_11)

## Before / after
- Before: `Spell.cleanup()` took `_lock`, and when its Spellbook was not driving the cleanup (a direct call) it called
  `self._spellbook.cleanup_and_remove_spell(self)` while still holding `_lock`, so the spell lock was held across the
  Book lock, frame locks and the Nexus record removal.
- After: `cleanup()` calls `_direct_removal_route()`, which under `_lock` returns None for a cleaned spell or a
  Book-driven cleanup, and otherwise the owning Spellbook and this spell's removal lock (created there on first use).
  With a route, `cleanup()` takes the removal lock with `_lock` released, re-checks `_cleaned` and calls
  `cleanup_and_remove_spell`; the Book's call back (with `_spellbook_cleanup` set) runs the local teardown. Without a
  route, the local teardown runs under `_lock` exactly as before; it now also deletes `_removal_lock`.
- `__init__` sets `_removal_lock = None`; the slot is appended after `implemented_protocols`, so the hot fast-door
  slot offsets do not move.

## Interface deltas
Internal only: `_removal_lock` slot and `_direct_removal_route()`. `cleanup()` keeps its signature and return.

## State / failure deltas
No hang against Book, root or frame teardown or a conjure of the Book. A direct call that races its Book's teardown
returns when the teardown cleaned the spell first, or raises the cleaned-Book RuntimeError from the Book. A direct
call on a parked spell still raises "Spellbook could not resolve the requested local spell." (unchanged).

## Dependency / ordering
New order for a direct cleanup: `_removal_lock` -> Book lock -> frame / Nexus -> spell lock (the Book's call back).
Nothing in Melder takes `_removal_lock` under another lock.

## Validation expectations
Spell unit tests that drive cleanup through a stub Book pass unchanged; new component tests force the teardown and
conjure interleavings and two direct cleanups; red on 0.2.8232 where the lock order is the defect.
