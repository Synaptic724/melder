# Component Patch: FrameViewerProfile

## Before
- reusable tool map only
- no frame-bound state

## After
- reusable template still exists
- selected clones may be bound by reference to:
  - frame name
  - frame descriptor
  - frame ACL configuration
  - compiled ACL surface
- binding validates expected ACL-view profile label/version when configured
