# Patch Architecture: Atomic ACL Projection Refresh Barrier

## Objective
Lift the current correct single-frame ACL refresh barrier into one reusable
batch refresh path across the union of impacted `Rift`s.

## Non-Goals
- Redesigning `RiftGate`.
- Redesigning `RiftSpace` merge/rebuild ownership.
- Redesigning command, viewer, or workstation public APIs.

## Boundary
- In scope:
  - `Nexus` batch refresh orchestration
  - `Rift` multi-frame projection refresh
  - focused tests and matching AR docs
- Out of scope:
  - room/viewer redesign
  - broader ACL model changes

## Invariants
- `RiftGate` remains Rift-scoped.
- New admission is blocked before projection refresh starts.
- In-flight guarded work is allowed to drain before projection swaps occur.
- Each impacted Rift is refreshed once per batch.
- Each impacted room merges once and rebuilds once per batch.
- The single-frame ACL callback path becomes a thin delegate into the batch
  primitive.

## Required Deltas
- Add one Nexus batch refresh helper over changed frame names.
- Add one Rift multi-frame refresh path.
- Extend `Nexus.create_frame_projection_sets_for_rift(...)` to accept a
  multi-frame scope.
- Reuse `RiftSpace.replace_projection_sets(..., merge=True)` and
  `_rebuild_frame_viewer(...)` as the one-shot room path.
