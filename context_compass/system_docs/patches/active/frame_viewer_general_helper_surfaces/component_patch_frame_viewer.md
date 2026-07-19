# Component Patch: FrameViewer

## Before
- viewer executes flat host methods mapped directly from profile tool names

## After
- viewer still routes one selected profile per frame
- the single `general` profile uses helper-object methods for frame, conduit,
  and spell inspection
- ACL filtering remains driven by the compiled access surface
