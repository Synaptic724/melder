# Component Patch: ICommandSystem

## Before
- `ICommandSystem` covered the pre-expansion getter/query/execution surface only

## After
- `ICommandSystem` includes the widened shared manual-runtime command methods
- `ICommandSystem` includes one command-surface introspection helper

## Contract
- protocol surface stays in lockstep with runtime `CommandSystem`
- no capability-only protocol branch is introduced
- room-specific behavior differences remain behavioral overrides, not protocol
  forks
