# Frame Link Contract Wiring Architecture Patch

## Objective
Bridge the compiled ACL/frame-link contract foundation into the actual
frame-surface objects so `FrameView` can be created from descriptor truth plus
compiled ACL output.

## Non-Goals
- do not implement the full Nexus canonical holding zone
- do not implement `FrameViewer` query strategies
- do not add event/update stream wiring

## Changed Components
- `src/melder/aether/nexus/rift/frame_link/frame_link.py`
- `src/melder/aether/nexus/rift/frame_link/frame_link_contract.py`
- `src/melder/aether/nexus/rift/frame_viewer/frame_view.py`

## Boundary Rules
- `FrameACLCompiler` remains the owner of compiled ACL truth.
- `FrameLinkContract` remains the frame-scoped effective contract object.
- `FrameLink` and `FrameView` consume derived contract output only.
- `FrameLink` must remain view-safe and must not hold raw runtime objects.
- `FrameView` may translate descriptor records plus compiled access output into
  links, but it must not become a second canonical store.

## Migration Order
1. add the minimal `FrameLinkContract` support needed for safe reuse/cloning
2. wire `FrameLink` to represent one derived link with contract-backed metadata
3. wire `FrameView` to build frame/conduit/spell links from descriptor truth
   plus compiled access output
4. validate with focused unit tests

## Rollback
- remove the new bridge/factory methods and return the files to placeholder-only
  status if the slice proves too coupled to the missing Nexus holding zone
