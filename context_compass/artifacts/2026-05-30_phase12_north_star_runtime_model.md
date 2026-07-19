# Phase12 North Star Runtime Model

## Purpose
Capture the runtime philosophy behind the new Phase 12 and later Phase 13 work
in a narrower artifact than the broader execution-strategy direction doc.

This is the reference for the end-state we are optimizing toward.
It is not the implementation plan.
It is not the full compiler architecture doc.

It is the runtime north star.

## Core Thesis
The compiler should stop shipping middle-of-the-road runtime behavior when it
already knows enough to do better.

The end-state is:
- `Meld` either creates on a sealed fast path
- or it jumps directly into a spell-owned bound runtime tool

That bound runtime tool should already know:
- the spell's ownership family
- the spell's storage family
- the spell's no-overrides lane
- the spell's overrides lane
- the later mutation lane
- the lock posture
- the registration posture
- the exact compiled callable family it should use

So the goal is not "better generic context logic."
The goal is "more exact spell-specific runtime patterns."

## Current Problem
Today too much late decision pressure still exists below the compiler:
- `Meld` still pays front-door resolution cost
- `CreationContextBuilder` still chooses route and lane details
- `CreationContext` still owns too much specialization logic
- Phase 13 currently only handles a narrow no-overrides compile lane

That means the runtime still spends time rediscovering things the compiler
already knew.

## Runtime End State
The runtime should trend toward this shape:

1. resolve spell
2. check hard validity and invalidation bits
3. pack dynamic inputs
4. invoke the exact spell-owned bound callable pack
5. return

That is the desired hot path.

Not:
- generic route selection
- generic lock selection
- generic helper dispatch
- generic override-path interpretation
- generic storage-owner interpretation

## Spell-Owned Runtime Binder
The spell should probably continue owning the runtime binding surface because:
- it is naturally local to the spell
- it is easy to invalidate when spell state changes
- it provides good warm-path locality

But what the spell owns should evolve.

The spell should not own a generic late-strategy context forever.
It should own a thinner runtime binder for one already-chosen codegen pattern.

That binder should hold:
- the chosen codegen pattern
- the concrete creations-owner surfaces for that pattern
- the compiled callable pack for that pattern

So the runtime object becomes a pattern binder, not a strategist.

## Ownership Truth Matters
Speed alone is not enough.
The chosen codegen must remain truthful to the spell's ownership family.

The important ownership families are:
- shared/root-owned unique
- conduit-local unique
- spellspace-local unique
- transient-many
- existing-creation

Those families do not have identical semantics for:
- creation
- reuse
- registration
- transfer of ownership
- pooling
- reset
- cleanup

So the compiler should choose:
- the fastest codegen
- that is still truthful to the spell's ownership and lifecycle contract

## Dynamic Input Packing
The compiler should aim for codegen patterns where the per-meld work becomes
small and explicit.

For the right families, the spell-owned runtime binder should only need:
- creations input(s)
- normalized override payload
- maybe packed positional root args

Then the runtime path is:
- pack dynamic values
- call the exact callable

That is where specialized callables, lambda-like packing, and route-aware
prebinding become valuable.

## Phase Responsibilities

### Phase 11
- builds raw execution truth
- builds raw plan variants
- gathers metrics and shape facts
- does not decide the final runtime pattern

### Phase 12
- consumes the full artifact truth surface
- examines the spell/runtime shape
- chooses the best codegen candidates
- lowers those into a `SpellCodegenPlan`

### Phase 13
- consumes the chosen `SpellCodegenPlan`
- emits the backend for that plan
- should not need to rediscover graph family or ownership shape broadly

### Runtime Binder
- binds the emitted callable pack to real creations-owner surfaces
- executes
- does not behave like another planner

## Strategy Pattern Meaning
The point of the Phase 12 and Phase 13 strategy systems is not abstraction for
its own sake.

The point is experimentation:
- try a new family
- benchmark it
- keep it or kill it

That gives the compiler a controlled way to evolve:
- route-aware families
- lock-aware families
- spellspace-aware families
- override-heavy families
- contract-heavy families
- tiny transient families
- shared singleton families

The system becomes:
- extensible
- measurable
- reviewable

instead of one generic emitter with more and more special cases.

## Processor vs Planner
The processor should not decide based on vague "supports overrides" style
criteria.

The processor should turn the current artifact surface into a meaningful shape
description:
- graph shape
- dependency shape
- call shape
- route/storage family
- override/patch geometry
- execution-plan shape

Then the planner should turn that description into the chosen codegen plan.

So the intended flow is:
- raw artifacts
- normalized processor state
- meaningful shape description
- chosen `SpellCodegenPlan`
- later backend emission

## Compiler Work Tradeoff
This direction is not trying to minimize compiler work at all costs.

It is acceptable for the new processor/planner stack to spend more time
earlier, including recomputing better planning shape from earlier compiler
truth, if that gives us:
- a stronger `SpellCodegenModel`
- a more exact `SpellCodegenPlan`
- a thinner runtime binder
- a faster and cleaner meld hot path

The current benchmark pressure supports that tradeoff. In the user's depth-9
hotpath benchmark, the current late planning/backend path was a large share of
conjure cost, with `root_blueprints`, `execution_plan`, and
`executor_compile` together taking most of the named compiler time. That is
exactly the sort of cost center this new architecture should eventually
replace rather than preserve.

So the rule is:
- spend compiler effort where it buys a better final plan
- do not preserve the old planning pipeline just because it already exists
- replace it once the new processor/planner stack is strong enough

## The Real Optimization Goal
We are optimizing toward:
- fewer branches
- fewer helper calls
- fewer temporary objects
- less late interpretation
- less repeated route selection
- less repeated storage-owner selection

And we want to do that:
- without lying about ownership
- without breaking transfer semantics
- without breaking cleanup/reset semantics
- without hiding complexity in runtime glue

## What This Is Not
This is not:
- a call to delete the spell-owned runtime cache
- a call to flatten every spell into bespoke handwritten code
- a call to ignore ownership semantics for speed
- a reason to keep generic `CreationContext` behavior forever

It is:
- a compiler-first push toward exact runtime patterns
- a runtime-binding model that gets thinner over time
- a structured way to optimize real hot paths

## North Star Summary
The end-state is:

- Phase 12 decides the spell's runtime/codegen pattern
- Phase 13 emits the best backend for that pattern
- the spell-owned runtime binder holds that pattern and its creations-owner
  surfaces
- `Meld` either creates directly on a sealed fast path or jumps straight into
  that exact bound tool

That is the north star.
