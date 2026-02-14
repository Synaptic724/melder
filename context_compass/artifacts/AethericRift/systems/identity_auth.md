# Identity and Auth (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Define the identity/auth story for Rift:
- internal calls (trusted, in-process)
- external calls (wrappers: HTTP/MCP/etc.)

## Proposed Model (PROPOSED)

### Internal Calls
- Caller provides an explicit profile/principal (RiftProfile or profile_id).
- No token required.

### External Calls
Two ideas appear:
- PROPOSED: RiftAuthKey (stable mapping key) -> profile + allowed domains.
- PROPOSED: RiftSessionToken (session token) -> profile + allowed domains + expiry.

The common requirement:
- Rift must be able to map external credentials into:
  - a principal/profile
  - an allowlist of domains
  - expiry/ttl

## Session Token Mechanics (PROPOSED)
From the session-token drafts:
- Issue a random token.
- Store only SHA256 server-side.
- Bind to profile_id and allowed domains.
- Enforce expiry/ttl and allow rotation/revocation later.

## Open Questions (UNKNOWN)
- Do we want RiftAuthKey and RiftSessionToken as separate layers, or pick one?
- Is there a distinct in-process RiftToken concept, or do profiles cover it?
- How do we bind session identity to CommandOps agent identity (agent id/mission)?

## Sources
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`

