# [Ticket] AethericRift Philosophical Context and End-State Model

**Type:** Architecture / Philosophy / Recovery Ticket

**Status:** Active Context Artifact

**Labels:** `aetheric-rift`, `philosophy`, `recovery`, `engineer-context`,
`workspace`, `runtime`, `state`, `profiles`, `tokens`, `frames`, `conduits`

---

## 1. Why This Document Exists

This document exists for one reason:

the AethericRift design is now large and subtle enough that future sessions,
future engineers, or future versions of the agent should not have to reconstruct
the end state from scattered notes or replayed chat.

This document is therefore not just a design summary.

It is a recovery artifact.

It is meant to answer:

- what AethericRift is
- why it exists
- how it relates to Melder
- what objects now matter
- what boundaries are strict
- what the static and dynamic room split means
- what profiles are really for
- how token/session/request behavior fits
- why the shell/state/system model exists
- what must be implemented and what must not be reopened casually

It is intentionally broad and philosophical.
It is also intentionally implementation-aware.

That combination is the point.

---

## 2. How To Read This Document

This document should be read in layers.

### 2.1 First read

Read for:

- worldview
- boundary clarity
- object set
- reasons the design exists

### 2.2 Second read

Read for:

- lifecycle
- profile semantics
- room semantics
- token/session behavior

### 2.3 Third read

Read for:

- implementation constraints
- things that are explicitly not the design
- what should not be reopened

This document is not supposed to be skimmed only as a changelog.
It is meant to restore the architecture in the reader’s head.

---

## 3. The Core Worldview

The current AethericRift worldview is based on a few foundational beliefs.

### 3.1 The runtime is a real world, not just wiring

Melder is not treated as “just DI.”

It is treated as a real runtime world:

- frames exist
- conduits exist
- scopes exist
- object lifetime is real
- dynamic linking is real
- mutation substrate mechanics are real
- cleanup and invalidation are real

That matters because the layer above it should not pretend it is working
against a flat static service graph when it is actually working against a live
runtime world.

### 3.2 The agent is an operator, not a text parser with opinions

The agent is not supposed to be trapped inside:

- only chat
- only a JSON call list
- only a toy REPL
- only a pretend command palette

The agent is an operator working on a system.

That means the system should give the agent:

- structure
- access
- introspection
- room to build local things
- governance
- and boundaries that are real enough to matter

but not so much fake restriction that the runtime becomes a toy.

### 3.3 Ideas are objects

This whole architecture only makes sense if ideas are treated as real objects.

That means:

- they have structure
- they have identity
- they can be versioned
- they can be exposed
- they can be promoted
- they can be discarded
- they can possess or mislead if not held at the right distance

That matters because:

- profiles are objects
- policies are objects
- rooms are objects
- mutation candidates are objects
- philosophical traps are also objects

One reason this architecture is useful is that it encourages object separation.

If something can be seen as an object:

- it can be inspected
- it can be bounded
- it can be accepted or rejected
- it can stop possessing the whole system

That philosophical move is not fluff here.
It is part of the architecture.

### 3.4 Local work and canonical change are not the same

One of the most important beliefs in this system is that:

- local work is cheap
- canonical change is expensive

If that distinction collapses, the system collapses.

So the architecture keeps separating:

- local room work
- dynamic local construction
- canonical mutation

That line has to stay visible.

---

## 4. The Stack

The current stack is:

- `Melder`
- `Aether`
- `AethericFrame`
- `Conduit`
- `AethericRiftSystem`
- `AethericRift`
- `RiftSpace`
- `StaticRiftSpace`
- `DynamicRiftSpace`
- `MutationResearch`
- `CommandOps`

These are not interchangeable.

### 4.1 Melder

Melder is the runtime substrate.

It owns:

- spell binding
- spellbooks
- conduits
- lifetime
- linking
- cleanup
- dev-ops state
- mutation substrate primitives

It is not:

- the AR room
- the AR operator layer
- the orchestration layer

### 4.2 Aether

`Aether` is the substrate root.

It is the global manager of frames and the substrate access point that already
exists in the Melder code.

It already does real work:

- ensure frame
- bind frame configuration
- register conduits
- expose conduit cloud
- expose frame-scoped services

So Aether is not a random implementation detail.
It is a real authority boundary.

### 4.3 AethericFrame

`AethericFrame` is a realm inside the substrate.

It owns frame-scoped things like:

- root conduits
- conduit cloud
- spell-system state
- dev-ops manager
- mutation research service

This makes a frame more than just a label.
It is a bounded runtime world.

### 4.4 Conduit

A conduit is a runtime channel/path/scope inside that world.

It is not the same thing as a Rift.

That distinction is important:

- the conduit belongs to substrate truth
- the Rift is the opening into the realm

### 4.5 AethericRiftSystem

This is the AR root manager.

It is not a replacement for Aether.
It is the AR system above Aether.

It owns:

- canonical Rift registration
- canonical Rift state
- token/session policy
- request guard behavior
- profile aggregation
- the AR system frame

### 4.6 AethericRift

This is the public AR object.

But it is no longer thought of as:

- a singleton
- the sole state owner
- a second substrate root

It begins as a shell and becomes live by binding to system-owned state.

### 4.7 RiftSpace

`RiftSpace` is the base room contract.

It defines what a room is.

It is not yet the final behavior surface.

### 4.8 StaticRiftSpace

This is the lower-risk room.

This is where the stronger rules live.

### 4.9 DynamicRiftSpace

This is the richer dynamic/codegen room.

This is where local runtime construction becomes available.

### 4.10 MutationResearch

This is not AR-local construction.

This is canonical evolution:

- versioning
- promotion
- rollback
- discard
- lineage

### 4.11 CommandOps

This is orchestration.

It should stay above AR, not be collapsed into it.

---

## 5. Aether Is The Root, But Not The Whole AR Layer

One of the biggest corrections in the design process was understanding the
relationship between `Aether` and AR.

### 5.1 What Aether already does

From source-backed inspection, `Aether` already exposes most of the substrate
surface AR needs:

- frame creation
- frame configuration binding
- conduit registration
- conduit cloud access
- conduit lookup by name
- conduit lookup by id
- mutation research access
- dev-ops access
- spell-system-state access

That means AR should not reimplement those responsibilities just because AR
exists.

### 5.2 Why Aether should not become AR

At the same time, `Aether` should not be forced to become:

- the public AR application service
- the room/workspace engine
- the AR request/session engine
- the place where every AR policy lives

So the right split is:

- `Aether` remains substrate manager
- `AethericRiftSystem` becomes AR manager
- `Aether` hosts and facades access into that system where appropriate
- `Aether` does not directly own the canonical Rift registry

That is a clean split.

### 5.3 Required Aether surface

The current direction assumes `Aether` should support:

- add Rift
- find Rift
- remove Rift
- cleanup Rift

through a RiftSystem facade

These are facade operations into the system-owned Rift registry, not a direct
claim that `Aether` itself owns the Rifts.

and also expose:

- `_get_conduits_by_frame(aetheric_frame_name="default")`

because AR needs a clean way to enumerate root conduits in the configured frame
without reaching through frame internals directly.

That is now part of the design contract.

---

## 6. AethericRiftSystem

`AethericRiftSystem` is the root manager of all Rifts.

This is one of the biggest settled changes.

### 6.1 Why the system object exists

Without it:

- every public Rift object becomes a partial authority
- state drifts outward
- token/session control gets muddy
- prebuilt mode gets awkward
- canonical ownership becomes vague

The system object solves that.

### 6.2 What it owns

It owns:

- canonical Rift registry
- canonical Rift registration
- canonical Rift state
- token issuance and policy
- session state
- request-entry/request-exit guarding
- profile aggregation and invalidation
- one AR system frame
- any direct live-Rift retrieval policy when raw Rift objects are handed out at
  all

### 6.3 What it is not

It is not:

- Aether
- transport
- scheduler
- CommandOps
- MutationResearch

It is the AR root manager only.

### 6.4 Why it should live behind or above Aether

Most users do not interact with `Aether` directly.

That model should be preserved.

So the best public model is:

- user creates `AethericRift`
- system registration happens behind the scenes
- `Aether` stays substrate-root in the background

That means the system can live in or behind Aether without making Aether the
whole user-facing API.

---

## 7. AethericRiftState

`AethericRiftState` is the canonical per-Rift state anchor.

This object exists because the public Rift object is not naturally a singleton.

### 7.1 Why state needs a separate home

If the public Rift object owns everything:

- state gets tied to shell lifetime
- revocation becomes awkward
- prebuilt mode becomes awkward
- multiple public objects pointing at the same conceptual Rift become messy

So state is moved out.

### 7.2 What it holds

It should hold:

- AR system-frame anchor
- configured target frame
- AR-local substrate references
- room state
- profile-derived state
- activation/registration state
- current room type
- token/session attachment state

### 7.3 What it enables

This split enables:

- shell-to-live hydration
- prebuilt/token-gated activation
- revocation without pretending the shell is the only truth
- many public Rift objects without singleton confusion

---

## 8. The Public Rift As Shell -> Register -> Hydrate

This is the other major settled concept.

### 8.1 Shell

The public `AethericRift` starts as a shell.

That means:

- it exists
- but it is not yet live runtime truth

### 8.2 Register

It registers into `AethericRiftSystem`.

At registration:

- canonical state may be created
- defaults may be attached
- creation may be denied if policy forbids it

### 8.3 Hydrate

When activation is allowed:

- the shell binds against the canonical state
- it becomes a live stateful Rift

Hydration is where it gains:

- substrate references
- room references
- profile view
- live operational metadata

### 8.4 Why this matters

This split gives:

- central state ownership
- lazy construction
- recursion control
- token-gated posture
- cleaner lifecycle

It is one of the strongest parts of the current architecture.

---

## 9. System Frame Versus Target Frame

This distinction is mandatory.

If it is blurred, the system gets confused fast.

### 9.1 System frame

`AethericRiftSystem` owns one internal AR system frame.

That frame exists to hold:

- canonical Rift state anchors
- AR-local substrate conduits
- workstation/bootstrap assets
- AR-internal support objects

It is not the realm the user is targeting.

It is not the thing the room should be exposing to the operator by default.

It is the AR support frame.

### 9.2 Target frame

Separately, each live Rift has one configured target frame.

That frame is:

- the realm the Rift opens into
- the frame the room is really about
- the frame whose conduits and objects are exposed by default
- the frame `FrameExaminer` inspects

This is the user-facing realm.

### 9.3 Why the split matters

Without this split:

- AR-local substrate gets mistaken for user-targeted runtime
- local construction and exposed runtime truth get mixed together
- provenance gets muddy
- the room stops being legible

So every live Rift conceptually has:

- one system-frame anchor
- one target frame

That should stay visible in docs, code, and implementation reasoning.

---

## 10. FrameExaminer

`FrameExaminer` is the read/inspection tool for the configured target frame.

### 10.1 Why it exists

Without a dedicated inspection object, one of two bad things happens:

- the public Rift absorbs all discovery responsibilities
- or the room is expected to “just know” what to expose

Both are bad.

The public Rift should not become a god-object.
And room population should not be magic.

So `FrameExaminer` exists as the explicit gathering layer.

### 10.2 What it gathers

It should gather:

- exposed conduits
- frame-level services
- frame profile truth
- spellbook profile truth
- spell profile truth
- any required metadata for room population

### 10.3 What it does not do

It should not:

- own canonical Rift state
- own room lifecycle
- enforce policy by itself
- replace `Aether`
- replace `AethericRiftSystem`

It is an inspection object.

### 10.4 How it fits

The normal flow is:

1. Rift has a configured target frame
2. `FrameExaminer` inspects that frame
3. gathered truth is handed to `AethericRiftSystem`
4. the system computes aggregate exposure
5. the room surface is populated from that result

That is a clean architecture.

---

## 11. The Room Model

The room model changed materially during design.

### 11.1 Base room contract

`RiftSpace` is now the base room contract.

That means it should define:

- target registries
- target metadata
- room lifecycle
- common bind/clear/list behavior
- workstation facade semantics

It is not by itself the whole behavior model anymore.

### 11.2 Concrete room surfaces

There are now two concrete room types:

- `StaticRiftSpace`
- `DynamicRiftSpace`

This is a real type split, not just a weak mode flag.

That is important because the execution contract is different enough that it
deserves a type-level distinction.

### 11.3 Why the split matters

If static and dynamic are only half-different flags on one room, then:

- static can accidentally become dynamic-lite
- dynamic can accidentally inherit fake safety claims
- state transitions become muddy
- docs become vague

The type split fixes that.

### 11.4 Static to dynamic transition

The current direction is:

- do not mutate a live static room into a dynamic room in place
- build a new dynamic Rift configured for the dynamic room type

That preserves a hard semantic boundary.

This is a better model than silently mutating the meaning of a live room.

---

## 12. StaticRiftSpace

`StaticRiftSpace` is the lower-risk enforcement boundary.

### 12.1 What static is for

It is for:

- mediated operation
- predeclared targets
- lower-risk interaction
- clearer control over what is callable

### 12.2 What static has

It still has:

- a real root conduit underneath
- real substrate truth underneath
- declared targets
- code execution against those declared targets

So static is not “no runtime.”

It is:

- real runtime
- narrow room surface

### 12.3 What static does not need

It should not need:

- surrogates
- `ObjectRef`
- fake Python proxy magic

Those ideas were considered and rejected because they distort Python semantics
and create a leaky fake control model.

### 12.4 How static should work

Static should work through:

- preconfigured `RiftMethod`s
- preconfigured `RiftAttribute`s
- mediated interaction over those exposed surfaces

So the static agent:

- operates on declared targets
- uses the static callable/value surface
- cannot grow the local runtime world through the conduit

That is the point.

### 12.5 Why static is the real enforcement boundary

If AR has a place where “stronger rules” should actually be made real, that
place is `StaticRiftSpace`.

Because static is the room where:

- the target surface is curated
- the room is prepopulated
- the substrate is real but not broadly surfaced

So static is where:

- stricter exposure
- stricter request gating
- token/session rules
- mediated access

have their clearest meaning.

---

## 13. DynamicRiftSpace

`DynamicRiftSpace` is the richer codegen/dynamic room surface.

### 13.1 What dynamic is for

It is for:

- codegen-native work
- local helper construction
- local object/tool creation
- richer experimentation

### 13.2 What dynamic adds

It keeps everything from static, plus:

- conduit-backed local construction
- direct use of richer room population
- local helper/object/tool workflows
- direct rebinding into the room when allowed

### 13.3 What dynamic does not imply

It does not automatically imply:

- canonical mutation
- MR semantics

Dynamic is still local room work unless it crosses the canonical boundary.

### 13.4 What dynamic really relies on

Dynamic should be understood honestly.

It relies mainly on:

- AST preflight
- hooks
- direct room registries

It should **not** pretend to be a hard Python security boundary.

That honesty matters.

### 13.5 The AST truth

AST is useful here, but only for:

- syntax filtering
- obvious forbidden construct filtering
- target/member path checks against the room
- intent classification

It is not enough to stop a determined in-process Python agent if real raw
objects are exposed.

That is why dynamic is governance, not containment.

---

## 14. Namespace

Namespace matters mainly in dynamic.

### 14.1 Static namespace

Static usually does not need much namespace machinery because:

- one configured frame
- one predeclared room surface
- one narrower target population

So flat names or explicit aliases are often enough.

### 14.2 Dynamic namespace

In dynamic, namespace matters because:

- multiple conduits may be exposed
- collisions happen
- provenance matters

The current direction is:

- namespace is conduit-centered
- if multiframe is active, frame name qualifies the conduit namespace

So:

- single-frame dynamic:
  conduit namespace is often enough
- multiframe dynamic:
  `frame_name.conduit_name` becomes necessary

### 14.3 Naming rule

If a conduit is unnamed:

- it may still exist in substrate truth
- but it should not be dynamically exposed unless it has an explicit alias

That keeps the namespace honest.

### 14.4 Why the frame itself is not the namespace anchor

Frames are mostly substrate/internal objects.

They matter for:

- selection
- provenance
- grouping

But the real dynamic runtime anchors are conduits.

So the namespace is better when it is conduit-centered, not frame-object-first.

---

## 15. The Target Model

The target model remains:

- `RiftAttribute`
- `RiftMethod`

### 15.1 Why it exists

It is not there because Python lacks variables or methods.

It exists because the room needs:

- declared things
- inspectable things
- validation anchors
- cleanup handles
- provenance

Without it, the room collapses into ambient raw state.

### 15.2 What these should be

They should stay lightweight.

They are:

- target records
- naming anchors
- inspection anchors
- cleanup anchors

They are not:

- workflow engines
- magical proxies
- a second ownership model

### 15.3 Why ObjectRef is not part of the active model

`ObjectRef` was considered.

It is not part of the active v1 model now.

Reason:

- it does not buy enough
- if you make it central, it gets clunky
- if you do not make it central, it does not solve much

The current model is cleaner without it.

---

## 16. Profiles

Profiles are one of the most misunderstood parts unless stated very clearly.

### 16.1 What profiles are not

Profiles are not:

- Python containment
- object-level raw-runtime enforcement
- a substitute for request guarding
- a substitute for AST

### 16.2 What profiles are

Profiles are:

- exposure policy
- setup policy
- room population policy

They answer:

- what gets exposed
- how it gets exposed
- what gets populated into the room

### 16.3 Bottom-up override

The merge order is:

- `AethericFrameProfile`
- `SpellbookRiftProfile`
- `SpellRiftProfile`

Lowest level wins.

That means:

- frame sets defaults
- spellbook refines them
- spell gives the final answer

### 16.4 What the layers define

#### AethericFrameProfile

Defines things like:

- whether the frame is exposable
- which conduits can be surfaced
- whether frame services are visible
- default exposure posture for things in the frame

#### SpellbookRiftProfile

Defines things like:

- which spells are available from the spellbook
- spellbook-level exposure defaults
- how spellbook-derived things populate the room

#### SpellRiftProfile

Defines things like:

- final per-spell exposure
- alias / exposed name
- whether it appears as method/attribute/metadata
- whether dynamic use is allowed

### 16.5 Where profile truth lives

Underlying profile truth should stay attached to substrate objects.

That means:

- frame-level truth lives with frames
- spellbook-level truth lives with spellbooks
- spell-level truth lives with spells/targets

Then `AethericRiftSystem` aggregates and indexes that truth.

This is important because AR should own the aggregate view, but not pretend it
invented the underlying profile truth.

### 16.6 Profile maintenance

`AethericRiftSystem` should invalidate and rebuild the aggregate when:

- frame profile changes
- spellbook profile changes
- spell profile changes
- exposed structure changes

Then the room is repopulated from substrate truth.

That is better than pretending the room is always perfectly live without an
explicit refresh boundary.

---

## 17. Tokens, Sessions, and Request Guard

### 17.1 Tokens

The current explicit names are:

- `AethericRiftCreationToken`
- `AethericRiftToken`

`AethericRiftCreationToken`:

- gates creation/registration when creation is restricted

`AethericRiftToken`:

- gates activation/use of a specific Rift state

### 17.2 Sessions

Sessions stay lightweight.

They track:

- Rift identity
- activity timestamps
- expiry/timeout state
- optional reverification
- optional refresh state

They do not:

- own threads
- become schedulers
- become mediator monsters

### 17.3 Request guard

Use a narrow request-entry/request-exit guard.

On request in:

- resolve Rift/session
- validate token/session
- enforce expiry/reverification
- update activity/in-flight bookkeeping

On request out:

- update activity
- decrement in-flight bookkeeping
- optionally refresh token/session state

This is enough for v1.

---

## 18. Why Static And Dynamic Are Both Needed

Static without dynamic would be too limiting.

Dynamic without static would be too sloppy.

The split exists because these are genuinely different contracts:

- static = stronger control, narrower surface
- dynamic = richer power, weaker containment

If you collapse them, the design gets dishonest.

---

## 19. Why MutationResearch Is Separate

MutationResearch is not:

- local helper creation
- local experimentation
- dynamic room growth

It is:

- canonical evolution
- versioning
- promotion
- rollback
- discard

That is why the dynamic room can be powerful without automatically becoming the
mutation lane.

---

## 20. Required Aether Surface

The current AR design assumes `Aether` should expose:

- add Rift
- find Rift
- remove Rift
- cleanup Rift

through the RiftSystem facade

These are facade operations into the system-owned Rift registry, not a direct
claim that `Aether` itself owns the Rifts.

and also:

- `_get_conduits_by_frame(aetheric_frame_name="default")`

That last one matters because frame-wide conduit enumeration should not require
direct reach-through into frame internals.

---

## 21. Implementation Doctrine

The engineer should not reopen these:

- `Aether` is substrate root
- `AethericRiftSystem` is root manager
- `AethericRiftState` is canonical state
- public Rift is shell -> register -> hydrate
- static and dynamic are different room types
- profiles are exposure/setup policy
- `_get_conduits_by_frame(...)` is needed
- token names are explicit

The engineer should implement from that.

---

## 22. What Still Remains Narrow

At this point the remaining questions are narrow:

- exact token field schemas
- exact `Aether` facade method names
- exact `FrameExaminer` method surface

Those are engineering refinements, not architecture uncertainty.

---

## 23. End-State Summary

If this document has to compress everything into a final short form, it is:

`Aether` is the substrate root.
`AethericRiftSystem` is the root manager of Rifts.
`AethericRiftState` is the canonical state for one Rift.
Public `AethericRift` objects begin as shells and hydrate against that state.
The system owns an AR system frame; each live Rift exposes one configured target
frame by default.
`FrameExaminer` gathers the target-frame truth.
`RiftSpace` is the base room contract.
`StaticRiftSpace` is the lower-risk enforcement boundary.
`DynamicRiftSpace` is the AST+hooks dynamic/codegen surface.
Profiles define exposure/setup policy with bottom-up override.
`RiftAttribute` and `RiftMethod` remain the declared target model.
MutationResearch remains the canonical evolution lane.

That is the end-state model.

---

## 24. Why Surrogates And ObjectRef Were Rejected

This part matters because it was a real architectural fork.

### 24.1 The temptation

At several points, one natural instinct was:

- maybe expose surrogate objects
- maybe expose `ObjectRef`
- maybe hide the real object behind a safer AR-owned shape

That sounds attractive because it feels like control.

### 24.2 Why that breaks down in Python

In Python, surrogate/proxy models are usually leaky and annoying.

They distort:

- dunder behavior
- identity expectations
- descriptor behavior
- iteration/context-manager semantics
- normal introspection
- the feel of real Python objects

So instead of gaining a clean control model, you often gain:

- weird edge cases
- broken expectations
- awkward layering
- false confidence

### 24.3 Why `ObjectRef` did not survive as a core concept

`ObjectRef` had a similar problem.

If it is central:

- everything becomes mediated through a handle
- the system gets clunky

If it is optional:

- it stops giving enough architectural value

So the active model dropped it from the core v1 set.

### 24.4 What replaced it

Instead of surrogates/ObjectRef, the current model uses:

- `StaticRiftSpace` as a real mediated room surface
- `RiftMethod`
- `RiftAttribute`
- exposure policy through profiles
- AST + hooks in dynamic

That is cleaner and more honest.

---

## 25. Why Profiles Do Not Equal Security

This distinction has to stay explicit.

### 25.1 The wrong idea

The wrong idea is:

- profiles list allowed methods
- therefore runtime behavior is truly constrained

That is not true in raw Python dynamic mode.

### 25.2 The right idea

Profiles are:

- exposure policy
- setup policy
- room-population policy

They determine:

- what gets seen
- what gets named
- what form it takes in the room

They do not magically make Python stop being Python.

### 25.3 Where the real control comes from

Real control comes from:

- the static room surface
- request-entry checks
- token/session gating
- explicit room-population choices
- room-type boundary

That is why static and dynamic need to be different room types, not just
different policies on one identical object.

---

## 26. Why StaticRiftSpace Still Allows Codegen

At one point there was a temptation to cripple static mode into:

- flat RPC
- JSON call picking
- no codegen

That was too weak.

### 26.1 Why no-codegen static was rejected

It would reduce the agent too much.

The agent still needs to:

- sequence calls
- branch
- loop
- transform local values
- compose multi-step work

So the current static model still allows codegen, but only over the curated
room surface.

### 26.2 What that means

Static codegen is:

- still expressive
- but not substrate-expansive

That is a strong compromise.

### 26.3 Why this matters philosophically

The agent is still supposed to be an operator.

A room that removes all ability to think and compose would stop being an
operator room and become a toy console.

That is why static is mediated, not crippled.

---

## 27. Why DynamicRiftSpace Is Not A Lie

Dynamic is useful precisely because it does not pretend to be something it is
not.

### 27.1 What dynamic gives

It gives:

- codegen-native work
- local helper construction
- local room growth
- richer experimentation

### 27.2 What dynamic does not pretend to give

It does not pretend to give:

- hard Python containment
- absolute method-level prevention once raw objects exist
- a perfect security story

### 27.3 Why that honesty matters

If dynamic is described honestly:

- engineers know what they are building
- operators know what they are trusting
- the room semantics stay defensible

If dynamic is described dishonestly:

- people think AST is a sandbox
- people think profiles are hard ACLs over raw Python
- the system becomes safety theater

That must be avoided.

---

## 28. The Role Of Request Guarding

One subtle but important design decision is not to create a giant mediator.

### 28.1 Why a giant mediator was rejected

A giant mediator tends to absorb:

- request flow
- policy
- lifecycle
- orchestration
- state mutation
- retry logic

and then it becomes a god-object.

That is not the right move here.

### 28.2 Why request guarding survived

What actually remained useful was much smaller:

- request-in checks
- request-out updates

That is enough for:

- token validation
- session validation
- expiry
- reverification
- activity tracking
- light in-flight bookkeeping

That’s the right level.

### 28.3 Why no thread ownership

The current model keeps sessions lightweight and avoids owning threads because:

- thread ownership is a different system concern
- the room should not become a scheduler
- CommandOps should remain the orchestration layer

So request guarding is kept deliberately small.

---

## 29. The Role Of FrameExaminer

`FrameExaminer` exists because inspection needs a home.

### 29.1 Why the public Rift should not inspect everything itself

If the public Rift owns:

- system state
- substrate references
- room lifecycle
- inspection
- profile gathering

then it becomes overloaded.

That weakens both clarity and maintainability.

### 29.2 Why the room should not own discovery

The room is for operation.

If the room also owns all discovery/gathering logic, then room creation becomes
opaque and too magical.

### 29.3 Why the examiner is the right split

`FrameExaminer` gives one clear place for:

- query
- inspect
- gather
- describe

without turning it into:

- state authority
- policy engine
- scheduler

That is a good architectural seam.

---

## 30. The Relationship Between AR And MutationResearch

This needs to remain sharply defined even though this document is AR-focused.

### 30.1 AR

AR is for:

- entering a real runtime world
- doing local work
- exposing a controlled room surface
- constructing local helpers
- operating on the current world

### 30.2 MR

MR is for:

- canonical evolution
- durable versioning
- promotion
- rollback
- discard

### 30.3 Why the line matters

If local dynamic construction is confused with mutation:

- dynamic becomes over-governed and useless

If canonical mutation is confused with local room work:

- the system loses its strong distinction between cheap local work and
  expensive canonical change

So the line is essential.

---

## 31. The Engineer’s Mental Model

If an engineer reads nothing else, they should internalize this:

### 31.1 The five truths

1. `Aether` is the substrate root.
2. `AethericRiftSystem` is the AR root manager.
3. `AethericRiftState` is canonical per-Rift state.
4. Public `AethericRift` is shell -> register -> hydrate.
5. `StaticRiftSpace` and `DynamicRiftSpace` are genuinely different room
   contracts.

### 31.2 The next five truths

6. `FrameExaminer` gathers target-frame truth.
7. profiles are exposure/setup policy, not Python security.
8. static is the enforcement boundary.
9. dynamic is AST+hooks over a richer room.
10. `_get_conduits_by_frame(...)` is the clean substrate accessor needed for
    configured-frame conduit enumeration.

### 31.3 The discipline

The engineer should not:

- re-open already-settled object names casually
- re-collapse static and dynamic into one weak room type
- re-invent a fake substrate lifecycle around AR
- drag MutationResearch into the base AR implementation prematurely

---

## 32. The Migration Philosophy

This planning repo is not the forever home of the design.

The purpose of these docs is to be migrated into the main code repo where the
runtime will actually live.

That is why this document is broad and explicit:

- it is meant to survive transfer
- it is meant to survive context loss
- it is meant to give future engineer-mode work a stable re-entry point

The package bundle and migration guide exist because of this.

---

## 33. Final Compression

If the whole design must be compressed one last time:

`Aether` owns runtime truth.
`AethericRiftSystem` owns AR truth.
`AethericRiftState` anchors one Rift.
Public `AethericRift` begins as shell and hydrates into live operation.
The system frame supports AR; the target frame is the realm exposed to the
operator.
`FrameExaminer` gathers target-frame truth.
`RiftSpace` is the room contract.
`StaticRiftSpace` is the enforcement room.
`DynamicRiftSpace` is the richer AST+hooks room.
Profiles define what is exposed and how.
`RiftAttribute` and `RiftMethod` remain the declared room targets.
`MutationResearch` remains the canonical evolution lane.

That is the architecture we settled on.
