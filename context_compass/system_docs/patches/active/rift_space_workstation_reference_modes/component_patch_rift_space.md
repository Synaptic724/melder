# Component Patch: RiftSpace

## Component Purpose and Boundary In Current Architecture
Base room/workspace object owned by `Rift`.

## Before / After Behavior Summary
Before:
- room owned the workstation but did not influence workstation binding mode

After:
- room kind determines the default workstation reference mode when a bind call
  receives `weak_ref=None`

## Interface Deltas
- no new public room API is required for this slice
- `RiftSpace` must pass the room-kind-derived default into the owned
  workstation during construction

## State and Lifecycle Deltas
- the room now fixes one default binding-reference mode for its workstation
  when it is created

## Failure Mode Deltas
- none beyond workstation weak-binding failures when explicit or room-default
  weak binding is requested for unsupported values

## Dependency and Ordering Constraints
- room mode is fixed at room creation time
- current semantics:
  - `static` -> weak default
  - `capability` -> strong default
  - `dynamic` -> strong default
  - `base` -> strong default

## Validation Expectations
- focused tests proving `static` and `capability` rooms resolve `weak_ref=None`
  differently through the same workstation API

## Unknowns and Open Decisions
- none for this slice
