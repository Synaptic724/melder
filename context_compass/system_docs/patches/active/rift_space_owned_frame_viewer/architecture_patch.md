# Patch Architecture: RiftSpace-Owned FrameViewer

## Objective
Move live `FrameViewer` assembly out of `Nexus` and into `RiftSpace` so the
room builds the viewer from installed `ViewProjection` objects instead of
receiving a Nexus-built viewer afterward.

## Non-Goals
- Command/codegen redesign.
- Explicit `frame_name` enforcement.
- Compatibility shims for removed viewer-builder methods.

## Boundary
- In scope:
  - `Nexus` projection ownership and viewer-cache seam removal
  - `Rift` refresh/orchestration updates
  - `RiftSpace` generic viewer assembly
  - `StaticRiftSpace` viewer wrapping
  - focused tests/docs
- Out of scope:
  - broader AR room API redesign
  - unrelated ACL model changes

## Invariants
- `Nexus` owns descriptor truth, ACL truth, and projection compilation only.
- `Rift` owns frame contracts and refresh orchestration.
- `RiftSpace` owns live viewer construction and replacement.
- Static viewer composition remains room-local.
- No backward-compat builder/cache seam remains after this slice.

## Required Deltas
- Add room-owned viewer assembly from installed `ViewProjection`s.
- Remove Nexus-owned viewer construction and cache ownership.
- Remove Rift-owned delegation helpers that only forward to Nexus builders.
- Rebuild attached room viewers from projection refresh on ACL change.
