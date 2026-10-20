- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The Book teardown, read whole on 0.2.8259. `Spellbook.cleanup` runs `_cleanup_components` under the Book
    lock: Bind's retirement, the risk-manager entry, the phase scheduler, the record's eviction of the whole Book,
    Nexus, then `_cleanup_spells`, which walks `_spells` (index -> active Spell) - unregister the index from
    SpellSystemStates, set `_spellbook_cleanup`, `Spell.cleanup()`, `SpellIndex.cleanup()` - and then
    `_inactive_spells` is cleared, never cleaned. A parked version's retirement is local, as the parked branch of
    `_dispose_spell` shows (`_spellbook_cleanup` set, then `Spell.cleanup()`): `Spell.cleanup` with that flag set skips
    `_direct_removal_route` and tears down only the spell's own fields (it never touches the index object), and
    `SpellIndex.cleanup` is idempotent and lock-guarded. A parked version holds no lineage registration (only active
    selections are registered), no resolution-map entry and no frame lookup of its own, and since 0.2.8259 the root's
    teardown unregisters its index from the frame before the Book is cleaned. So the fix is one loop after the
    active one: retire each parked version locally and clean each index no active member holds.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:370-397
  - src/melder/aether/spellbook/spellbook.py:405-555
  - src/melder/aether/spellbook/spellbook.py:557-600
  - src/melder/aether/spellbook/spellbook.py:4503-4651
  - src/melder/aether/spellbook/spellbook.py:2695-2736
  - src/melder/aether/spellbook/spell.py:614-762
  - src/melder/aether/spellbook/spell.py:764-801
  - src/melder/aether/spellbook/bind/spell_index.py:118-137
  IMPACT: The change is one module (spellbook.py), no new lock edge (spell and index locks under the Book lock, as the
    active loop takes them), no persisted or cached shape.
  NEXT: The patch docs, the red tests and a prototype in a /tmp mirror (MEASURE note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
