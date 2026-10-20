# Component patch: the removal path refuses a member with parked siblings (direct_cleanup_refusal_2026_10_18)

## Before / after behavior
- Before: `cleanup_and_remove_spell` resolves the active spell and, under the Book lock, unregisters its index,
  emits the spell's and the index's removal to the record and pops its maps; then it drops the RiskManager entry,
  the frame registry's index, the id maps and the frame claim, and cleans the spell and the index - whatever other
  members the index holds. A direct `Spell.cleanup()` routes there (`_direct_removal_route`).
- After: in the same first Book-locked section, after the spell is resolved and before `unregister_index`, an
  index that holds members besides this spell (`SpellIndex.is_sole_member` False) refuses the call: the error is
  logged and raised, and nothing has changed. A sole member is removed as before.

## Interface deltas
- None in signatures. Behaviour: RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a
  multi-member index, and disposing it would leave the index's parked versions without an active one. Notch the
  index to one of them, dispose them with cleanup_spell, or move them out with remove_from_spell_index first." from
  both public doors. `_dispose_spell` words `cleanup_spell`'s refusal the same way after its "cleanup_spell: spell
  <id>" prefix. `cleanup_and_remove_spell`'s and `Spell.cleanup`'s docstrings name it under Raises, the method's
  Contract says the sole-member rule, and `cleanup_spell`'s Contract names the remedies.

## State and failure deltas
- No new state. The refusal happens before the first mutation, so a refused call leaves the index, both versions,
  SpellSystemStates, the record, the frame registry and claim, Nexus and any borrower as they were; the spell stays
  live and can be notched away from and removed afterwards.
- `cleanup_spell` decides in one Book-locked section (`_dispose_spell`) and removes an active sole member in
  another (this method), and no transaction admits it, so a version staged onto the index in between used to be
  orphaned by the removal. It now meets the refusal: `cleanup_spell` raises it, having invalidated the spell
  first (`invalidate_spell`: its creation context cleared, resolution required again, its index marked
  structurally changed), and nothing is removed. Not covered by a test (a thread interleaving).
- Not changed (pre-existing): a staging or index move onto the index that starts after this method's first locked
  section is not ordered against the rest of the removal - `_apply_add_to_index` checks the target's owner by its
  selected spell_id, which this method drops from the id maps only later, and a direct removal runs no
  transaction - so callers still quiesce moves before a direct removal, as they quiesce Book teardown.

## Dependency and ordering
- Callers: `_dispose_spell` (it decides on an active sole member; a version staged after that decision meets the
  refusal, above) and `Spell.cleanup` when `_spellbook_cleanup` is unset (user code). Every internal
  `Spell.cleanup()` sets that flag first.
- Lock order: Book -> index, as `_dispose_spell`; the check calls no other object.

## Validation expectations
- Integration, probe D2 and D3 as tests: with English active and French parked on its index, `English.cleanup()`
  and `cleanup_and_remove_spell(English)` (by Spell and by spell_id) raise the RuntimeError; afterwards the index is
  live and selects English, English is active and uncleaned, French parked and uncleaned, the frame finds both, the
  borrower's copies are as before and English melds.
- Integration: after the refusal each remedy works - notch to French, then `cleanup_spell(English)` (a parked
  version; a direct `English.cleanup()` refuses a parked version) leaves French active alone on the live index;
  `cleanup_spell(French)`, then `English.cleanup()` removes English with its index; `remove_from_spell_index(French)`,
  then `English.cleanup()` removes English with its index and leaves French parked, alone in a fresh index.
- Integration: `cleanup_spell(English)` raises its refusal naming the three remedies, and changes nothing.
- Integration, control: English alone on its index is removed by either door, its index cleaned and unregistered.
- GIL off and on; the probe re-run shows D2 and D3 refused, as D1.
