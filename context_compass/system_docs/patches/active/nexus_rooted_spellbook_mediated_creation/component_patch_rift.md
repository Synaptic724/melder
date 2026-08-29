# Component Patch: Rift Nexus Creation Return Shape

## Before
- `Rift.create_nexus_frame(...)` delegates to Nexus and returns the managed
  frame object.

## After
- `Rift.create_nexus_frame(...)` delegates to Nexus and returns the rooted
  conduit produced by the Nexus-managed creation path.
- The caller gets an immediately usable conduit/workspace anchor instead of a
  frame shell.

## Validation Expectation
- Focused tests prove the Rift-facing Nexus creation surface returns the rooted
  conduit and preserves topology behavior by mode.
