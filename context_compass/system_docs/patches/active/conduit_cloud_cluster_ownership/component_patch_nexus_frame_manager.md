# component_patch_nexus_frame_manager

## Metadata
- Patch ID: conduit_cloud_cluster_ownership
- Component: nexus_frame_manager
- Status: draft
- Owner: codex
- Created: 2026-05-18T22:47:37Z
- Updated: 2026-05-18T22:47:37Z

## Component Purpose and Boundary
- Current boundary:
  - Nexus-managed frame payload assembly reads cluster names directly from
    `frame._conduit_clusters`.
- Target boundary:
  - Nexus-managed frame payload assembly reads cluster names from the
    cloud-owned cluster registry.

## Before/After Behavior Summary
- Before:
  - cluster payload fields come from frame-owned cluster state
- After:
  - cluster payload fields come from cloud-owned cluster state

## Interface Deltas
- Inputs:
  - none
- Outputs:
  - frame payload shape is unchanged
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
1. Cloud must exist before Nexus-managed frame payload assembly runs.
2. Payload generation must still produce stable empty tuples for zero clusters.

## Validation Expectations
- Test/validation item 1:
  - focused unit validation through `test_nexus_frame_manager.py`
- Evidence target 1:
  - `tests/unit/melder/aether/test_nexus_frame_manager.py`

## Unknowns and Open Decisions
- UNKNOWN:
  - none
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - Nexus-managed frame payloads source cluster names from the cloud owner
- Remaining risks:
  - stale tests or support fakes may still assume direct frame cluster ownership
- Next entrypoint:
  - runtime code changes in the bounded ownership files
