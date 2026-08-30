# Architecture Patch: RiftSpace Mode Specific Command Systems

## Objective
Refactor the current single `CommandSystem` ownership model into a composed
mode-specific family under `rift_space/command_system/` so each room type owns
the right command surface while keeping the shared command API.

## Non-Goals
- no new public agent API outside `RiftSpace.command_system`
- no handle/proxy capability design
- no ACL/compiler schema changes

## Changed Components
- `RiftSpace`
- `StaticRiftSpace`
- `CapabilityRiftSpace`
- `DynamicRiftSpace`
- `CommandSystem` family under `rift_space/command_system/`

## Invariants
- `RiftSpace` remains the owner of the command surface
- the command API shape stays stable through `space.command_system`
- mode-specific behavior moves out of inline `space_kind` checks and into the
  composed command-system subclasses

## Interface Deltas
- import path for the base command system moves under
  `rift_space/command_system/`
- room subclasses now construct a mode-specific command system

## Migration Order
1. create `rift_space/command_system/`
2. move the base command system into the folder
3. add static/capability/dynamic command-system subclasses
4. add room-owned factory composition in `RiftSpace`
5. update imports and focused tests

## Rollback
Rollback is code-level only for this patch. Do not leave half the room classes
on the old import path and half on the new composition seam.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_refactor_rift_space_to_mode_specific_command_systems_task.md`
