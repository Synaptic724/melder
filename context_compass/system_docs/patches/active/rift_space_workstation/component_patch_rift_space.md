# Component Patch: RiftSpace

## Component Purpose and Boundary In Current Architecture
Base room/workspace object owned by `Rift`.

## Before / After Behavior Summary
Before:
- room owned metadata, viewer, selected viewer target ids, and event config only

After:
- room also owns a workstation canvas

## Interface Deltas
- add `workstation` property
- cleanup must cascade through the workstation

## State and Lifecycle Deltas
- `RiftSpace` now owns one more child object

## Failure Mode Deltas
- no new room-level failure modes beyond workstation contract failures when the
  caller uses the workstation

## Dependency and Ordering Constraints
- workstation cleanup should happen before room state is nulled

## Validation Expectations
- focused tests proving workstation ownership and cleanup through `RiftSpace`

## Unknowns and Open Decisions
- none for the first room-local workstation cut
