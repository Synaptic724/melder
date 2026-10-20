# Component patch: ConduitWard _emit_spell_disposed (cleanup_releases_contracts_2026_10_19)

## Before
A version's contract records are removed per contract by `_uncontract_member_spell` (the lender-side Detail, then the
borrower's entry and borrowed id through `Spellbook._remove_contracted_spell`), called by the index emissions only:
`_emit_index_member_removed` (the contracts that link the index, for `remove_from_spell_index`) and
`_emit_index_destroy`. No emission covers a disposed version on every contract, and none touches a version grant.

## After
`_emit_spell_disposed(spell_id)`: under the ward lock, for every contract whose owner side holds a Detail for the
version - an index link's member Detail or a version grant - `_uncontract_member_spell(contract, self, spell_id)`;
then the contract record of each contract it changed, after the lock, as `_emit_index_destroy` does. A contract that
holds no Detail for the version is untouched, and a contract is never severed (an empty contract is a live link).
`_emit_index_destroy`'s docstring: `member_ids` may be empty - cleanup_spell's version left every contract first.

## State and failure deltas
- The borrower's entry goes, active or parked; an active one marks its consumers (rule 2).
- A borrower Book holding no entry under a lender-side Detail raises from `_remove_contracted_spell`, as the index
  emissions do; the cleanup then stops before the disposal.

## Dependencies and ordering
- Lock order ward -> contract -> borrower Book, the index emissions' order; called with no Book lock held.

## Validation expectations
- Covered through `cleanup_spell` (component patch Conduit); probes K1-K5, K7.
