# Nexus Component Patch

## Before
- Nexus caches projected `FrameView` objects only.

## After
- Nexus also caches projected `FrameViewer` objects.
- viewer cache keys must reflect:
  - projected frame names
  - per-frame current ACL configuration ids
  - downstream contract profile name

## Invariants
- cached viewers are never returned directly
- invalidation is explicit on touched frame/ACL mutation paths
