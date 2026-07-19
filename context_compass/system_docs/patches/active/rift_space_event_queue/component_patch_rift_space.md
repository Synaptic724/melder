# Component Patch: RiftSpace

## Component Purpose and Boundary In Current Architecture
Base room/workspace object owned by `Rift`.

## Before / After Behavior Summary
Before:
- room owned event configuration but had no queue/state for runtime events

After:
- room owns one local event queue plus explicit queue helpers
- room may optionally run one managed queue-consumer thread

## Interface Deltas
- queue snapshot/drain helpers
- optional `manage_event_queue(...)`
- optional `stop_managing_event_queue(...)`
- internal event-publisher callback wired into the owned workstation

## State and Lifecycle Deltas
- `RiftSpace` now owns:
  - queue
  - queue lock
  - managed-consumer stop signal
  - optional managed-consumer thread

## Failure Mode Deltas
- managed queue consumption must stay explicit/opt-in
- cleanup must stop the managed queue thread before nulling queue state

## Dependency and Ordering Constraints
- queue belongs to the room
- workstation only publishes binding events into the room callback
- command system remains separate

## Validation Expectations
- focused tests for queue publishing, draining, and managed-consumer lifecycle

## Unknowns and Open Decisions
- none for this slice
