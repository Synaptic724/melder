# Architecture Patch: Rift Space Command System

## Patch Scope and Non-Goals
Scope:
- add a room-local command system to `RiftSpace`
- keep viewer discovery separate
- keep workstation persistence separate

Non-goals:
- ACL enforcement
- command describe/discovery APIs
- dynamic codegen execution context

## Changed-Components Matrix
| component | change |
|---|---|
| `CommandSystem` | new room-local controlled getter/execute surface |
| `RiftSpace` | owns command system alongside workstation |

## Interface and Boundary Deltas
- `RiftSpace` owns:
  - workstation
  - command system
- command system performs:
  - controlled getters
  - explicit execute helpers
- command system does not own persistence

## Cross-Component Invariants
- viewer owns discovery/description
- workstation owns persistence and local target state
- command system owns controlled retrieval/execution only

## Migration / Rollout Order
1. inspect live viewer target model
2. add command system
3. wire it into `RiftSpace`
4. add focused tests

## Rollback Strategy
- remove command system integration and restore `RiftSpace` to workstation-only
  if the first cut proves semantically wrong

## Validation Expectations and Evidence Plan
- focused `RiftSpace`/command-system tests in the Rift/Nexus unit slice

## Ticket Coverage Map
- story:
  - `tickets/stories/2026-04-11_add-command-system-to-rift-space_story.md`
- task:
  - `tickets/tasks/2026-04-11_add-command-system-to-rift-space_task.md`

## Unknowns and Decision Requests
- UNKNOWN: exact first getter/execute methods until the viewer target model is
  re-read
