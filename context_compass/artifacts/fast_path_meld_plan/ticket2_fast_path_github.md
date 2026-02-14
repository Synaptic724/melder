# 🚀 Fast-Path Meld: Move Runtime Graph Work Into Conjure via Compiled Execution Plans

## Context / Problem

Benchmarks show Melder is ~O(100x) slower than other Python DI systems in best-case meld scenarios (e.g., warm cached root and cold root resolves). We want to re-architect so that:

- **Best-case meld** (no overrides, no mutations, no validation gates, no dirty roots) is basically:
    - “lookup cached instance and return”, or
    - “execute a precomputed plan and register instances”
- **Worst-case meld** (overrides, mutation overlays, contract changes, or gated validity) can fall back to:
    - revalidation + recompilation + slower dynamic execution

We are OK with **increasing conjure cost** if it makes meld extremely fast.

---

## Goals

1. **Make the optimistic case blazing fast**
    - No overrides
    - No mutation_override
    - Valid lineage + valid per-conduit resolution
    - Not dirty under change-control
    - Hook-free path preferred (or hook-aware plan variant)

2. **Precompute everything possible in conjure**
    - Turn “graph reasoning” into “plan execution”

3. **Support correctness + flexibility**
    - If assumptions break, fall back cleanly:
        - revalidate (phases 1–7)
        - rebuild plan
        - run slower engine

---

## Non-Goals (for v1)

- Fully optimizing override-heavy workloads (we can add this later via plan deltas / preindexed override routing).
- Eliminating all locks everywhere (but we *do* want an optimistic no-lock read for cache hits).

---

## Current System: What the 7 Conjure Phases Produce

### Phase 1 — Requirements
**Purpose**
- Inspect spell callable signature / fields.
- Classify each parameter DI shape:
    - plain arg, normal DI, SpellMap, SpellContract, MutationContract, etc.

**Outputs**
- `SpellRequirements` (per spell): parameter requirements + DI shapes

**Runtime usage**
- Should be **zero** (compile-time only), but currently used indirectly when meld-time revalidation happens.

---

### Phase 2 — Symbolic Graph
**Purpose**
- Build a “symbolic” dependency graph of spell→spell requirements without committing to a concrete DAG wiring.

**Outputs**
- `SpellSymbolicGraph` (per spell): dependency edges + socket descriptors

**Runtime usage**
- None in ideal world; used to build phase 3.

---

### Phase 3 — Local Frame / DAG
**Purpose**
- Materialize a concrete DAG / resolution frame for each spell.
- Compute a deterministic topological order for its dependencies.

**Outputs**
- `SpellResolutionFrame` (per spell)
- `Spell.dependency_graph` + `Spell.dependencies`
- Ordered node IDs (topological sort list)

**Runtime usage**
- Meld runtime consumes `resolution_frame` + DAG for execution.

---

### Phase 4 — Validation (Structural)
**Purpose**
- Validate:
    - broken bindings
    - cycles
    - invalid DI shapes / sockets
- Update structural validity flags.

**Outputs**
- `Spell.validation_result`, `Spell.is_broken`, `Spell.validated`
- Updates SpellSystemStates structural validity (VALID / INVALID / UNKNOWN / GATED)

**Runtime usage**
- Meld checks validity gates; if UNKNOWN/GATED it may rerun phases 1–4.

---

### Phase 5 — Root Blueprints (Deep DAG)
**Purpose**
- Build deep DAG blueprints for root resolution.
- Produce a per-conduit spell visibility / system index.

**Outputs**
- `RootResolutionBlueprint` (per root spell, per conduit)
- `SpellSystemIndex` (frame-level, scoped to conduit)

**Runtime usage**
- MeldRuntime / MeldEngine use the root blueprint as the “global graph definition”.

---

### Phase 6 — System Validation (Per-Conduit Resolution Validity)
**Purpose**
- Validate resolution correctness at the system level:
    - deep DAG integrity
    - cross-conduit contract visibility / binding consistency
- Writes per-conduit resolution validity.

**Outputs**
- Per-conduit resolution validity in SpellSystemStates (VALID / INVALID / UNKNOWN / GATED)

**Runtime usage**
- If per-conduit validity is UNKNOWN/GATED, meld may rerun phases 5–7.

---

### Phase 7 — Change Control Wiring
**Purpose**
- Ensure ChangeControlManager is ready.
- Build component-of index from Phase 5 DAG artifacts.
- Register revalidator hook so dirty roots can be revalidated & rebuilt.

**Outputs**
- component-of index
- registered revalidator callback

**Runtime usage**
- Meld gates on dirty roots (must revalidate before execution).

---

## Current System: What Still Happens at Meld Time (Hot Path Work)

Even in “normal” best-case conditions, meld time is currently doing a lot of dynamic work:

### Meld gating / orchestration
- Checks structural validity gates
- Checks per-conduit resolution validity gates
- Checks change-control dirtiness
- Optional hook execution path (pre/activation/post)

### Runtime execution path (MeldRuntime + MeldEngine)
- Pull DAG + requirements + resolution frame
- Retrieve root blueprint
- Apply mutation overlays via `GraphMutator` (even if empty, object creation overhead exists)
- Apply per-call overrides via `SpellOverrider` (even if empty, object creation overhead exists)
- Build an “occurrence graph” (path-aware expansion for Existence.many and socket wiring)
- Resolve contract sockets dynamically (scan contracted providers + local fallback)
- For each node occurrence:
    - decide reuse vs construct
    - lock and lookup in the correct creations map
    - invoke constructor/callable
    - register into creations based on Existence
    - execute activation hooks if created

This is exactly the stuff we want to avoid in the optimistic path.

---

## Proposal: Add Conjure Phases to Produce a “Compiled Meld Plan”

### Big Idea
Conjure should produce a **compiled execution plan** per root blueprint, so meld runtime can become a tight loop (or even generated Python code) instead of building graphs and performing dynamic socket resolution.

### New Artifact
**`CompiledMeldPlan`** (per root spell, per conduit)

A plan is essentially:
- A flattened list of execution steps in topological order
- Each step contains:
    - callable target (already resolved)
    - dependency indices (already resolved)
    - argument assembly recipe (precomputed)
    - cache/reuse policy + creations container selection
    - precomputed registration instructions
    - (optional) a prebuilt “fast function” for execution

---

## New Conjure Phases (Suggested)

### Phase 8 — Compile Root Execution Plans (NEW)
**Inputs**
- Phase 5 root blueprints
- Phase 1–4 artifacts as needed for param/socket metadata
- Conduit-scoped contract visibility and provider resolution results

**Work**
For each `RootResolutionBlueprint`:
1. Compute and store the **final ordered execution list** of *occurrences*:
    - Expand Existence.many nodes into path-specific occurrences
    - Expand SpellMap/collection sockets into fixed provider lists where possible
2. Resolve **contract sockets** to a concrete provider spell_id when the conduit wiring is stable
    - If a contract is still “open/late”, mark plan as “fast-path-ineligible”
3. Produce an **arg binding recipe** per occurrence:
    - For each parameter:
        - dependency result comes from which earlier step index
        - or comes from caller args (root params)
        - or comes from a constant/default
4. Precompute **cache + registration routing** per occurrence:
    - Which creations container to use (caller vs owner)
    - Which dict to hit (`unique`, `unique_per_scope`, cluster, lineage, spellspace)
    - Whether many should skip cache reuse entirely
5. Produce a **plan signature**:
    - includes conduit_id + root_id + “contract wiring signature” + spellspace semantics
    - used to detect invalidation cheaply at runtime

**Outputs**
- Attach `compiled_plan` (and signature) onto the `RootResolutionBlueprint`
- Also optionally attach a `compiled_fast_fn` (see Phase 9)

---

### Phase 9 — Optional Codegen for Ultra-Fast Execution (NEW, optional but likely required)
**Why**
If we want to get close to dependency-injector numbers, we need to remove:
- dict-heavy interpreter overhead
- repeated attribute lookups
- repeated branching per node

**Approach**
Generate a Python function per (root, conduit) plan:

- locals bind:
    - creations dict references
    - spell callables
    - per-node cache accessors
- executes:
    - optimistic cache check for reuse-eligible existences
    - direct calls and assignments to local vars
    - minimal registration calls

This is similar in spirit to “compiled providers” patterns.

**Fallback**
If codegen disabled, execute a compact interpreter using arrays/tuples for steps.

---

## Runtime Changes: “Fast Path First, Fall Back on Trouble”

### Step 0: Optimistic cache hit return (should be *extremely* cheap)
In `Meld.meld()` (or just inside `_resolve_instance_with_locks`):
- Do a no-lock `dict.get()` check first for reuse-eligible existences.
- If found and overrides are absent, return immediately.
- If missing, proceed to construction.

(This alone can dramatically reduce warm-root time.)

---

### Step 1: Fast-path eligibility check
Before invoking the legacy engine:

Fast path requires:
- `overrides` empty
- `spell.mutation_override` empty
- plan exists for this (root, conduit)
- plan signature matches current conduit wiring state
- lineage validity is VALID
- per-conduit resolution validity is VALID
- root is not dirty under change-control
- hooks disabled OR plan variant includes hooks

If any condition fails → fall back.

---

### Step 2: Execute compiled plan
`CompiledMeldPlan.execute(context)`:
- uses precomputed step list
- uses precomputed dependency indices to pull args from a result array
- performs reuse/construct/register using precomputed existence policy
- returns root instance

---

### Step 3: Fall back path (existing behavior)
If:
- overrides present
- mutation overlay present
- contract socket late-bound
- validity gated/unknown
- change-control dirty
  → use current `MeldRuntime + GraphMutator + SpellOverrider + MeldEngine` path.

---

## Key Work We’re Moving Out of Meld and Into Conjure

### Move into conjure (Phase 8/9)
- Occurrence graph construction (including Existence.many path expansion)
- Contract socket resolution (provider selection)
- Arg binding recipes (param → provider index / caller arg / default)
- Cache + registration routing decisions (existence → creations container + dict)
- (optional) override targeting indices (later)
- (optional) code generation (Phase 9)

### Keep in meld (fast path)
- A few constant-time gate checks:
    - validity flags
    - dirty-root boolean
    - plan signature check
- Executing the plan (tight loop / generated function)
- Minimal creations interaction (get/register)

### Keep in meld (slow path)
- GraphMutator + SpellOverrider
- dynamic contract scanning + fallback logic
- revalidation triggers / rerun phases 1–7

---

## Implementation Plan (Suggested Milestones)

### Milestone A — “Zero-cost warm hit” + “No-overrides plan execution”
- [ ] Add optimistic no-lock read path for reuse checks
- [ ] Add `CompiledMeldPlan` data model
- [ ] Add Phase 8: compile plans from root blueprints
- [ ] Add fast-path selector in meld runtime
- [ ] Ensure plan invalidation triggers fallback safely

### Milestone B — Compact interpreter + data layout optimizations
- [ ] Replace dict-heavy step structures with tuples/arrays (integer indices)
- [ ] Prebind spell call targets and commonly used creations maps to locals
- [ ] Precompute spellspace id once per meld execution (for spellspace existences)

### Milestone C — Optional codegen
- [ ] Generate a Python function per plan and cache it on the blueprint
- [ ] Add debug mode: dump generated code for inspection
- [ ] Add safety: signature mismatch triggers regeneration

---

## Acceptance Criteria

### Correctness
- All existing behavior preserved when fast path is disabled.
- Fast path produces identical instances and registration semantics vs legacy engine (for eligible cases).
- Fast path automatically falls back when:
    - overrides present
    - mutation overrides present
    - late-bound contracts exist
    - validity is UNKNOWN/GATED/INVALID
    - dirty root under change-control

### Performance (Targets)
(Exact numbers depend on how much of the path we can bypass, but targets should be aggressive)

- Warm cached root:
    - target: **≤ 1 µs** (stretch: 0.4–0.6 µs)
- Cold root resolve (depth 9-ish):
    - target: **≤ 0.2 ms** (stretch: 0.09–0.14 ms)
- Mixed workloads:
    - significant drop in avg step time and spellspace cycle time

### Observability
- Add structured timers:
    - fast path hit rate
    - time in eligibility checks
    - time in plan execution
    - fallback reason counters
- Add benchmark harness knobs:
    - hooks on/off
    - change-control on/off
    - dynamic mode on/off

---

## Risks / Tradeoffs

- More work in conjure means more memory and compilation time
    - acceptable given problem statement
- Plan invalidation must be correct or we risk stale wiring
    - signature must include contract wiring version / conduit linkage signature
- Codegen increases complexity
    - keep optional; start with interpreter

---

## Open Questions
- What is the best “contract wiring signature” to include for invalidation?
    - conduit_id + contract mapping version? + ConduitWard lineage generation?
- Do we want separate plan variants for:
    - hooks enabled/disabled
    - spellspace enabled/disabled
- Can we introduce a “fast mode” where:
    - change-control is disabled
    - hook path is disabled
    - locks are minimized for cache hits
      to compete on pure DI speed benchmarks?
