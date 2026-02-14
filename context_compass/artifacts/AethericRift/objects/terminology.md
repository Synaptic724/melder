# Terminology (Working)

## Purpose
The source tickets use overlapping words ("remote", "domain", "surface") with
different meanings. This file proposes a stable vocabulary so the rest of the
docs can be precise.

## Proposed Vocabulary (PROPOSED)
- Rift: The library-level gateway into the living Melder system. (AethericRift)
- Domain: A workspace/view that exposes a curated remote API surface. (RiftDomain)
- Surface: A named execution reality (typically backed by a Conduit or surrogate).
- Session: The unit of interaction ownership (lifetime, cleanup, auth binding).
- Scope: A lifetime envelope inside a Conduit (existing Melder concept).
- Creation: A realized object inside a Conduit/Scope (existing Melder concept).
- AethericSpace: A stateful "bench" for holding objects/results across steps.
- ObjectRef: An opaque handle to a live object (usually session-bound).

## Ambiguous Terms (Known Conflicts)
- "Remote"
  - In `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`, "Remote" is
    a permission-bearing session view derived from a RiftToken.
  - In `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`, "Remote" is a
    stateful tool object (often modeled as an FSM/HSM) with an attached RemoteACL.
  - In `context_compass/artifacts/aethericrift_ticket87.md`, the remote interface is
    primarily described as RiftDomain operations, not a separate "remote" object.

## Proposed Disambiguation (PROPOSED)
- RemoteSession: A session-bound view for a caller (keycard/session semantics).
- RemoteTool: A stateful exposed tool object (FSM/HSM) that carries a RemoteACL.

## Open Questions (UNKNOWN)
- Do we actually need both RemoteSession and RemoteTool as first-class objects,
  or should one concept collapse into RiftDomain + Spell exposure?
- Is a "surface" always just a Conduit, or do we need an explicit surrogate
  conduit abstraction in v1?

## Sources
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket85.md`
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/aethericriftticket111.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`

