# [Ticket] AethericRift Implementation Contract

**Type:** Implementation / Engineer Handoff Ticket

**Status:** Active Implementation Contract

**Labels:** `aetheric-rift`, `implementation`, `engineer-handoff`, `melder`,
`workspace`, `static-rift-space`, `dynamic-rift-space`, `profiles`, `tokens`

---

## 1. Purpose

This ticket is the AR-only implementation contract.

It is narrower than the long-form unified architecture ticket.
Its job is to answer one question:

**what exactly needs to be implemented for AethericRift v1?**

This ticket should be readable by an engineer who wants:
- the object set
- the system boundaries
- the order of work
- the concrete missing APIs
- the places where the design is intentionally strict

---

## 2. What This Ticket Is Not

This is not:
- a full MutationResearch implementation plan
- a transport/API design
- a security proof
- a replacement for the AR patch docs

Use this ticket as the high-level implementation contract, then use the active
patch docs as the detailed engineer contract.

---

## 3. Core Implementation Targets

The implementation target is now this object set:

- `AethericRiftSystem`
- `AethericRiftState`
- `AethericRift`
- `FrameExaminer`
- `RiftSpace`
- `StaticRiftSpace`
- `DynamicRiftSpace`
- `RiftConfiguration`
- `RiftProfile`
- `AethericFrameProfile`
- `SpellbookRiftProfile`
- `SpellRiftProfile`
- `RiftConduit`
- `RiftAttribute`
- `RiftMethod`
- `RiftValidationSystem`
- request/session guard behavior
- token objects:
  - `AethericRiftCreationToken`
  - `AethericRiftToken`

---

## 4. Top-Level Runtime Shape

### 4.1 Aether

`Aether` remains the substrate root.

It should:
- own frames
- own conduit/service truth
- host and facade access to `AethericRiftSystem`

It should not become the whole AR application layer.

### 4.2 AethericRiftSystem

This is the root manager of all Rifts.

It should own:
- canonical Rift registry
- canonical Rift registration
- canonical `AethericRiftState`
- token issuance/validation policy
- lightweight session state
- request-entry/request-exit guard behavior
- profile aggregation/indexing
- one AR system frame
- any direct live-Rift retrieval policy when raw Rift objects are handed out at
  all

### 4.3 AethericRift

This is the public AR object.

It should:
- begin as a shell
- register into `AethericRiftSystem`
- hydrate against canonical state when allowed
- become the live runtime/control object for one Rift instance

### 4.4 AethericRiftState

This is the canonical per-Rift state record.

It should hold:
- target frame
- system frame anchor
- AR-local substrate references
- active room type
- profile-derived state
- token/session attachment state

---

## 5. System Frame Versus Target Frame

This distinction is mandatory.

### 5.1 System Frame

Owned by `AethericRiftSystem`.

Purpose:
- internal AR substrate/support frame
- AR-local conduits
- bootstrap/workstation support assets
- canonical state anchors

### 5.2 Target Frame

Configured on the live Rift.

Purpose:
- the realm the Rift opens into
- the source of exposed conduits/objects/services
- the frame `FrameExaminer` inspects

Do not collapse these two frame roles.

---

## 6. Required Aether Additions

The current design now assumes these `Aether` responsibilities:

- facade add Rift
- facade find Rift
- facade remove Rift
- facade cleanup Rift

These are facade operations into `AethericRiftSystem`, not a claim that
`Aether` directly owns the canonical Rift registry.

And one required substrate accessor:

- `_get_conduits_by_frame(aetheric_frame_name="default")`

That accessor is needed so AR can enumerate the configured frame's root
conduits without reaching through frame internals directly.

---

## 7. FrameExaminer

`FrameExaminer` is the read/inspection tool for the configured target frame.

It should gather:
- exposed conduits
- relevant frame services
- frame profile truth
- spellbook profile truth
- spell profile truth

It feeds the gathered view into `AethericRiftSystem`.

It should not own:
- canonical Rift state
- room lifecycle
- policy enforcement

---

## 8. Room Model

### 8.1 RiftSpace

Base room contract only.

It should define:
- target registries
- target metadata
- bind/clear/list behavior
- common room lifecycle

### 8.2 StaticRiftSpace

The lower-risk enforcement boundary.

It should:
- use preconfigured or explicitly bound `RiftMethod`s and `RiftAttribute`s
- avoid surrogate/ObjectRef dependence
- avoid conduit-backed local construction
- enforce the static interaction contract directly

### 8.3 DynamicRiftSpace

The richer AST+hooks dynamic surface.

It should:
- support codegen
- support conduit-backed local construction
- use direct dict-backed room registries
- rely on AST preflight plus hooks, not fake Python containment

Moving from static to dynamic should be modeled as building a new dynamic Rift,
not mutating a live static Rift in place.

---

## 9. Target Model

`RiftAttribute` and `RiftMethod` remain the declared room target model.

They should stay lightweight and exist for:
- explicit naming
- room population
- validation anchors
- cleanup/provenance metadata

They should not become workflow engines.

---

## 10. Profile Model

Profiles are exposure/setup policy.

They are not Python sandboxing.

### 10.1 Merge Order

Bottom-up override wins:

- `AethericFrameProfile`
  provides defaults
- `SpellbookRiftProfile`
  refines those defaults
- `SpellRiftProfile`
  provides the final override

### 10.2 What Profiles Need To Define

Profiles should define:
- what is exposed
- how it is exposed
- what gets populated into the room
- static versus dynamic exposure posture
- aliases/names where relevant

### 10.3 What The System Must Maintain

`AethericRiftSystem` should maintain the aggregate profile view and invalidate
it when:
- frame profile changes
- spellbook profile changes
- spell profile changes
- underlying exposed structure changes

Then the system rebuilds room exposure from substrate truth.

---

## 11. Namespace Rules

Namespace matters mainly in `DynamicRiftSpace`.

### 11.1 Static

In static, namespace pressure is low because:
- one configured frame
- one enforced room surface
- predeclared targets

So namespace can usually be flat there.

### 11.2 Dynamic

In dynamic, namespace is conduit-centered.

Rule:
- single-frame dynamic:
  conduit namespace is usually enough
- multiframe dynamic:
  `frame_name.conduit_name` becomes necessary

### 11.3 Naming Rule

If a conduit is unnamed:
- it may still exist in substrate truth
- but it should not be dynamically exposed unless it has an explicit alias

---

## 12. Token / Session / Request Model

### 12.1 Tokens

Use explicit token names:
- `AethericRiftCreationToken`
- `AethericRiftToken`

`AethericRiftCreationToken`
- gates creation/registration when creation is restricted

`AethericRiftToken`
- gates activation/use of a specific Rift state

### 12.2 Sessions

Sessions should stay lightweight.

Track:
- Rift identity
- activity timestamps
- expiry / timeout state
- optional reverification state
- optional token refresh state

Do not:
- own threads
- become schedulers
- become giant mediator objects

### 12.3 Request Guard

Use a narrow request-entry/request-exit guard.

On request in:
- resolve Rift/session
- check token/session validity
- check expiry/reverification
- update activity and in-flight bookkeeping

On request out:
- update activity
- decrement in-flight bookkeeping
- optionally refresh token/session state

---

## 13. Static Versus Dynamic Control Boundary

The current design line is:

- `StaticRiftSpace`
  = real enforcement boundary
- `DynamicRiftSpace`
  = richer power surface with AST+hooks governance only

That is an honest split.

Do not try to make dynamic feel like secure static.
Do not try to make static feel like full dynamic freedom.

---

## 14. Build Order

The implementation order should be:

1. `Aether` facade additions and `_get_conduits_by_frame(...)`
2. `AethericRiftSystem`
3. `AethericRiftState`
4. `AethericRift` shell-to-live lifecycle
5. system frame ownership
6. token/session/request-guard behavior
7. `FrameExaminer`
8. `RiftSpace` base contract
9. `StaticRiftSpace`
10. `RiftAttribute` / `RiftMethod`
11. `RiftValidationSystem`
12. profile objects + profile aggregation
13. `DynamicRiftSpace`
14. later MR integration

---

## 15. What The Engineer Should Not Reopen

Do not reopen:
- whether `Aether` is the substrate root
- whether `AethericRiftSystem` owns canonical Rift state
- whether public `AethericRift` is shell-to-live
- whether static/dynamic are different room types
- whether profiles are exposure/setup policy
- whether `_get_conduits_by_frame(...)` is needed

Those are current design decisions.

---

## 16. Remaining Narrow Questions

The only narrow things left are:
- exact token field schemas
- exact `Aether` facade method names/signatures
- exact `FrameExaminer` method surface

Those are engineering-level refinements now, not architecture uncertainty.
