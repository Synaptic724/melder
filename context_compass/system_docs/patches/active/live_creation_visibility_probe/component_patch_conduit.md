# Component Patch: Conduit

## Before
- `Conduit` exposes `meld(...)` but no first-class no-create liveness query.

## After
- `Conduit` exposes `has_live_creation(...)` as the public facade.
- `Conduit` also exposes `describe_live_creation_status(...)` for richer
  runtime diagnostics.
- The facade delegates to `Meld` and does not own lookup/storage logic itself.
