# Component Patch: Meld

## Before
- `Meld` can resolve and create/reuse through `meld(...)`.
- No first-class no-create live-creation query exists.

## After
- `Meld` exposes a no-create live-creation probe that:
  - resolves the spell exactly the way `meld(...)` does
  - inspects live runtime storage only
  - produces richer live-status data
  - still supports a bool-shaped "live right now" facade
