# Component Patch: Rift

## Before
- can create a multi-frame viewer through Nexus
- no explicit frame-specific viewer transaction

## After
- checks `FrameLinkContract` for a requested frame
- creates one frame-specific viewer transaction through Nexus only when the
  contract allows that frame
