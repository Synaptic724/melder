# Component Patch: RiftSpace

## Component Purpose and Boundary In Current Architecture
Base room/workspace object owned by `Rift`.

## Before / After Behavior Summary
Before:
- owned viewer, selected viewer target ids, event config, workstation

After:
- also owns command system

## Interface Deltas
- add `command_system` property
- cleanup cascades through command system as another room-owned child

## State and Lifecycle Deltas
- one additional child object owned by the room

## Failure Mode Deltas
- no new room-level failure modes beyond command-system contract failures when
  used by callers

## Dependency and Ordering Constraints
- command-system cleanup should happen before room state is nulled
- command system must not own discovery or persistence

## Validation Expectations
- focused tests proving ownership and first command operations through `RiftSpace`

## Unknowns and Open Decisions
- none beyond exact first command methods
