- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: E1-E7 are in src as previewed and approved (apply_s9_refusal.py --apply: "all anchors found", "applied").
    E1: `cleanup_and_remove_spell`, in its first Book-locked section after the spell is resolved and before
    `unregister_index`, refuses an active member that is not its index's sole member (`SpellIndex.is_sole_member`),
    logging and raising RuntimeError "Spellbook cannot remove spell <id>: it is the active member of a multi-member
    index, and disposing it would leave the index's parked versions without an active one. Notch the index to one of
    them, dispose them with cleanup_spell, or move them out with remove_from_spell_index first."; E2-E4 its
    Contract, Raises and Threading; E5 `_dispose_spell`'s refusal reworded to the same tail after its "cleanup_spell:
    spell <id>" prefix (its log line keeps the short form); E6 `cleanup_spell`'s Contract names the three remedies;
    E7 `Spell.cleanup`'s Raises names the refusal. spellbook.py is 7802 lines (+31), spell.py 1972 (+4); no other src
    file changed, and `__version__` is still 0.2.8255 until the notch.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:602-775
  - src/melder/aether/spellbook/spellbook.py:4390-4455
  - src/melder/aether/spellbook/spellbook.py:4457-4599
  - src/melder/aether/spellbook/spell.py:581-727
  - src/melder/aether/spellbook/bind/spell_index.py:421-452
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/apply_s9_refusal_apply.txt:1-2
  IMPACT: The refusal is in place on all three doors; Book teardown (`_cleanup_spells`) and the parked disposal still
    set `_spellbook_cleanup` first and never reach the check.
  NEXT: The tests, the probe and the whole tree, GIL off and on (MEASURE note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
