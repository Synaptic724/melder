# Component patch: DevOps risk tracking names (spell_index_naming_2026_10_18)

## Before / after behavior
- `_ConduitRiskState` (`src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py`): the slot and
  attribute `lineages` - the SpellIndex ids a conduit knows about - is `spell_index_ids`.
- RiskManager: the slot `_lineage_conduits` (SpellIndex id -> conduit ids) is `_spell_index_conduits`;
  `_resolve_lineage_id(spell)` is `_resolve_spell_index_id(spell)` and `_resolve_lineage_id_from_spell_id(spell_id)`
  is `_resolve_spell_index_id_from_spell_id(spell_id)`; each still returns `spell.spell_index.id` or
  `SpellSystemState.spell_index_id` (or None).
- `on_structural_validity_change(lineage_id, validity)` -> `on_structural_validity_change(spell_index_id,
  validity)`. Its one caller, SpellSystemState's validity publication (`spell_system_state.py`, the
  `risk_manager.on_structural_validity_change(index_id, validity)` call), passes the id positionally; no caller in
  src or tests passes it by keyword.
- `_update_structural_risk(conduit_id, lineage_id, validity)` -> `spell_index_id`;
  `_update_resolution_risk(conduit_id, lineage_key, validity)` -> `risk_key`: the key is a SpellIndex id when the
  verdict folds onto one and "spell:<spell_id>" when it does not, so it is named for what it is, not for one of
  the two.
- The locals in `remove_conduit`, `unregister_spell`, `on_structural_validity_change`,
  `on_resolution_validity_change` and `_register_spell_risk` (`lineages`, `lineage_id`) follow:
  `spell_index_ids`, `spell_index_id`.
- ConduitWard._invalidate_contract_consumers
  (`src/melder/aether/conduit/conduit_ward/conduit_ward.py`): the loop over the SpellIndex ids
  `mark_contract_dependents_dirty` returns names its variable `spell_index_id` (was `lineage_id`).

## Interface deltas
- None public: RiskManager is internal (AGENT_ACCESS: internal), owned by DevOpsManager. Its attribute and method
  names change; the RiskManager tests read `_lineage_conduits` and a bucket's `lineages` and move with them.

## State / failure deltas
- None. The same sets are filled and read under the same lock; the Book flag's distillation
  (`_refresh_spellbook_flag`, `_has_unexcluded_risk`) is unchanged.

## Dependency / ordering
- SpellSystemState's positional call needs no edit. SpellSystemStates' class docstring names the callback,
  `RiskManager.on_structural_validity_change(...)`, whose name does not change.

## Validation expectations
- `tests/unit/melder/aether/dev_ops/risk_manager/test_risk_manager.py`, the non-resolvable flag unit and component
  tests and the ConduitWard contract tests, GIL off and on.
