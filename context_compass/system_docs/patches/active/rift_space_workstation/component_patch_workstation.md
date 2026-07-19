# Component Patch: Workstation

## Component Purpose and Boundary In Current Architecture
Room-local canvas for saved bindings and active-target operations inside one
`RiftSpace`.

## Before / After Behavior Summary
Before:
- `RiftSpace` had no local binding canvas

After:
- `Workstation` stores saved bindings
- `Workstation` tracks an active target
- `Workstation` can clear, cleanup, release, and call the current target

## Interface Deltas
- object binding store
- attribute/value binding store
- method/callable binding store
- target selection/get/clear
- `cleanup_target(*method_names)`
- `call_target(..., bind_as_name=..., bind_as_store=...)`

## State and Lifecycle Deltas
- workstation is owned by `RiftSpace`
- workstation cleanup clears all stores and target state

## Failure Mode Deltas
- target operations fail fast if no target exists
- `call_target` fails fast if the target is not callable
- `cleanup_target` fails fast if the target lacks the requested cleanup method(s)

## Dependency and Ordering Constraints
- workstation must stay independent from command/discovery logic in the first cut

## Validation Expectations
- focused tests for binding, targeting, calling, cleanup, and `RiftSpace` ownership

## Unknowns and Open Decisions
- none for the first workstation-only cut
