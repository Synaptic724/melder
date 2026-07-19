# Component Patch: StaticCommandSystem

## Before
- static specialized spell getters using the drifted `get_spell_object_by_*`
  names

## After
- static specialization follows the aligned command names:
  - `get_spell_by_source_id(...)`
  - `get_spell_by_index_id(...)`
  - `get_spell_by_id(...)`

## Contract
- static spell behavior remains unchanged
- only the command-surface naming is aligned in this patch
