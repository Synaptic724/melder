# Identity and Sessions (Objects)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose
Consolidate the identity/session/token concepts referenced across the idea
tickets. Names and exact mechanics are not final.

## Concepts (PROPOSED)

### Internal Identity (Profile)
- PROPOSED: In-process/trusted callers pass a RiftProfile (or profile_id)
  explicitly, without tokens.

### External Identity (Auth Key)
- PROPOSED: At a network/API boundary, a simple auth key maps to a profile and
  allowed domains.
- Candidate names in tickets:
  - RiftAuthKey (mapping key)
  - RiftSessionToken (session token)

### Session Token (RiftSessionToken) (PROPOSED)
Some tickets propose a per-session token:
- Random token issued to a caller.
- Store SHA256 server-side (do not store raw token).
- Token maps to:
  - profile_id
  - allowed domain ids
  - expiry/ttl

### RiftToken + RemoteSession (PROPOSED)
Some tickets propose a capability grant object (RiftToken) and a "keycard"
session view (Remote):
- RiftToken is an in-process capability grant (not a transport credential).
- A RemoteSession is derived from the RiftToken and rift configuration and
  carries an effective permission profile.

## Known Conflicts (UNKNOWN)
- Is RiftToken a separate concept from RiftSessionToken, or are they the same
  thing described at different layers (in-process vs over-the-wire)?
- Is "Remote" a session view, or an exposed tool object? (See terminology doc.)
- Do we want long-lived sessions at all in v1, or is a stateless adapter enough?

## Open Questions (UNKNOWN)
- Token lifecycle: rotation, revocation, multi-device/multi-wrapper behavior.
- What minimum identity fields are required for ACL evaluation and audit events?
- How does session identity map to CommandOps agent identity (agent id, mission)?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`

