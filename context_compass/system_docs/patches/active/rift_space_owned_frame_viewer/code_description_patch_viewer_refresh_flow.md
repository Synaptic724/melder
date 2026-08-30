# Code Description Patch: Viewer Refresh Flow Ownership

## Control Flow
1. `Rift.target_frame(...)` or one frame ACL change requests a refresh.
2. `Nexus` compiles fresh `FrameProjectionSet` objects for the affected
   frame/Rift scope.
3. `Rift.refresh_runtime_projections(...)` installs those sets onto the owned
   `RiftSpace`.
4. `RiftSpace` rebuilds its viewer from installed `ViewProjection`s.
5. `StaticRiftSpace` converts the generic viewer into `StaticFrameViewer`
   before storing it.

## Edge Semantics
- Missing projection for a frame remains a hard error.
- No viewer cache survives in `Nexus`.
- `rift_gate` is passed at viewer construction time instead of patched in
  afterward.

## Idempotency / Lifecycle
- Replacing a viewer still cleans the previous attached viewer if the object is
  different.
- Projection replacement still cleans old projection sets before installing new
  ones.

## Non-Goals
- No explicit-frame targeting changes in this patch.
- No command/codegen surface changes in this patch.
