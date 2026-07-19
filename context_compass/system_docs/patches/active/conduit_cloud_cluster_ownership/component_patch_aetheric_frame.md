# component_patch_aetheric_frame

## Metadata
- Patch ID: conduit_cloud_cluster_ownership
- Component: aetheric_frame
- Status: draft
- Owner: codex
- Created: 2026-05-18T22:47:37Z
- Updated: 2026-05-18T22:47:37Z

## Component Purpose and Boundary
- Current boundary:
  - `AethericFrame` owns root conduits, spell/version registries, and also the
    cluster registry directly.
- Target boundary:
  - `AethericFrame` owns root conduit and spell/version registries plus one
    `ConduitCloud`; cluster storage is no longer a frame-owned top-level store.

## Before/After Behavior Summary
- Before:
  - frame allocates `_conduit_clusters`, passes it into the cloud, and cleans
    clusters directly during frame teardown.
- After:
  - frame allocates only the cloud; cloud allocates and cleans cluster state.

## Interface Deltas
- Inputs:
  - `ConduitCloud` no longer receives a prebuilt cluster registry from frame init.
- Outputs:
  - frame no longer exposes direct cluster ownership in its interface surface.
- Error semantics:
  - unchanged

## State and Lifecycle Deltas
- Owned state changes:
  - remove direct frame-owned `_conduit_clusters`
- Lifecycle/cleanup changes:
  - cluster cleanup happens inside cloud cleanup

## Failure Mode Deltas
- New failure mode:
  - none
- Removed failure mode:
  - stale dual-owner assumptions between frame and cloud
- Changed failure mode:
  - cluster misuse now fails through cloud-owned state rather than frame-owned state

## Dependency and Ordering Constraints
1. Frame must construct the cloud before any cluster operations occur.
2. Frame cleanup must call cloud cleanup before dropping borrowed conduit registries.

## Validation Expectations
- Test/validation item 1:
  - targeted mypy on `aetheric_frame.py`
- Evidence target 1:
  - filtered mypy output for `src\\melder\\aether\\aetheric_frame.py`

## Unknowns and Open Decisions
- UNKNOWN:
  - none
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - frame boundary narrows to cloud ownership instead of direct cluster ownership
- Remaining risks:
  - stale direct cluster reads in bounded consumers
- Next entrypoint:
  - `component_patch_conduit_cloud.md`
