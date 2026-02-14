# RiftProfile (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
RiftProfile represents the principal ("who") a call is acting as: an AI agent
persona, a human operator, or an external service identity mapped via auth.

Profiles provide global capability caps and domain allowlists so authorization
can be expressed as "profile + domain + operation".

## Responsibilities (PROPOSED)
- Identity
  - profile_id and optional metadata (role/group/category).
- Capability caps
  - Tier-level caps (VIEW / STATE / GRAPH) and other "never allowed" flags.
- Domain access
  - Which domain ids the profile can access at all.
  - Optional per-domain overrides (e.g., VIEW-only in prod, GRAPH in lab).

## Non-Goals (PROPOSED)
- A profile is not a session; it is a stable principal definition.
- A profile does not own transport auth tokens (those map into profiles).

## Owned State (PROPOSED)
- Stable identity fields (ids, labels).
- Capability caps.
- Allowed domain ids and optional per-domain limits.

## Open Questions (UNKNOWN)
- Do we model profiles as pure configuration, or as runtime objects with hooks?
- Do we need both "profile" and "role" layers, or is role a profile attribute?
- How do profiles relate to CommandOps agents and their runtime identity?

## Sources
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`

