# RiftConduit (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Some drafts define a RiftDomain as backed by a "RiftConduit": a primary DI
universe that owns canonical references, scopes, and the live objects the domain
routes to.

This may be:
- a thin wrapper around an existing Melder Conduit, or
- just the Conduit itself (no new wrapper type).

## Responsibilities (PROPOSED)
- Own the strong references to live objects (creations) produced for the domain.
- Own scope lifetimes (create/close scopes, clear a scope's objects).
- Provide the execution reality used by RiftDomain invoke/get/set operations.

## Relationship to RiftDomain (PROPOSED)
- Domain is a view/router and does not own lifetimes.
- RiftConduit (or Conduit) owns lifetimes and cleanup.

## Known Conflicts (UNKNOWN)
- Some tickets avoid inventing a RiftConduit type and rely on existing Conduit.
- Some tickets want RiftConduit/RiftLesserConduit as explicit objects for
  conceptual clarity and lifetime management.

## Open Questions (UNKNOWN)
- Do we create a distinct RiftConduit type in v1, or treat it as a domain binding
  to a Conduit?
- If distinct, what does it add beyond naming/metadata?
- How do "surrogate conduits" relate to RiftConduit?

## Sources
- `context_compass/artifacts/aethericriftticket85.md`

