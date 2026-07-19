# Nexus Frame Surface Projection Architecture Patch

## Objective
Expose the first thin Nexus facade that projects `FrameView` and
`FrameViewer` objects from descriptor truth plus current ACL configuration.

## Non-Goals
- no new standalone projection manager
- no update subscription model
- no search DSL
- no raw runtime-object exposure

## Changed Components
- `src/melder/aether/nexus/nexus.py`

## Boundary Rules
- Nexus remains the facade root only.
- Descriptor truth stays in `FrameDescriptorManager`.
- ACL truth stays in `FrameACLManager` + `FrameACLCompiler`.
- `FrameView` and `FrameViewer` remain derived consumer-facing objects.

## Migration Order
1. add thin Nexus helpers to resolve descriptors + current ACL config
2. compile access output
3. project a `FrameView`
4. optionally assemble a `FrameViewer`
5. validate the bridge with focused tests
