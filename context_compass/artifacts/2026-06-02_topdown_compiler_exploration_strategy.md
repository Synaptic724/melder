# Top-Down Compiler Exploration Strategy

## Purpose
This artifact is the deep strategy anchor for Melder's next compiler phase.

It captures:
- what the current architecture already gives us
- where the compiler/runtime boundary is still hybrid
- what we must converge before real optimization work
- how the exploratory harness should work
- what graph and runtime shapes we need to test
- why top-down compilation is still the right long-term bet

This is not a benchmark report.
This is the architecture and exploration plan that should guide the next two
months of work.

## Current Architecture
Melder is a top-down dependency graph runtime, not a bottom-up DI resolver.

That matters because the runtime already has these layers:
- phases 1-4:
  structural understanding of the spell and its constructor surface
- phases 5-7:
  rooted system graph construction, system validation, and change-control
  wiring
- phase 8:
  occurrence graph analysis
- phase 9:
  model fitting into structured sections
- phase 10:
  generalized lane planning
- phase 11:
  spell-static creation packaging
- runtime:
  `CreationContextBuilder`, `CreationContext`, `Meld`, `ConduitMeld`,
  `SpellSpaceMeld`, and `Creations`

The key point is that Melder already pays to understand more than a bottom-up
resolver:
- full parameter classification
- local topology
- rooted deep DAGs
- system-level validation
- contract-aware and mutation-aware routing
- rich override targeting
- existence-aware routing

That is the expensive part.
The compiler exists so we can amortize that expense.

## What Is Already Good
The current architecture already has the right broad division of labor.

### Structural compiler layers
Phases 1-4 are explicit and useful:
- Phase 1 emits `SpellRequirements`
- Phase 2 emits symbolic sockets
- Phase 3 resolves normal DI into concrete local DAG edges and local topology
- Phase 4 validates structural truth and publishes structural validity

This gives us rich compile-time knowledge that bottom-up systems do not have
without rediscovering things locally.

### Rooted system layer
Phases 5-7 are also real:
- Phase 5 lifts local topology into rooted deep DAG blueprints plus a frame
  index
- Phase 6 validates system-level structure for a conduit
- Phase 7 wires change-control and revalidation around those rooted artifacts

This means our compiler is not just a constructor helper. It is already a
system-aware planning surface.

### Analyzer and processor split
The post-rooted pipeline has real separation:
- the analyzer owns path-aware occurrence graph expansion
- the processor fits distinct model sections

That sectioning matters. The model is not one opaque blob. It already
contains separate views of:
- occurrence order
- instance/sharedness
- contract payload routing
- runtime spell facts
- injection wiring
- override targeting
- mutation targeting

That is exactly the kind of decomposition we need for later strategy
selection.

### Planner and codegen creation split
The planner is no longer just a legacy execution-plan bag. It builds
generalized lane plans and fast-path arrays, and codegen creation already
consumes those lane plans rather than going straight back to old runtime
objects.

That means the target architecture is visible.

## Where The Hybrid Still Exists
The current system is still a hybrid port.

### Phase 11 discovery is not a real family selector yet
`CodegenCreationDiscoverySystem` still returns the raw internal generalized
strategy chain:
- setup
- no overrides
- overrides
- mutation overrides

That is implementation plumbing, not true discovery.

The discovery system should eventually choose a creation strategy family based
on meaningful shape and policy facts from the `SpellCodegenModel`.

### The generalized codegen creation compilers are still huge
The no-overrides and overrides codegen creation compilers still carry too much
of the old runtime-emitter burden directly.

That is not automatically wrong, but it means the real shape of the future
system has not yet been separated cleanly into:
- discovery
- strategy family selection
- shared build state
- family-specific packaging

### Runtime still rehydrates too much spell-static packaging
`CreationContextBuilder` and `CreationContext` consume `_spell_codegen_creation`,
but the runtime still has to reconstruct and specialize a lot of behavior that
we eventually want phase 11 to hand over in a cleaner form.

The boundary is visible, but not converged.

## The Real Goal
The goal is not to make top-down compilation disappear.

The goal is:
1. pay the top-down cost once
2. preserve what we learned as meaningful spell-static artifacts
3. let discovery choose the best strategy family for the object graph shape
4. compile those decisions into specialized runtime routes
5. reuse those routes so warm execution pays far less tax

That is how Melder beats bottom-up systems long-term.

If we only compare cold path against Dishka, we are comparing the wrong thing.

Dishka has bottom-up advantages:
- less upfront graph work
- less global analysis
- faster first-pass activation

Melder should win elsewhere:
- better diagnostics
- better validation
- deeper override power
- richer agent-facing manipulation
- better shape-aware specialization
- stronger warm-path amortization once compilation is done

## Why The Compiler Matters
The compiler is where Melder's top-down leverage becomes real.

Without the compiler, top-down understanding is just overhead.

With the compiler, top-down understanding becomes:
- reusable rooted structure
- reusable occurrence truth
- reusable routing models
- reusable strategy selection
- reusable spell-static execution packaging

And once the discovery systems are mature, the compiler can do more than build
one generalized route. It can choose among families:
- narrow vs wide graph handling
- shallow vs deep graph handling
- transient-heavy vs shared-heavy routes
- override-heavy vs override-light routes
- contract-heavy vs simple routes
- mutation-aware vs mutation-free routes

That is the point.

## The Boundary We Need To Converge
We need a stricter rule:

### Compiler owns
- graph understanding
- rooted structure
- occurrence structure
- model section fitting
- strategy-family selection
- spell-static route packaging

### Runtime owns
- per-call override payloads
- admission/gating
- live storage routing
- specialization cache lookup
- execution of compiled spell-static routes

Runtime should not have to rediscover planner intent.
Compiler should not try to own caller transients.

The clean boundary is `_spell_codegen_creation`.

That artifact should eventually be the authoritative spell-static handoff.

## The Two-Month Exploration Window
We should spend a bounded exploration phase before locking in the next
optimization architecture.

The purpose of that phase is not to "just benchmark."
It is to learn what strategy families are actually worth supporting.

### Exploration goals
- measure cold vs warm behavior separately
- see which graph shapes dominate real usage
- understand when top-down cost pays for itself
- discover where specialized execution families matter
- verify whether wide, deep, shared, and override-heavy graphs should produce
  different compiler decisions

### Exploration outputs
- object graph taxonomy
- harness and scenario generator
- metrics model
- discovery signal candidates
- strategy family candidates
- convergence decisions for phase 11 and runtime handoff

## Harness Design
We need a real exploration harness.

It should be able to generate and execute many object graph configurations
without rewriting benchmark code every time.

### Harness responsibilities
- generate graph scenarios
- bind them into Melder
- compile them
- run cold and warm execution passes
- record structural and runtime metrics
- compare scenario families across strategy variants

### Harness inputs
- graph width
- graph depth
- existence mode
- spell type
- collection DI presence
- SpellContract presence
- MutationContract presence
- override posture
- mutation posture
- validation posture
- dynamic vs automatic mode

### Harness outputs
- compile-time cost
- warm execution cost
- generated artifact sizes
- selected strategy family
- route-family distribution
- validation cost
- override specialization cost
- reuse behavior across existences

## Shape Taxonomy
All of these are still DAGs over Python objects.
That does not make them all the same.

We should organize scenarios by multiple independent axes.

### Width
- solo:
  one-object or almost-one-object chains
- narrow:
  low branching factor
- medium:
  moderate fanout
- wide:
  many siblings per level

### Depth
- shallow:
  one or two meaningful dependency layers
- medium:
  several layers
- deep:
  long dependency chains with cumulative context

### Reuse and lifetime
- `many`
- `unique_per_conduit`
- `unique`
- `unique_per_conduit_cluster`
- `unique_per_conduit_lineage`
- `unique_per_spell_space`
- existing creation

### Call form
- class spell
- method spell
- lambda spell
- existing creation spell

### Override posture
- no overrides
- root positional override only
- targeted override only
- mixed targeted and positional override
- mutation overrides

### Contract posture
- no SpellContract
- SpellContract but no provider
- SpellContract with provider
- MutationContract present

### Validation posture
- clean valid graph
- ambiguous graph
- gated graph
- invalid graph
- dirty-root change-control path

### Structure family
- deep and narrow
- shallow and wide
- mixed fanout DAG
- shared heavy graph
- transient heavy graph
- contract heavy graph
- override heavy graph

This taxonomy is the raw material for future discovery heuristics.

## What Discovery Should Eventually Do
Discovery should not permanently return "generalized chain."

Discovery should eventually inspect the fitted model and ask:
- what shape is this graph?
- what execution pressure does it imply?
- what reuse or lifetime posture dominates?
- how much override machinery is likely?
- how much contract or mutation machinery is likely?
- can we use a narrow specialized route?
- do we need a wide or deep strategy family?

That means future discovery systems should look at signals such as:
- node count
- max depth
- max width
- dependency arity histogram
- target-spec count
- contract payload count
- mutation patch count
- route family
- shared-node ratio
- whether fast transient execution is even available

## Benchmark Discipline
We need discipline here or we will fool ourselves.

### Measure separately
- cold compile cost
- cold first execution
- warm repeated execution
- no-overrides path
- override-heavy path
- validation-enabled path
- mutation-aware path

### Compare fairly
Dishka should be compared on the paths where it is actually competitive.
Melder should be compared on the paths where its features matter.

If we compare only trivial cold-path construction, we under-measure Melder's
advantage.
If we compare only our best warm path, we under-measure the real tax.

We need both.

## Immediate Convergence Work
Before the harness is built, we still need a tighter architecture boundary.

### Immediate compiler goals
- make codegen creation discovery choose a real grouped family contract
- introduce shared build-state where grouped strategies are still duplicating
  spell-static derivation
- reduce phase-11 leakage of raw internal plumbing

### Immediate runtime goals
- keep `CreationContextBuilder` as a consumer of compiler-owned spell-static
  packaging, not as a second planner
- keep `CreationContext` focused on runtime specialization and dispatch
- keep `Meld` focused on lookup, gating, and storage routing

## What Success Looks Like
After the exploration phase, we should be able to say:
- this family of graphs should take this strategy
- this lifetime mix should take that strategy
- this override or mutation posture changes the route in a measurable way
- this warm-path specialization pays off
- this remaining cold-path cost is acceptable

And then we can start serious optimization with evidence instead of instinct.

## Current Recommendation
Do not optimize phase 11 in isolation anymore.

Treat phase 11 as the front edge of the broader top-down compiler convergence
program:
- compiler boundary convergence
- harness
- taxonomy
- exploration
- then optimization

That is the correct order if we want Melder to surpass bottom-up DI systems
without losing the reasons it exists.
