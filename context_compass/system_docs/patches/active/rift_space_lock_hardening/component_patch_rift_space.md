# Component Patch: RiftSpace

## Component Purpose and Boundary In Current Architecture
Base room/workspace object owned by `Rift`.

## Before / After Behavior Summary
Before:
- room owned mutable grouped state but had no per-instance lock

After:
- room owns one `RLock`
- grouped mutation and cleanup paths serialize on that lock

## Interface Deltas
- no public API shape change
- internal setter-like and cleanup paths become lock-guarded

## State and Lifecycle Deltas
- `RiftSpace` now owns one lock alongside its existing room-local state
- cleanup should run under the room lock

## Failure Mode Deltas
- no new user-facing failure modes
- grouped mutation/cleanup semantics become less race-prone in no-GIL runtime

## Dependency and Ordering Constraints
- lock guards grouped room state only
- simple deque operations should not gain a second redundant queue lock

## Validation Expectations
- focused `test_nexus.py` stays green after lock hardening

## Unknowns and Open Decisions
- none for this slice
