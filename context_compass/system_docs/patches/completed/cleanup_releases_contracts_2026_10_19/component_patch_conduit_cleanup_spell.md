# Component patch: Conduit cleanup_spell (cleanup_releases_contracts_2026_10_19)

## Before
`Conduit.cleanup_spell` calls `self._spellbook._dispose_spell(spell)` and, only when the Book reports a destroyed
index, `self._conduit_ward._emit_index_destroy(index_id, (spell_id,))` after the disposal. A version whose index
survives tells no contract (probe K1), a version grant is never touched (K2, K3), and the emission uses the calling
conduit's own ward, so a lesser conduit's call reaches no contract (K7).

## After
`cleanup_spell` takes the ward of the Book's root conduit (`self._spellbook._conduit._conduit_ward`; a lesser's ward
holds no contracts) and hands its `_emit_spell_disposed` to the Book as `release_contracts`: the Book calls it after
its decision and before its disposal, so every contract drops the version first. When the Book reports a destroyed
index, `ward._emit_index_destroy(index_id, ())` drops the index links after the disposal - no member ids, the
version having left every contract already. The docstring (Contract, Raises, Threading) says so.

## State and failure deltas
- Borrowers drop the version before it is disposed; a refused call touches no contract.
- A raise from the release propagates before anything is disposed (the Book's in-flight mark is cleared), so a retry
  repeats the release and the disposal.

## Dependencies and ordering
- Needs the Spellbook's `release_contracts` hook and the ward's `_emit_spell_disposed` (their patches).

## Validation expectations
- Integration tests for an index link's parked member, a version grant parked and active, a lesser conduit's call,
  the refusal touching nothing and the order (the borrower drops a live version); probes K1-K3, K7, U2, U3 re-run.
