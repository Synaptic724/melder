# ObjectRef (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
ObjectRef is an opaque handle that refers to a real live object inside the
runtime (in-process or across a boundary via a wrapper).

Even if the system avoids calling it a "handle protocol", cross-boundary usage
implies opaque references for stateful objects.

## Proposed Contract (PROPOSED)
- Opaque identifier
  - The caller cannot forge meaning from the id.
- Session-bound by default
  - An ObjectRef is valid only within the session that produced it.
- Maps to a real object
  - The runtime owns the object; the ref is a pointer, not the object itself.
- Supports cleanup
  - Refs can become invalid when scope/session ends or object is cleaned.

## Addressing Variants (UNKNOWN)
Possible ways to locate a target:
- Handle-only addressing (ObjectRef -> live object).
- Tuple addressing (spell_key + scope_id -> creation) for stateless calls.
- Hybrid model where describe uses spell identity and invoke returns refs.

## Open Questions (UNKNOWN)
- Lifetime semantics: session-bound only vs TTL vs explicit release.
- How refs relate to AethericSpace: does the bench store only refs?
- Error taxonomy: what error is returned when a ref is expired?

## Sources
- `context_compass/artifacts/aethericriftticket111.md`
- `context_compass/artifacts/aethericrift_ticket87.md`

