# ACL Stack and Tier Model (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Define how capability exposure and authorization decisions are expressed for Rift:
- What layers exist.
- What each layer is responsible for (no overlap).
- How effective permission is computed (intersection).

## Baseline Goals (PROPOSED)
- Explicit exposure: nothing is "accidentally" visible or invokable.
- Intersection semantics: multiple slices can restrict power; a single deny blocks.
- Tier model: reason about capability at a coarse level (VIEW/STATE/GRAPH).
- Works with unfiltered introspection artifacts:
  - object-local profiles are captured without ACL filtering,
  - ACL filtering is applied downstream at Rift/Domain exposure time.

## Layer Variants (Observed in Source Tickets)

### Variant 1 (Spell + Conduit + Remote)
Seen in `aethericrift+aethericspace-ticket101.md`:
- Spell ACLs
- Conduit ACLs
- Remote ACLs (per token/caller slice)

### Variant 2 (Spell + Conduit + Domain + Profile)
Seen in `aethericrift_ticket87.md` and `tickets_aethericRift86-64-54-87.md`:
- SpellACL (spell surface)
- ConduitACL (lifetimes/scopes)
- RiftDomainACL (workspace slice)
- RiftProfileACL (principal caps)

### Variant 3 (Object + Domain + Agent Profile)
Seen in `aethericriftticket85.md`:
- Object ACL (tool definition surface)
- Domain ACL (workspace projection)
- Agent Profile ACL (who is calling)

### Variant 4 (RemoteTool ACL)
Seen in the "Remote ACL system" section of `tickets_aethericRift86-64-54-87.md`:
- RemoteTool carries a RemoteACL at definition time with:
  - principal filters
  - operation-level permissions
  - scope/context constraints
  - guard predicates

## Tier Model (PROPOSED)
Multiple tickets use a three-tier capability framing:
- VIEW: inspect/list/describe (read-only)
- STATE: invoke safe operations, change state, create/destroy instances (bounded)
- GRAPH: structural changes (binding/linking/mutation/ownership transfer)

Note: exact mapping from operations to tiers is not finalized.

## Effective Permission (PROPOSED)
Baseline stance:
- Effective permission is always the intersection of all applicable slices.
- Deny takes precedence over allow.

## Open Questions (UNKNOWN)
- Minimum v1 layer set: do we need all 4 slices (Spell/Conduit/Domain/Profile),
  or can RemoteSession/Domain collapse?
- How deep does ACL need to go:
  - spell-level only, or method/attribute/member-level?
- How do RemoteTool ACLs (FSM transitions) relate to the Spell/Domain ACL stack?
- Defaults: what is the safe default visibility for AI (especially for remotes)?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket85.md`
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`
- `context_compass/artifacts/ai_profile_inventory_ticket_update.md` (unfiltered artifact map principle)

