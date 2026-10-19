# Architecture patch: minted_index_registry_2026_10_18

## Objective and non-goals
- Objective: the index `remove_from_spell_index` creates is known to its frame like every other index - registered
  in the frame's spell registry the way a post-conjure `bind` registers the index it creates (the owner's word,
  2026-10-18: "it should properly follow the general spell index creation and registry binding processes the same
  way it does during bind"). A version separated into an index of its own, parked or later notched active there, is
  then found by spell_id (the Conduit lookups, a grant, an ownership transfer), counted by bind's collision guard and
  read right by MutationResearch residency, and a root's teardown leaves no registry entry for it. Today (probes
  M2-M7 and V2-V3 on 0.2.8256): `get_spell_by_spell_id` and `get_conduit_by_spell_id` raise "Spell version <id> not
  found in any conduit.", a grant and a transfer by spell_id raise the same, another Book of the frame - or of
  another frame under process-wide spell ids - binds its spell_id, and `residency_view` reads it `declared_only`.
- Non-goals: a new index state (an index whose version is parked is the agent's inventory, active when the agent
  notches it - the owner, 2026-10-18; the S10 ruling stands, the minted index selects its parked member); the
  binding signature an active version in a minted index takes
  (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); the parked versions Book teardown leaves uncleaned
  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned); a restore or graft of a separated version
  (STORY-2026-10-17-restore_drops_separated_parked_version); index-link borrowers (a minted index has none until a
  link is made to it).

## Changed components
- Spellbook, `remove_from_spell_index`'s seam (`_apply_remove_from_index`): registers the index it creates with the
  frame, with bind's guard (`self._conjured and self._conduit is not None`) and bind's call
  (`Aether._register_single_spell_index` under the Book's root conduit), after the Book-locked move. The index is
  already created as Bind creates one (`SpellIndex(initial_id=...)`).
- Spellbook, the root's teardown unregistration (`_unregister_conduit_spells_from_aether`, called only by
  `Conduit._cleanup_normal_conduit`): also unregisters the index of every parked version, so an index holding only
  parked versions leaves the registry with the root's other indexes.
- MutationResearch, `residency_view` (`_locate_live_membership`): a version is `active` when its index selects it and
  the frame's lineage registry tracks it as that index's current version; the minted index selects its parked member
  and no lineage tracks that member until a notch registers it, so it reads `parked`.
- Docstrings: `_remove_from_spell_index`, `_apply_remove_from_index`, `_unregister_conduit_spells_from_aether`,
  `residency_view`, `_locate_live_membership`, and the readers `Spell._spell_index_unless_cleaned` lists.

## Invariants
- Every index a conjured Book owns is in the frame's spell registry under the Book's root conduit from the moment it
  is created (`bind`) or minted (`remove_from_spell_index`) until it is destroyed (`_destroy_spell_index`, when its
  last member leaves) or its root is torn down. A frame lookup by spell_id finds every version its Book owns.
- A root's teardown leaves no spell-registry entry for the root: the frame drops a conduit's entry once its set is
  empty (`AethericFrame.unregister_conduit_spells`), and the teardown unregisters every index the root registered.
- `residency_view` calls a version active exactly when its Book holds it active: its index selects it and its
  lineage is registered with it as current (`bind` and a notch register one; parking never does).
- No new lock or lock-order edge: the registration takes the frame lock alone, after the Book lock is released, as
  bind's does; the teardown reads each parked version's index under the Book lock through the spell's own lock
  (Book -> spell, the order Book teardown takes) and unregisters with the frame lock alone after it; residency takes
  the lineage registry's lock, then the lineage state's, each alone.

## Interface deltas
- No signature changes. Behaviour, fixed: after `remove_from_spell_index(spell_id=X)`,
  `Conduit.get_spell_by_spell_id(X)` returns X and `get_conduit_by_spell_id(X)` the owning root - parked, and after
  a notch makes X active there; `add_spell_to_contract(spell_id=X)` and `transfer_spell_ownership` by spell_id
  proceed; `residency_view(X)` reads `parked`, then `active` after the notch.
- Behaviour, the existing refusal now reached: while X is in a minted index, another Book binding X's spell_id
  raises the existing RuntimeError "Spell ID collision detected. ..." (it was accepted, so two Books held one
  spell_id), in its frame and, under process-wide spell ids, in another frame.

## Migration order
1. These patch docs, linked from the story; the owner's word (2026-10-18). 2. Red tests (new files; no held file).
3. spellbook.py and spell.py back from melder_0 after S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code
land; mutation_research.py claimed (M1-39). 4. The edits A-D. 5. The tests green with the GIL off and on; probes
M1-M7 and V1-V4 re-run; the whole tree in a mirror. 6. System documents with their indexes, the graph, the release
note; the next free notch. 7. Closure; the rebuild last; the files handed back.

## Rollback
- Revert the edits: the minted index leaves the registry again and the defect returns. Nothing persisted, cached or
  emitted changes (the spell registry is in-memory frame state, and the record already takes both index snapshots
  at the move), so no cache generation or record version moves either way.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md |
