# Frame Link Component Patch

## Before
- `FrameLink` is a passive placeholder with no bridge from compiled ACL output.

## After
- `FrameLink` can be created from derived frame-surface inputs that already
  respect the effective `FrameLinkContract`.
- The object remains view-safe and carries only stable ids, display names,
  contract, and derived metadata.

## Invariants
- no raw runtime object references
- cleanup remains idempotent
- if multiple links need the same effective contract, each link must own a safe
  detached contract object or a clearly non-owning reference contract
