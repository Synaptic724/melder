# Component Patch: ICommandSystem

## Before
- `ICommandSystem` exposed spell-object getters but no explicit spell
  activation helpers

## After
- `ICommandSystem` includes:
  - `meld(...)`
  - `meld_existing_spell(...)`

## Contract
- protocol surface stays in lockstep with runtime `CommandSystem`
- helper names remain explicit so they do not overload the meaning of the
  existing spell-object getters
