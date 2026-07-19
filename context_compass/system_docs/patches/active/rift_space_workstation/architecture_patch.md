# Architecture Patch: Rift Space Workstation

## Patch Scope and Non-Goals
Scope:
- add a room-local workstation canvas owned by `RiftSpace`
- let the workstation store saved bindings and active-target state
- expose local target operations only

Non-goals:
- command/discovery system
- ACL enforcement
- dynamic codegen execution context

## Changed-Components Matrix
| component | change |
|---|---|
| `Workstation` | new room-local binding/target canvas |
| `RiftSpace` | owns workstation and cleans it with the room |

## Interface and Boundary Deltas
- `RiftSpace` gains a `workstation`
- workstation owns:
  - saved object bindings
  - saved attribute/value bindings
  - saved method/callable bindings
  - active target state
- workstation does not discover targets

## Cross-Component Invariants
- `RiftSpace` remains the room
- workstation remains the local canvas inside the room
- command/discovery remains a later sibling system
- `cleanup_target(...)` only acts on the saved active target

## Migration / Rollout Order
1. add workstation type
2. wire it into `RiftSpace`
3. add focused tests

## Rollback Strategy
- remove workstation integration and restore `RiftSpace` to its prior state if
  the first cut proves semantically wrong

## Validation Expectations and Evidence Plan
- focused `RiftSpace`/workstation tests in the existing Rift/Nexus unit slice

## Ticket Coverage Map
- story:
  - `tickets/stories/2026-04-11_add_workstation_to_rift_space_story.md`
- task:
  - `tickets/tasks/2026-04-11_add_workstation_to_rift_space_task.md`

## Unknowns and Decision Requests
- UNKNOWN: whether saved bindings should later carry extra metadata beyond
  object/attr/method store separation
