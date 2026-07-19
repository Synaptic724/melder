# Component Patch: Rift

## Before
- `Rift` exposed frame targeting, frame access, and room management but no
  direct conduit-discovery facade surface.

## After
- `Rift` exposes conduit-discovery helpers that resolve a target frame and
  delegate to `Aether` / `ConduitCloud`.

## Contract
- `Rift` is a facade only.
- When `frame_name` is omitted, it resolves through the current target-frame
  defaults.
- Missing/ambiguous default target frame state fails fast.

## Validation Expectations
- Focused Rift/Nexus tests should prove default-frame resolution and delegated
  discovery behavior.
