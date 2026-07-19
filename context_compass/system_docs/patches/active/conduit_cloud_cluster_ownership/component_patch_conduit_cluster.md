# component_patch_conduit_cluster

## Metadata
- Patch ID: conduit_cloud_cluster_ownership
- Component: conduit_cluster
- Status: draft
- Owner: codex
- Created: 2026-05-18T22:47:37Z
- Updated: 2026-05-18T22:47:37Z

## Component Purpose and Boundary
- Current boundary:
  - `ConduitCluster` owns membership/share state but requires
    `IAethericFrame` to look peers back up.
- Target boundary:
  - `ConduitCluster` owns membership/share state and depends only on a
    cloud-facing conduit lookup surface for peer resolution.

## Before/After Behavior Summary
- Before:
  - join/leave/refresh hooks read `frame._conduits` directly
- After:
  - join/leave/refresh hooks read live peers through `IConduitCloud`

## Interface Deltas
- Inputs:
  - cluster hook host changes from `IAethericFrame` to `IConduitCloud`
- Outputs:
  - no public behavior change
- Error semantics:
  - peer lookup continues to skip missing conduits best-effort

## State and Lifecycle Deltas
- Owned state changes:
  - none
- Lifecycle/cleanup changes:
  - none

## Failure Mode Deltas
- New failure mode:
  - none
- Removed failure mode:
  - stale frame-only dependency for cluster hooks
- Changed failure mode:
  - peer lookup now fails through cloud lookup contract instead of direct dict access

## Dependency and Ordering Constraints
1. Cluster hooks must not reintroduce frame ownership through backdoor field access.
2. Cloud must expose enough lookup truth for join/leave/refresh operations.

## Validation Expectations
- Test/validation item 1:
  - targeted mypy on `conduit_cluster.py`
- Evidence target 1:
  - filtered mypy output for `src\\melder\\aether\\conduit\\conduit_cluster.py`

## Unknowns and Open Decisions
- UNKNOWN:
  - none
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - cluster hooks use the actual orchestrator host instead of the stale frame seam
- Remaining risks:
  - transfer/descriptor consumers that still think clusters are frame-owned
- Next entrypoint:
  - `component_patch_frame_descriptor_manager.md`
