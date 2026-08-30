# Architecture Patch: Rift Space Lock Hardening

## Patch Scope and Non-Goals
Scope:
- add explicit `RLock` ownership to `RiftSpace`
- add explicit `RLock` ownership to `Workstation`
- serialize grouped mutation and cleanup paths

Non-goals:
- lock every nearby class by default
- queue API redesign
- ACL enforcement or ACL subsystem refactors

## Changed-Components Matrix
| component | change |
|---|---|
| `RiftSpace` | own an `RLock` and use it for grouped mutation/cleanup |
| `Workstation` | own an `RLock` and use it for grouped mutation/cleanup |

## Interface and Boundary Deltas
- no public API expansion is required
- internal mutation/cleanup semantics become explicitly serialized

## Cross-Component Invariants
- `Rift` keeps its existing `RLock`
- `RiftSpace` and `Workstation` become the next locked room/runtime objects
- `CommandSystem` remains unlocked in this slice because it is still mostly a facade
- reviewed ACL objects remain unchanged in this slice where locks already exist or grouped mutable state is absent

## Migration / Rollout Order
1. add `RLock` ownership to `Workstation`
2. add `RLock` ownership to `RiftSpace`
3. wrap grouped mutation and cleanup paths
4. run focused tests

## Rollback Strategy
- remove the new locks and restore the prior room/workstation state if the
  hardening slice proves semantically wrong

## Validation Expectations and Evidence Plan
- focused `tests/unit/melder/aether/test_nexus.py` coverage must remain green
- lock/no-lock review conclusions should be recorded in the task notes

## Ticket Coverage Map
- task:
  - `tickets/tasks/2026-04-11_harden_rift_space_and_workstation_locking_task.md`

## Unknowns and Decision Requests
- none for this slice
