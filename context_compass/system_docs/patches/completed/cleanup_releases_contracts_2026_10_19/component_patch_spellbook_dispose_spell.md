# Component patch: Spellbook cleanup_spell and _dispose_spell (cleanup_releases_contracts_2026_10_19)

## Before
`Spellbook.cleanup_spell` is `self._dispose_spell(spell)`: no conduit is involved, so no contract hears of the
disposal - a parked version's index-link borrowers keep it (probe K4), and a sole member's borrowers keep the index
link to the destroyed index and an active entry of the cleaned version (K5). `_dispose_spell` decides under the Book
lock (owned, active, sole; the in-flight mark), refuses, then disposes inside a try whose finally clears the mark,
and returns the destroyed index's id or None.

## After
- `cleanup_spell`: on a conjured Book it calls its root conduit's `cleanup_spell(spell=spell)`, the one path that
  releases the contracts; before conjure no contract exists and it calls `_dispose_spell(spell)`.
- `_dispose_spell(spell, *, release_contracts: Optional[Callable[[str], None]] = None) -> Optional[str]`: after the
  decision and the refusals, first inside the try, it calls `release_contracts(spell_id)` when given, then invalidates
  and disposes as before. The return is unchanged. Docstrings of both say so.

## State and failure deltas
- A refusal raises before the hook, so no contract changes. A raise from the hook ends the call with nothing
  disposed; the finally clears the in-flight mark.

## Dependencies and ordering
- The hook runs with no Book lock held: the decision section is released before it, the disposal's sections are
  taken after it, so the ward -> contract -> borrower Book order it takes meets no Book lock of this Book.

## Validation expectations
- Unit tests for the hook (called between the decision and the disposal with the spell_id, not called on a refusal,
  the mark cleared when it raises) and integration tests for the direct door; probes K4, K5 re-run.
