# Component Patch: Nexus

## Before
- `create_rift(...)` finalizes Rift configuration and validates target-frame legality immediately.
- Bare Rift creation and target-frame selection are collapsed into one step.

## After
- `create_rift(...)` builds a bare Rift only.
- Target-frame legality remains Nexus-owned, but is consumed later by an explicit Rift targeting action.
- Viewer projection remains descriptor + current ACL derived through Nexus.
