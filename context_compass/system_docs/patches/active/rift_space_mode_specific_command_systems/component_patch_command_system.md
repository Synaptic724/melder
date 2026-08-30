# Component Patch: CommandSystem

## Before
- one generic `CommandSystem` owns all runtime behavior
- static/capability mode differences are expressed through inline checks

## After
- one shared base command system holds common logic
- `StaticCommandSystem`, `CapabilityCommandSystem`, and `DynamicCommandSystem`
  override or specialize only the mode-specific behavior

## Interface Deltas
- command-system modules now live under `rift_space/command_system/`
- public command methods remain stable through the base interface

## State / Failure Deltas
- static/capability/dynamic behavior is composed by room type
- raw runtime-object policy becomes a subclass concern instead of a generic
  branch buried in one implementation
