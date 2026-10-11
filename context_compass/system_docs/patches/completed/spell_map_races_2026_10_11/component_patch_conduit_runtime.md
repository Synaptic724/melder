# Component patch: Conduit Runtime, Aether, Ward, Transfer, Command System (spell_map_races_2026_10_11)

## Before / after
- Conduit.get_spell_permissions and CommandSystem.get_spell_by_id walked the live _spells map with has_spell to
  resolve a lineage id; after: Spellbook.find_spell_by_id (O(1), the id maps). Same answers; get_spell_permissions
  stops holding the conduit lock across the lookup.
- Conduit.get_spell_by_id and get_conduit_by_spell_id: behaviour unchanged - ValueError for an unclaimed id or an
  unknown frame (owner decision 2026-10-11). The docstrings, which promised None, now document the raise;
  get_conduit_by_spell_id's annotation becomes Conduit; get_spell_by_id keeps Optional[Spell] for a Book that does
  not resolve an id its conduit owns. Aether is unchanged.
- TransferOfOwnership._conduit_has_impacted_lineage snapshots the owned and contracted maps;
  _enumerate_borrowers keeps has_spell (it also reads selected_spell_id, which a cleaned index does not have; a
  cleaned shared index now always surfaces as has_spell's documented RuntimeError).

## Validation expectations
get_spell_permissions on current and parked ids without iterating the live map; unclaimed id -> ValueError from
Conduit.get_spell_by_id and get_conduit_by_spell_id; existing ward, transfer and command-system suites green.
