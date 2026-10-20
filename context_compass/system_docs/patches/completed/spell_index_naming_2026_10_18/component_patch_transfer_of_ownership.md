# Component patch: ownership transfer names (spell_index_naming_2026_10_18)

## Before / after behavior
In `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`:
- `_mark_lineage_dirty(spell)` -> `_mark_spell_index_dirty(spell)`: marks the spell's SpellIndex structurally
  changed (`SpellSystemStates.mark_structural_change`). Its calls in `_transfer_owned_dependencies` and
  `_dirty_dependencies` follow. Its Args line names `spell_index`, but the parameter is `spell` (a pre-existing
  docstring error): corrected to `spell: Spell whose SpellIndex is marked structurally changed.`.
- `_mark_lineage_disabled(spell_index)` -> `_mark_spell_index_disabled(spell_index)`: disables the SpellIndex's
  state for the transfer window and registers the rollback. Its RuntimeError "Failed to register lineage for
  transfer disable." reads "Failed to register the SpellIndex's state for the transfer's disable.". Its call in
  `execute` follows.
- `_conduit_has_impacted_lineage(conduit, impacted_lineages)` -> `_conduit_has_impacted_index(conduit,
  impacted_index_ids)`; its call in `_collect_impacted_conduit_ids` follows.
- `_collect_impacted_conduit_ids(*, impacted_lineages, summary)` -> `impacted_index_ids` (keyword-only; one caller,
  `_gate_transfer_impacts`, whose local `impacted_lineages` - the impact closure of SpellIndex ids - is
  `impacted_index_ids`).
- Kept: the scope-tree text in this file - the `unique_per_conduit_lineage` comments in `execute` and "the lesser
  lineage" in `_collect_impacted_conduit_ids`.

## Interface deltas
- None public: all four methods are private. The transfer tests patch or call them by name
  (`test_transfer_of_ownership.py`, `test_transfer_of_ownership_contracts.py`) and move with them.
- One RuntimeError text changes; it is raised only when `register_index` leaves no state, and no test asserts it.

## State / failure deltas
- None.

## Dependency / ordering
- Each definition changes with its calls in one change set.

## Validation expectations
- The transfer unit tests and the transfer integration tests, GIL off and on.
