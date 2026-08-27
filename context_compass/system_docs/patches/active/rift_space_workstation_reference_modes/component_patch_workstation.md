# Component Patch: Workstation

## Component Purpose and Boundary In Current Architecture
Room-local binding canvas for saved bindings and active-target operations
inside one `RiftSpace`.

## Before / After Behavior Summary
Before:
- workstation stored all bindings strongly in three dict stores
- bind methods had no reference-mode control

After:
- workstation stores bindings through strong and weak backing stores
- bind methods accept `weak_ref: Optional[bool]`
- `weak_ref=None` resolves through the room default captured at workstation
  creation
- explicit weak binding raises when the target cannot be weak-referenced

## Interface Deltas
- `bind_object(name, value, weak_ref=None)`
- `bind_attribute(name, value, weak_ref=None)`
- `bind_method(name, value, weak_ref=None)`
- binding resolution/release/describe now span both strong and weak backing
  stores transparently

## State and Lifecycle Deltas
- workstation now owns strong and weak backing stores per binding category
- cleanup must release both strong and weak backing stores

## Failure Mode Deltas
- weak binding raises for non-weakref-able values
- ambiguous name resolution still raises
- dead weak bindings continue to fail fast through underlying weak-store access

## Dependency and Ordering Constraints
- weak storage should use the existing weak data-structure package
- no silent downgrade from weak to strong
- target cleanup/call behavior stays unchanged above the new storage model

## Validation Expectations
- focused tests for explicit strong bind, explicit weak bind, mode-default
  bind, and unsupported weak bind

## Unknowns and Open Decisions
- none for this slice
