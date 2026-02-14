# AethericSpace (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
AethericSpace is a stateful "bench" that stores real objects produced/consumed
by a caller so multi-step workflows can reuse results over time.

This exists to support "toolchain workflows" rather than only stateless calls.

## Responsibilities (PROPOSED)
- Object arena
  - Store references/handles for objects the caller intentionally keeps.
  - Allow later operations to reference prior results.
- Session/scope coherence
  - Associate stored objects with the session and scope(s) that created/own them.
- Cleanup discipline
  - When a session ends, the bench is cleared.
  - When a scope is disposed, bench entries tied to that scope are cleared.
- Optional bench operations (conceptual)
  - purge, release, snapshot/export (if ever needed; not committed).

## Non-Goals (PROPOSED)
- Not a persistence layer by default.
- Not a "handle protocol framework" as a standalone product.

## Invariants (PROPOSED)
- Objects are never "mystical":
  - If the underlying scope is gone, the bench must not keep pretending the
    object exists.
- Ownership remains with Conduits/Scopes:
  - The bench does not become a second strong owner if that would break lifetime
    rules.

## Open Questions (UNKNOWN)
- Is AethericSpace per-session only, or can a domain host multiple benches?
- Does the bench store only ObjectRefs, or can it also store stable identity
  references (spell lineage keys, etc.)?
- What are the memory/object count limits and eviction policies (if any)?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket111.md`

