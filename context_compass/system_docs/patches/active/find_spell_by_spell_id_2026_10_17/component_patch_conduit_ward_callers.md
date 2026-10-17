# Component patch: ConduitWard callers of the spell_id lookup (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- `_check_spell_id_and_spell` (the grant and ungrant check): the call is renamed `get_spell_by_spell_id`, nothing
  else changes. A parked spell_id now resolves to the parked spell, its own spell_id matches, and the grant or
  ungrant proceeds - a grant parks the copy on the borrower (`_add_inactive_contracted_spell`), as a grant of the
  Spell object already did.
- `_link_spell_dependencies` and `_preflight_contract_dependency_collisions` (their `walk`): before,
  `owner_conduit.get_spell_by_id(dep_id)` gave the version the dependency's index has active, also for a
  dependency id a notch has parked since the root was compiled; after, the walk finds the spell by spell_id
  (`get_spell_by_spell_id`) and asks the owner's Book for that spell's index's active spell (`_find_spell`). Same
  spell granted, same refusal when none.
- `_transfer_spell_ownership`: a str handle resolves the spell by spell_id, then the spell its index has active on
  this conduit (`get_spell_by_index_id`, the call the SpellIndex branch makes) - the old answer for a spell this
  conduit owns.
- `_get_spells_in_contract_by_conduit`, outbound half: a granted version lists its own Spell (was the index's active
  spell). The inbound half reads through `Spellbook._find_contracted_spell_by_id`, out of scope, and keeps its
  answer; for a parked grant the two halves differ until that lookup is fixed.

## Interface deltas
- None of the ward's signatures change.

## State and failure deltas
- No new state; the error messages of the walks and of the transfer are unchanged.

## Dependency and ordering
- The walks run outside the contract lock with no other lock held; the explicit step takes the dependency owner's
  Book lock alone. `_transfer_spell_ownership` holds no lock when it resolves the handle.

## Validation expectations
- Integration: `borrower.add_spell_to_contract(spell_id=French, conduit=lender)` returns True and the borrower holds
  a parked copy of French; `remove_spell_from_contract(spell_id=French, ...)` removes it.
- A grant with `link_dependencies=True` of a consumer compiled against English, after a notch of the dependency to
  French, contracts French active on the borrower, as before.
