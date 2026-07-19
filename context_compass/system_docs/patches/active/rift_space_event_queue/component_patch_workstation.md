# Component Patch: Workstation

## Component Purpose and Boundary In Current Architecture
Room-local binding canvas for saved bindings and active-target operations
inside one `RiftSpace`.

## Before / After Behavior Summary
Before:
- workstation stored strong/weak bindings but emitted no room-level event when
  weak bindings died

After:
- workstation publishes one callback-driven event when a weak binding is
  collected

## Interface Deltas
- workstation construction takes one optional event-publisher callback
- weak binding installation registers one node callback that publishes:
  - event type
  - logical store
  - binding name
  - workstation id
  - owner space id

## State and Lifecycle Deltas
- workstation owns one optional event-publisher callback reference
- cleanup clears that callback reference

## Failure Mode Deltas
- best-effort publication only; callback errors must not break GC/cleanup

## Dependency and Ordering Constraints
- event publication belongs to weak-binding collection only in this slice
- queue ownership remains on `RiftSpace`

## Validation Expectations
- focused tests proving weak-binding collection publishes one queue event

## Unknowns and Open Decisions
- none for this slice
