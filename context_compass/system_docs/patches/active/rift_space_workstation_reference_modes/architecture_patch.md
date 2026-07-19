# Architecture Patch: Rift Space Workstation Reference Modes

## Patch Scope and Non-Goals
Scope:
- add explicit strong and weak binding storage to the room-local workstation
- let `weak_ref=None` resolve through the owning room kind
- keep the bind API narrow instead of adding a second binding subsystem

Non-goals:
- event queue ownership or consumption
- command ACL enforcement
- stale-binding recovery beyond current fail-fast behavior

## Changed-Components Matrix
| component | change |
|---|---|
| `Workstation` | split binding storage into strong and weak paths and resolve per-bind reference mode |
| `RiftSpace` | provide the room-kind default used when workstation binds receive `weak_ref=None` |

## Interface and Boundary Deltas
- workstation bind APIs accept `weak_ref: Optional[bool]`
- `weak_ref=True` means weak storage
- `weak_ref=False` means strong storage
- `weak_ref=None` means use the room default
- room defaults:
  - `static` -> weak
  - `capability` -> strong
  - `dynamic` -> strong
  - current `base` room -> strong

## Cross-Component Invariants
- explicit `weak_ref` overrides room default every time
- explicit weak binding must not silently degrade to strong
- workstation remains the storage canvas; ACL behavior still belongs elsewhere
- room mode is fixed when the room is created and should not mutate later

## Migration / Rollout Order
1. add the reference-mode task and patch docs
2. retrofit workstation storage and bind APIs
3. wire room-kind defaulting through `RiftSpace`
4. update focused Rift/Nexus tests

## Rollback Strategy
- remove the weak stores and restore the workstation to strong-only binding if
  the reference-mode model proves incoherent

## Validation Expectations and Evidence Plan
- focused `tests/unit/melder/aether/test_nexus.py` coverage for:
  - explicit weak bind
  - explicit strong bind
  - `weak_ref=None` defaulting by room kind
  - explicit weak failure for non-weakref-able values

## Ticket Coverage Map
- task:
  - `tickets/tasks/2026-04-11_add_workstation_reference_modes_to_rift_space_task.md`

## Unknowns and Decision Requests
- none for this slice
