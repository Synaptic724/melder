# [Ticket] AethericRift and MutationResearch Unified Current Architecture

**Type:** Architecture / Philosophy Ticket

**Status:** Active Planning Context

**Labels:** `aetheric-rift`, `mutation-research`, `melder`, `commandops`,
`workspace`, `codegen`, `dynamic-runtime`, `agent-operator`, `state`,
`migration`, `salvage`

---

## 1. Intent

Capture the current high-level architecture and philosophy for how:

- Melder,
- AethericRift,
- MutationResearch,
- and CommandOps

fit together as one agent-native runtime stack.

This document is intentionally broader and more complete than the shorter
implementation-facing freeze note. Its job is to preserve the current model we
actually formed in discussion, not just the minimal object list for tomorrow’s
coding start.

---

## 2. What This Document Is

This is the current source-of-truth style document for:

- the big-picture runtime worldview
- the role of AethericRift
- the role of MutationResearch
- the role of Melder
- the role of CommandOps
- the actual AR object model
- the workspace and codegen model
- the room split (`StaticRiftSpace`, `DynamicRiftSpace`, MR-enabled)
- the difference between local construction and canonical mutation
- and the operator workflow the agent should follow

This is not:

- the transport/API design
- the final implementation plan
- or a complete security proof

---

## 3. Core Story

The system should be understood as one runtime world with two major kinds of
activity:

1. operating against the current live reality
2. evolving what that reality is

Melder is the substrate and lifecycle truth.
AethericRift is the governed live interaction membrane over that truth.
MutationResearch is the governed protocol for canonical structural evolution of
that truth.
CommandOps is the orchestration and operational tooling layer above both.

This is not two disconnected products.
It is one system with:

- a current world
- a local working room
- and an explicit path for future-state change

---

## 4. Why This Exists

Traditional software assumes:

- static structures
- mutation as exceptional
- manual operator-driven coordination
- tooling outside the runtime
- and restart/redeploy as the normal unit of change

The current model assumes something different:

- agents work inside a legible runtime world
- they inspect live objects and capabilities
- they use codegen as a native control language
- they can build local tools and helpers in a workspace
- they can validate, discard, salvage, or promote those results
- and durable state matters more than frozen object form

That is the center of the current architecture.

---

## 5. Melder

Melder is the substrate.

It owns:

- spells
- conduits
- scopes
- object lifetimes
- object sharing
- cleanup semantics
- change-control truth
- mutation substrate mechanics

Melder is not:

- the transport layer
- the agent orchestration layer
- or the AethericRift user-facing workspace layer

But it is the thing that makes the world legible and structurally real enough
for the layers above it to matter.

---

## 6. AethericRift

AethericRift is the governed runtime control surface.

It is the thing the operator/agent actually enters.

It is responsible for:

- entering the runtime through `Aether`
- creating and managing workspaces
- providing a codegen-native operating surface
- managing the workspace target model
- validating and classifying codegen
- routing into the underlying runtime
- surfacing the workspace-local room where useful work happens

It is not:

- the web server
- the transport protocol
- the scheduler
- the final external sentinel system

It is the runtime membrane.

---

## 7. MutationResearch

MutationResearch is the canonical evolution protocol.

It is not generic workspace-local object creation.
It is not casual experimentation.
It is not every temporary helper the agent builds.

It is specifically for:

- iterating on existing durable/canonical things
- structural mutation that matters outside the local workspace
- versioning
- validation
- promotion
- rollback
- discard
- lineage
- migration
- salvage when retiring or superseding canonical structures

MutationResearch is where “future state” becomes official.

---

## 8. CommandOps

CommandOps is the orchestration layer.

It should own:

- missions
- multi-agent coordination
- scheduling
- retries
- operator workflows
- probes/patchers/analyzers/scaffolds when those belong to operational tooling

AR should not become CommandOps.
Melder should not become CommandOps.

CommandOps lives above the runtime world and helps drive it.

---

## 9. The AethericRift Runtime Model

### 9.1 Aether

`Aether` is the global root.

AR enters through `Aether`.

`Aether` should be treated as the host and facade entrypoint for Rift access,
not just a pass-through factory and not the canonical owner of Rift instances.

This matches the real Melder substrate:
- `Aether` already owns frame creation
- `Aether` already binds frame configuration
- `Aether` already registers root conduits
- `AethericFrame` already owns conduit, dev-ops, and mutation services

### 9.2 AethericRift

An `AethericRift` is created through `Aether`.

In the refined model, the public Rift begins as a shell and then binds against
system-owned state.

That means:

- `AethericRiftSystem` owns canonical Rift state
- `AethericRift` is the public lazy-bound object
- registration/activation hydrates the shell against canonical state

The live Rift then owns or carries access to:

- an AR-local `Spellbook`
- a default root `Conduit`
- its `RiftConfiguration`
- its `RiftValidationSystem`
- one active room surface, typically either `StaticRiftSpace` or
  `DynamicRiftSpace`

The Rift itself is the control/runtime object.
It is not merely a passive facade and it is not just another target in the
workspace namespace.
But it should still be understood as an `Aether`-managed service object.

### 9.2.1 AethericRiftSystem

`AethericRiftSystem` is the internal AR management system.

It should:
- own canonical Rift registry
- own canonical Rift state
- register/list/destroy Rifts
- own system-wide AR defaults and policy
- manage token-gated creation/activation modes when enabled
- govern any direct live-Rift retrieval that returns raw Rift objects
It should be treated as the root manager of all Rift instances.

It should not replace `Aether`.
It should live above or behind `Aether`, while still using `Aether` as the
substrate root.

### 9.2.2 System Frame Versus Target Frame

The current model now has two different frame concepts and they should not be
collapsed.

#### System frame

`AethericRiftSystem` should own one AR-internal frame.

That frame exists to hold:

- AR system-owned state
- AR-local substrate resources
- the AR-facing conduit used by a live Rift
- any workstation/bootstrap assets the system needs

This is not the user-targeted business/runtime frame.

#### Target frame

Separately, each live Rift has one configured target frame.

That target frame is:

- the realm the Rift opens into by default
- the frame whose conduits and objects are exposed into the room
- the frame that `FrameExaminer` and profile aggregation reason about

So the current model is:

- system frame = AR internal substrate/support frame
- target frame = user-facing exposed realm

That distinction matters because otherwise the AR-local substrate and the
user-targeted realm get mixed together.

### 9.3 AR-local Spellbook

The Rift owns its own Spellbook because the workspace needs a real local
construction substrate.

The AR-local Spellbook is not the broader user/system Spellbook.
It exists so the Rift can materialize:

- local tools
- helpers
- probes
- patchers
- temporary workspace objects

without polluting broader system frames by default.

This AR-local Spellbook should be treated as an ordinary Melder Spellbook, not
as a fake AR-only abstraction.

That matters because the real substrate already gives us the lifecycle we need:
- `Spellbook.__init__` ensures its target frame exists in `Aether`
- `SpellbookCreationSystem` freezes configuration and binds it back into
  `Aether`
- `SpellbookCreationSystem` then drives the real conjure flow into a root
  conduit

### 9.4 Root Conduit

The AR-local Spellbook conjures one default root conduit through that existing
Melder lifecycle.

That conduit is:

- the local execution reality for the workspace
- the construction substrate for dynamic mode
- the thing that can be cleaned up when the workspace/Rift closes

This gives the workspace a real runtime world rather than a fake bag of Python
locals.

### 9.5 RiftConduit

`RiftConduit` is the workspace-facing reference to that backing conduit.

It exists so the workspace can talk about or expose the conduit as a real thing
without pretending the workspace itself owns conduit lifetime truth.

Important:

- in `simple`, the root conduit exists but `RiftConduit` is not surfaced to the
  operator as a construction tool
- in `dynamic`, the root conduit may be surfaced through `RiftConduit` so local
  construction can happen against the real substrate

So `RiftConduit` is not a second conduit system.
It is just the workspace-facing reference to the actual backing conduit.
It rides the same substrate that Melder already uses for lesser-conduit
creation and lesser-to-normal upgrade.

---

## 10. RiftSpace

`RiftSpace` is the workroom.

This is where the agent does work.

It is:

- the agent-facing working environment
- the namespace for targets
- the place where local objects and helpers can be bound
- the place where codegen is aimed
- the place where cleanup happens

`RiftSpace` is not the owner of substrate lifetime truth.
Melder still owns that.

But `RiftSpace` is the operator-facing room over that truth.

### 10.1 What RiftSpace Holds

It should minimally hold:

- `attributes: dict[str, RiftAttribute]`
- `methods: dict[str, RiftMethod]`

plus metadata:

- source/provenance
- local/shared/imported/promoted status
- cleanup policy
- optional lifecycle hints
- configuration/mode

### 10.2 What RiftSpace Is Not

It is not:

- the transport layer
- a fake scheduler
- a second ownership system
- or canonical mutation by itself

It is the room.

---

## 11. Workstation

The “workstation” idea is still valid, but it should be interpreted as:

- the semantic operation surface experienced through `RiftSpace`

not:

- a separate primary runtime owner

So workstation behavior is expressed through the workspace, not through a giant
parallel object hierarchy.

That means the workstation idea survives, but it is facaded through
`RiftSpace`.

---

## 12. Core AR Objects

### AethericRiftSystem
Owns canonical Rift state, registration, and token-gated AR management policy.

### AethericRift
Owns the AR runtime and workspaces.

It should be created and managed by `Aether`, while still owning the AR-local
substrate for one Rift instance.

In the refined model it should begin as a shell and become a live stateful Rift
after registration/activation against canonical state.

### AethericRiftState
Canonical system-owned state for one Rift instance.

### StaticRiftSpace
The lower-risk concrete room surface.

### DynamicRiftSpace
The richer concrete room surface.

### RiftSpace
Base room/workspace contract.

### RiftConfiguration
Defines how a specific Rift/space behaves.

### RiftProfile
Top-level capability/ACL aggregate.

### SpellbookRiftProfile
Spellbook-level AR defaults.

### SpellRiftProfile
Per-spell AR override.

### AethericFrameProfile
Frame-level state/governance profile.

### RiftConduit
Workspace-facing handle/attachment concept for the real conduit.

### RiftAttribute
Named workspace object/value target.

### RiftMethod
Named workspace callable target.

### RiftValidationSystem
Codegen parse/validate/classify subsystem.

---

## 13. What Is Not In The Active V1 Model

Not active top-level AR objects:

- `RiftDomain`
- `RemoteTool`
- `RiftSurface`
- `ObjectRef`
- `RiftLesserConduit`
- `ConduitProfile`
- `RefAttr`
- `RefMethod`

Those are either older ideas, optional concepts, or no longer part of the
active v1 object language.

---

## 14. Target Model

### RiftAttribute

`RiftAttribute` is a named workspace object/value target.

Examples:

- imported system object
- local helper object
- probe
- temporary created object
- composed object in the workspace

### RiftMethod

`RiftMethod` is a named workspace callable target.

Examples:

- exposed system method
- local helper function
- utility runner
- temporary workspace-local operation

These are not just naming conveniences.
They are the actual declared target model codegen and validation operate
against.

---

## 15. Codegen Model

### 15.1 Codegen Is A String

The agent submits a code string.

It is not expected to build AST objects directly.

### 15.2 Validation

`RiftValidationSystem`:

- parses the string to AST
- checks allowed syntax
- checks declared names/member paths against the workspace target registry
- classifies the request posture/intent
- applies validation hooks from configuration

### 15.3 Execution

After validation:

- the code runs in the workspace context
- it can use declared targets
- in `dynamic` mode it may also use the root conduit for local construction

### 15.4 Codegen Is Not Automatically Durable

Most codegen outcomes are not canonical mutation.
They are often:

- local helpers
- probes
- workspace-local tools
- temporary constructed objects

That is normal AR work, not MutationResearch.

---

## 16. Mode Split

### 16.1 StaticRiftSpace

Lower-risk operation over predeclared targets.

Allowed:

- inspect targets
- use declared `RiftAttribute` / `RiftMethod`
- submit codegen against that declared target universe

Not allowed:

- direct conduit-backed local construction
- workspace-local materialization through the conduit
- canonical mutation path

### 16.2 DynamicRiftSpace

Everything in `StaticRiftSpace`, plus:

- direct use of the workspace root conduit as a construction substrate
- local helper/tool/object creation in the workspace
- binding those local outputs back into the workspace registries

Still not implied:

- canonical mutation/versioning by default

### 16.3 MutationResearch-enabled

Adds:

- canonical iteration on durable runtime structures
- versioning
- validation
- promotion
- rollback
- discard
- lineage

---

## 17. Local Construction vs Canonical Mutation

This is one of the most important boundaries.

### Local workspace construction

Not mutation by default.

Examples:

- create helper object
- create local runner
- build probe
- create analyzer
- create temporary composed object

These stay in the workspace and can die with it.

### Canonical mutation

This is MutationResearch.

Examples:

- iterating on an existing durable canonical object
- versioning a durable runtime structure
- promoting a new canonical form
- migrating state from old form to new form

That is the durable evolution path.

---

## 18. Simple vs Dynamic Is About Construction Freedom

Static/simple is not “no conduit exists.”

A conduit still exists underneath the space.

The distinction is:

- in `simple`, I do not use the conduit as a local construction instrument
- in `dynamic`, I do

That is the clean mode split.

---

## 19. Validation Limits

AST and target/member validation are useful, but they are not an all-powerful
security answer.

They are good for:

- syntax filtering
- target/member allowlists
- lane classification
- auditability of intent

They are not enough to guarantee adversarial same-process containment.

So the architecture truth is:

- AST/validation gives the governed supported path
- stronger sentinel systems can and should be layered on by users
- AR provides the structure and hook points, not a fantasy universal validator

---

## 20. User Responsibility Boundary

The goal is not to make AR the place where every future trust and validation
problem is solved.

The goal is to:

- give users a strong structure
- give the agent a legible world
- give the runtime a coherent workspace model
- and let stronger sentinel/validation systems be added where needed

Users adapt to the structure.
AR does not need to solve all organizational trust models itself.

---

## 21. Tomorrow’s Build Direction

Tomorrow’s build should start from the current object set, not the stale
February decomposition.

The first slice should establish:

1. `AethericRift`
2. AR-local `Spellbook`
3. root conduit
4. `RiftConfiguration`
5. `RiftSpace`
6. `RiftAttribute`
7. `RiftMethod`
8. `RiftValidationSystem`

Then:

- `StaticRiftSpace` end-to-end
- `DynamicRiftSpace` conduit-backed local construction
- MutationResearch integration later

---

## 22. Acceptance Criteria

This document is serving its purpose if:

1. the current object language is explicit
2. the role of AR, MR, Melder, and CommandOps is explicit
3. the mode split is explicit
4. the local-vs-canonical mutation boundary is explicit
5. the next implementation slice can start from this document without inheriting
   stale February assumptions

---

## 23. Authoritative Naming

This document is using the current active object language.

Current preferred names:

- `AethericRift`
- `RiftSpace`
- `RiftConfiguration`
- `RiftProfile`
- `AethericFrameProfile`
- `SpellbookRiftProfile`
- `SpellRiftProfile`
- `RiftConduit`
- `RiftAttribute`
- `RiftMethod`
- `RiftValidationSystem`

Names intentionally not part of the active v1 object set:

- `RiftDomain`
- `RemoteTool`
- `RiftSurface`
- `ObjectRef`
- `RiftLesserConduit`
- `ConduitProfile`
- `RefAttr`
- `RefMethod`

If older active docs disagree with these names, this document wins until they
are rewritten.

---

## 24. The AethericRift Control Object In Detail

`AethericRift` is the actual runtime control object.

It is not just a naming shell.
It is not just a facade in the weak sense.
It is the object that owns the AR-local runtime machinery for a workspace.

But it should not be the canonical owner of all Rift state by itself.

The cleaner model is:

- the public `AethericRift` begins as a shell
- `AethericRiftSystem` owns canonical `AethericRiftState`
- registration/activation hydrates the shell against that canonical state

That lets us:

- allow many Rift objects to be created
- keep canonical state centralized
- support prebuilt/token-gated modes cleanly
- avoid turning the public Rift object itself into a singleton

At minimum it should own:

- AR-local `Spellbook`
- root `Conduit`
- `RiftConfiguration`
- `RiftValidationSystem`
- active `RiftSpace` registry

It should be created through `Aether`, not independently of it.
And `Aether` should remain the higher-level manager that creates and tracks Rift
instances against the broader Melder runtime.

It should be able to:

- create a new `RiftSpace`
- list active spaces
- close spaces
- expose current configuration state
- expose the root conduit when mode allows
- surface the current profile picture used for target exposure and validation
- bind lazily to system-owned state when registration/activation succeeds

It should not be:

- the transport server
- the web framework
- the scheduler
- the final validation authority for every org policy

### 24.1 AethericRiftSystem

`AethericRiftSystem` should own:

- canonical Rift registry
- canonical Rift state objects
- registration of Rifts
- token-gated creation/activation policy
- system-level AR defaults
- profile aggregation/indexing support

### 24.2 AethericRiftState

`AethericRiftState` should hold:

- configured target frame
- AR system frame linkage
- AR-local substrate references
- workspace state
- profile-derived state
- activation/registration status

It is the canonical state anchor for one Rift.

In the refined model it should also carry:

- the Rift's AR-local conduit reference
- whether that conduit is merely allocated versus actively surfaced
- token/registration state
- current room type (`StaticRiftSpace` or `DynamicRiftSpace`)

### 24.3 Why The Shell/State Split Exists

This split exists for a few concrete reasons.

#### It prevents accidental singleton behavior

The public `AethericRift` objects are not naturally singletons.

If we want canonical state to behave like one stable thing, that state has to
live somewhere else.

That “somewhere else” is `AethericRiftState`, owned by
`AethericRiftSystem`.

#### It supports lazy construction cleanly

The public Rift can exist as:

- an inert shell
- a registered but not-yet-live shell
- a live hydrated Rift

without forcing the public object itself to be the canonical state anchor from
the moment it is constructed.

#### It supports defensive modes

If we want:

- prebuilt Rift instances
- creation-token requirements
- use-token requirements
- recursion control around codegen trying to spawn new Rifts

then the shell/state split makes that much easier.

### 24.4 Registration And Hydration Lifecycle

The lifecycle should be thought of explicitly.

#### Step 1: shell creation

The user may construct a public `AethericRift` object.

At this point it is only a shell.

It is not yet the authoritative owner of a live runtime.

#### Step 2: system registration

The shell is registered into `AethericRiftSystem`.

At registration time the system may:

- create canonical `AethericRiftState`
- attach defaults
- deny registration if creation policy forbids it

#### Step 3: activation / hydration

When allowed, the shell binds against the canonical state and becomes a live
Rift.

That hydration step is where the shell gains:

- AR-local substrate references
- room references
- current profile view
- metadata needed for actual operation

#### Step 4: use

Once hydrated, the Rift can create or expose the configured room surface.

#### Step 5: revoke / cleanup

Because canonical state is system-owned, revocation and cleanup can happen
without pretending the public Rift shell is the only durable source of truth.

### 24.5 Prebuild And Token-Gated Modes

The current model should support both open and defensive postures.

#### Open posture

- the user constructs a Rift shell
- it registers
- it hydrates normally

#### Prebuilt / forced-registration posture

The system may be configured to require prebuilt registration and tokens.

That means:

- real Rift states are created ahead of time by the system
- creation of new live Rifts may require `AethericRiftCreationToken`
- use of a specific Rift may require `AethericRiftToken`

This is useful not because it makes Python perfectly safe, but because it gives
the system a real way to control who can cause new runtime openings to become
live.

That matters for:

- defensive AI posture
- recursion control
- deployment posture
- preapproved/operator-owned workspaces

The current token names should therefore be treated as:

- `AethericRiftCreationToken`
- `AethericRiftToken`

### 24.6 System Frame Ownership

`AethericRiftSystem` should own one internal AR frame.

That frame is where the system keeps:

- canonical Rift state anchors
- AR-local substrate conduits
- core workstation/bootstrap assets

The public-target frame is a different thing.

This means a live Rift conceptually has:

- one system-frame anchor
- one configured target frame

That distinction should remain visible in the docs and in the code.

### 24.7 Aether Facade Responsibilities

`Aether` should facade access into the `AethericRiftSystem`.

That means it should expose a narrow helper surface for:

- add Rift
- find Rift
- remove Rift
- cleanup Rift

Those are facade operations into the system-owned Rift registry; they should
not turn `Aether` into the canonical Rift owner or a bypass getter for raw
live Rift objects.

And on the substrate side it should also expose:

- `_get_conduits_by_frame(aetheric_frame_name="default")`

so AR can enumerate root conduits in the configured frame without reaching
through frame internals directly.

---

## 25. The AR-local Spellbook

The Rift owns its own Spellbook for one reason:

- the workspace needs a real local construction substrate

This AR-local Spellbook is not the same thing as the broader user/application
Spellbook.

But it is still a normal Melder Spellbook.

It exists so the Rift can:

- materialize local helpers
- build probes
- create local tools
- host temporary workspace objects
- conjure the root conduit that underpins the space

This matters because otherwise the workspace becomes either:

- fake Python locals with no substrate truth
or
- direct pollution of the user’s broader runtime world

The AR-local Spellbook solves that.

It keeps workspace-local construction real without making it canonical by
default.

Because it is a normal Melder Spellbook, AR should reuse:
- frame attachment through `Aether`
- configuration bind-back into `Aether`
- the existing conjure path

rather than wrapping all of that in a parallel AR-only lifecycle fiction.

---

## 26. The Root Conduit

The root conduit is the local execution and construction reality for a space.

In all modes:

- the space has a root conduit underneath it

In `StaticRiftSpace`:

- the conduit exists
- the agent does not directly use it as a construction instrument

In `DynamicRiftSpace`:

- the conduit is surfaced as a local construction tool
- the agent can use it to materialize local helpers and objects

So the mode distinction is not:

- conduit exists vs conduit does not exist

It is:

- conduit hidden as construction tool vs conduit exposed as construction tool

Melder already has the substrate transitions AR may rely on here too:
- root conduit creation
- lesser conduit creation
- lesser-to-normal upgrade with preserved creations and gate rebinding

AR should reuse those substrate transitions where needed instead of inventing a
second room-scoping lifecycle.

This is one of the most important design clarifications.

---

## 27. RiftSpace In Detail

`RiftSpace` is the room.

It is:

- the agent-facing namespace
- the place where local things can be bound
- the place where imported system objects appear
- the place codegen runs against
- the place where cleanup is explicit

It is not:

- the owner of substrate lifetime truth
- the scheduler
- the mutation authority

`RiftSpace` should own:

- target registries
- target metadata
- local cleanup state
- occupancy/session state as needed
- configuration-aware access to runtime behavior

It should support:

- listing targets
- describing targets
- binding attributes
- binding methods
- clearing targets
- running code
- closing/cleaning the space

That is the operational center of AR.

---

## 28. RiftSpace Registries

The target model should be explicit.

At minimum:

- `attributes: dict[str, RiftAttribute]`
- `methods: dict[str, RiftMethod]`

Each entry should be able to carry metadata such as:

- `name`
- `source`
- `local/shared/imported/promoted`
- cleanup policy
- notes
- optional tags
- optional validation hints

The point of the registry is:

- codegen has a target universe
- validation has a target universe
- the operator can inspect what exists
- cleanup can be explicit

Without that, the workspace devolves into ambient Python state and loses one of
its strongest advantages.

---

## 29. RiftAttribute In Detail

`RiftAttribute` is a named workspace value/object target.

Typical examples:

- imported system object
- imported data structure
- local helper object
- temporary analyzer
- temporary patch helper
- local composed object

It is not a full sandbox.
It is not a second ownership model.
It is a workspace-visible target.

Its main reasons to exist are:

- target naming
- AST/member validation target
- cleanup handle
- provenance carrier

It should stay lightweight.

If it becomes too magical, it is doing too much.

---

## 30. RiftMethod In Detail

`RiftMethod` is a named workspace callable target.

Typical examples:

- exposed system method
- utility runner
- local helper function
- generated callable used repeatedly in the workspace

Its main reasons to exist are:

- explicit callable target naming
- validation target
- cleanup handle
- inspectability

Again, it should stay lightweight.

It is a target record, not a workflow engine.

---

## 31. Why The Target Model Exists At All

The target model is not there because Python lacks variables or methods.

It is there because the workspace needs:

- declared things
- inspectable things
- clear names
- cleanup handles
- validation anchors

Without it, codegen would operate against ambient raw state and the room would
lose most of its legibility.

So the target model is one of the architectural pillars, not fluff.

---

## 32. RiftValidationSystem In Detail

`RiftValidationSystem` is the codegen parse/validate/classify subsystem.

It should own:

- AST parsing
- AST allow/deny validation
- target/member path validation
- mode-aware validation
- intent classification
- validation hook execution

It should not own:

- transport concerns
- the whole runtime
- the complete external sentinel story

The important distinction is:

- it validates the supported path
- it does not solve every possible trust problem by itself

That is why user-added sentinels still matter.

---

## 33. RiftConfiguration In Detail

`RiftConfiguration` defines how the Rift behaves.

It is about runtime behavior, not caller capability.

Likely responsibilities:

- `mode = simple | dynamic`
- configured target frame selection/exposure
- conduit exposure rules
- target registration rules
- occupancy/thread settings
- validation hook registrations
- cleanup defaults
- maybe audit defaults

It is not the ACL profile.

That distinction must stay clean:

- config = behavior/settings
- profile = capability/exposure/ACL semantics

Practical reading of that now:

- the Rift configuration chooses which frame is exposed by default
- `Aether` provides the real support for that frame
- the Rift exposes conduits and objects from that configured frame into the
  room/workstation surface
- profiles decide what from that exposed frame surface is actually visible and
  usable

---

## 34. Profile Layering In Detail

Current profile stack:

- `RiftProfile`
- `AethericFrameProfile`
- `SpellbookRiftProfile`
- `SpellRiftProfile`

### RiftProfile
Top-level aggregate capability picture.

### AethericFrameProfile
Frame-level posture and state/governance picture.

### SpellbookRiftProfile
Spellbook-level defaults for AR behavior/exposure.

### SpellRiftProfile
Per-spell override.

This stack gives us:

- global capability picture
- frame posture
- spellbook defaults
- spell-specific refinement

That is enough for v1 without reintroducing `ConduitProfile`.

### 34.1 Where Profiles Actually Live

Profiles should not be thought of as AR-invented truth detached from the
substrate.

The current model is:

- frame-level posture lives with the frame side of the system
- spellbook-level posture lives with the spellbook side
- spell-level posture lives with the spell/object side
- `AethericRiftSystem` aggregates and indexes those profile references

So the system owns the aggregate AR view, but the underlying profile truth is
still attached to the substrate objects that actually matter.

### 34.2 How Profiles Feed The Workspace

Profiles are not magic runtime enforcement.

What they actually do is shape exposure.

That means:

- which conduits from the target frame are visible
- which objects from those conduits are visible
- which methods or attributes get projected into the room
- which room type is appropriate for the current Rift posture

So the workflow is:

1. configured target frame is selected
2. frame/spellbook/spell profiles are aggregated
3. the room surface is populated from that aggregate exposure picture

That is a much more honest model than pretending profiles alone are a security
boundary.

### 34.3 Bottom-Up Override Rule

The current merge rule is:

- `AethericFrameProfile` provides defaults
- `SpellbookRiftProfile` refines those defaults
- `SpellRiftProfile` provides the final override

So the lowest level wins.

That means a spell-level profile can override both spellbook and frame posture,
while a spellbook-level profile can override frame defaults but not a concrete
spell override.

### 34.4 What Profiles Actually Need To Define

Profiles should define:

- what is exposed
- how it is exposed
- what gets populated into the room

not:

- a fake guarantee that Python itself is contained

Concretely:

#### AethericFrameProfile

Should define things like:

- whether the frame is exposable
- which conduits can be surfaced
- whether frame-level services are visible
- default exposure posture for things inside the frame

#### SpellbookRiftProfile

Should define things like:

- which spells are available from the spellbook
- spellbook-level exposure defaults
- how spellbook-derived things should populate the room

#### SpellRiftProfile

Should define things like:

- final per-spell exposure
- final alias or exposed name
- whether it appears as `RiftMethod`, `RiftAttribute`, or metadata
- whether dynamic use is allowed

### 34.5 Profile Maintenance

`AethericRiftSystem` should maintain the aggregate profile view.

That means:

- frame profile changes should invalidate the aggregate
- spellbook profile changes should invalidate the aggregate
- spell/profile or structure changes should invalidate the aggregate

The system should then rebuild the exposed room view from substrate truth.

---

## 35. Workstation As A Semantic Surface

`Workstation` should be treated as:

- the semantic operation surface experienced through `RiftSpace`

not:

- a separate top-level owning object

That means workstation tells us what operations exist conceptually:

- discover
- invoke
- get/set
- create/destroy
- bind/unbind
- codegen submit/validate/run

And in the current AR direction, that workstation surface is fed by:

- the configured target frame selected by the Rift
- the conduits exposed from that frame
- the profile-filtered targets surfaced into the room

But the actual live object doing that is still the space.

That is the clean separation.

---

## 36. The Codegen Lifecycle

The agent submits a string.

The system:

1. stores the code artifact
2. parses to AST
3. validates syntax
4. validates target/member paths against the workspace registry
5. classifies intent
6. executes in the workspace context
7. optionally materializes local outputs back into the workspace

That means codegen is:

- expression language
- build language
- operation language

But not automatically:

- canonical mutation

That boundary matters.

---

## 37. StaticRiftSpace In Detail

`StaticRiftSpace` is the lower-risk workspace surface.

It is the main enforcement boundary.

It still has:

- a root conduit underneath
- declared targets
- codegen

It should not need:

- surrogates
- `ObjectRef`
- fake Python proxy layers

Instead it should work through:

- preconfigured or explicitly bound `RiftMethod`s
- preconfigured or explicitly bound `RiftAttribute`s
- mediated interaction over those exposed surfaces

So in `StaticRiftSpace`, the agent:

- operates on declared preconfigured targets
- uses the static callable/value surface
- cannot grow the local runtime world through the conduit

That is a real mode.
It is not “no runtime.”

---

## 38. DynamicRiftSpace In Detail

`DynamicRiftSpace` keeps everything from `StaticRiftSpace` and adds:

- direct root conduit use as local construction substrate
- local helper creation
- local object creation
- local tool creation
- binding those outputs back into the workspace

It still does not automatically imply:

- canonical mutation

So `DynamicRiftSpace` is:

- local runtime freedom

not:

- canonical structural evolution by default

What Dynamic really relies on is:

- AST preflight
- hooks
- direct dict-backed target registries

It should not pretend to be safer than that.

### 38.1 Namespace In Dynamic

Namespace matters mainly in `DynamicRiftSpace`.

#### Static

In static, namespace pressure is low:

- one configured frame
- one enforced/static surface
- predeclared target names

So namespace can often be omitted or kept flat there.

#### Dynamic

In dynamic, namespace is useful because:

- more than one conduit may be surfaced
- names can collide
- provenance matters

The current direction is:

- namespace is conduit-centered
- if multiframe is active, frame name qualifies the conduit namespace

So:

- single-frame dynamic: conduit namespace is usually enough
- multiframe dynamic: `frame_name.conduit_name` becomes necessary

#### Naming rule

If a conduit is unnamed, it should not participate in dynamic namespace
exposure.

That means:

- unnamed conduits can still exist in substrate truth
- but dynamic exposure requires a usable conduit name or explicit alias

---

## 39. Local Construction Versus MutationResearch

This must stay explicit.

### Local construction

Examples:

- helper object
- probe
- analyzer
- local method
- local tool
- temporary composed object

These are AR workspace activity.

### Canonical mutation

Examples:

- versioning an existing durable object
- promoting a new durable form
- rolling back a canonical change
- migrating durable state between canonical forms

This is MR.

This is one of the most important boundaries in the architecture.

---

## 40. Validation Limits And Sentinel Layering

AST and target validation are useful for:

- syntax filtering
- declared-target governance
- member-path governance
- intent classification
- auditable supported-path behavior

They are not enough for:

- final adversarial same-process security guarantees

So the right architecture is:

- AR provides the supported path and hook points
- users can layer stronger sentinel systems on top

That keeps AR honest and extensible.

---

## 41. What Tomorrow’s Build Should Mean

The build should start from:

1. `AethericRift`
2. AR-local `Spellbook`
3. root conduit
4. `RiftConfiguration`
5. `RiftSpace`
6. `RiftAttribute`
7. `RiftMethod`
8. `RiftValidationSystem`

Then:

- `simple` mode end-to-end
- `dynamic` mode local construction
- MR integration later

That is the actual build direction now.

---

## 42. The Operator Model

The architecture assumes that the operator is not merely a passive API caller.

The operator:

- inspects the current runtime world
- discovers available capabilities
- binds or imports what is needed into the workspace
- writes codegen to operate on those declared targets
- may build local helpers, tools, probes, or composed objects
- validates and re-validates work
- decides whether outputs stay local, are discarded, are salvaged, or are
  promoted into canonical mutation flow

This matters because the workspace is not designed as a toy shell.
It is a room for meaningful runtime work.

The operator is expected to:

- work with explicit targets
- understand that local construction and canonical mutation are different
- clean up transient workspace state
- respect the distinction between substrate truth and workspace convenience
- use stronger sentinels or external validation when the task requires it

This is not a “human babysitting loop” architecture.
It is a governed operator architecture.

---

## 43. Governed Responsibility Versus Babysitting

The current architecture is not trying to trap the agent in a tiny
permission-poor environment.

It is also not trying to assume the agent is infallible.

The system is aiming for:

- enough freedom to do meaningful work
- enough structure to make the world legible
- enough validation to keep the supported path coherent
- enough lifecycle/cleanup semantics to recover from mistakes

This means:

- the agent is treated as a participant in the system
- the user is not expected to manually babysit every action
- stronger validation/sentinel layers can exist on top of AR
- but AR itself is not trying to solve every future safety problem internally

This is the difference between:

- a toy sandbox
and
- a governed runtime room

The room is not harmless by default.
It is useful by design and bounded by policy, cleanup, audit, and mutation
boundaries.

---

## 44. The Agent’s Working Ethics In This System

The intended working discipline for the operator in this world should be:

1. inspect before acting
2. prefer the least intrusive path that solves the job
3. build local helpers in the workspace before mutating canonical structures
4. keep local construction local unless there is a reason to promote
5. validate before promotion
6. preserve meaningful state when forms change
7. clean up transient structures aggressively
8. leave a legible trail of what was built, used, discarded, or promoted

This leads to the following practical distinctions:

- local helper creation is cheap
- local experimentation is normal
- canonical mutation is expensive
- durable promotion is a distinct event
- salvage is a first-class outcome, not a failure afterthought

The operator should not treat every created thing as:

- permanent
- canonical
- or shared by default

Likewise, the system should not force every created thing to become durable.

The architecture is strongest when:

- the operator can act freely in the local room
- while still understanding when the work is about to become canonical

---

## 45. The Workspace Lifecycle

The workspace lifecycle should be treated as explicit and normal.

Suggested lifecycle:

1. create/open `RiftSpace`
2. inspect current declared targets
3. import or bind any additional system objects needed for the task
4. optionally create local helpers, tools, or probes in `dynamic`
5. run codegen against the current target universe
6. keep, clear, or replace local targets as the work progresses
7. decide whether any output should move into canonical mutation flow
8. close/cleanup the workspace when the tranche is done

What closing the workspace should imply:

- local target cleanup
- release of local transient tools
- release/cleanup of the root-conduit-local transient world where appropriate
- no silent persistence of temporary runtime sludge

What closing the workspace should not imply:

- destruction of canonical user runtime objects imported from outside the
  workspace
- mutation rollback unless the work had actually crossed into MR semantics

The workspace should feel disposable and reconstructable.
That is one of its strengths.

---

## 46. Local Construction In Detail

One of the most important things we settled on is:

**local workspace construction is normal AR activity**

Examples of local construction:

- creating helper objects
- building local utility methods
- generating probes
- creating analyzers
- creating temporary strategy objects
- building local composed views over system objects
- constructing temporary local toolchains for the current problem

These things live in the workspace.
They are not canonical by default.
They should be easy to:

- name
- inspect
- replace
- clear
- discard

This matters because a lot of useful runtime work depends on building temporary
machinery around the live system:

- probes
- analyzers
- adapters
- patch helpers
- comparison tools
- migration helpers

If the system cannot host those locally, the architecture loses much of its
power.

---

## 47. Canonical Mutation In Detail

MutationResearch is where local work stops being local.

Canonical mutation begins when one or more of these become true:

- the operator is iterating on a durable existing canonical object
- the result is intended to survive beyond the workspace
- the result should become part of the stable runtime world
- state migration between forms matters
- rollback becomes a real system obligation
- promotion/discard becomes a real release decision

This means a mutation is not:

- just any codegen
- just any helper object
- just any local creation

It is:

- canonical evolution of durable structure

That distinction is critical because without it:

- the workspace becomes too heavy
- every helper feels like a release artifact
- and the operator cannot reason clearly about what is temporary versus what is
  part of the actual system

MutationResearch should therefore remain:

- explicit
- governed
- versioned
- validation-heavy
- promotion-aware

and distinct from ordinary local work.

---

## 48. The Relationship Between The Workspace And The Root Conduit

The root conduit is the local runtime reality for the space.

Important clarifications:

- the conduit exists in both `StaticRiftSpace` and `DynamicRiftSpace`
- the existence of a conduit does not make the space “dynamic” by itself
- `StaticRiftSpace` means the conduit is not exposed as a local construction instrument
- `DynamicRiftSpace` means the conduit is exposed as a local construction instrument

This distinction is important because otherwise the mode split collapses.

If the conduit is always exposed for arbitrary construction, then
`StaticRiftSpace` has
no real meaning.

If the conduit exists but is hidden as a construction tool in
`StaticRiftSpace`, then:

- the room still has a real execution substrate
- but the operator is limited to the declared target surface

That is the right tradeoff.

In `DynamicRiftSpace`, the conduit can be used to:

- materialize local helper objects
- create local utility structures
- bind those local outputs back into the room
- support richer local experimentation

This is one of the strongest parts of the model.

---

## 49. The Role Of AethericFrameProfile

The architecture needed a frame-level profile because the workspace is not the
only level at which AR semantics matter.

`AethericFrameProfile` should represent:

- the frame’s AR-relevant posture
- frame-level governance/state that shapes the room
- defaults or constraints that belong above spellbook/spell granularity but
  below the purely global level

This keeps us from collapsing all governance into either:

- a top-level aggregate profile
or
- the workspace configuration

The profile layering now looks like:

- `RiftProfile`
  top-level aggregate capability picture
- `AethericFrameProfile`
  frame-level posture
- `SpellbookRiftProfile`
  spellbook-level defaults
- `SpellRiftProfile`
  most specific override

This is a more mature layering than the older February profile concepts.

---

## 50. The Validation Story

The architecture now treats validation more honestly than many systems do.

What AR validation is good for:

- syntax filtering
- target/member allowlists
- lane classification
- auditability of code intent
- providing a governed supported path

What AR validation is not:

- a total solution to adversarial same-process security
- the only validation layer a serious deployment should rely on

This matters because if we pretend AST and target validation solve everything,
we build a false mental model.

The actual intended validation stack is:

1. built-in AST and target/member validation
2. optional user-defined hooks in `RiftValidationSystem`
3. optional stronger sentinel systems layered by the user or org
4. optional external or subprocess validation paths where needed

So AR provides:

- the structure
- the supported path
- the extension points

not:

- the entire future of safety and trust

---

## 51. Workspace Collaboration And Sharing

The current architecture no longer treats collaboration as the center of the
model, but it still needs to be understood.

The main room is `RiftSpace`.

By default, the room is one working environment with one root conduit.
Multiple agents may eventually operate in or around such rooms, but the
important thing is:

- local work should stay local by default
- canonical work should not happen accidentally
- promotion/share should be explicit

The architecture should remain compatible with:

- one agent in one room
- several agents coordinating through higher-level tooling
- richer multi-agent orchestration through CommandOps

But the v1 room should not be defined primarily by multi-agent complexity.

That is a later scaling concern, not the thing that makes the room itself
coherent.

---

## 52. Dynamic Objects In Practice

The current philosophy should also be restated in practical terms.

Dynamic objects are worth entertaining here because the system wants to support:

- live capability inspection
- local helper construction
- scoped experimentation
- reusable transient tools
- promotion of better structures later
- salvage of meaningful state later

This is why durable state remains the center:

- local forms can change
- helper structures can come and go
- the workspace can be created and destroyed
- but meaningful state should still survive when it matters

That is why the architecture is less about “objects that can be monkey patched”
and more about:

- continuity-bearing capability structures

This distinction matters because it tells us what kind of system we are really
building.

---

## 53. What The Long-Form Ticket Should Continue To Do

This document should be extended as the architecture settles further.

It should accumulate:

- clarified object roles
- clarified mode semantics
- clarified operator workflow
- clarified mutation boundaries
- clarified lifecycle and cleanup semantics
- clarified profile layering

It should not become:

- an implementation changelog
- an overfitted code inventory
- or a stale summary that falls behind the actual design

The point is that if memory is wiped, this should be one of the first files that
lets us reconstruct the current worldview without replaying all the chat
history.

---

## 54. Workspace Target Registration Model

The workspace should not be treated as ambient Python state.

It should have an explicit target registration model.

That model exists so:

- the operator knows what is available
- codegen has a declared target universe
- validation has something concrete to validate against
- cleanup has named handles
- the room stays legible over time

At minimum the workspace should support:

- register attribute target
- register method target
- list attribute targets
- list method targets
- inspect target metadata
- clear/remove a target
- clear all local transient targets if desired

The target model should support both:

- imported runtime things
- locally created workspace things

That is what makes the room usable rather than accidental.

---

## 55. Target State Classes

Every workspace target is not the same kind of thing.

At minimum, the architecture should acknowledge these distinctions:

### 55.1 Imported

A target imported or bound from the broader system/runtime world.

Examples:

- a real service object
- a system helper
- a spell-backed capability
- a monitoring object

These are not local by origin.

### 55.2 Local

A target created inside the workspace using local construction.

Examples:

- a helper object
- a patch helper
- a temporary analyzer
- a temporary utility method

These are expected to die with the workspace unless deliberately promoted.

### 55.3 Shared

A target that is available to more than one actor or workspace context by design.

This is not the default assumption for every local thing.
It is something that should be visible and explicit.

### 55.4 Promoted

A target whose value has moved beyond local workspace utility and become part of
the broader accepted runtime world.

This is where MR begins to matter.

These distinctions should be represented in metadata and in operator reasoning.

---

## 56. Workspace Registration Philosophy

Registration inside the workspace should be easy, because local utility
construction is a core part of the system.

The operator should be able to:

- bind an imported object as a `RiftAttribute`
- bind a callable as a `RiftMethod`
- build a helper object and register it
- build a helper method and register it
- replace a local target
- clear a local target

Registration should not imply:

- canonical durability
- global mutation
- promotion
- persistence beyond the space unless explicitly chosen

This is important because the room is supposed to support:

- experimentation
- temporary local machinery
- transient helper structures

without forcing every created thing to become a permanent system concern.

---

## 57. Build, Validate, Execute, Cleanup

The work loop inside AR should be understood in explicit phases.

### 57.1 Discover

The operator:

- enters the workspace
- inspects available targets
- inspects target provenance and metadata
- determines whether the job needs only existing targets or also local
  construction

### 57.2 Bind / Import

If needed, the operator:

- binds imported system objects into the room
- names them as attributes or methods

### 57.3 Build

The operator:

- writes codegen as a string
- maybe intends to produce:
  - local helper object
  - local helper method
  - probe
  - analyzer
  - composed object
  - temporary utility

### 57.4 Validate

`RiftValidationSystem`:

- parses AST
- validates syntax
- validates names/member paths
- classifies intent
- applies hooks

### 57.5 Execute

The code runs against the workspace context.

In `simple`:

- it uses declared targets only

In `dynamic`:

- it may also use the root conduit as a local construction substrate

### 57.6 Register local outputs

If the execution produced useful local objects or methods:

- register them in the workspace target registries

### 57.7 Cleanup

When the tranche is done:

- clear local helpers that no longer matter
- clear temporary targets
- close the workspace when the room is no longer needed

### 57.8 Promote only when truly needed

If the result should become canonical:

- move into MR semantics

This phase view matters because otherwise:

- every code block looks the same
- local helper creation gets mixed with canonical mutation
- cleanup gets ignored

---

## 58. Validation Layers In Practice

Validation should be thought of as layered.

### 58.1 Native AR validation

Built into the Rift:

- AST parse
- syntax checks
- target/member checks
- intent classification
- validation hooks

### 58.2 User hooks

Configured through `RiftConfiguration`:

- custom checks
- custom restrictions
- extra validation passes

### 58.3 Sentinel systems

Layered on top by the user or org:

- anomaly detection
- stronger behavioral restrictions
- local policy systems
- external trust models

### 58.4 External validation when needed

When the task warrants it:

- testbench
- subprocess validation
- external harnesses

This layered model is healthier than pretending one validator is enough.

---

## 59. Imported Objects Versus Local Objects

One of the recurring confusions in the architecture is between:

- imported system objects
and
- locally constructed workspace objects

The distinction should remain explicit.

Imported object:

- came from outside the room
- often matters to the broader system already
- should not be assumed local or disposable

Local workspace object:

- was created in the room
- exists to help with the current work
- should be considered disposable by default

Promotion is the event that turns:

- local

into:

- durable/canonical

That boundary needs to stay visible everywhere in the design.

---

## 60. Collaboration And Sharing

The current architecture is not centered on multi-agent sharing, but it should
still be able to talk about it.

At minimum:

- one room should work well for one operator
- the room should not assume a scheduler
- CommandOps remains the place where mission-level multi-agent coordination
  lives

The room should still be compatible with:

- multiple operators entering
- shared targets
- explicit sharing or imported bindings

But the architecture should not lose its center by trying to solve all
collaboration semantics first.

The room comes first.
The coordination story can grow around it.

---

## 61. Why This Is Not Just A DI Container

This stack is more than:

- DI
- plus FastAPI
- plus some validation

because it also gives:

- a legible runtime world
- codegen-native operation
- workspace-local construction
- canonical mutation as a later explicit path
- local helper/tool ecosystems
- profile layering
- substrate-backed cleanup and scope semantics

That is why the architecture matters.

It is not only about injecting dependencies into handlers.
It is about giving the operator a world to work in.

---

## 62. Why The Room Matters

The room is one of the deepest ideas in the whole system.

Without the room, the operator gets:

- a pile of APIs
- or a tool catalog
- or raw substrate access

With the room, the operator gets:

- context
- declared targets
- local construction
- cleanup boundaries
- a place to build and throw away temporary machinery

That is why the workspace is not a side detail.
It is the center of the AR experience.

---

## 63. Durable State Revisited

The architecture still keeps returning to one core truth:

- durable state matters more than frozen object form

This applies at every level:

- local objects can be rebuilt
- local methods can be regenerated
- workspaces can be closed and reopened
- helpers can be discarded

But if meaningful state is lost, the system loses continuity.

That is why:

- mutation
- migration
- salvage
- promotion
- rollback

are not optional philosophical extras.
They are the continuation mechanisms for a living runtime world.

---

## 64. The Main Recovery Principle

If memory is wiped, this document should let us recover:

- what the system is
- what the room is
- what the operator can do
- what is local versus canonical
- what objects are real in the active model
- what modes exist
- where MR begins

That is the actual standard this document should be judged against.

---

## 65. Operator Workflow Examples

The architecture becomes much clearer when expressed as concrete operator
tranches rather than abstract object lists.

### 65.1 Simple-mode operational use

Scenario:
- the operator enters a `StaticRiftSpace`
- the room already exposes predeclared targets such as:
  - `service_status`
  - `validator`
  - `incident_writer`

Workflow:
1. inspect available targets
2. write codegen against those declared names
3. validate
4. execute
5. receive result
6. no new local runtime construction occurs

What this is good for:
- diagnostics
- bounded automation
- controlled invocation over an already approved surface
- lower-risk operational use

### 65.2 Dynamic local helper construction

Scenario:
- the operator enters a `DynamicRiftSpace`
- the root conduit is available as a local construction substrate
- the operator needs a temporary analyzer or helper object

Workflow:
1. inspect current targets
2. write codegen that builds a local helper object or helper callable
3. validate
4. materialize through the root conduit
5. register as `RiftAttribute` or `RiftMethod`
6. use it for the current task
7. clear it or let it die with the workspace later

What this is good for:
- temporary probes
- analyzers
- adapters
- patch helpers
- short-lived local tooling

### 65.3 Canonical mutation workflow

Scenario:
- the operator is no longer just building local helpers
- the operator is iterating on a durable canonical object

Workflow:
1. inspect the canonical object and current lineage
2. prepare candidate change
3. validate candidate
4. run canonical mutation lifecycle
5. decide promote / rollback / discard
6. if needed, migrate or salvage meaningful state

What this is good for:
- real structural evolution
- durable versioning
- canonical state transitions

### 65.4 Local experimentation that never becomes canonical

Scenario:
- the operator wants to compare two local candidate helpers

Workflow:
1. create `candidate_a`
2. create `candidate_b`
3. bind both into the room
4. compare behavior against imported system targets
5. keep one as a workspace helper or discard both

This never becomes MR unless one candidate crosses the canonical boundary.

---

## 66. Workspace Registry Semantics

The workspace target registries should not just be thought of as dictionaries.
They are the declared object universe for the room.

At minimum:

- `attributes: dict[str, RiftAttribute]`
- `methods: dict[str, RiftMethod]`

For each entry, we should be able to know:

- name
- kind
- bound value/callable
- source/provenance
- local / imported / shared / promoted state
- cleanup policy
- optional notes or tags

### 66.1 Registration rules

The workspace should support:

- register attribute
- register method
- replace attribute
- replace method
- clear attribute
- clear method
- list all current targets
- inspect one current target

### 66.2 Why explicit registries matter

They give us:

- a declared universe for AST/member validation
- a stable naming surface for codegen
- clear cleanup handles
- inspectable room state
- a way to distinguish local versus imported versus promoted things

Without explicit registries, the room degrades into ambient Python state and
loses one of its core architectural advantages.

### 66.3 Registry state classes

Every target should conceptually be classifiable as one of:

- `imported`
- `local`
- `shared`
- `promoted`

That state should not be implicit only in the operator’s head.
It should be representable in metadata.

### 66.4 Cleanup semantics

The cleanup model should assume:

- `local` targets can die with the room unless explicitly preserved
- `imported` targets should not be destroyed just because the room closes
- `promoted` things are no longer just workspace-local concerns

This keeps cleanup coherent and prevents accidental durable-state mistakes.

---

## 67. Simple And Dynamic Examples

### 67.1 Simple mode example

Available targets:

- `validator`
- `service_status`
- `incident_writer`

Allowed codegen shape:

```python
if validator.check(service_status):
    incident_writer.write("status looks healthy")
```

Not allowed:

- use conduit to create local helper objects
- register new runtime objects in the room
- use mutation flow

This is still codegen-native, but the room is fixed in structure.

### 67.2 Dynamic mode example

Available targets:

- imported targets from simple mode
- root conduit surfaced into the room

Allowed codegen shape:

```python
# build local helper logic, materialize it, register it into the room,
# then use it against current targets
```

The important difference is:

- the room can now grow local helper structures
- but that still does not mean canonical mutation has happened

### 67.3 Why this distinction matters

If `simple` can freely create and register new local runtime structures, then
it is no longer meaningfully different from `dynamic`.

If `dynamic` is allowed to do canonical mutation without crossing into MR, then
MR loses its role.

So:

- `StaticRiftSpace` = fixed target universe
- `DynamicRiftSpace` = local workspace construction
- `MR` = canonical evolution

That three-way distinction is one of the most important design anchors we have.

---

## 68. Local Construction Versus MR Promotion

This deserves one more concrete pass because the system easily becomes muddy
without it.

### 68.1 Local construction

Local construction means:

- build helper objects
- build temporary methods
- build probes
- build analyzers
- build patch helpers
- build local composed structures
- bind them into the room
- use them
- clear them later

This is ordinary AR work in `dynamic`.

### 68.2 Promotion threshold

A local thing crosses into MR concern when one or more of these become true:

- it is intended to survive the workspace
- it is intended to become a durable part of the runtime world
- it iterates on an already canonical object
- it requires durable versioning/rollback semantics
- meaningful state migration is now part of the work

### 68.3 Why this threshold matters

Without this threshold:

- every local helper feels too heavy
- or every canonical mutation feels too casual

That is exactly what the architecture is trying to avoid.

The rule is:

- local work stays local by default
- canonical evolution is explicit

That is the practical operational doctrine.

---

## 69. Target Registration API Semantics

The workspace target model becomes much stronger if registration rules are
explicit instead of implied.

At minimum, the room should conceptually support:

- `register_attribute(name, value, metadata?)`
- `register_method(name, callable, metadata?)`
- `replace_attribute(name, value, metadata?)`
- `replace_method(name, callable, metadata?)`
- `clear_attribute(name)`
- `clear_method(name)`
- `describe_target(name)`
- `list_attributes()`
- `list_methods()`

### 69.1 Registration expectations

For every registration, the room should know:

- target name
- target kind (`attribute` or `method`)
- source/provenance
- cleanup policy
- local/imported/shared/promoted classification
- optional notes/tags

### 69.2 Name collision rules

The architecture should not leave this fuzzy.

The likely default should be:

- register fails if the name already exists
- replace is the explicit operation for overwriting

This matters because it keeps the room from silently mutating under the
operator’s feet.

### 69.3 Replacement semantics

Replacing a target should be explicit because replacement can mean:

- a harmless local helper update
- or a meaningful change in the active local working set

So:

- `replace_*` should be explicit
- replacement should update metadata
- replacement should leave a clear trail for inspection or audit if desired

### 69.4 Clearing semantics

Clearing a target should:

- remove the target from the declared universe
- prevent further codegen from treating that name as valid
- not silently destroy canonical imported things it does not own

This is one of the strongest reasons the target model exists.

### 69.5 Imported target rules

If a target is imported from outside the room:

- its provenance should be explicit
- the room may stop referencing it
- but the room should not assume it owns the underlying canonical object

This avoids accidental overreach by local cleanup.

### 69.6 Promoted target rules

If a target has been promoted into a broader canonical role, it should stop
being treated as an ordinary local binding.

That means:

- metadata should reflect promotion
- local clear/remove semantics should no longer be treated as sufficient
- the operator should be forced through the appropriate canonical path instead

This is another place where local versus canonical must remain explicit.

---

## 70. Local Construction Lifecycle

The room supports local construction in `dynamic`, but that process needs an
explicit lifecycle.

### 70.1 Materialize

A local helper/tool/object is materialized through the root conduit.

This means:

- it is not just an ambient Python local
- it has a real substrate-backed runtime existence
- it can be bound into the room as a target

That is what makes local workspace construction meaningful.

### 70.2 Bind

Once materialized, the result can be bound into the room:

- as a `RiftAttribute`
- or as a `RiftMethod`

depending on what kind of thing it is.

### 70.3 Use

Once bound:

- codegen can target it
- direct room operations can target it
- it becomes part of the local working world

### 70.4 Replace

If a better local helper is built:

- replace the target explicitly
- keep provenance clear
- do not pretend replacement is invisible

### 70.5 Clear

When no longer needed:

- clear it from the room
- let local cleanup semantics run
- if it only exists locally, it should be expected to die cleanly

### 70.6 Workspace close

When the room closes:

- local transient objects should be expected to disappear with the room or its
  root conduit reality
- imported canonical things should not be destroyed merely because they were
  visible in the room

### 70.7 Promotion threshold

If a locally constructed object becomes important enough to survive the room:

- it should no longer be treated as merely local
- it should cross the canonical boundary explicitly
- if it is versioned/promoted, that is no longer ordinary room cleanup

This is the point where MR semantics or broader durable runtime semantics start
to matter.

### 70.8 Recovery expectation

After restart or memory wipe:

- local room objects are not assumed durable by default
- what must survive should have been promoted, externalized, or represented in
  durable state

This is why the room is strong for work, but not the same thing as the
canonical city.
