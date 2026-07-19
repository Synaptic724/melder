# Component Patch: CommandSystem

## Before
- base command surface could fetch spell metadata objects and topology/runtime
  objects, but it had no explicit command helper for spell activation

## After
- base `CommandSystem` owns explicit activation helpers:
  - `meld(...)`
  - `meld_existing_spell(...)`

## Contract
- `meld(...)` resolves the owner conduit through published descriptor
  truth and then delegates to `Conduit.meld(...)`
- `meld_existing_spell(...)` resolves the owner conduit through published
  descriptor truth and then delegates to `Conduit.meld_existing_spell(...)`
- existing spell-object getters remain unchanged
