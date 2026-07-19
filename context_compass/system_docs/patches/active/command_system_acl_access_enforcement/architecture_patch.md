# Architecture Patch: Command System ACL Access Enforcement

## Objective
Compile command enablement into the ACL surface and enforce that compiled state
on `CommandSystem` access/fetch paths for frames, conduits, and spells.

## Non-Goals
- no workstation-bound object policing after bind
- no viewer redesign
- no broader room-mode redesign in this patch

## Changed Components
- `CompiledFrameACLAccessSurface`
- `FrameACLCompiler`
- `CommandSystem`

## Invariants
- ACLs gate command access before bind
- already-bound workstation objects remain outside post-bind ACL policing
- spell command gating uses stable `spell_index_id`

## Interface Deltas
- compiled ACL surface gains command enablement outputs
- command system selected-target and direct getter paths fail fast when the
  compiled command ACL does not permit access

## Migration Order
1. add compiled command enablement fields
2. compile command enablement
3. enforce in command-system access paths
4. update focused tests

## Rollback
Rollback is code-level only for this patch. Do not partially enforce only some
command fetch paths.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md`
