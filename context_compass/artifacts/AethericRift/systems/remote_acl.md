# RemoteTool ACL (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Define the per-RemoteTool ACL concept described in the "AethericRift ACL System
for Remotes" section of the idea tickets.

This is distinct from (but likely interacts with) the Spell/Conduit/Domain/Profile
ACL stack.

## Proposed Model (PROPOSED)
- Each RemoteTool carries an attached RemoteACL descriptor.
- RemoteACL defines:
  - principal filters (agent id, role, group, external principal)
  - operation/transition permissions (allow/deny per action)
  - scope/context constraints (must run in surface X, environment Y, etc.)
  - optional guard predicates derived from runtime state

## Permission Types (PROPOSED)
Minimum permission distinctions called out in the draft:
- view: can discover/inspect the remote descriptor
- invoke: can trigger an operation/transition
- introspect: can query internal state/history
- admin: can change configuration/ACL (very restricted)

## State-Aware Permissions (PROPOSED)
If RemoteTools are modeled as FSM/HSMs:
- Transition-specific ACL rules (per transition).
- Optional state-aware constraints and guard predicates.

## Attachment and Defaults (PROPOSED)
- ACL is specified at remote registration time.
- Provide a fluent/builder style for specifying policies (exact API later).
- Safe default when ACL is missing:
  - non-visible to AI agents unless explicitly opted in
  - visible only to system/human operator identities

## Open Questions (UNKNOWN)
- Is RemoteTool ACL just a special case of Domain/Spell ACL (and should be merged),
  or is it a separate layer?
- How do we compute effective permission when both RemoteACL and Domain/Profile
  tiers apply?
- Does RemoteACL need to reference VIEW/STATE/GRAPH tiers, or does it operate at
  a different granularity?

## Sources
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md` (Remote ACL system section)

