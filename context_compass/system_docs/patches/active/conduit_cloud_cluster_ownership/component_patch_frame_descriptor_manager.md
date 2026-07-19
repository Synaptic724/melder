# component_patch_frame_descriptor_manager

## Metadata
- Patch ID: conduit_cloud_cluster_ownership
- Component: frame_descriptor_manager
- Status: draft
- Owner: codex
- Created: 2026-05-18T22:47:37Z
- Updated: 2026-05-18T22:47:37Z

## Component Purpose and Boundary
- Current boundary:
  - descriptor publication reads cluster names directly from
    `frame._conduit_clusters`.
- Target boundary:
  - descriptor publication reads cluster names from the frame-owned cloud,
    which is now the real cluster owner.

## Before/After Behavior Summary
- Before:
  - cluster count and names come from frame-owned cluster state
- After:
  - cluster count and names come from cloud-owned cluster state

## Interface Deltas
- Inputs:
  - none
- Outputs:
  - frame payload still reports `cluster_count` and `cluster_names`
- Error semantics:
  - unchanged

## State and Lifecycle Deltas
- Owned state changes:
  - none
- Lifecycle/cleanup changes:
  - none

## Failure Mode Deltas
- New failure mode:
  - none
- Removed failure mode:
  - direct dependency on frame-owned cluster registry
- Changed failure mode:
  - payload reads now depend on cloud availability

## Dependency and Ordering Constraints
1. Cloud must be present while frame descriptors are being refreshed.
2. Payload generation must continue to tolerate zero clusters.

## Validation Expectations
- Test/validation item 1:
  - focused unit validation through frame-manager/descriptor consumers
- Evidence target 1:
  - `tests/unit/melder/aether/test_nexus_frame_manager.py`

## Unknowns and Open Decisions
- UNKNOWN:
  - none
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - descriptor payloads stop reaching into stale frame-owned cluster state
- Remaining risks:
  - other payload builders may still assume direct frame ownership
- Next entrypoint:
  - `component_patch_nexus_frame_manager.md`
