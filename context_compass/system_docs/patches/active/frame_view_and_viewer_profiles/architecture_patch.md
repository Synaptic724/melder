# Frame View And Viewer Profiles Architecture Patch

## Objective
Add the first profile foundations for `FrameView` and `FrameViewer` so the
read-side surface is configurable through bounded modifiers over a shared
viewer model.

## Non-Goals
- no full command catalog
- no search DSL
- no separate behavior engine per profile

## Changed Components
- `src/melder/aether/nexus/rift/frame_viewer/`

## Boundary Rules
- profiles modify defaults and enabled capability sets over the shared viewer
  surface
- profiles do not redefine permissions
- profiles do not create brand new viewer paradigms

## Migration Order
1. add minimal profile objects
2. add one seeded `general` posture
3. add simple builder/catalog foundations
4. validate the slice
