# Component patch: Conduit Runtime and Spellbook Core - spell disposal (cross_object_lock_gaps_2026_10_11)

## Before / after
- `Conduit.cleanup_spell` read `spell.spell_index`, the index id, `is_sole_member` and the member set with no lock,
  then called `Spellbook.cleanup_spell`, which decided again under the Book lock; the destroy emission followed the
  first, unlocked read. A second call on a disposed spell raised AttributeError. After: it calls the internal
  `Spellbook._dispose_spell`, which decides under the Book lock and returns the id of the index it destroyed (None
  when the index survived); the Conduit emits the destroy for exactly that index, with the disposed spell as its one
  member (an index is destroyed only when the spell was its sole member).
- `Spellbook.cleanup_spell` (public, same signature and result) delegates to `_dispose_spell`. Ownership, activity
  and sole membership are read under the Book lock off the Book's id maps by identity (`_spells_by_id`,
  `_inactive_spells`); while the spell is in them its fields are live, because `Spell.cleanup` deletes them only after
  the Book has popped it. A spell no longer in the maps is classified outside the Book lock through
  `Spell._spell_index_unless_cleaned` (the spell's own lock, which `Spell.cleanup` takes before the Book lock):
  cleaned -> RuntimeError "cleanup_spell: spell <id> has already been disposed.", otherwise the existing
  "not owned by this spellbook" RuntimeError. The multi-member refusal and both disposal branches are unchanged.

## Interface deltas
New internal `Spellbook._dispose_spell(spell) -> Optional[str]`. Public signatures unchanged.

## State / failure deltas
New RuntimeError text for a spell already disposed (was AttributeError). Disposal itself is unchanged.

## Dependency / ordering
Book lock and spell lock are taken one after the other, never nested here; the destroy emission runs after both are
released, under the ward lock (ward patch).

## Validation expectations
Index-link destroy cascade unchanged (F9 suite); a second cleanup_spell raises the new RuntimeError; the
inactive-member and multi-member refusals unchanged.
