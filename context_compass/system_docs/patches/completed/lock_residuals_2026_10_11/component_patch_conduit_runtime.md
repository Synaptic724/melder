# Component patch: Conduit Runtime - contracted lookup, inspection, disposal docs (lock_residuals_2026_10_11)

## Before / after
- `find_contracted_spell`: took the conduit lock and walked `spellbook._contracted_spells.keys()` live, while a link
  or sever started by a peer writes those keys under the Book lock holding the peer's conduit lock, not this one;
  RuntimeError "dictionary changed size during iteration" / "dictionary keys changed during iteration" (Note 2).
  After: `check_cleaned()`, then `list(spellbook._contracted_spells)` in one call and the keyed per-peer lookup
  (`_find_contracted_spell_by_id`, lock-free) with no lock held.
- `inspect_spell`: held the conduit lock across `Spellbook.inspect_spell`, which reaches frame locks; frame teardown
  takes the frame lock, then each conduit's lock (`permanent_cleanup`). After: no conduit lock.
- `cleanup_spell`: unchanged code; the docstring names the new refusal and the Book-locked mark.

## Interface deltas
None (signatures and results unchanged).

## State / failure deltas
`find_contracted_spell` no longer raises RuntimeError under concurrent links and severs. A teardown of this conduit
racing either lookup is unsupported, as for every Conduit lookup (it may raise AttributeError).

## Dependency / ordering
Removes conduit -> spell (parked-copy branch) and conduit -> SpellIndex (fallback probe) from find_contracted_spell
and conduit -> Book -> frame from inspect_spell. Adds nothing.

## Validation expectations
Existing contracted-lookup and inspection tests unchanged; the new interleaving test for find_contracted_spell and the
lock-discipline test for inspect_spell pass on 0.2.8232 and fail on 0.2.8231.
