# Nexus Frame Projection Code Description Patch

## Control Flow
1. resolve descriptor from `FrameDescriptorManager`
2. resolve current ACL configuration from `FrameACLManager`
3. compile the current access surface
4. project a `FrameView`
5. if requested, assemble one `FrameViewer`

## Error Semantics
- missing frame descriptors should fail fast
- invalid profile names should fail fast
- frame-name mismatches should fail fast

## Non-Goals
- no caching layer
- no update subscriptions
- no holding-zone rewrite
