# Frame Link Contract And Viewer Cache Architecture Patch

## Objective
Finish the current frame-surface contract/viewer layer with:
- real `FrameLinkContract` helper APIs
- cached Nexus `FrameViewer` projection

## Non-Goals
- no search DSL
- no subscription/update push model
- no holding-zone redesign

## Changed Components
- `src/melder/aether/nexus/rift/frame_link/frame_link_contract.py`
- `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
- `src/melder/aether/nexus/nexus.py`

## Boundary Rules
- helper APIs should expose stable consumer-facing contract semantics, not raw
  metadata passthrough only
- cached viewers must return detached clones
- invalidation may be broad but must be correct on touched paths

## Migration Order
1. add contract helper APIs
2. add viewer clone support
3. add Nexus viewer cache
4. invalidate cached viewers on touched descriptor/ACL mutation paths
5. validate the slice
