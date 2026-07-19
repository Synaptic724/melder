# architecture_patch

## Metadata
- Patch ID: devops_information_registry_identity
- Status: draft
- Owner: codex
- Created: 2026-05-22T22:08:36Z
- Updated: 2026-05-22T22:08:36Z

## Patch Scope and Non-Goals
- Objective:
  - Add an `AethericFrame`-owned `DevOpsInformationRegistry`.
  - Replace `TransactionIdentity` with `DevopsIdentity`.
- Non-goals:
  - Change transaction strategy behavior.
  - Rework spellbook/conduit transaction policy.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| AethericFrame | modify | own and dispense the new registry | DevOpsInformationRegistry |
| DevOpsManager | modify | borrow and expose the frame-owned registry | DevOpsInformationRegistry |
| DevOpsInformationRegistry | add | central frame-local topology and transaction object index | none |
| DevopsIdentity | add/rename | generalize identity away from transaction-only naming | none |

## Interface and Boundary Deltas
- Boundary delta 1:
  - `AethericFrame` gains a new owned registry surface and passes it into
    `DevOpsManager`.
- Interface delta 1:
  - `TransactionIdentity` import paths become `DevopsIdentity`.

## Cross-Component Invariants
- Invariant 1:
  - The registry is frame-local and owned by `AethericFrame`, not process-global.
- Invariant 2:
  - Identity cleanup must unregister from the registry safely before dropping
    its own fields when a registry is attached.
- Invariant 3:
  - Registry cleanup must clear relation and transaction indexes under one lock.

## Migration and Rollout Order
1. Add the new registry and renamed identity objects.
2. Wire `AethericFrame` to create and own the registry.
3. Wire `DevOpsManager` to borrow the registry.
4. Update direct runtime imports/references to the new identity type.

## Rollback Strategy
- Rollback trigger:
  - Rename surface proves wider than the approved slice.
- Rollback steps:
  - Stop after object creation and keep downstream behavior untouched.
- Post-rollback verification:
  - Runtime imports still resolve and no partial rename remains.

## Validation Expectations and Evidence Plan
- Validation item 1:
  - Object construction, registration APIs, and cleanup semantics remain explicit.
- Evidence source 1:
  - direct source reread of touched files.

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks:
  - `tickets/tasks/2026-05-22_add_devops_information_registry_and_devops_identity_task.md`

## Unknowns and Decision Requests
- UNKNOWN:
  - whether downstream spellbook/conduit registration wiring should happen in
    the same slice.
- DECISION_REQUEST:
  - none yet

## Context / Handoff Summary
- What changed:
  - patch lane opened for registry + identity work
- What remains:
  - implement the objects and wire `DevOpsManager`
- Next entrypoint:
  - `component_patch_devops_information_registry.md`
