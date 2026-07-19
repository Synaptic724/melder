# Execution Strategy Compiler Direction

## Purpose
Capture the actual Phase 12 and Phase 13 direction in a form strong enough to
survive implementation slicing.

This is not a final architecture spec.
It is the spirit artifact for the next compiler push.

## Core Thesis
The current compiler is already real.
It is not generic sludge.
It is also not yet right-sized.

What exists today is a middle state:
- Phase 10 gives us override targeting truth
- Phase 11 gives us raw execution-plan truth
- current Phase 13 emits real backend code
- `CreationContext` still carries too much late interpretation and binding
  complexity

So the problem is not that the compiler lacks information.
The problem is that too much of that information is not being turned into the
best possible final output shape soon enough.

## What Already Exists
The compiler already knows a lot:
- rooted graph and ownership truth
- occurrence shape
- injection shape
- override targetability shape
- execution-plan step truth
- raw plan metrics

We recently strengthened that by:
- moving compiler-owned execution-plan metrics off `Spell` and onto
  `SpellCompilerArtifact`
- adding incremental shape profiles from Phases 1, 8, 9, 10, and 11

So the missing piece is not another raw-analysis phase.
The missing piece is the right-sizing phase that consumes what we already know.

## Migration Model
The current scaffold should not become a permanent adapter layered on top of
the old planning stack.

The intended migration is:
- extend the new `artifact_processor` and `codegen_planner` until they are the
  real planning architecture
- use current `8-11` only as temporary migration oracles and parity
  references
- allow the new processor to spend meaningful compiler work deriving better
  planning shape from earlier compiler truth when that produces stronger plan
  selection
- replace the old `8-11` planning stack once the new model and planner can
  stand on their own
- remake the current Phase 13 surface as a pure backend emitter over the
  chosen `SpellCodegenPlan`

So the end-state is not "Phase 12 consumes old execution plans forever."
The end-state is "Phase 12 becomes the replacement planning architecture."

## The Real Problem
The final emitted runtime still carries too much generic behavior:
- existence branches
- reuse vs create branches
- lock selection branches
- registration branches
- contract payload merge logic
- override target count handling
- generic helper dispatch
- generic kwargs and call-shape handling

At the same time, `CreationContext` still carries too much of the compiler's
burden:
- route-family interpretation
- dispatch-hint interpretation
- override specialization machinery that wants stronger upstream ownership

That means the compiler is producing workable output, but not the tightest
output it could.

## Desired End State
We want a cleaner three-step backend:

1. build raw execution truth
2. examine that truth and right-size it into a fully formed codegen plan
3. emit the final backend from that chosen plan

Mapped onto the current system:
- Phase 11 owns step 1
- new Phase 12 owns step 2
- current Phase 13 owns step 3

## Phase Contract

### Phase 10
Keep it.

Its job is still:
- override patch targeting
- mutation patch targeting

### Phase 11
Keep it.

Its job is still:
- build raw execution plan variants
- compute execution and runtime shape truth
- write compiler-owned plan data onto `SpellCompilerArtifact`

Phase 11 should not become the strategy selector.
It should remain the raw truth producer.

### New Phase 12
This is the real addition.

Its job is:
- consume artifact-owned shape profiles
- consume Phase 10 patch-map truth
- consume raw Phase 11 execution-plan truth
- run examination strategies over that truth
- select the best codegen candidates
- lower those candidates into a fully formed codegen plan
- write that plan back to compiler-owned artifact state

This phase is not another generic planner.
This phase is the right-sizing and customization pipeline.

### Current Phase 13
This is the renamed current backend emitter layer.

Its job is:
- consume the fully formed Phase 12 codegen plan
- select the correct backend-emitter strategy for that plan
- emit, compile, and cache the final executors

Phase 13 should not be rediscovering graph family or runtime shape.
If it still has to guess broadly, Phase 12 failed to do enough.

## Concrete Phase 12 Shape
Phase 12 should be modeled explicitly around two internal layers:
- examination
- codegen-plan shaping

Those both belong in Phase 12.
They are not separate phases.

### Examination Layer
- `SpellExaminationBuilder`
  - builds the normalized examination inputs from existing artifact truth
  - takes the gathered phase profiles and raw plan truth and prepares the
    views the strategies should consume
- `SpellExaminationStrategy`
  - one examination strategy rule or family matcher
  - reads current compiler truth
  - decides which codegen candidates are legitimate or preferred
- `SpellExaminationSystem`
  - orchestrates the ordered examination flow
  - runs the strategies
  - resolves priority and conflict
  - produces the accepted examination outcomes

### Codegen Plan Layer
- `SpellCodegenPlanStrategyBuilder`
  - lowers accepted examination results into compile-ready codegen plan
    structures
- `SpellCodegenPlanStrategy`
  - one plan-shaping strategy
  - turns examination outcomes into concrete codegen-ready families, hints,
    rows, and emitter-facing outputs

### Phase 12 Output
Phase 12 should output a fully formed compiler-owned codegen plan artifact.

Working name:
- `SpellCodegenPlan`

This output should not be a loose metrics bag.
It should be complete enough that:
- Phase 13 can compile directly from it
- `CreationContext` can bind the resulting outputs cleanly
- no later layer has to rediscover what the compiler already knew

Expected contents of that plan:
- selected no-overrides strategy family
- selected overrides strategy family
- later mutation strategy family
- lowered step strategy rows
- lock strategy hints
- registration strategy hints
- override handling family
- call-mode handling hints
- emitter-family identity
- fallback reason when a generic path is required

## Concrete Phase 13 Shape
Phase 13 is the backend-emitter layer, not another right-sizing phase.

Current target classes:
- `SpellCodegenStrategy`
  - one backend emission strategy family
- `SpellCodegenBuilder`
  - binds and builds the concrete backend-emitter inputs from the chosen
    `SpellCodegenPlan`
- `SpellCodegenCreatorSystem`
  - orchestrates final backend creation and compile

This means the strategy layering is:

1. Phase 12 strategies
- examine and shape
- decide which codegen plan family fits

2. Phase 13 strategies
- emit and compile the chosen plan

That separation is deliberate.
It prevents Phase 12 from collapsing into another generic Phase 11, and it
prevents Phase 13 from becoming another late-stage strategist.

## Why This Is Better

### 1. Better output code
Common families can lose generic branches and helper noise.

### 2. Better ownership
Compiler choices stay on compiler-owned artifacts instead of leaking into
`Spell` and `CreationContext`.

### 3. Better extensibility
New ideas become additive strategy families:
- add one
- benchmark it
- keep it or kill it

Instead of contaminating generic runtime code every time.

## Benchmark Pressure
We now have a concrete benchmark signal that the current late planning/backend
path is worth replacing, not merely wrapping.

From the depth-9 hotpath benchmark the user ran:
- total conjure: `51.567ms`
- `root_blueprints`: `13.037ms`
- `execution_plan`: `4.708ms`
- `executor_compile`: `18.246ms`

That does not make Phase 11 alone the single slowest named phase in this
sample. The single slowest named phase is the current backend compile step.
But it does show the broader old planning/backend path is a major share of
compiler cost, which is exactly the seam this new architecture is meant to
replace.

That changes the design pressure in one important way:
- it is acceptable for the new processor/planner stack to spend meaningful
  compiler work earlier, including recomputing better planning shape from
  earlier compiler truth, if that produces a cleaner and more exact final plan
  and lets us replace the old costly pipeline.

## What We Already Collect
The artifact now already carries cheap incremental profiles that Phase 12 can
consume:
- Phase 1 requirements shape
- Phase 8 occurrence and graph shape
- Phase 9 injection shape
- Phase 10 override shape
- Phase 11 execution and runtime shape

That means Phase 12 does not need to become a second heavy discovery pass.
It should mainly classify, select, and lower.

## Converging 8-11
If the new stack is going to replace the current planning pipeline, then it
must replace what current `8-11` actually do, not just their names.

Current responsibilities are layered like this:

### Current Phase 8
- expands rooted blueprints into runtime occurrences
- decides execution order
- decides canonical shared occurrences
- decides instance-key planning
- carries SpellContract override payload routing

### Current Phase 9
- turns occurrences into per-instance call wiring
- decides dependency-key wiring per parameter
- carries list aggregation flags
- carries positional override usage
- carries contract payloads per instance

### Current Phase 10
- turns rooted sockets into override-target maps
- records specificity by TargetSpec
- records mutation edge rewires by TargetSpec

### Current Phase 11
- turns the earlier planning layers into execution recipes
- chooses creations-target routing
- chooses lock/register/runtime hints
- builds the three current lane variants
- builds fast and fast-transient arrays
- produces the current Phase 13 handoff

So the replacement target is not one old plan object.
It is four layers of planning semantics.

## SpellCodegenModel Consequence
The current tiny selector-only `SpellCodegenModel` is good enough for the
scaffold, but it is too thin for the real replacement goal.

If Phase 12 is going to converge `8-11`, then `SpellCodegenModel` should grow
into a normalized planning IR with explicit sections, while still avoiding raw
artifact mirroring.

That means:
- `SpellCompilerArtifact`
  - remains the raw truth store
- `SpellCodegenModel`
  - becomes the distilled planning IR
- `SpellCodegenPlan`
  - becomes the chosen lane plan built from that IR

### Proposed SpellCodegenModel Sections

#### 1. Build / Route Section
- `build_kind`
- `existence`
- `route_family`
- current root/build selectors only

#### 2. Occurrence Section
Normalized from current Phase 8:
- `root_spell_id`
- `execution_order`
- `root_instance_key`
- `shared_spell_ids`
- `contract_dependencies_complete`
- `occurrence_graph_rows`
- `instance_key_rows`
- `canonical_occurrence_rows`
- `contract_override_rows`
- `contract_override_spell_rows`

This is not the raw `OccurrencePlan` object.
It is the normalized planning IR section extracted from it.

#### 3. Injection Section
Normalized from current Phase 9:
- `injection_instance_rows`
- per-instance param-source rows
- per-instance contract payload rows
- per-instance positional override flags
- per-instance list aggregation flags

This is not the raw `InjectionPlan` object.
It is the normalized call-wiring IR section extracted from it.

#### 4. Patch Section
Normalized from current Phase 10:
- `override_target_rows`
- `mutation_target_rows`
- override specificity rows
- any distilled targetability families we still want for quick selection

This is not the raw patch-map object.
It is the normalized targeting IR section extracted from it.

#### 5. Execution Recipe Section
This is the part that replaces current Phase 11 step synthesis:
- normalized step recipe rows
- per-step creations target kind
- per-step dependency wiring
- per-step override match metadata
- per-step contract payload metadata
- per-step lock/register hints
- per-step spellspace/owner-conduit requirements
- optional fast-call candidate rows
- optional fast-transient candidate rows

This is the critical difference.
Instead of storing the old `ExecutionPlan` objects, the processor should build
the normalized execution recipe section directly.

#### 6. Selector / Family Section
On top of the normalized planning IR, the model can still keep:
- `graph_family`
- `call_shape_family`
- `override_shape_family`
- `fast_transient_eligible`

Those are still useful.
They are just no longer the whole model.

## Current-Compatible SpellCodegenPlan
The first useful planner target should be a current-behavior-compatible
combined plan so we can test the new mode without immediately deleting the old
pipeline.

That means `SpellCodegenPlan` should initially emit three lanes:
- `no_overrides`
- `overrides`
- `overrides_with_mutations`

Those lanes should be built from the normalized model sections above, not by
reading the old `ExecutionPlan` objects directly.

The first plan mode can be thought of as:
- `legacy_compatible_rebuild`

Meaning:
- the new processor rebuilds the planning IR
- the new planner emits a plan that still matches current runtime behavior
- we benchmark that against the old `8-11 -> current 13` path

Once that parity mode is stable, we can add better plan families beside it and
measure them honestly.

## Strategy Family Direction
The first cut should grow around families, not one generic plan.

Example family dimensions:
- no-overrides vs overrides
- transient-unrolled vs step-plan
- caller singleton vs shared singleton vs spellspace singleton
- small plan vs large plan
- lockless vs creations-lock vs spell-lock plus creations-lock
- contract-light vs contract-heavy
- override target count `0 / 1 / 2 / many`
- root positional override present or absent
- `CALLN` fallback
- generic fallback

These are not all separate classes on day one.
They are the family boundaries we want Phase 12 and Phase 13 to recognize.

## CreationContext Consequence
`CreationContext` should thin out as a result of this work.

Its future role should be:
- bind chosen executors
- bind chosen patch-map outputs
- expose runtime entry doors

Its future role should not be:
- act like a late-stage strategist
- reinterpret compiler shape heuristics
- carry broad customization pressure that belongs in Phase 12

So the goal is:
- stronger compiler
- thinner binder

Not:
- stronger compiler plus another smart runtime middle layer

## Spell vs Artifact Ownership
Compiler-owned output data belongs on `SpellCompilerArtifact`.

That includes:
- raw plan metrics
- shape profiles
- strategy-selection outputs
- codegen-plan outputs
- emitter-family hints

Runtime-owned state remains on `Spell`.

The earlier move of execution-plan metrics off `Spell` was the right first cut.

## Performance Spirit
This direction is about making stronger compile-time choices:
- compile away generic existence branches when the step family is already known
- compile away generic helper dispatch on hot families
- compile away generic kwargs building for fixed-arity families
- compile away generic lock selection for known shapes
- compile away broad override-shape branching where the override family is
  already selected

We are not promising fake numbers in the abstract.
We are building the seam where real wins can happen.

## North Star Runtime Shape
The north-star runtime model is:

- `Meld` should either create immediately on a sealed fast path
- or jump directly into a spell-owned prebound runtime tool with almost no
  extra decision-making

That means the long-term target is not a generic context object that keeps
figuring things out late.
It is a spell-specific runtime binding that already knows:

- the ownership and storage family
- the no-overrides path
- the overrides path
- the later mutation path
- the lock and registration posture
- the exact compiled callable family for this spell

In the best shape:
- Phase 12 examines all compiler truth and decides the exact codegen pattern
- Phase 13 emits the best backend for that chosen pattern
- the spell-owned runtime binder stores the resulting callable pack
- `Meld` just resolves the spell, checks the hard validity bits, and invokes
  the exact lane

This is where dynamic input packing matters.
For the right families, the per-meld work should reduce to:
- resolve spell
- pack the dynamic inputs
- call the exact bound runtime tool
- return

That is the north-star speed model:
- least branches
- least helper dispatch
- least temporary objects
- least repeated route selection
- least repeated context interpretation

The spell-owned runtime binder should therefore trend toward a solidified
codegen pattern binder, not a generic late-strategy context.
It binds:
- the chosen codegen pattern
- the concrete creations owner surfaces for that pattern
- the compiled callable pack for that pattern

This model also respects ownership semantics:
- some unique families are shared-owner rooted
- some are conduit-local
- some are spellspace-local
- some are transient-many
- transfer, reset, and cleanup semantics differ across those families

So the compiler should not only choose the fastest codegen.
It should choose the fastest codegen that is still truthful to the spell's
ownership and lifecycle family.

## What This Direction Is Not
It is not:
- a full compiler rewrite
- a rejection of Phases 8 to 11
- another raw-analysis pass that duplicates Phase 11
- a demand to flatten every weird graph into bespoke code

It is:
- a deliberate right-sizing layer
- a stronger output compiler
- a better long-term extension seam

## Immediate Implementation Spirit
The first real implementation slices should look like:

1. scaffold the Phase 12 classes
2. define the `SpellCodegenPlan` artifact contract
3. route Phase 12 to build that plan from existing artifact truth
4. later rewrite Phase 13 around emitter strategies that consume the plan
5. then thin `CreationContext` around the new contract

Longer-term, once the new processor/planner stack is authoritative:
6. stop depending on the old `8-11` planning stack
7. remove or collapse the old planning phases
8. remake current Phase 13 as the clean backend emitter for the new plan

That is the clean order.

## Immediate Investigation Questions
1. What exact fields should `SpellCodegenPlan` carry?
2. Which examination strategies should exist in the first cut?
3. Which codegen-plan strategies should exist in the first cut?
4. Which Phase 13 emitter strategies need to exist on day one to consume the
   first plan families cleanly?
5. How thin can `CreationContextBuilder` become once the Phase 12 plan is real?

## Final Spirit
The whole point is:
- stop shipping middle-of-the-road output code
- let the compiler make stronger assumptions when it already has enough truth
- keep the next optimization wave additive and extensible

That is the actual spirit of this direction.
