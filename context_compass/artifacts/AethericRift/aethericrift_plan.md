# AethericRift Plan (Working Artifact)

## Status
- Status: draft
- Updated: 2026-01-24
- Owner: TBD

## Purpose
Create one coherent, reviewable plan for AethericRift (and adjacent concerns like
AethericSpace + ACL + audit ledger) from months of partial idea tickets.

This file is the "single page" we use to converge the design into explicit
decisions, then split implementation into smaller tickets.

## Rules (So We Do Not Lie To Ourselves)
- This doc is a working artifact, not an approved spec.
- Everything is tagged as one of: PROPOSED, DECIDED, UNKNOWN.
- "DECIDED" only exists when the user explicitly confirms it in-session.
- Once a section is DECIDED, we copy the decision into the active tickets in:
  - `context_compass/epics/`
  - `context_compass/stories/`
  - `context_compass/tasks/`

## Sources (Idea Pile, Not Truth)
These are inputs. They contain drift and contradictions.
- `context_compass/artifacts/aethericrift+aethericspace-ticket101.md`
- `context_compass/artifacts/aethericriftticket85.md`
- `context_compass/artifacts/aethericrift_ticket87.md`
- `context_compass/artifacts/aethericriftticket111.md`
- `context_compass/artifacts/tickets_aethericRift86-64-54-87.md`
- `context_compass/artifacts/transaction_audit_ledger.md`

Active planning tickets we will eventually align to:
- Epic: `context_compass/epics/2026-01-23_aethericrift_acl_alignment_epic.md`
- Story: `context_compass/stories/2026-01-23_aethericrift_design_discussions_story.md`
- Tasks: `context_compass/tasks/2026-01-23_*_task.md`

## Current Goal (This Week)
Produce a consistent, minimal "Most Reasonable Product" design that we can
implement without rewriting the core later.

Output target: a stable set of decisions for each axis:
- Core objects
- Exposure model
- ACL stack
- Runtime semantics
- Interaction modes
- Identity/auth
- Audit ledger
- Governance modes

## Design Axes (Working Strawman)

### Axis A: System Boundary and Responsibility Split
- PROPOSED: AethericRift is a library-level gateway. It does not own transport.
- PROPOSED: "Wrappers" (HTTP/MCP/etc.) own endpoint concerns (auth, rate limits,
  serialization, protocol semantics).
- PROPOSED: Melder remains the substrate (lineages, conduits, scopes, existence,
  linking, cleanup).
- PROPOSED: CommandOps owns governance/scheduling culture (missions/agents).
- UNKNOWN: Which parts of "governance" must be enforced inside Rift vs left to
  outer wrappers or CommandOps.

### Axis B: Core Object Model (Names Are Placeholder)
- PROPOSED: AethericRift (control plane / router / capability gateway)
- PROPOSED: RiftDomain (workspace/view; remote API surface; does not own lifetimes)
- PROPOSED: RiftProfile (principal / role; global capability caps)
- PROPOSED: RiftSurface (named execution reality, typically backed by a Conduit)
- PROPOSED: Scope (lifetime envelope inside a Conduit; always relevant)
- PROPOSED: AethericSpace (bench/object arena for stateful workflows)
- PROPOSED: ObjectRef (opaque handle to a live object in a scope/session)
- UNKNOWN: Which of these must be first-class objects in v1 vs implied by config.

### Axis C: Exposure Model
- PROPOSED: There is a conduit-agnostic "catalog" for discoverability.
- PROPOSED: Exposure is anchored to lineage identity by default (not version id).
- PROPOSED: Conduit/surface chooses the living version at execution time unless
  explicitly pinned.
- UNKNOWN: Whether "surrogate conduits" are required for curated surfaces or just
  recommended.
- UNKNOWN: How to keep surface identity comprehensible across multiple conduits.

### Axis D: Interaction Modes
- PROPOSED: Workstation/REPL mode: stateful bench + multi-step workflows.
- PROPOSED: Static exposure mode: curated call-only surface (still sessioned).
- PROPOSED: Both modes compile to a single internal CallSpec-like representation.
- UNKNOWN: Whether static mode requires an explicit session or allows an
  adapter-driven ephemeral session per call.

### Axis E: Runtime Semantics (Operations, Scopes, Execution)
- PROPOSED: Rift never bypasses conduit/scope semantics; all work happens in a
  surface + scope context.
- PROPOSED: "Describe/list/invoke/get_attr/set_attr" exist as conceptual ops.
- UNKNOWN: Scope selection rules for invoke (pick existing scope, create new,
  how caller expresses intent).
- UNKNOWN: Whether Rift itself ever queues or runs parallel work, or whether that
  is entirely owned by CommandOps/wrappers.

### Axis F: ACL Stack and Tiers
- PROPOSED: Effective permission is an intersection of multiple ACL slices.
- PROPOSED: Tier model exists (VIEW / STATE / GRAPH) to reason about capability.
- UNKNOWN: Exact slice set (spell vs lineage vs conduit vs domain vs profile) and
  the minimum v1 we can ship without painting ourselves into a corner.
- UNKNOWN: How attribute/method/member-level ACLs map onto the existing Melder
  inspection/profile artifacts.

### Axis G: Identity/Auth
- PROPOSED: Internal calls can pass a profile/principal directly (no token).
- PROPOSED: External calls can map a token (RiftAuthKey or session token) to a
  profile and allowed domains.
- UNKNOWN: Token lifecycle, rotation, and revocation model (philosophical only).

### Axis H: Audit Ledger / Transaction Model
- PROPOSED: We need append-only audit events for bind/link/ownership/permission.
- PROPOSED: Events are machine-queryable and correlated by txn_id + parent links.
- UNKNOWN: Initial persistence backend (JSONL vs SQLite vs in-memory + flush).
- UNKNOWN: Where the actor/conduit context is sourced in-process (thread local,
  explicit parameter, or wrapper injection).

### Axis I: Governance / AI Usage Modes
- PROPOSED: We care about four usage modes: observation, intervention,
  reconstruction, mutation.
- UNKNOWN: Which mode boundaries are enforced by ACL tiers vs by explicit domain
  wiring vs by CommandOps policy.

## Consolidation Work Plan (No Code Yet)
1) Extract contradictions across the artifacts per axis.
2) For each axis, write a 1-2 page "decision proposal" section here with:
   - options
   - tradeoffs
   - recommended default
   - explicit open questions
3) Walk it with the user and mark DECIDED items explicitly.
4) Copy DECIDED items into the active `context_compass/tasks/` tickets.
5) Only then: create implementation epics/stories/tasks.

## Mapping Folder (Current)
We started the consolidation split under:
- `context_compass/artifacts/AethericRift/README.md`

Structure:
- `context_compass/artifacts/AethericRift/objects/` (object-level concepts)
- `context_compass/artifacts/AethericRift/systems/` (system-level concepts)

## Open Questions (Scratch)
- UNKNOWN: What is the minimal v1 object model that still supports the
  workstation vs static split without rewrites?
- UNKNOWN: How do we represent ObjectRef lifetime (session-bound only, TTL,
  explicit release) without building a full "handle protocol" framework?
- UNKNOWN: What is the correct coupling between audit ledger and ACL enforcement
  (log allow/deny decisions, or only log state mutations)?
