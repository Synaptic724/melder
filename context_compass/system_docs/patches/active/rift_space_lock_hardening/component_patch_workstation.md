# Component Patch: Workstation

## Component Purpose and Boundary In Current Architecture
Room-local binding canvas for saved bindings and active-target operations
inside one `RiftSpace`.

## Before / After Behavior Summary
Before:
- workstation owned grouped mutable binding state but had no per-instance lock

After:
- workstation owns one `RLock`
- grouped bind/release/target/cleanup paths serialize on that lock

## Interface Deltas
- no public API shape change
- internal bind/target/cleanup behavior becomes lock-guarded

## State and Lifecycle Deltas
- workstation now owns one lock alongside strong/weak binding stores and target state
- cleanup should run under the workstation lock

## Failure Mode Deltas
- no new public failure modes
- grouped workstation state becomes less race-prone in no-GIL runtime

## Dependency and Ordering Constraints
- lock guards grouped workstation state only
- weak-store internals still use their own container semantics for node-level operations

## Validation Expectations
- focused `test_nexus.py` stays green after workstation lock hardening

## Unknowns and Open Decisions
- none for this slice
