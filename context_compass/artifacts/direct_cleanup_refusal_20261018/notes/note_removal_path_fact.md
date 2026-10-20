- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The removal path, read whole on 0.2.8255; melder_0's FACT note stands. `cleanup_and_remove_spell` resolves
    only an active spell (`_spells_by_id`), then under the Book lock unregisters its index from SpellSystemStates,
    emits the spell's and the index's removal to the record, and pops `_spells` and its address lookup; outside the
    lock it unregisters the RiskManager entry and the frame registry's index, drops the id maps, releases the frame
    claim by spell_id, and cleans the spell and the index - with no membership check. It has two callers:
    `_dispose_spell`, only for an active sole member (it refuses an active member of a multi-member index under the
    Book lock with `index.is_sole_member`), and `Spell.cleanup` through `_direct_removal_route` when
    `_spellbook_cleanup` is unset. Every internal `Spell.cleanup()` sets that flag first (Book teardown, this
    method's own tail, the parked disposal, Bind's retirement of an unpublished spell), so the missing check is
    reached only by a direct call from user code. `SpellIndex.is_sole_member` is O(1) under the index lock, and
    `_dispose_spell` already takes it under the Book lock (Book -> index). The tests that call the method today
    remove sole members (structural-snapshot `_event_remove`, per-frame custody, the restore tombstone, membership
    eviction). `Spell.cleanup`'s docstring lists the method's refusals, so spell.py takes a docstring line too.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-748
  - src/melder/aether/spellbook/spellbook.py:4427-4569
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spell.py:581-723
  - src/melder/aether/spellbook/spell.py:725-763
  - src/melder/aether/spellbook/bind/spell_index.py:421-451
  - src/melder/aether/spellbook/bind/bind.py:455-463
  - tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py:203-206
  - tests/integration/melder/crystallizer/test_crystallizer_membership_integration.py:154-175
  IMPACT: The fix is the story's: the multi-member check `_dispose_spell` makes, in `cleanup_and_remove_spell` before
    anything is unregistered; no lock added, no other caller affected. spell.py is not among the files melder_0
    released (M0-194), so it is claimed before its docstring line is written.
  NEXT: Write the patch (architecture and component, direct_cleanup_refusal_2026_10_18) and the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
