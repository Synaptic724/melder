# architecture_patch

## Metadata
- Patch ID: conduit_cloud_cluster_ownership
- Status: draft
- Owner: codex
- Created: 2026-05-18T22:47:37Z
- Updated: 2026-05-18T22:47:37Z

## Patch Scope and Non-Goals
- Objective:
  - move conduit-cluster ownership and lifecycle into `ConduitCloud`
  - remove the stale `IAethericFrame` hook dependency from `ConduitCluster`
  - keep `Aether` unchanged in this stage
- Non-goals:
  - no `Aether` cluster API removal in this slice
  - no broader conduit/aether owner decomposition outside cluster services

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| aetheric_frame | modify | frame should own the cloud, not the cluster registry | conduit_cloud |
| conduit_cloud | modify | cloud becomes the real cluster owner and orchestration host | conduit_cluster |
| conduit_cluster | modify | cluster should depend on a cloud-facing host, not a frame | conduit_cloud |
| frame_descriptor_manager | modify | descriptor payloads must source cluster names from the cloud | conduit_cloud |
| nexus_frame_manager | modify | Nexus-managed frame payloads must source cluster names from the cloud | conduit_cloud |

## Interface and Boundary Deltas
- Boundary delta 1:
  - `AethericFrame` retains ownership of root conduit and spell/version
    registries, but cluster registry ownership moves into `ConduitCloud`.
- Boundary delta 2:
  - `ConduitCluster` stops depending on `IAethericFrame` and instead consumes
    only the cloud-facing conduit lookup surface it actually needs.
- Interface delta 1:
  - `IConduitCloud` grows cluster-name/frame-name lookup needed by cluster and
    descriptor consumers.
- Interface delta 2:
  - `IAethericFrame` stops advertising direct cluster ownership.

## Cross-Component Invariants
- `Aether` is not changed in this stage.
- `ConduitCloud` remains frame-scoped and must not grow into a root service
  locator.
- `ConduitCluster` owns membership/share state only; live conduit lookup flows
  through the cloud.
- Descriptor and Nexus-manager payload generation still reports cluster names
  from the live frame-scoped runtime truth.

## Migration and Rollout Order
1. Move cluster storage/cleanup ownership into `ConduitCloud`.
2. Retarget `ConduitCluster` hook signatures from frame to cloud.
3. Redirect bounded consumers from `frame._conduit_clusters` to the cloud.
4. Run focused validation on the ownership slice.

## Rollback Strategy
- Rollback trigger:
  - one bounded consumer proves to require direct frame-owned cluster state
    rather than a cloud-facing view
- Rollback steps:
  - revert the cluster-store move
  - restore the prior frame-owned cluster registry
  - keep any pure typing/doc improvements only if still truthful
- Post-rollback verification:
  - focused mypy and the touched unit ring return to the pre-slice baseline

## Validation Expectations and Evidence Plan
- Validation item 1:
  - targeted mypy on `aetheric_frame.py`, `conduit_cloud.py`,
    `conduit_cluster.py`
- Evidence source 1:
  - targeted mypy output filtered to those files
- Validation item 2:
  - focused unit test ring for frame-descriptor/Nexus consumers
- Evidence source 2:
  - `tests/unit/melder/aether/test_nexus_frame_manager.py`

## Ticket Coverage Map
- Epic:
  - `tickets/epics/2026-05-18_recompose_conduit_aether_spellbook_runtime_ownership_epic.md`
- Story:
  - none
- Tasks:
  - `tickets/tasks/2026-05-18_move_conduit_cluster_ownership_into_conduit_cloud_task.md`

## Unknowns and Decision Requests
- UNKNOWN:
  - whether any deferred `Aether` cluster helper callers outside this slice
    still need redirection later
- DECISION_REQUEST:
  - none at patch entry

## Context / Handoff Summary
- What changed:
  - this patch lane defines the stage-2 conduit-network owner move only
- What remains:
  - later `Aether` helper removal and any broader root-owner cleanup
- Next entrypoint:
  - `component_patch_conduit_cloud.md`
