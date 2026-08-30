# Architecture Patch: Rift Space Event Queue

## Patch Scope and Non-Goals
Scope:
- add a room-local event queue to `RiftSpace`
- publish weak-binding collection events into that queue
- add explicit queue-management helpers

Non-goals:
- ACL enforcement
- global/system-wide eventstream design
- action/memory event model redesign

## Changed-Components Matrix
| component | change |
|---|---|
| `RiftSpace` | owns queue state and explicit queue helper methods |
| `Workstation` | publishes weak-binding collection events through a room callback |

## Interface and Boundary Deltas
- `RiftSpace` gains:
  - queue ownership
  - queue snapshot/drain helpers
  - optional managed queue-consumer thread helpers
- workstation stays the producer for binding-related events
- queue consumption remains explicit and opt-in

## Cross-Component Invariants
- weak-binding collection publishes one room-local event
- queue ownership belongs to the room, not the workstation
- managed consumption must remain explicit so direct queue readers are not
  silently bypassed

## Migration / Rollout Order
1. add queue state to `RiftSpace`
2. add weak-binding publication hook in workstation
3. add queue helpers and focused tests

## Rollback Strategy
- remove queue ownership and callback wiring, leaving weak-binding semantics in
  place if the queue model proves wrong

## Validation Expectations and Evidence Plan
- focused `tests/unit/melder/aether/test_nexus.py` coverage for:
  - weak-binding collection event publication
  - queue snapshot/drain behavior
  - optional managed consumer thread behavior

## Ticket Coverage Map
- task:
  - `tickets/tasks/2026-04-11_add_rift_space_event_queue_and_weak_binding_events_task.md`

## Unknowns and Decision Requests
- none for this slice
