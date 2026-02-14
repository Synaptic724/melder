# RiftDomain (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
RiftDomain is the workspace/view that exposes the remote API surface the caller
actually uses. It presents a curated projection of spells and conduits, and
translates generic operations (invoke/get/set/describe) into real work executed
through Conduits, Scopes, and Creations.

## Core Constraints (PROPOSED)
- RiftDomain does not own lifetimes.
  - Conduits/Scopes own strong references and cleanup.
  - Domain may keep weakrefs/caches for efficiency only.
- No internal worker pools or queues; synchronous facade.
- Re-entrant and thread-safe via minimal locking around internal maps.

## Responsibilities (PROPOSED)
- Static registry
  - Which spells are exposed in this domain (spell_key -> descriptor).
  - Which conduits/surfaces are attached (conduit_id/surface_id -> binding).
  - Domain ACL slice (what is visible/allowed in this workspace).
- Dynamic working set (optional)
  - Weakrefs to recently used objects (by handle id, or by (spell_key, scope_id)).
  - Cached member descriptors (allowed attrs/methods) for faster describe/invoke.
- Remote API implementation
  - See `systems/remote_api_contract.md` for the proposed operation set and
    semantics.

## Suggested Remote API Surface (PROPOSED)
The recurring operation set across tickets:
- describe_rift
- list_spells
- describe_spell
- invoke_spell
- get_attr
- set_attr
- list_conduits
- list_open_conduits
- close_conduit

## Owned State (PROPOSED)
- Exposed spell registry and descriptors.
- Conduit/surface attachment registry.
- Domain ACL slice/config.
- Optional caches: weakref maps, descriptor caches, per-session accelerators.

## Invariants (PROPOSED)
- Domain never keeps the only strong reference to a live creation.
- Domain must tolerate conduit/scope cleanup at any time.
- All access goes through ACL evaluation before touching live objects.

## Failure Modes (PROPOSED)
- AccessDenied (ACL intersection deny).
- SpellNotFound (spell_key not exposed in this domain).
- ConduitGone / ScopeExpired / CreationGone (target went away).
- BadRequest (invalid args, invalid scope selection, invalid attr path).

## Open Questions (UNKNOWN)
- Scope selection semantics for invoke_spell (existing vs new, caller intent).
- Attr targeting semantics (spell-level vs instance-level; handle vs key tuple).
- Domain lifecycle: who creates/destroys domains (static vs per-mission).

## Sources
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`
- `context_compass/artifacts/aethericriftticket85.md`

