# component_patch_conduit_cloud

## Metadata
- Patch ID: conduit_cloud_cluster_ownership
- Component: conduit_cloud
- Status: draft
- Owner: codex
- Created: 2026-05-18T22:47:37Z
- Updated: 2026-05-18T22:47:37Z

## Component Purpose and Boundary
- Current boundary:
  - `ConduitCloud` is the public cluster API surface but borrows the actual
    cluster store from `AethericFrame`.
- Target boundary:
  - `ConduitCloud` owns cluster registry state and all cluster lifecycle
    orchestration while still borrowing root conduit registries from the frame.

## Before/After Behavior Summary
- Before:
  - cloud owns cluster methods but not cluster storage
- After:
  - cloud owns both cluster methods and cluster storage

## Interface Deltas
- Inputs:
  - constructor drops borrowed cluster-registry injection
- Outputs:
  - expose cluster-name listing and frame-name access needed by bounded consumers
- Error semantics:
  - cluster lookup and cleanup stay value-error/idempotent

## State and Lifecycle Deltas
- Owned state changes:
  - `_conduit_clusters` becomes cloud-owned state
- Lifecycle/cleanup changes:
  - cloud cleanup now cleans owned clusters before dropping the store

## Failure Mode Deltas
- New failure mode:
  - none
- Removed failure mode:
  - split ownership between frame and cloud
- Changed failure mode:
  - cluster lifecycle bugs now collapse to one owner

## Dependency and Ordering Constraints
1. Cloud may borrow root conduit registries but must not own conduit lifecycle.
2. Cluster helpers must only rely on cloud-facing lookup surfaces.

## Validation Expectations
- Test/validation item 1:
  - targeted mypy on `conduit_cloud.py`
- Evidence target 1:
  - filtered mypy output for `src\\melder\\aether\\conduit_cloud.py`

## Unknowns and Open Decisions
- UNKNOWN:
  - none
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - cloud becomes the real cluster owner instead of a facade over frame-owned state
- Remaining risks:
  - consumer files still reaching around the cloud
- Next entrypoint:
  - `component_patch_conduit_cluster.md`
