# RiftDomain Remote API Contract (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Define the stable operation set and expected semantics for the remote interface
exposed by RiftDomain.

This is a conceptual contract; names and exact payload shapes are not final.

## Proposed Operation Set (PROPOSED)
Recurring set across multiple tickets:
- describe_rift
- list_spells
- describe_spell
- invoke_spell
- get_attr
- set_attr
- list_conduits
- list_open_conduits
- close_conduit

## Shared Rules (PROPOSED)
- All operations are synchronous (no internal worker pools).
- All operations are ACL-gated (effective permission intersection).
- Domain does not own lifetimes; conduit/scope/creation lifetimes rule outcomes.

## Operation Semantics (PROPOSED)

### describe_rift
Intent:
- Describe the domain workspace: identity, surfaces, constraints, and what the
  caller is allowed to see/do (at least at a tier level).

### list_spells
Intent:
- Enumerate the spells/capabilities exposed in this domain.

Notes:
- Listing should reflect the caller's effective visibility (ACL-filtered).

### describe_spell
Intent:
- Return a machine-usable description of a spell's exposed surface:
  - stable identity key(s)
  - available operations/methods
  - readable/writable attributes
  - doc/provenance summaries when available

Notes:
- Underlying inspection artifacts may be "unfiltered" (object-local truth) with
  ACL applied downstream to hide/deny details.

### invoke_spell
Intent:
- Invoke a method/action on a target spell within a selected surface + scope
  context.

Key questions:
- How scope is selected/created for the invocation.
- Whether invocation targets:
  - a spell identity directly (create/resolve a creation), or
  - an existing ObjectRef/handle.

### get_attr / set_attr
Intent:
- Read or write an attribute on a target.

Key questions:
- What is the target model?
  - spell-level attrs vs instance attrs
  - handle-based targeting vs (spell_key, scope_id) targeting
- How attr paths are expressed and validated.

### list_conduits
Intent:
- Enumerate conduits/surfaces attached to the domain (not necessarily open).

### list_open_conduits
Intent:
- Enumerate conduits currently open/active for this domain/session context.

### close_conduit
Intent:
- Domain-level detach/close of a conduit binding (not necessarily full shutdown).

Notes:
- Some drafts frame this as a domain-level operation used to stop using a conduit.
- Actual runtime shutdown may be through control spells, not the domain itself.

## Error Model (UNKNOWN)
We need a stable taxonomy (names placeholder):
- AccessDenied (ACL deny)
- DomainNotFound / SpellNotFound
- ConduitGone / ScopeExpired / CreationGone / ObjectRefExpired
- BadRequest (invalid scope selection, invalid attr path, invalid args)

## Sources
- `context_compass/artifacts/aethericrift_ticket87.md` (operations + semantics sections)
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`

