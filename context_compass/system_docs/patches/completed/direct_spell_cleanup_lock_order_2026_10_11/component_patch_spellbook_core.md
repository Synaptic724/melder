# Component patch: Spellbook Core - removal under a torn-down Book (direct_spell_cleanup_lock_order_2026_10_11)

## Before / after
- `cleanup_and_remove_spell`: checked `check_cleaned()` before taking the Book lock and read the id maps inside it. A
  call that passed the check and then waited for the lock while the Book was torn down read the deleted maps and
  failed with AttributeError; with a direct `Spell.cleanup()` holding the spell lock, that wait was the hang. After:
  inside the locked section, a cleaned Book returns when the Spell given has been cleaned (the teardown cleaned it),
  and otherwise raises through `check_cleaned()` as a call made after the teardown does. Docstring gains Threading
  and the cleaned-Book Raises entry.
- `cleanup_spell` docstring and the `_dispose_spell` comment: they described a direct `Spell.cleanup` as taking the
  spell lock, then the Book lock; they now say Book teardown and conjure stamping take Book -> spell and a direct
  cleanup no longer holds the spell lock when it reaches the Book.

## Interface deltas
None (no signature change; one new early return for a Spell already cleaned by a concurrent teardown).

## State / failure deltas
AttributeError in that window becomes a return or the documented cleaned-Book RuntimeError.

## Dependency / ordering
No lock added or nested; the re-check reads `_cleaned` (and the given Spell's `_cleaned`) under the Book lock the
section already holds.

## Validation expectations
Existing removal tests (signature release, crystallizer custody, fast-door staleness) unchanged; new tests for the
torn-down-Book window red on 0.2.8232 (AttributeError).
