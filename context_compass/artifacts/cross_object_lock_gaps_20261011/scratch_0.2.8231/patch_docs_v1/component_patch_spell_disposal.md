# Component patch: Conduit Runtime and Spellbook Core - spell disposal (cross_object_lock_gaps_2026_10_11)

## Before / after
- Conduit.cleanup_spell read spell.spell_index, the index id, is_sole_member and the member set with no lock, then
  called Spellbook.cleanup_spell, which decided again under the Book lock; the destroy emission followed the first,
  unlocked read. A second call on a disposed spell raised AttributeError. After: Conduit.cleanup_spell calls the
  internal Spellbook._dispose_spell, which decides under the Book lock and returns the id of the index it destroyed
  (None when the index survived); the Conduit emits the destroy for exactly that index, with the disposed spell as
  its one member.
- Spellbook.cleanup_spell (public, unchanged signature and result) delegates to _dispose_spell. Ownership is read off
  the Book's id maps under the Book lock; while the spell is in them its fields are live (Spell.cleanup deletes them
  only after the Book has popped it). A spell no longer in the maps is classified outside the Book lock through
  Spell._spell_index_unless_cleaned (the spell's own lock; Spell.cleanup takes it before the Book lock):
  cleaned -> RuntimeError "cleanup_spell: spell <id> has already been disposed.", otherwise the existing
  "is not owned by this spellbook" RuntimeError.

## State / failure deltas
New RuntimeError text for a spell already disposed (was AttributeError). Disposal itself is unchanged.

## Validation expectations
Index-link destroy cascade unchanged (F9 suite); double cleanup raises the new RuntimeError; the inactive-member
and multi-member refusals unchanged.
