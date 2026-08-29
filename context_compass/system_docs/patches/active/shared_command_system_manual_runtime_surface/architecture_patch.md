# Shared Command System Manual Runtime Surface Architecture Patch

## Objective
Expand the shared manual-runtime command vocabulary on base `CommandSystem`
instead of forking capability-only APIs.

## Non-Goals
- No codegen-only command work.
- No broader Rift/RiftSpace redesign.
- No capability integration harness in this patch.

## Changed Components
- `CommandSystem`
- `StaticCommandSystem`
- `interfaces.py` (`ICommandSystem`)

## Boundary Contract
- shared manual-runtime operations live on base `CommandSystem`
- `StaticCommandSystem` explicitly denies unsafe topology-mutation methods
- `CapabilityCommandSystem` and `DynamicCommandSystem` inherit the shared
  manual-runtime surface
- codegen-only behavior stays outside the base command layer
- one explicit command-surface introspection helper exists so room support is
  inspectable without guessing

## Migration Order
1. add the new shared manual-runtime methods to `CommandSystem`
2. add static deny overrides for unsafe topology mutation
3. update `ICommandSystem`
4. add focused capability/static tests
