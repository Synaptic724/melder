# Nexus Frame Surface Projection Cache Architecture Patch

## Objective
Add a small Nexus-local cache for projected `FrameView` objects with explicit
invalidation on descriptor and ACL changes.

## Non-Goals
- no dedicated new projection manager
- no `FrameViewer` cache
- no subscription/push update model
- no holding-zone redesign

## Changed Components
- `src/melder/aether/nexus/nexus.py`
- `src/melder/aether/nexus/rift/frame_viewer/frame_view.py`
- `src/melder/aether/nexus/rift/frame_link/frame_link.py`

## Boundary Rules
- cache only one canonical projected `FrameView` per cache key
- returned values must be detached clones, never the cache-owned instance
- invalidation must be explicit on every touched descriptor/ACL mutation path

## Cache Key
- `frame_name`
- current ACL `configuration_id`
- downstream `contract_profile_name` or empty string

## Migration Order
1. add clone support where needed
2. add cache storage on Nexus
3. add invalidation helper(s)
4. call invalidation from touched descriptor/ACL mutation paths
5. validate the slice
