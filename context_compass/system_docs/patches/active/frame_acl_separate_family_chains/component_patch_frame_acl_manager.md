# Component Patch: FrameACLManager

## Before
- many facades assumed one frame-global bundle chain

## After
- chain/history/current/head operations are explicitly family-aware
- manager can assemble one effective ACL snapshot from selected view/command/codegen
  family chains

## Contract
- manager remains the frame-name -> container owner
- manager does not own chain nodes directly
