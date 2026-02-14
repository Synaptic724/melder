# RiftSurface (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
A RiftSurface is a named execution reality for Rift operations. It typically
corresponds to:
- a Conduit, or
- a surrogate/curated Conduit that presents a controlled view of a deeper system.

Surfaces exist so a single Rift can expose multiple environments (dev/lab/prod)
without losing clarity about where an operation runs and what existence/lifetime
rules apply.

## Responsibilities (PROPOSED)
- Identity
  - Stable surface_id and human-friendly name.
- Binding to runtime
  - Resolve to a specific Conduit (or surrogate) at execution time.
- Policy surface
  - Carry environment-level constraints (e.g., which scopes are allowed, what
    kinds of operations are permitted in this surface).

## Notes on Surrogate Conduits (PROPOSED)
Some tickets recommend surrogate conduits as the "front-stage" surface form:
- Surrogate conduits present curated views/behaviors.
- The underlying raw conduits still exist, but are not exposed directly.

## Non-Goals (PROPOSED)
- A surface is not an endpoint, not a network binding.
- A surface does not redefine Melder semantics; it selects which Conduit reality
  applies.

## Open Questions (UNKNOWN)
- Is RiftSurface a first-class runtime object in v1, or just config on RiftDomain?
- Are surrogate conduits required for production surfaces, or only recommended?
- How is surface identity represented when multiple conduits map to one surface?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket111.md`

