# Architecture patch: direct_spell_cleanup_lock_order_2026_10_11

## Objective
Remove the spell -> Book lock edge left by the lock_residuals lane (E; ticket Notes 4 and 9, owner decision Note 11).
A direct `Spell.cleanup()` of a live owned spell holds the spell lock across `Spellbook.cleanup_and_remove_spell`,
which takes the Book lock, frame locks (`_remove_spells_from_aether`) and the Nexus record removal. Book teardown
(`_cleanup_spells`, reached from root and frame teardown) and conjure's ownership stamping (`define_conduit_into_spells`
-> `Spell._add_owned_conduit`) take the spell lock under the Book lock, so when they meet, both threads hang. Ticket:
tickets/tasks/2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md.

## Non-goals
- No change to the meld path, to any public signature, or to what a direct cleanup removes: it still goes through
  `cleanup_and_remove_spell`.
- F2 (a direct removal of a multi-member index's active spell) and F3 (parked spells at Book teardown) stay out
  (owner, Note 11).
- A Book teardown that starts after `cleanup_and_remove_spell`'s first locked section is still not ordered against the
  rest of that removal (pre-existing; callers quiesce removals before tearing a Book down).
- Meld-time reruns (spell lock -> `_phase_run_lock`) are not audited here.

## Changed components
- Binding Pipeline (Spell): `Spell.cleanup` takes its decision under `_lock` through the new
  `_direct_removal_route()` and runs the Book removal after leaving it, under a per-spell `_removal_lock` (new last
  slot, None until the first direct cleanup, deleted at cleanup).
- Spellbook Core: `cleanup_and_remove_spell` re-checks the Book inside its locked section; `cleanup_spell` and
  `_dispose_spell` stop describing the spell -> Book order as current.

## Invariants
1. `Spell.cleanup()` never holds the spell lock while it waits for or holds the Book, frame or Nexus locks. Across the
   Book removal it holds only `_removal_lock`, which nothing else in Melder takes, so no lock-order cycle runs through
   it (a caller holding `with spell:` or another Melder lock around a direct cleanup brings the old order back).
2. Two direct cleanups of one spell run the Book removal once: the second waits on `_removal_lock`, finds `_cleaned`
   and returns, as it waited on the spell lock before.
3. A cleanup the Book drives (`_spellbook_cleanup` set) is unchanged: local teardown under `_lock`, no removal lock.
4. A `cleanup_and_remove_spell` call that waited for the Book lock while the Book was torn down returns when that
   teardown cleaned the Spell it was given, and otherwise raises the cleaned-Book RuntimeError, instead of failing
   with AttributeError on the deleted maps.

## Interface deltas
- Internal: slot `Spell._removal_lock: Optional[RLock]`, method `Spell._direct_removal_route()`.
- Behaviour: a direct `Spell.cleanup()` no longer hangs against a concurrent Book, root or frame teardown or a conjure
  of its Book. In the window that hung, the call now returns (the teardown cleaned the spell) or raises "Spellbook has
  already been cleaned.". No signature change, no record, cache or persisted format change.

## Migration order
Patch docs -> tests (red on 0.2.8232) -> src (scratch) -> full tree -> component docs -> architecture doc and indexes
-> graph -> notch 0.2.8233 and release note -> assets and llm_support last.

## Rollback
Revert spell.py and spellbook.py and remove the new test file.

## Coverage matrix
| invariant | test |
| --- | --- |
| 1 | a direct cleanup parked at its Book call holds no spell lock (red on 0.2.8232 by an `_is_owned()` probe, no hang) |
| 1, 4 | root teardown runs to the end while a direct cleanup waits for the Book lock; the direct call then returns and the spell is cleaned once |
| 1 | conjure's ownership stamping finishes while a direct cleanup waits; the spell is then removed from the conjured Book |
| 2 | two direct cleanups of one spell run the Book removal once and both return (preservation) |
| 3 | existing Spell unit tests (stub Book) and Book teardown tests, unchanged |
| 4 | `cleanup_and_remove_spell` waiting while the Book is torn down: returns for the Spell the teardown cleaned, raises the cleaned-Book error for an id (both AttributeError on 0.2.8232) |
