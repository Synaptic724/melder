# architecture_patch

## Metadata
- Patch ID: nexus_singleton_public_surface
- Status: draft
- Owner: codex
- Created: 2026-03-28T22:47:05Z
- Updated: 2026-03-28T22:47:05Z

## Patch Scope and Non-Goals
- Objective:
  Replace the current public AR entry model with a public `Nexus` singleton
  that owns Rift registry/config/lifecycle state while keeping `Aether` as the
  hidden substrate host. Remove the separate public `RiftState` concept and
  treat `Rift` as the live runtime object that owns its own immediate runtime
  state.
- Non-goals:
  - full workstation/workspace implementation
  - MutationResearch or CommandOps changes
  - broad Melder naming rewrites outside the AR subtree

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| nexus | add/rename | public root should hide Aether and own Rift registry/config state | aether |
| rift | modify | live Rift should own the runtime/config/frame-assignment state it actually needs | nexus |
| aether | modify | keep private hosted Nexus singleton slot without public facade exposure | none |

## Interface and Boundary Deltas
- Boundary delta 1:
  `Aether` continues to own real `AethericFrame` objects and substrate
  services, but it should no longer be the public API root for Rift work.
- Boundary delta 2:
  `Nexus` becomes the public singleton root for Rift-domain behavior. It owns
  only Nexus config, enabled/configured state, Rift registries, and Rift
  creation/access policy.
- Boundary delta 3:
  `Aether` privately constructs and hosts the inert Nexus singleton at boot so
  package startup still eagerly establishes the shared runtime roots.
- Boundary delta 4:
  `Rift` becomes the live object that owns its own immediate runtime state
  (finalized Rift config snapshot, frame-name assignments/defaults, spaces,
  workstation/workspace refs) instead of requiring a separate public
  `RiftState`.
- Boundary delta 5:
  Real frame targeting remains a `Rift` concern. `Nexus` decides frame names
  and policy, but it should not directly target `Aether` for operational frame
  access to avoid circular-domain coupling.

## Cross-Component Invariants
- Invariant 1:
  `Aether` is still the substrate singleton and owns frames.
- Invariant 2:
  `Nexus` is a second singleton with a different responsibility domain:
  Rift registry/config/lifecycle only.
- Invariant 3:
  Public Rift usage should not require touching `Aether`.
- Invariant 4:
  `Nexus` may exist at boot but remain unconfigured and disabled until
  explicit user engagement.
- Invariant 5:
  `Rift` should own the live state it needs; no separate public state object is
  required until true persistence/rehydration demands it.

## Migration and Rollout Order
1. Add the Nexus patch docs and route the active ticket.
2. Refactor the hosted ARS singleton into private Nexus hosting inside Aether.
3. Expose a public `Nexus` singleton entrypoint.
4. Fold required live state into `Rift` and remove the separate public
   `RiftState` design.
5. Update focused tests and AR docs to the new public model.

## Rollback Strategy
- Rollback trigger:
  The Nexus public-root model forces hidden persistence or workstation/workspace
  machinery we do not yet want.
- Rollback steps:
  1. Restore the older ARS naming and public facade shape.
  2. Restore the separate `RiftState` object if required.
  3. Remove Nexus patch docs from the active patch lane.
- Post-rollback verification:
  The public API exposes one coherent root again and the docs/tests match it.

## Validation Expectations and Evidence Plan
- Validation item 1:
  `Aether` privately hosts Nexus without publicly facading Rift operations.
- Evidence source 1:
  `src/melder/aether/aether.py`
- Validation item 2:
  `Nexus` is the public singleton root for Rift creation/config/registry.
- Evidence source 2:
  `src/melder/aether/aetheric_rift_system/`
- Validation item 3:
  `Rift` owns its live state directly and no separate public `RiftState`
  remains in the active model.
- Evidence source 3:
  `src/melder/aether/aetheric_rift_system/aetheric_rift/`

## Ticket Coverage Map
- Story:
  STORY-2026-03-16-aethericrift-system-bootstrap
- Tasks:
  - TASK-2026-03-22-implement-aethericrift-system-configuration-governance
  - TASK-2026-03-28-refactor-rift-public-surface-into-nexus-singleton

## Unknowns and Decision Requests
- UNKNOWN:
  Whether the current filesystem/module layout should keep the legacy
  `aetheric_rift_system` package name while the public symbols become
  `Nexus`/`Rift`, or whether the folder should be renamed immediately.
- DECISION_REQUEST:
  None for the current narrow public-surface refactor.

## Context / Handoff Summary
- What changed:
  The active AR design now pivots to a public `Nexus` singleton root with
  hidden `Aether` substrate ownership.
- What remains:
  Concrete workstation/workspace ownership remains a follow-up slice below this
  refactor.
- Next entrypoint:
  `component_patch_nexus.md`
