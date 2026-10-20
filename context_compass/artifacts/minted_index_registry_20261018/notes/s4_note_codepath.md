- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The minting seam, the frame's spell registry and every reader of it, read whole on 0.2.8256. The registry
    maps a conduit id to a set of SpellIndex (`_spell_registry`) beside the Book's live `_spell_ids`
    (`_selected_spell_registry`). Conjure registers the indexes that hold an active spell (`set(_spells.keys())`), a
    post-conjure `bind` its new index (`_register_single_spell_index`: the frame lock alone, after the Book lock),
    and `_destroy_spell_index` unregisters an emptied index under the spell's owner id; `_apply_remove_from_index`
    mints `SpellIndex(initial_id=spell_id)` and registers nothing, so every walk of `_spell_registry` misses it -
    `find_index_for_spell`, `find_conduit_id_for_spell` (so `Aether._get_conduit_by_spell_id`, the spell_id lookups,
    a grant and a transfer by spell_id), `_find_index_for_spell_unless_cleaned`, MutationResearch's
    `_locate_live_membership`, graft's resident check and the transfer's `_spell_in_registry`. Three readers shape
    the fix. (1) `Aether._check_for_spell`, bind's collision guard, asks `has_spell` (the live `_spell_ids`, which
    hold French) and then returns `find_index_for_spell` - None for French - so another Book of the frame, or of
    another frame under process-wide ids, may bind French's spell_id while it lives in the minted index (to be
    probed). (2) Root teardown unregisters only `set(_spells.keys())`, before the Book is cleaned
    (`_cleanup_normal_conduit` step 4), and the frame drops a conduit's entry only when its set empties, so a minted
    index registered while its version stays parked would outlive the root in the registry: the fix must unregister
    it at teardown too. (3) `_locate_live_membership` calls a version active when its index selects it
    (`index.selected_spell_id == spell_id`), and the minted index selects its parked member (S10, withdrawn by the
    owner: activation takes a notch), so once registered, a parked French there would read `active`, not `parked`.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4303-4388
  - src/melder/aether/spellbook/spellbook.py:4224-4269
  - src/melder/aether/spellbook/spellbook.py:4128-4222
  - src/melder/aether/spellbook/spellbook.py:5919-5924
  - src/melder/aether/spellbook/spellbook.py:2672-2716
  - src/melder/aether/aether.py:2505-2544
  - src/melder/aether/aether.py:2550-2624
  - src/melder/aether/aether.py:2744-2800
  - src/melder/aether/aetheric_frame/aetheric_frame.py:873-976
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1010-1038
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1187-1307
  - src/melder/aether/conduit/conduit.py:1034-1178
  - src/melder/mutation_research/mutation_research.py:1374-1525
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:332-373
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1173-1200
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1429-1487
  IMPACT: The fix is three edits, not one: register the minted index at the seam, unregister every index the root
    registered at its teardown, and let residency call a version active only when its Book holds it active. The
    third reaches mutation_research.py, outside the story's EXECUTION_BOUNDARY, so it goes to the owner.
  NEXT: Prove (1)-(3) in a /tmp mirror: the duplicate binds on the tree, then the seam's registration alone (teardown
    and V2), then all three edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
