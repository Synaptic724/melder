# Component Patch: ICommandSystem

## Before
- `ICommandSystem` exposed the drifted direct-wrapper names

## After
- `ICommandSystem` mirrors the aligned command names:
  - `link(...)`
  - `get_spell_by_source_id(...)`
  - `get_spell_by_index_id(...)`
  - `get_spell_by_id(...)`

## Contract
- protocol surface stays in lockstep with runtime `CommandSystem`
- this patch changes names only, not the underlying room-mediated mechanics
