# Architecture Patch: Command System Room Mode Runtime Gating

## Objective
Apply room-mode gating to raw runtime-object getters in `CommandSystem` so
`static` and `capability` rooms do not expose naked runtime objects while
`dynamic` keeps the current ACL-gated runtime getter behavior.

## Non-Goals
- no workstation-bound object policing after bind
- no handle/proxy wrapper system
- no ACL/compiler schema changes

## Changed Components
- `CommandSystem`

## Invariants
- command ACLs still gate access before bind
- room mode adds a second gate for raw runtime-object exposure
- `static` and `capability` do not expose raw runtime objects in this cut
- `dynamic` keeps current ACL-gated raw runtime getter behavior

## Interface Deltas
- raw runtime-object getters now fail fast in `static` and `capability`
- descriptor/record getters remain available

## Migration Order
1. add room-mode gate helpers in `CommandSystem`
2. gate selected-target runtime-object access
3. gate direct conduit/spell runtime-object getters
4. update focused tests

## Rollback
Rollback is code-level only for this patch. Do not partially gate only some raw
runtime-object getters.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_implement_command_system_room_mode_runtime_gating_task.md`
