# Patch Architecture: NexusFrameManager Mode-Constrained Creation

## Objective
Constrain raw `NexusFrameManager` authoring so the manager cannot create
Nexus-managed frames in ways that contradict the active
`single` / `indexed` / `one_per_workspace` behavior model.

## Non-Goals
- Auto-provisioning Nexus frames.
- Changing the Rift-facing Nexus creation and targeting APIs.
- Designing a new owner-aware raw builder API in this patch.

## Boundary
- In scope:
  - raw `NexusFrameManager.create(...)`
  - raw `NexusFrameManager.create_dynamic_frame(...)`
  - mode-aware validation on those paths
  - focused tests/docs
- Out of scope:
  - `create_frame_for_rift(...)`
  - `get_frame_for_rift(...)`
  - frame-link authorization
  - broader frame-builder redesign

## Invariants
- Frame creation remains explicit; no hidden provisioning.
- Rift-facing mode-aware behavior remains unchanged.
- `single` may expose only the canonical shared Nexus-managed frame name.
- `one_per_workspace` requires Rift-owned private-frame semantics and therefore
  should not be creatable through the ownerless raw manager path.
- `indexed` remains the permissive many-named-frame mode.

## Required Deltas
- Add mode-aware validation before raw manager creation is allowed.
- In `single`, allow only the configured shared default frame name.
- In `one_per_workspace`, fail fast on raw manager creation and direct callers
  toward Rift-scoped creation.
- In `indexed`, keep explicit named creation allowed.
