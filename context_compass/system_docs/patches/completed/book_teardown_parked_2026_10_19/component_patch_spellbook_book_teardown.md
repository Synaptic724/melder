# Component patch: Spellbook book teardown (book_teardown_parked_2026_10_19)

## Before
`Spellbook._cleanup_spells` walks `_spells` (index -> active Spell): it unregisters each index from
SpellSystemStates, sets `_spellbook_cleanup` and cleans the active Spell, then cleans the index. `_cleanup_components`
then clears `_inactive_spells` without cleaning one of them, and an index only parked versions hold is never reached.

## After
After the active loop, `_cleanup_spells` walks `_inactive_spells`: for each parked version it reads its index while
the version is live, notes the index when no active member holds it (`index not in _spells`), sets
`_spellbook_cleanup` and calls `Spell.cleanup()` - the local teardown the parked branch of `_dispose_spell` runs.
Then it cleans each noted parked-only index. Each step is best-effort and logged, as in the active loop. The
docstrings of `_cleanup_spells` (Contract, Threading) and `_cleanup_components` (Contract) say so.

## State and failure deltas
- Parked Spells and parked-only SpellIndexes of a torn-down Book read cleaned; `Spell.cleanup()` on them returns.
- No unregistration is added: a parked version is in no SpellSystemStates lineage, and its index left the frame
  registry at the root's teardown (`_unregister_conduit_spells_from_aether`, 0.2.8259).
- A failure cleaning one parked version or index is logged and the teardown goes on.

## Dependencies and ordering
- Runs inside `Spellbook.cleanup()` under the Book lock, after the active loop; the Crystallizer and Nexus steps
  before it are unchanged.

## Validation expectations
- tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py: six regression
  cases red on 0.2.8259 (a parked version on a shared index and alone in its own index, with the frame kept and
  collapsed; a version parked before conjure under a direct `Spellbook.cleanup()`; a parked managed version's
  Spell) and two controls; all green with the edit, the GIL off and on.
- Probe T1-T5 re-run: T2 and T3 fixed, T1, T4 and T5 unchanged. The whole tree in a mirror.
