# AethericRift (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
AethericRift is the library-level gateway into the living Melder system. It is
explicitly not an endpoint owner: transport, external auth providers, rate
limiting, and serialization live in wrappers outside the rift.

This object is the "entrance" where we apply consistent capability exposure and
authorization decisions before allowing calls into a workspace (domain) and then
into conduits/scopes/creations.

## Responsibilities (PROPOSED)
- Registry
  - Track RiftProfiles (principals).
  - Track RiftDomains (workspaces / remote API surfaces).
  - Track surface attachments (which domains can use which surfaces/conduits).
- Auth / identity mapping
  - Internal calls: accept an explicit principal/profile (no token).
  - External calls: map an auth key or session token to a profile and allowed
    domain ids.
- Routing
  - Resolve (profile, domain) and forward calls synchronously to the domain.
- Top-level authorization gate
  - Enforce effective permission as an intersection of ACL slices (exact slice
    set TBD; see `systems/acl_stack.md`).
- Observability hooks (minimal)
  - Ensure calls can emit audit/transaction events when needed.

## Non-Goals (PROPOSED)
- No worker pools, no internal queues, no background threads.
- No transport ownership (HTTP/MCP/etc. wrappers live outside).
- No sandbox promises; exposure is intentionally powerful when configured.

## Execution Model (PROPOSED)
- All calls execute synchronously on the caller's thread.
- Thread-safety is achieved with minimal locking around registry/auth maps.

## Owned State (PROPOSED)
- Profile registry (profile_id -> RiftProfile).
- Domain registry (domain_id -> RiftDomain).
- Auth/session mapping (token/auth_key -> profile_id + allowed domains + expiry).
- Configuration for ACL evaluation and surface/domain wiring.

## Failure Modes (PROPOSED)
- Unknown domain/profile/token -> AccessDenied / NotFound style error.
- Domain not allowed for profile -> AccessDenied.
- ACL deny -> AccessDenied with a stable reason code.
- Downstream (domain/conduit) unavailable -> ConduitGone / DomainGone semantics.

## Open Questions (UNKNOWN)
- Do we need Rift to be aware of "surfaces" as first-class objects, or is that
  entirely domain-managed?
- Does Rift own session lifecycle (create/close sessions), or do wrappers own it
  and Rift only validates tokens?
- Do we need a separate RemoteSession concept, or do tokens directly authorize
  domain operations?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`

