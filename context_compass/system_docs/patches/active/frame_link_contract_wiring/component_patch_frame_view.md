# Frame View Component Patch

## Before
- `FrameView` is a passive placeholder with no contract-aware construction path.

## After
- `FrameView` can be built from descriptor truth plus compiled ACL output.
- The view translates only visible frame/conduit/spell surfaces into
  `FrameLink` objects.
- The view remains a derived projection, not a second canonical store.

## Inputs
- `FrameDescriptor`
- `CompiledFrameACLAccessSurface`
- optional downstream `FrameLinkContractProfile`

## Output
- one frame-scoped `FrameView` containing only visible `FrameLink` objects
  keyed by link id
