# AR Codegen Capability Surface Philosophy

## Metadata
- Artifact ID: ART-2026-04-26-ar-codegen-capability-surface-philosophy
- Parent Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: active
- Created: 2026-04-26T13:03:57Z
- Updated: 2026-04-26T14:09:07Z

## Purpose
Capture the philosophy for AR codegen as a capability surface before later
Crystallizer and MutationResearch work hardens around the wrong model.

This artifact exists to keep the ordering clear:
- first understand AR and codegen as capability surfaces
- then understand how agents work with those capabilities
- only then decide how Crystallizer and mutation systems should preserve,
  promote, and replace what agents build

## Why This Matters Now
The stack is at the point where capability exceeds explanation.

That is dangerous.
If we do not explain what AR/codegen actually is, later systems will be built
on a flattened story like:
- codegen equals mutation
- AR equals "a bunch of tools"
- anything useful should immediately become file-backed

That would undersell the real system and distort the later design.

This artifact therefore exists to preserve the real ordering:
- capability first
- workflow second
- crystallization and mutation later

## Relationship To Sandbox Design
This artifact explains the capability side of the system.
It should be paired with:
- `artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md`

The split is:
- this artifact
  - what AR/Rift/codegen are for
  - why they are mediated capability surfaces
- the sandbox artifact
  - where lower-trust execution should run
  - why the planned CommandOps direction should use container/pod workers
    instead of copying Codex local host-process sandboxing directly

That pairing matters because capability philosophy without sandbox philosophy
can accidentally give agents too much raw reach, while sandbox philosophy
without capability philosophy can flatten Rift into "just another tool runner."

## Core Thesis
AR is not the whole philosophy of the system.
AR is the mediated capability surface over Melder.

That means:
- `Melder` owns the live object world and runtime capabilities
- `Rift` exposes a mediated surface into that world
- `Codegen` gives agents a governed construction and execution surface inside
  that world
- `CommandOps` owns orchestration, debugger-style control, workflows, and
  broader agent operating philosophy

This separation matters because Melder should remain a capability world, not a
catch-all home for every higher-level agent workflow idea.

Another way to say it:
- Melder gives the terrain
- AR gives reach into that terrain
- CommandOps defines how actors move through it

## What AR Gives The Agent
Current AR/codegen source already supports a meaningful capability surface:

- `viewer`
  - perception over descriptor and ACL truth
- `workstation`
  - local working memory and bound object storage
- `target`
  - focused selected object from the workstation
- `command`
  - mediated action surface over room/runtime capabilities
- `codegen`
  - governed validate/execute recursive control surface

At the room level:
- `CodegenRiftSpace` owns the internal `CodegenSystem`
- `CodegenCommandSystem` is the public room-facing facade
- `CodegenSystem` owns:
  - transaction context construction
  - validation
  - namespace construction
  - compile
  - exec
  - lifecycle event publication through the room event system

So codegen already is a live runtime facility.
It is not a future-only concept.

## Room Postures Matter
AR is not one flat mode.
The room posture changes what the agent can do and how directly it can do it.

### Static
- restrictive
- live-only spell-facing retrieval
- no topology mutation
- reuse-oriented interaction
- best understood as a read-and-reuse room

### Capability
- broad manual runtime and object access
- richer command surface
- no codegen execution
- best understood as a direct manual control room

### Codegen
- governed live Python execution
- selected runtime-helper surface
- internal codegen engine owned by the room
- best understood as a synthesis and construction room

This matters philosophically because "AR capability" is not singular.
It is posture-shaped.

## What Codegen Is
Codegen should not be defined primarily as mutation.

Codegen is an agent-native construction and execution surface over a live
capability world.

Its first meaning is:
- the place where an agent can turn understanding into executable structures
  inside the runtime

More sharply:
- codegen is where thought becomes executable in the live world
- not every execution is a mutation
- not every execution is a durable commitment
- not every useful execution needs a file

That makes codegen closer to:
- a runtime composition medium
than to:
- a glorified script runner

## Current Codegen Mechanics
Current source-backed mechanics are already quite concrete:

1. Build a transaction context
- `transaction_id`
- `frame_name`
- raw `code`
- deterministic `code_hash`
- optional `CodegenProjection`
- namespace configuration
- later the built namespace

2. Validate before execution
- AST structure checks
- import policy checks
- builtin policy checks
- top-level name resolution
- attribute and reflection policy
- recursive codegen policy

3. Build the live namespace
- namespace entries are assembled from room/runtime strategies
- the namespace is not arbitrary; it is posture-shaped

4. Compile and execute
- compile to a code object
- `exec(...)` against the built namespace
- read `result` if present

5. Publish lifecycle and memory
- validation and execution events go to the room event system
- top-level validate/execute calls emit full-source room-memory records

That means codegen already has:
- identity
- policy
- execution
- observability

What it lacks is not existence.
What it lacks is a fuller operational philosophy around how agents should use it.

## Agent Act Taxonomy
The capability philosophy is clearer if agent behavior is divided into acts.

### Probe
- inspect live objects
- inspect relationships
- derive bounded facts
- no persistence required

### Harness
- create temporary executable probes around live objects
- exercise a behavior path
- compare outputs or conditions

### Adapter
- wrap or re-present an existing object or capability
- create proxies, shims, and translators
- improve usability without replacing the incumbent yet

### Challenger
- construct a competing implementation beside the incumbent
- compare behavior while both still exist
- learn before replacing

### Utility
- build reusable helper functions, classes, or local runtime tools
- keep them available in the workspace or conduit

### Progenitor
- create genuinely new first-class runtime objects or definitions
- bind or otherwise preserve them for later use

These acts are the real codegen vocabulary.
Mutation is only one later use of those acts.

## Codegen As Thought Externalization
One reason this matters is that codegen strings are not just scripts.
They are provisional thought artifacts.

An agent can use codegen to:
- ask a question of the runtime
- build a temporary harness
- construct a helper
- shape a rival implementation
- create a new reusable object

So codegen output may represent:
- a thought
- a tool
- a challenger
- a service
- a candidate future

That is a richer model than "generated code."

## Residency Levels For Codegen Outputs
Useful residency levels are:
- `transient`
  - one-off execution or probing
- `sessional`
  - kept around in the current runtime or room
- `bound`
  - registered into the live runtime world
- `crystallized`
  - preserved as remembered source-bearing state
- `promoted`
  - accepted as durable authority outside the current runtime

This progression matters because it prevents the system from collapsing every
successful runtime experiment directly into durable source truth.

It also means the system can support meaningful intermediate states:
- worth keeping
- not yet source authority
- too important to lose

## Workstation And Target
The workstation is not just storage.
It is the agent's local working-memory surface.

The active target is not just a convenience value.
It is focused attention.

That gives the AR/codegen capability surface a strong cognitive shape:
- `viewer` -> perception
- `workstation` -> working memory
- `target` -> focused attention
- `command` -> action
- `codegen` -> synthesis

This is more than metaphor.
It helps explain why the system feels different:
- the agent is not just calling tools
- it is arranging a temporary cognitive world inside the runtime

## Construction Before Substitution
The philosophy should bias toward additive construction before destructive
replacement.

That means:
- build helpers before rewriting systems
- build challengers before deleting incumbents
- build instrumentation before making irreversible decisions
- build runtime alternatives before promoting source changes

This is not caution theater.
It is a capability-maximizing strategy:
- additive structures are easier to compare
- easier to route
- easier to discard
- easier to learn from

It also produces a better runtime philosophy:
- construct first
- compare second
- substitute third
- promote fourth

## Runtime Before Promotion
The runtime is the first battlefield.
The file is not.

That means:
- runtime is where ideas compete
- source is where winners become durable

So codegen should be understood as the fast local arena for:
- probing
- harnessing
- adapting
- challenging
- building utilities
- creating new bound objects

Promotion and durable mutation are later acts built on top of that.

This is why the file should not dominate the philosophy.
For many important workflows, the file is:
- the later source authority
not:
- the first place where ideas should fight

## Plurality Is A Capability
The system's power is not just that an agent can write code.
The power is that multiple possible structures can coexist in one runtime long
enough to compare them.

That means the runtime should be comfortable with:
- incumbents
- challengers
- temporary harnesses
- temporary utilities
- session-only experiments
- later-promoted winners

This plurality is how the system learns what deserves durability.

This is a major philosophical break from normal software practice.
Normal systems often assume:
- one implementation
- one file
- one accepted truth

This system should be comfortable with:
- incumbents
- challengers
- temporary tools
- sessional constructions
- competing local futures

That is not confusion.
That is the actual power of the runtime.

## Mutation Is Secondary
Mutation matters, but it should not define codegen.

The correct relationship is:
- codegen is the live construction surface
- mutation is one downstream act that may use that surface

This implies:
- not every codegen output is meant to replace something
- not every successful codegen act should touch a file
- not every useful codegen object is a mutation candidate

Mutation should later be framed in terms of:
- substitution
- promotion
- durability
- incumbent/challenger resolution

not as the whole point of codegen itself.

## What Codegen Does Not Yet Own
Just as important as what codegen is, is what it is not.

Codegen does not yet own:
- durable source identity
- source-owner mapping
- file/module promotion
- structured revert
- git-like history
- incumbent/challenger adoption policy
- orchestration and debugger control

That boundary is good.
It prevents the codegen engine from collapsing into a giant everything-system.

## Melder Vs CommandOps
Melder / Rift should own:
- the live capability world
- the mediated room surfaces
- local working-memory and action surfaces
- the governed codegen execution surface

CommandOps should own:
- orchestration
- workflows
- probing and interception
- thread and process control
- debugger-style mechanics
- actor continuity and coordination
- broader agent operating philosophy

If this split is lost, Melder will absorb higher-level workflow logic that
belongs elsewhere.

This is one of the most important boundary rules in the whole stack.

Melder should stay:
- powerful
- weird
- capable

But it should not become the place where every agent philosophy and workflow
mechanic gets shoved just because it can support them.

## Workflow Implications
This capability philosophy implies workflow families such as:
- runtime inspection workflows
- runtime harness and comparison workflows
- local tool-building workflows
- challenger/incumbent comparison workflows
- codegen-native asset workflows
- later promotion and mutation workflows

Those workflows belong primarily to CommandOps, but they consume Melder/Rift
capabilities directly.

Concrete workflow families implied by the current philosophy:

### Inspection workflows
- perception-first
- gather facts from live objects and projections

### Harness workflows
- build local executable checks around live capabilities

### Toolsmithing workflows
- create local runtime utilities and reusable helpers

### Challenger workflows
- build and compare competing implementations

### Codegen-native asset workflows
- create assets that never need an initial file backing

### Promotion workflows
- later decide what should become durable authority

### Mutation workflows
- only after capability, comparison, and promotion logic are clear

That ordering matters.

## Why This Artifact Exists
This artifact exists to keep later design work honest.

It says:
- AR is a capability surface, not the whole philosophy
- codegen is a broader construction surface than mutation
- agents need a vocabulary of acts, not one bucket called mutation
- later Crystallizer work should inherit this philosophy instead of guessing
  what codegen is for

## Fog Of War
One of the reasons this philosophy is necessary is that agent work happens
under fog of war.

Agents do not begin with total certainty.
They begin with:
- partial source knowledge
- partial runtime knowledge
- partial dependency knowledge
- partial workflow knowledge

So the system should be designed for:
- progressive clarification
- bounded experiments
- additive construction
- reversible local learning

That is a much better fit for real agent behavior than pretending the agent
always knows the full truth before acting.

## Comparative Evidence
The real scarce resource in this system is not generated code.
It is comparative evidence.

Any system can generate more code.
What matters is:
- what was compared
- against what incumbent
- in what room/posture
- under what path
- with what observed result

That means the philosophy should optimize for:
- comparison
- observation
- coexistence
- evidence

more than for raw generation alone.

## The Vision
Yes, the vision is visible now.

The point is not simply:
- "agents can mutate Python"

The point is:
- agents can inhabit a live capability world
- build executable structures inside it
- compare competing realities inside one runtime
- retain what matters
- later decide what deserves durable authority

That is a much bigger idea than ordinary code editing, and it is why this
artifact matters before the later systems are built.

## Source Anchors
- `src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py`
- `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
- `src/melder/aether/nexus/rift/codegen_system/codegen_system.py`
- `src/melder/aether/nexus/rift/codegen_system/codegen_transaction_context.py`
- `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
- `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py`
