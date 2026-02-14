# Frontload Meld runtime into Conjure: compile RootExecutionPlan for an optimistic fast path

## Problem / Motivation

Deep-graph benchmarks show Melder is **~130–150× slower** than `dependency-injector` in key scenarios (cold + warm root resolve, “new graph each call”, spellspace workloads). The biggest opportunity is to **optimize the *best-case* scenario**:

- No overrides
- No mutation overrides
- No spell is dirty/gated
- No revalidation required
- We just want: **execute a precomputed plan**, reuse cached instances, and return

The system still needs full flexibility (deep overrides, mutation rewiring, spellspace scoping, validation gates), but those should be **slow paths**.

---

## Current Architecture Summary (as implemented today)

### Conjure pipeline (Spellbook.conjure)

Conjure does:

1) validate/freeze configuration
2) bind config to Aether
3) run **structural phases (1–4)**
4) allocate conduit_id
5) run **resolution phases (5–7)** scoped to that conduit_id
6) construct Conduit and wire into spells + hooks

---

## Catalog: Current Conjure Phases (1–7)

> Goal of this section: be explicit about **what each phase produces** and **what artifacts exist** by the end of conjure.

### Phase 1 — Requirements extraction
**Purpose:** Convert a spell’s callable signature into a structured “requirements” description.

**What it does:**
- Inspect the target callable signature (`inspect.signature(...)`).
- Build a `SpellRequirements` object with one entry per parameter.
- Classify each parameter into a `ParameterDIShape` (NORMAL DI, SpellMap default, SpellContract, MutationContract, etc.).
- Capture relevant metadata (annotation, defaults, SpellMap payload, etc.).

**Primary artifact:** `SpellRequirements` (per spell)

---

### Phase 2 — Symbolic graph construction
**Purpose:** Turn Phase-1 parameter requirements into a *symbolic dependency graph* (still not bound to concrete spell IDs).

**What it does:**
- Derive dependency “needs” from parameter shapes and annotations.
- Builds a `SpellSymbolicGraph` describing *what* the spell depends on symbolically.

**Primary artifact:** `SpellSymbolicGraph` (per spell)

---

### Phase 3 — Local resolution frame / DAG construction
**Purpose:** Bind symbolic needs to real spells available in the Spellbook (and produce a local dependency DAG).

**What it does:**
- Resolve dependencies “against the Spellbook” (i.e., bind symbolic edges → concrete spell IDs).
- Build a local DAG/topology for the spell, including:
    - which dependency spell IDs satisfy which parameters
    - socket/edge metadata needed later (normal vs contract vs mutation sockets)
- Update system state with dependency spell IDs + topology.

**Primary artifacts:**
- `SpellResolutionFrame`
- `SpellLocalTopology`
- dependency spell_id sets stored into system state

---

### Phase 4 — Per-spell validation
**Purpose:** Validate Phase 1–3 artifacts and mark spell as valid/broken.

**What it does:**
- Runs `SpellValidationSystem.validate_spell(...)`.
- Caches validation result (diagnostics, errors).
- Updates lineage validity state: valid vs invalid/gated.

**Primary artifacts:**
- `SpellValidationResult` (per spell)
- SpellSystemState validity updates

---

### Phase 5 — Root blueprint construction (system-level DAGs + index)
**Purpose:** Build *deep DAG blueprints* for each root and a frame-level index to support resolution.

**What it does:**
- Uses existing Phase 1–4 artifacts only (no new discovery).
- For each root spell in the frame:
    - Build a `RootResolutionBlueprint` containing:
        - `deep_dag`: full reachable DAG under the root
        - `ordered_node_ids`: topo order (deps first, root last)
        - `socket_refs` + `dag_index`: overlay socket metadata & targeting index

**Primary artifacts:**
- `RootResolutionBlueprint` per root
- `SpellSystemIndex` (frame-level)

---

### Phase 6 — System-level validation
**Purpose:** Validate Phase 5 artifacts at system level, producing per-conduit resolution validity and diagnostics.

**What it does:**
- Runs system strategies across:
    - root blueprints
    - system index
    - Phase 4 outcomes (broken spell ids, etc.)
- Produces system-level diagnostics and updates per-conduit resolution validity.

**Primary artifact:**
- `SpellSystemValidationState` (diagnostics, validity)

---

### Phase 7 — Change-control wiring
**Purpose:** Prepare change-control and revalidation wiring for the frame.

**What it does (idempotent):**
- Ensure ChangeControlManager exists for the frame
- Rebuild “component-of” index from Phase 5 root blueprints
- Register revalidator callback (run phases 1–7 for dirty roots)

**Primary artifact:**
- Change-control wiring ready for meld-time gating / revalidation

---

## Catalog: What still happens during Meld runtime today (and costs us)

### Meld-time validation gate (runtime)
Before we run the engine, MeldRuntime/Meld checks validity:

- If spell lineage validity is UNKNOWN/GATED:
    - acquire spell lock
    - run `spell.run_structural_phases()` (Phases 1–4)
    - raise if still invalid/gated

- If per-conduit resolution validity is UNKNOWN/GATED:
    - run `spellbook._run_resolution_phases_for_conduit(conduit_id)` (Phases 5–7)
    - raise if still invalid/gated

This is correct behavior — but in the *best case* we should hit a very cheap “already valid” check.

---

### MeldRuntime.execute (current responsibilities)
At runtime (per meld call), the runtime currently:
- enforces invariants / validity checks
- snapshots or uses build-time artifacts
- creates a per-execution `ResolutionFrame` for overrides
- instantiates a `MeldEngine` and calls `engine.run(blueprint)`
- does cleanup

---

### MeldEngine.run (current per-call work)
Even when we have a deep blueprint already, the engine still does **a lot** each call:

- Collect/normalize override targets
- Build an **occurrence graph** (to support Existence.many / path-based instance keys)
- Extend occurrence graph with ordered nodes
- Build execution order (topo) for occurrence nodes
- Build an “instance plan” (instance keys by spell id, canonical occurrences, root key)
- Validate override targets for shared spells
- For each node in execution order:
    - build kwargs for the node (including contract override payload lookup)
    - call construct logic
    - store results

This means even in the “warm” scenario we’re paying for repeated graph/plan work.

---

### Overrides and mutation rewiring at runtime
Two key runtime helpers add overhead when enabled:

- **GraphMutator**: clones DAG + rewires mutation sockets based on mutation overrides, recomputes topo order, rebuilds socket index (runtime)
- **SpellOverrider**: parses TargetSpec keys, resolves sockets via DagTargetingEngine, applies specificity precedence to produce socket-level override map

These are valuable features, but should be “only if needed”.

---

## Goal State

### “Final product” after conjure phases
For each root blueprint, we want a **compiled execution artifact** that represents:

- The **exact topo-ordered list** of everything we need to “make”
- The **exact dependency indices** needed to build each node
- The **exact caching/registration behavior** per Existence and per scope
- The **exact places to patch** when overrides/mutations exist (hot-swaps)
- The **minimal runtime checks** required for correctness

Call this artifact:

> **RootExecutionPlan** (or “CompiledMeldPlan”)

---

## Proposal: Add new Conjure phases to compile an optimistic RootExecutionPlan

### Overview
After Phase 5 (and ideally after Phase 6 validation passes), compile an “optimistic plan” per root such that the meld fast path becomes:

> `execute(plan) -> (reuse cached instances) -> instantiate missing -> register -> return root`

### New phases (recommended)
Add these phases after Phase 5 (or after Phase 7) — whichever is easiest to wire into the current lifecycle.

#### Phase 8 — Occurrence expansion + schedule compilation
**Goal:** Precompute what MeldEngine currently recomputes per call.

- Expand root blueprint DAG into **occurrence-level nodes** when Existence.many/path semantics apply.
- Precompute:
    - `execution_order` as a list of integer indices
    - `instance_key` per step (spell_id + path tuple)
    - canonical occurrences per spell_id (if needed)
- Precompute “shared spell ids” bookkeeping if it’s stable.
- Store as: `OccurrencePlan`

#### Phase 9 — Injection plan compilation (factory plan)
**Goal:** Remove per-call kwargs-building and signature gymnastics.

For each node occurrence:
- Precompute `ArgPlan`:
    - positional arg slots (indices into resolved results array)
    - keyword arg slots (param_name -> dep_index)
    - default handling rules
    - SpellMap/SpellContract placeholders if needed
- Prebind the call target:
    - store direct reference to constructor/factory callable
    - avoid repeated attribute lookups
- Store as `FactoryPlan`

#### Phase 10 — Override + mutation patch map compilation
**Goal:** Make deep override application a patch operation, not a rebuild.

- Create `override_slot_map`:
    - `SocketRef -> (step_index, slot_kind, slot_index)`
- Create `mutation_patch_map`:
    - `SocketRef -> edge patch instructions`
- Add caching:
    - LRU cache `TargetSpec.parse(raw_key)` results
    - optionally cache resolved sockets for common keys

#### Phase 11 (optional) — Codegen for hot path execution
**Goal:** Replace generic loop with specialized function.

- Generate a Python function per RootExecutionPlan that:
    - uses local variables for hot dict lookups
    - executes steps in-line
    - does minimal branching
- Cache compiled code object keyed by (root_plan_version, flags)

> This is optional, but likely required if we want to approach single-digit microseconds.

---

## Proposed Runtime Behavior

### Fast path (the one we optimize)
Conditions:
- No overrides
- No mutation overrides
- root + conduit validity already valid
- RootExecutionPlan exists and matches current blueprint version

Then:
1) (optional) quick root-cache check (if root existence allows reuse)
2) run plan executor:
    - for step in topo order:
        - check reuse for that instance_key if Existence allows
        - else build args from indices and call target
        - register into Creations (correct bucket/scope)
3) return root instance

### Slow paths (fallback routes)
- If overrides present:
    - either patch-in override values (via override_slot_map) and execute
    - or compile/lookup a variant plan keyed by override signature
    - fallback to existing MeldEngine if patching fails

- If mutation overrides present:
    - if patchable via mutation_patch_map: patch and execute
    - else fallback to GraphMutator + existing engine path

- If validity gated/unknown:
    - invoke existing meld-time validation gate (Phases 1–7 as needed)
    - rebuild/refresh plan cache for updated blueprint version

---

## Data Structures (sketch)

### RootExecutionPlan (core)
- `plan_id` / `plan_version` (derived from blueprint + conduit_id)
- `root_spell_id`
- `steps_count`
- `root_step_index`
- `execution_order: list[int]`
- `step_spell_id: list[str]`
- `step_path: list[tuple[str, ...]]` (empty tuple for non-many)
- `step_instance_key: list[_InstanceKey]` (prebuilt tuple key)
- `step_existence_mode: list[int]` (enum/int for speed)
- `step_scope_selector: list[int]` (owner/caller/spellspace)
- `step_factory: list[callable]`
- `step_deps_flat: list[int]` + offsets (avoid nested lists)
- `step_kwargs_keys_flat: list[str]` + offsets (if kwargs needed)
- `step_kwargs_dep_indices_flat: list[int]` + offsets
- `override_slot_map: dict[SocketRef, SlotPointer]` (or a compact integer map)

### SlotPointer
- `step_index: int`
- `kind: enum {POS, KW, SPECIAL}`
- `slot_index: int` or `kw_name: str`

---

## Implementation Tasks

### Phase compilation
- [ ] Implement `RootExecutionPlan` and compact step storage (prefer structure-of-arrays).
- [ ] Implement Phase 8: build occurrence graph + precompute execution_order at conjure-time.
- [ ] Implement Phase 9: compile per-step ArgPlan / FactoryPlan (remove kwargs building at runtime).
- [ ] Implement Phase 10: build override_slot_map + mutation_patch_map at conjure-time.
- [ ] Integrate with change-control:
    - [ ] Invalidate cached plans when root blueprint version changes
    - [ ] Rebuild plan after revalidation completes

### Runtime integration
- [ ] Add `FastMeldExecutor` that executes RootExecutionPlan.
- [ ] Add gating logic in `MeldRuntime.execute`:
    - fast path if (valid + no overrides + plan available)
    - else fallback to existing engine
- [ ] Add early-return optimization: if root instance already cached and no overrides, return immediately (skip engine entirely).

### Overrides & mutations
- [ ] Add LRU cache for `TargetSpec.parse`.
- [ ] Implement “patch overrides” mode:
    - resolve TargetSpec -> sockets -> slot pointers -> patch injection values
- [ ] Mutation overrides:
    - fast: patch if possible
    - slow: GraphMutator fallback

### Perf work
- [ ] Add microbench hooks for:
    - time spent in gating
    - plan execution time
    - override application time
    - allocations (optional)
- [ ] Ensure cleanup behavior unchanged.

### Optional: Codegen & Cython
- [ ] Add optional plan codegen path: emit python AST or source for plan executor, compile + cache.
- [ ] Evaluate Cython for:
    - tight loop executor
    - flattened dependency arrays
    - instance key handling
    - potentially override-slot application

---

## Acceptance Criteria / Targets

### Primary goals (realistic, pure Python fast path)
- **Warm root resolve (depth 9 unique)**: 23.5 µs → **< 2.0 µs** (≥10× improvement)
- **Cold root resolve (depth 9 unique)**: 8.2 ms → **< 0.5 ms** (≥16× improvement)
- **Depth 9 many (new graph each call)**: 12.47 ms → **< 2.0 ms** (stretch depends on whether conjure happens inside loop)

### Stretch goals (requires aggressive optimization: codegen and/or Cython)
- Warm root: **~0.4–0.8 µs** (approaching 2–4× of dependency-injector)
- Cold root: **< 0.2 ms** for depth 9

### Correctness
- No behavior regressions:
    - override semantics match current (path/unique/broadcast)
    - mutation overrides still work
    - spellspace scoping still correct
    - meld-time validation gates still enforced when needed

---

## Expected Performance Outcome (estimate)

I do **not** expect we go from ~130× slower → **2–3× slower** in a single step *in pure Python*.

What I *do* expect if we frontload plan compilation and implement a true fast path:
- Likely **10–30× runtime improvement** for warm and cold melds in deep DI graphs (because we’re currently recomputing occurrence graphs + execution plans + kwargs building per call).
- That would move us from ~130× slower down to something like **~5–15× slower** in the first iteration.
- To reach **~2–3×**, we probably need:
    - an optimized “reuse root instantly” fast path,
    - plan compilation + flattened arrays,
    - and either **codegen** (specialized executor) or **Cython** for the tight loop and indexing.

---

## Notes: What “codegen” means here

“Codegen” = generate a specialized Python function for a specific root plan that:
- hardcodes the execution order
- hardcodes which indices feed which parameters
- minimizes dict lookups, attribute lookups, and branches
- can be cached as a compiled callable on the Conduit/plan

This is basically “turn the plan into straight-line Python”.

---

## Notes: Where Cython can help

Cython helps most when we have:
- tight loops over simple arrays
- repeated dictionary/tuple operations we can reduce
- branchy but predictable execution logic we can compile down

If we design RootExecutionPlan as compact arrays, Cython becomes much more effective.

---

## Risks / Tradeoffs

- Conjure time will likely increase (we are intentionally frontloading).
- Need careful invalidation when:
    - spell versions change
    - change-control revalidation reruns phases
    - conduit contracts/linking affects available providers
- Plan patching for overrides/mutations must not change semantics.

---

## Deliverables

- RootExecutionPlan artifact per root
- FastMeldExecutor implementation + runtime gating
- Override/mutation patch maps
- Bench results showing meaningful speedup on deep graph tests
