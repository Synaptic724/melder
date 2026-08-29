# Nexus Component Patch

## Before
- Nexus projects `FrameView` objects on demand every call.

## After
- Nexus caches projected `FrameView` objects by a stable cache key and returns
  detached clones.
- Nexus invalidates cached entries on touched descriptor and ACL mutation paths.

## Invariants
- no shared cached object is returned directly to callers
- invalidation may be broader than strictly necessary, but must be correct
