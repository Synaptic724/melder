# 🚀 Compile “Meld ExecutionProgram” during Conjure (frontload work, make meld a tight loop)

## Summary
Melder is currently **orders of magnitude slower** than competitive DI libraries on *meld-time resolution* (especially cold root). We should **shift as much work as possible** into conjure and produce a **precompiled execution artifact** per root that allows meld to run as a **tight, branch-minimized loop**:

- No graph walking at meld time
- No per-node spell lookups
- No repeated validation / targeting logic
- Minimal locking
- Fast-path optimized for “no overrides, no dirtiness, no gates” (the optimistic case)
- Slow-path exists for overrides, linking changes, dirty roots, and revalidation

This ticket proposes the **target end-state artifact** (ExecutionProgram), the **new conjure phases** to produce it, the **runtime fast-path** and **fallback paths**, and a perf target/estimate.

---

## Background / Motivation (from benchmarks)
Current behavior suggests:
- Conjure is heavy (acceptable if it buys runtime speed)
- Meld cold root is the main pain (must be near-constant overhead + “just execute the plan”)

We’re explicitly optimizing for:
- **Best case:** no override, validity already computed, nothing dirty, contract graph stable → meld does a fast gate + executes plan
- **Fallback:** if anything invalidates assumptions → we revalidate/recompile and/or take a slower runtime route

---

## Current pipeline: Conjure phases 1–7 (what each phase produces)

### Phase 1 — Requirements extraction (per-spell)
**Output:** `SpellRequirements`  
Goal: From the spell’s call target signature, capture *what DI needs to supply* (parameter requirements) without looking up other spells.

### Phase 2 — Symbolic graph construction (per-spell)
**Output:** `SpellSymbolicGraph`  
Goal: Convert requirements into a symbolic edge set representing “sockets”, still **without** committing to concrete provider spell IDs.

### Phase 3 — Resolution frame construction (per-spell)
**Output:** `SpellResolutionFrame`  
Goal: Resolve symbolic dependencies into **concrete targets** (spell IDs / bindings), update direct dependency lists, resolve SpellMap defaults, resolve single vs collection DI targets, etc.

### Phase 4 — Structural validation (per-spell)
**Output:** `SpellValidationResult` + “broken” flag + lineage validity updates  
Goal: Run spell-level validation strategies (annotation/SpellMap shape, contract provider presence checks, binding cycle detection, callable hygiene, existing-creation compatibility, policy enforcement, etc).

### Phase 5 — Root blueprint generation (per-conduit)
**Output:** `RootResolutionBlueprint` (deep DAG per root) + frame-level index  
Goal: Build the deep DAG for each root and produce a **topological order** (dependencies first, root last). This phase is already structurally ideal for compilation.

### Phase 6 — System validation (per-conduit)
**Output:** System-level validation diagnostics + per-conduit validity updates  
Goal: Validate the *whole resolved system* (graph consistency, root reachability, cycles, contract graph cycles, scalability/viability heuristics, etc).

### Phase 7 — Change-control integration + artifact cleanup (per-conduit)
**Output:** Change-control dirty tracking integration + cleanup of heavy phase artifacts  
Goal: Register/refresh revalidation hooks, integrate with dirty-root gating, and clear intermediate artifacts that should not persist.

---

## What still happens in meld today (why cold root is slow)
Even in the “happy path”, meld currently does a bunch of work that should not happen on the hot path:

### A) Validity gating can trigger phase re-runs
At meld time:
- If structural validity is UNKNOWN/GATED → reruns phases 1–4 under per-spell lock
- If per-conduit resolution validity is UNKNOWN/GATED → reruns phases 5–7
This creates branching + locks + “maybe compile” work during meld.

### B) Overrides can induce runtime graph mutation
Mutation override support currently implies cloning/rewiring DAG structures (graph work in the hot path).

### C) Per-node resolution may be doing repeated orchestration
If the meld engine resolves dependencies by re-entering “meld logic” per node (lookups, existence selection, hooks, gating), cold root becomes N × overhead.

---

## Target end-state: the “final execution artifact” (ExecutionProgram)
We want conjure to output the **thing meld executes**.

### ExecutionProgram (per root, per conduit scope)
Think: a tiny “bytecode” or instruction stream.

**Core idea:** execution becomes:

1) Fast gate check (valid, not dirty, matches plan epoch)  
2) Run a simple for-loop over precompiled steps  
3) Return root instance

### Proposed structure
```python
@dataclass(slots=True)
class ExecutionProgram:
    program_id: str                  # stable hash/ulid of the plan
    root_spell_id: str               # version id
    topo_node_ids: tuple[str, ...]   # topo order (deps first, root last)
    node_index: dict[str, int]       # spell_id -> index (only used in slow paths / debug)
    ops: tuple["NodeOp", ...]        # compiled ops in topo order
    root_op_index: int               # index of root in ops (likely last)

    # override support
    mutation_patchpoints: dict[str, tuple[int, int]]
    # e.g. override_key -> (consumer_op_index, arg_slot_index)

    # validity / invalidation
    structural_epoch: int            # incremented when phases 1-4 change
    resolution_epoch: int            # incremented when phases 5-7 change
    conduit_id: str                  # compiled for this conduit scope
````

```python
@dataclass(slots=True)
class NodeOp:
    spell_id: str
    # execution
    call_target: object              # callable or class; None for EXISTING_CREATION
    arg_sources: tuple["ArgSource", ...]  # precompiled arg fetchers
    kwarg_sources: tuple[tuple[str, "ArgSource"], ...]  # optional
    
    # caching / existence
    existence_kind: int              # small int enum
    cache_read: "CacheReadSpec"      # where/how to reuse
    cache_write: "CacheWriteSpec"    # where/how to store after creation
    
    # hooks (pre-resolved tuples for fast iteration)
    activation_hooks: tuple[callable, ...]
```

```python
@dataclass(slots=True)
class ArgSource:
    kind: int                        # NODE_VALUE / COLLECTION / CONSTANT / SPELLMAP / CONTRACT / etc
    data: object                     # usually int index or tuple[int,...] or constant payload
```

### Key properties of this artifact

* Uses **integer indexing** into a local list for dependency access (`values[idx]`)
* Stores hook lists as **tuples** (fast iteration, no allocations)
* Stores existence decisions as **small ints** to avoid repeated enum conversions
* Avoids graph traversal and spell lookups at runtime
* Has explicit patchpoints for overrides so we don’t rebuild the DAG in the fast path

---

## Proposed new conjure work (frontload into conjure)

### New Phase 5B — Compile RootResolutionBlueprint → ExecutionProgram

Input:

* RootResolutionBlueprint (topo order + sockets/index)
* Per-spell resolution artifacts (Phase 3 frames)
* Existence + SpellType + hook tuples
* Conduit policy + spellspace rules where relevant

Output:

* ExecutionProgram per root stored in a **per-conduit runtime cache** (e.g., ConduitResolutionState)

What to compute here:

* Convert spell IDs → contiguous integer indices (topo order index)
* Precompute per-node:

    * Existence cache location (local creations vs owner creations vs spellspace)
    * Cache keys (spell_id, and any scope keys)
    * ArgSource list (node indices for single DI, tuple of indices for collection DI, SpellMap compiled payload, etc.)
    * Direct call_target references (avoid getattr + indirection during meld)
    * Hook tuples (pre/activation/post where applicable — or at least activation tuple for created instances)
* Precompute **root fast-return**:

    * if root existence is cached and already present, program can return immediately without touching any other nodes

### New Phase 5C — Compile override patch metadata

Goal: keep overrides off the hot path unless override is present.

Instead of cloning/rewiring graphs at runtime:

* Build `mutation_patchpoints` mapping:

    * override_key → (which op index + which arg slot gets swapped)
* Also build optional “override plan cache”:

    * cache key: `(root_spell_id, frozenset(mutation_override.items()))`
    * value: derived ExecutionProgram with patched indices
    * limits: small LRU to avoid unbounded growth

### New Phase 7B — Keep only what runtime needs; clean everything else

During cleanup, aggressively drop:

* symbolic graphs, validation contexts, scanners, temporary phase schedulers
  …but keep:
* ExecutionProgram(s)
* minimal diagnostic summaries (optional)

---

## Meld runtime: compiled fast path vs slow path

### Fast path contract (the optimistic bet)

MeldRuntime should do **exactly**:

1. Resolve target spell_id (already needed)
2. Gate:

    * root not dirty (change-control)
    * lineage validity == VALID
    * per-conduit resolution validity == VALID
    * plan epochs match state epochs
3. If no overrides: run `execute(program)`
4. Return

### Fast path executor (tight loop)

Pseudocode:

```python
def execute(program, ctx):
    ops = program.ops
    values = [None] * len(ops)   # local stack
    # Optional: created_flags = bytearray(len(ops)) if needed

    # root fast return: if root is cached and present, return it
    root_op = ops[program.root_op_index]
    inst = try_cache_get(root_op.cache_read, ctx)
    if inst is not _MISSING:
        return inst

    for i, op in enumerate(ops):
        # 1) cache check (if any)
        inst = try_cache_get(op.cache_read, ctx)
        if inst is not _MISSING:
            values[i] = inst
            continue

        # 2) build args from values (no lookups, no graph)
        args = materialize_args(op.arg_sources, values, ctx)
        kwargs = materialize_kwargs(op.kwarg_sources, values, ctx)

        # 3) create
        inst = op.call_target(*args, **kwargs)

        # 4) store
        cache_put(op.cache_write, ctx, inst)

        # 5) activation hooks (only if created)
        for fn in op.activation_hooks:
            fn(inst)

        values[i] = inst

    return values[program.root_op_index]
```

### Slow path triggers

If any of these are true, we bail out of fast path:

* structural validity UNKNOWN/GATED/INVALID
* per-conduit resolution validity UNKNOWN/GATED/INVALID
* root dirty under change-control
* no compiled program found
* override contains keys not present in `mutation_patchpoints`
* override targets a spell_id outside the program graph (needs graph extension / rebuild)

Slow path action:

* Run existing gating + revalidation pipeline (phases 1–7 as required)
* Recompile ExecutionProgram (Phase 5B/5C)
* Then execute (fast path should succeed immediately after)

---

## Invalidation model (so meld doesn’t “discover work”)

To keep meld fast, we need **clear invalidation signals**:

### Invalidate structural epoch (Phases 1–4)

On:

* bind/scan updates
* spell version changes
* dependency updates / SpellMap changes
* any structural validation change

Action:

* bump structural_epoch
* mark affected roots dirty (or their programs invalid)

### Invalidate resolution epoch (Phases 5–7)

On:

* conduit link/unlink
* ownership transfer
* contract provider changes
* dynamic policy changes

Action:

* bump resolution_epoch
* mark per-conduit program set dirty

### Runtime behavior

* If epochs mismatch → do not attempt partial repair in meld; go slow path
* After slow path completes, the next meld should always hit fast path

---

## Override handling (optimized)

### No overrides (default case)

* zero overhead beyond “if override_map: …” check

### Overrides present (best effort fast override)

1. Validate override payload shape (cheap)
2. For each override_key:

    * patch the op’s arg source index (or swap provider index)
3. Execute patched program

If override introduces a provider not already in topo graph:

* either (A) build a derived expanded program (more work)
* or (B) fall back to slow path which rebuilds blueprint + program

---

## Cython / codegen notes

### “Codegen” (what I mean)

Two flavors:

1. **Plan-as-data (recommended first):** ExecutionProgram = data + tight Python loop
2. **Generated Python function:** generate a specialized function per root with locals & direct calls

    * Pros: fastest pure-Python you can get
    * Cons: complexity, debugging, hot reload, linecache, tooling

### Where Cython helps (after the plan works)

High ROI:

* The program execution loop (indexing + branch minimization)
* Cache get/put logic (PyDict_GetItem, etc.)
* Arg materialization (fast list/tuple building)

Lower ROI:

* Anything that still calls user Python constructors (the call dominates)
* Introspection/validation phases (not in meld hot path)

---

## Performance estimate (honest)

Right now cold root is multi‑ms. If we:

* eliminate per-node re-entry into “meld logic”
* eliminate runtime DAG operations
* eliminate runtime targeting / scanning
* execute a compiled topo op list using list indexing

…then a **20×–80× reduction** in *cold root overhead* is realistic on “deep graph, trivial constructors” microbenches.

That would put you in the zone of:

* **Cold root:** ~0.15ms–0.50ms (vs DI ~0.04–0.08ms) → ~2×–10× slower depending on final tightness
* **Warm root:** potentially ~0.5µs–2.0µs (vs DI ~0.2µs) → ~2×–10× slower

Getting to **~2–3×** is *plausible* if the fast path becomes extremely lean (few branches, minimal locks, direct refs, integer indexing) and the benchmark constructors are trivial. If your runtime keeps extra features in the hot path (contracts, hooks, dynamic checks per node), the floor rises.

Cython/codegen can plausibly shave an additional **~1.5×–3×** off *Melder’s internal overhead* once the plan is already tight.

---

## Acceptance criteria

* [ ] Add ExecutionProgram compilation (Phase 5B/5C) and store per root
* [ ] Meld fast path executes without:

    * graph traversal
    * phase scheduler
    * per-node spell lookups
* [ ] Bench targets (depth 9 unique):

    * [ ] cold root ≤ 0.25ms (stretch: ≤ 0.15ms)
    * [ ] warm root ≤ 1.0µs (stretch: ≤ 0.5µs)
* [ ] Overrides: zero overhead when not used; patchpoint fast override works
* [ ] Slow path: correctness preserved; epochs invalidate; recompute brings system back to fast path
* [ ] No semantic regressions for existence scopes and spellspace gating

---

## Implementation checklist

### Data model + compiler

* [ ] Define `ExecutionProgram`, `NodeOp`, `ArgSource`, Cache specs (slots + small ints)
* [ ] Implement compiler: (RootResolutionBlueprint + Phase3 frames + spell metadata) → ExecutionProgram
* [ ] Compile mutation patchpoints (override_key → (op_idx, arg_slot_idx))
* [ ] Add per-root override plan cache (LRU)

### Runtime integration

* [ ] Add `ConduitResolutionState.get_program(root_spell_id)` (or similar)
* [ ] Update MeldRuntime to:

    * [ ] gate fast path (validity + dirty + epoch match)
    * [ ] execute program when possible
    * [ ] fall back to slow path (revalidate + recompile) when necessary

### Invalidation wiring

* [ ] On bind transaction end, bump structural epoch + dirty affected roots
* [ ] On link/unlink/transfer, bump resolution epoch + dirty per-conduit programs
* [ ] Ensure slow path recomputes and clears dirty markers

### Profiling + correctness tests

* [ ] Add perf counters (fast path hit rate, slow path causes)
* [ ] Add microbench: execution loop only (no hooks) to measure internal overhead
* [ ] Add tests for overrides, spellspace resets, dynamic link/unlink

### Optional acceleration

* [ ] Cythonize the program runner (loop + cache ops + arg materialization)
* [ ] Optional: Python codegen specialized runner per root (if needed)

```

---

## Grounding notes (why I’m confident about the “what exists today” parts)
You can delete this section before pasting into GitHub; it’s just the anchors I used from your project docs/code:

- Phase 1–4 artifacts on `SpellResolutionProfile` (`requirements`, `symbolic_graph`, `resolution_frame`, `validation`):contentReference[oaicite:0]{index=0}  
- Phase 1 intent & constraints (`SpellRequirementsFinder`):contentReference[oaicite:1]{index=1}  
- Phase 2 intent (`SpellSymbolicGraph` is “edges without concrete spell ids”):contentReference[oaicite:2]{index=2}  
- Phase 5–7 definitions + meld-time lazy revalidation behavior:contentReference[oaicite:3]{index=3}  
- Phase 5 blueprint generation already computes **topological order** (`ordered_node_ids`) and builds `RootResolutionBlueprint`:contentReference[oaicite:4]{index=4}  
- Phase 5 entrypoint description (“builds deep DAG blueprints… uses only existing Phase 1–4 artifacts”):contentReference[oaicite:5]{index=5}  
- Meld-time gating behavior and when it re-runs phases under lock:contentReference[oaicite:6]{index=6}  
- Runtime override behavior via `GraphMutator` (clones DAG, rewires targeted edges):contentReference[oaicite:7]{index=7}  
- Existence selection semantics used by meld runtime (owner_creations vs local creations, etc.):contentReference[oaicite:8]{index=8}  
- Conjure + meld flow diagrams (Spellbook.conjure runs phases 1–7; Conduit→Meld→MeldRuntime→MeldEngine):contentReference[oaicite:9]{index=9}