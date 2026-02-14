# RemoteTool (Object)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Some tickets use "Remote" to mean a stateful exposed tool object (not a session).
The mental model is: remotes are objects (often state machines) that AI drives,
instead of directly poking raw services.

This doc captures that idea as "RemoteTool" to disambiguate it from a session.

## Proposed Shape (PROPOSED)
- A RemoteTool is a first-class object registered with AethericRift.
- It has a descriptor:
  - remote_id, name, category
  - state machine definition (states, transitions) when applicable
  - exposed operations/transitions
  - attached RemoteACL (who can view/invoke/introspect/admin)

## Relationship to RiftDomain / Spells (UNKNOWN)
Open design question: is a RemoteTool distinct from a spell/creation, or is it
simply a curated projection of spells into a tool namespace?

Both ideas appear in the source tickets.

## Open Questions (UNKNOWN)
- Do we want RemoteTools in v1, or do domains + spell exposure cover the need?
- If RemoteTools exist, are they implemented as:
  - a wrapper around spells/creations, or
  - separate orchestrator objects that call underlying spells?
- How does RemoteTool interact with the VIEW/STATE/GRAPH tier model?

## Sources
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md` (Remote ACL system section)

