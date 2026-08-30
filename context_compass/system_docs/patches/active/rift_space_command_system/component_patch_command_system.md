# Component Patch: CommandSystem

## Component Purpose and Boundary In Current Architecture
Room-local command surface for controlled retrieval and execution.

## Before / After Behavior Summary
Before:
- `RiftSpace` had viewer discovery and workstation persistence only

After:
- `CommandSystem` sits between them and provides controlled getter/execute
  operations

## Interface Deltas
- first getter/execute surface only
- no bind/store operations
- no describe/list operations

## State and Lifecycle Deltas
- owned by `RiftSpace`
- no long-lived persistence beyond its room ownership and references

## Failure Mode Deltas
- should fail fast when selected targets are missing or the resolved target
  surface is incompatible with the requested getter/execute method

## Dependency and Ordering Constraints
- depends on the live viewer target model
- must not subsume workstation persistence

## Validation Expectations
- focused tests for the first getter/execute operations only

## Unknowns and Open Decisions
- exact first command methods depend on the current viewer target objects
