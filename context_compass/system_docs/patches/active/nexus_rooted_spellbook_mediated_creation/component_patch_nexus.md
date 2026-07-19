# Component Patch: Nexus Frame Creation Grammar

## Before
- `Nexus.create_nexus_frame_for_rift(...)` returns a frame and relies on the
  frame manager’s frame-first realization path.

## After
- `Nexus.create_nexus_frame_for_rift(...)` returns the rooted conduit created
  through the Spellbook-mediated Nexus path.
- Nexus remains the owner of topology and naming policy, but no longer exposes
  frame-first empty-shell creation as the public result.

## Validation Expectation
- Focused tests prove the Nexus-facing public creation grammar is rooted,
  Spellbook-mediated, and conduit-returning.
