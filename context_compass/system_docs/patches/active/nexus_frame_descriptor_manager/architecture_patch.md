# architecture_patch

## Metadata
- Patch ID: nexus_frame_descriptor_manager
- Status: draft
- Owner: codex
- Created: 2026-04-04T20:41:17Z
- Updated: 2026-04-04T20:41:17Z

## Patch Scope and Non-Goals
- Objective:
  Extract the frame-scoped descriptor/store subsystem out of `Nexus` into a
  dedicated thread-safe `FrameDescriptorManager`, leaving `Nexus` as the
  façade/root for Rift policy, registry, and topology work.
- Non-goals:
  - final ACL system implementation
  - final viewer/query contracts
  - backward-compat shims for the old in-class descriptor-store paths

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| nexus | modify | keep façade/root responsibilities while dropping frame-scoped store ownership | passive ingest + descriptor lanes |
| frame_descriptor_manager | add | own frame descriptors, passive publish/remove flows, and Nexus-managed frame-record helpers | nexus |

## Interface and Boundary Deltas
- Boundary delta 1:
  `Nexus` remains the public/internal root for Rift registry, configuration,
  enablement, and topology decisions.
- Boundary delta 2:
  Frame-scoped descriptor/store state moves under one dedicated manager object
  owned by `Nexus`.
- Boundary delta 3:
  The manager owns the descriptor dictionary, posture refresh, passive
  publication/removal, and Nexus-managed frame-record storage helpers.
- Boundary delta 4:
  `Nexus` keeps façade methods for frame-facing behavior when they are part of
  the intended semantic root, but delegates the actual frame-scoped state work
  to the manager.

## Cross-Component Invariants
- Invariant 1:
  `Nexus` no longer directly owns `_frame_descriptors_by_name`.
- Invariant 2:
  `FrameDescriptorManager` owns frame-scoped state only, not Rift registry or
  process-wide Nexus configuration.
- Invariant 3:
  Multi-step frame-scoped mutations remain explicitly lock-guarded.
- Invariant 4:
  `FrameDescriptor` remains the per-frame aggregate, not a runtime
  frame replacement.

## Migration and Rollout Order
1. Add active patch docs and route the refactor lane.
2. Lock the exact split between façade methods and manager-owned methods.
3. Introduce `FrameDescriptorManager` with explicit `RLock`.
4. Migrate frame-scoped methods and dictionary ownership.
5. Retarget `Nexus` call sites to the manager.
6. Remove the old in-class state paths from `Nexus`.
7. Validate focused runtime/test behavior.

## Rollback Strategy
- Rollback trigger:
  The refactor leaves partial dual ownership between `Nexus` and the manager.
- Rollback steps:
  1. Stop at the investigation split.
  2. Keep the task notes and patch docs as the bounded migration contract.
  3. Do not ship a partially duplicated ownership model.

## Validation Expectations and Evidence Plan
- Validation item 1:
  `Nexus` no longer owns the descriptor dictionary or direct frame-scoped store
  mutation logic.
- Evidence source 1:
  `src/melder/aether/nexus/nexus.py`
- Validation item 2:
  `FrameDescriptorManager` owns the migrated frame-scoped methods and keeps
  them thread-safe.
- Evidence source 2:
  `src/melder/aether/nexus/frame_descriptor_manager.py`

## Ticket Coverage Map
- Epic:
  EPIC-2026-04-04-frame-descriptor-manager-refactor
- Story:
  STORY-2026-04-04-extract-frame-descriptor-manager
- Tasks:
  - TASK-2026-04-04-migrate-nexus-frame-state-into-frame-descriptor-manager

## Unknowns and Decision Requests
- UNKNOWN:
  Which small façade helpers should stay on `Nexus` after the migration.
- DECISION_REQUEST:
  None yet.

## Context / Handoff Summary
- What changed:
  The manager extraction now has a patch-gated lane.
- What remains:
  Lock the method split and execute the migration.
- Next entrypoint:
  `component_patch_frame_descriptor_manager.md`
