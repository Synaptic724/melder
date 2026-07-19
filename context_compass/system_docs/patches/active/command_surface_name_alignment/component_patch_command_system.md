# Component Patch: CommandSystem

## Before
- direct wrappers used drifted names:
  - `link_conduits(...)`
  - `get_spell_object_by_source_id(...)`
  - `get_spell_object_by_index_id(...)`
  - `get_spell_object_by_id(...)`

## After
- direct wrappers align to lower runtime names:
  - `link(...)`
  - `get_spell_by_source_id(...)`
  - `get_spell_by_index_id(...)`
  - `get_spell_by_id(...)`

## Contract
- the renamed methods preserve the existing command-layer mechanics
- only the names change in this patch
- room-mediated filtering/ACL/publication behavior stays the same
