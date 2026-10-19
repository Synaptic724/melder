# Component patch: the minted index is registered as bind registers its index (minted_index_registry_2026_10_18)

## Before / after behavior
- Before: `_apply_remove_from_index` checks ownership, that the spell is parked, a member of `source_index` and not
  its only member; under the Book lock it creates `SpellIndex(initial_id=spell_id)` (as Bind creates an index),
  removes the spell from the source and repoints `spell.spell_index`; then it emits both index snapshots to the
  record. It registers nothing with the frame, so the frame's spell registry - which `find_index_for_spell` and
  `find_conduit_id_for_spell` walk, and with them every lookup, grant and transfer by spell_id and bind's collision
  guard (`Aether._check_for_spell`) - never lists the new index. The root's teardown
  (`_unregister_conduit_spells_from_aether`) unregisters `set(self._spells.keys())`, the indexes with an active
  version.
- After: right after the Book-locked move, with bind's guard (`self._conjured and self._conduit is not None`), the
  seam calls `Spellbook._aether._register_single_spell_index(self._get_required_conduit_surface()._id, new_index,
  self._aetheric_frame_name)` - the call a post-conjure `bind` makes for the index it creates. The record emission
  follows as before. `_unregister_conduit_spells_from_aether` adds to its set, under the Book lock, the index of
  every version in `_inactive_spells`, read through `Spell._spell_index_unless_cleaned` (a version cleaned meanwhile
  is skipped); an index shared with an active version is already in the set.

## Interface deltas
- None in signatures. Behaviour: the architecture patch's Interface deltas. Docstrings: the entry's Contract and the
  seam's summary say the fresh index is registered as `bind` registers the index it creates; the seam's Steps gain
  step 4 (the registration) and a Threading section; the teardown method gains Contract and Threading sections;
  `Spell._spell_index_unless_cleaned`'s Purpose lists the teardown among its readers.

## State and failure deltas
- New registry state: one frame-registry entry per minted index, under the Book's root conduit. It leaves when the
  index empties - `_destroy_spell_index` already calls `_remove_single_spell_index` with the spell's owner id, a
  no-op for a minted index until now - or at the root's teardown.
- `_remove_from_spell_index` is reached only through `Conduit.remove_from_spell_index`, so the Book is conjured and
  the guard holds; it keeps bind's shape for an unconjured Book, which registers its indexes at conjure
  (`_register_conduit_spells_in_aether`, the indexes with an active version - a minted index cannot exist before
  conjure).
- A notch inside the minted index finds it registered and registers no frame entry of its own, as today; the
  ownership transfer's flip moves the registered index to the target root (probe M7).
- Failure: a registration that raises (no such frame - the Book's frame outlives the Book) propagates after the
  move, and the Conduit ends the transaction as failed, as it does for any later step of the seam that raises.

## Dependency and ordering
- Callers: `Conduit.remove_from_spell_index` (the seam runs inside its `remove_from_index` transaction);
  `Conduit._cleanup_normal_conduit` step 4 (the teardown unregistration), before the Book's own cleanup.
- Locks: seam - the Book lock for the move, released, then the frame lock alone for the registration (bind's
  order, and `_destroy_spell_index`'s for the unregistration). Teardown - the Book lock, each parked spell's own lock
  inside it (Book -> spell, as Book teardown's `_cleanup_spells`), released, then the frame lock alone.

## Validation expectations
- Integration: with English active and French parked on its index under its own binding name, after
  `remove_from_spell_index(spell_id=French)` the frame finds French's index and its conduit,
  `get_spell_by_spell_id(French)` returns French and `get_conduit_by_spell_id(French)` the lender; after a notch to
  French in its index the same holds, `meld(spell_id=French)` builds French, a borrower's
  `add_spell_to_contract(spell_id=French)` is accepted and `transfer_spell_ownership` by spell_id moves French to
  the target root, which the frame then names.
- Integration: while French is in the minted index, another Book binding French (same class, address and
  existence) is refused "Spell ID collision detected" - a conjured Book's post-conjure bind and an unconjured Book's
  bind; under process-wide spell ids a Book of another frame too.
- Integration: after the lender root is torn down (another root keeps the frame alive) the frame holds no
  spell-registry or id-set entry for the lender and does not find French's index.
- Integration: after French moves back with `add_to_spell_index`, the frame no longer lists the minted index and
  finds French in English's index.
- Control: a version parked in English's index is found before and after the move of another version (M1).
- GIL off and on; probes M1-M7 re-run.
