# Nexus Component Patch

## Before
- Nexus exposes descriptors and ACL configuration separately.
- Consumers must manually bridge descriptor truth, compiler output, and frame-surface projection.

## After
- Nexus exposes thin helpers that project:
  - one `FrameView`
  - one `FrameViewer`
  from descriptor truth plus current ACL configuration.

## Invariants
- Nexus remains a facade, not a second projection engine
- projection remains derived-only
- no raw runtime object exposure
