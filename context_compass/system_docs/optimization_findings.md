# Melder Performance Optimization — Findings & Handoff

Status: handoff document for a fresh agent. Self-contained — assumes no prior
conversation context. All paths are relative to the repo root.

This captures (1) optimizations already implemented in this session, (2) open
opportunities with evidence and recommended fixes, and (3) measurement caveats.

---

## 0. Critical environment warnings (read first)

- **The working tree is corrupting files.** Several `.py` files were found with
  runs of trailing NUL bytes appended (`executor_code_cache.py` had 4,828;
  `spellbook_creation_system.py` and three `transaction_manager/` files had
  5–68 each). Cause appears to be the user's edit/delete tooling writing with a
  stale length. **Before trusting any file, scan for NUL bytes**
  (`open(p,'rb').read().count(0)`). Strip pure-trailing-NUL runs to recover the
  file (verified safe — the real content is intact before the NUL run).
- **Line endings:** working tree is CRLF on every file; `HEAD` is LF. `git diff`
  looks enormous because of this. Use `git diff --ignore-cr-at-eol` to see real
  changes. Keep new/edited files CRLF to match the working tree.
- **Benchmark noise:** the dev machine is a hybrid-core Intel (P-cores +
  E-cores). µs-level timings are unreliable without core pinning. Use
  `benchmarks/p_core_affinity/p_core_affinity.py`, pin to P-cores, and report
  **min or p50, not mean**. A conjure time swinging 45ms→77ms between runs is
  E-core scheduling, not code.
- The melder test suite cannot be run in the analysis sandbox (`ulid` missing,
  no network). All landed changes were verified by `py_compile` + standalone
  harnesses (stubbing melder enums/exceptions). The full 52-test suite + the
  benchmark `errors=0` are the real gate — run them on the dev machine.

---

## 1. Already implemented this session (verify, then keep)

### 1.1 Unified source-keyed executor code cache  — LANDED
- New file: `src/melder/aether/spellbook/spell_compiler/executor_code_cache.py`
- Edited: `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py`
  (`_compile_emitted_no_overrides_executor` routes through it),
  `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_overrides_executor.py`
  (`compile_phase12_overrides_executor_code_object` routes through it).
- What: Phase 12 emits identity-free executor source (spell identity is supplied
  at `exec()` time via the namespace, not baked into source). Two spells with
  the same plan shape emit byte-identical source. The cache keys compiled
  `code` objects on `sha256(source)`, so identical shapes — within one conjure,
  across conjures, across Spellbooks — share one compile. Lock-free reads;
  `compile()` runs outside the lock; bounded FIFO eviction (4096).
- Measured: `execution_plan` conjure phase 32.3ms → 20.8ms (−36%); the
  `compile()` call vanished from the top-20 conjure allocations.
- Verified: 32-thread stress harness, errors=0.

### 1.2 Removed dead per-CreationContext override code-object cache — LANDED (UNSTABLE)
- Edited: `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- What: `_override_executor_code_object_cache_by_plan_signature` was keyed on
  the same `shape_key` as `_override_specialization_cache`, which is checked
  first — so it could never produce a hit. Dead code. Removed the slot, init,
  cleanup, and the `_get_or_build_override_executor_code_object` method; the
  call site now goes straight to `compile_phase12_overrides_executor_code_object`
  (which is cached by 1.1).
- **WARNING:** this edit was reverted by the working tree twice during the
  session. **Verify it is actually present** — grep for
  `_override_executor_code_object_cache_by_plan_signature`; if it still exists,
  re-apply. Zero performance impact (dead cache); pure cleanup.

### 1.3 Phase 5 reachability hoist — LANDED
- Edited: `src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py`
- What: `compiler_phase_5.py:332` builds a deep blueprint for every non-root
  spell; each `_build_single_root_dag` re-ran a full reachability DFS, so a
  shared subtree was re-walked once per dependent. Added
  `_compute_reachable_by_id` — one Kahn-ordered pass computing every spell's
  reachable set, memoized per snapshot on the builder; `_build_single_root_dag`
  takes the precomputed set (falls back to the original DFS if not supplied).
- Measured: `root_blueprints` phase 14.8ms → 13.0ms (−12%).
- Verified: equivalence harness — 4,000 random graphs (incl. cyclic), 82,662
  node checks, 0 mismatches vs the original DFS.

### 1.4 No-overrides constructor inline — LANDED
- Edited: `src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py`
- What: the step-plan executor used to emit `_construct_spell_instance(...)`
  per step, which re-interpreted the plan recipe (`_build_kwargs_no_overrides`
  loop, dict build, branching) on every meld. Added `_inlinable_common_shape`
  (predicate) + `_emit_construct_instance` + `_raise_meld_construction_error`:
  for the common shape (callable spell, not existing-creation, single-value
  deps, no contract payload, no positional/`__args__` override) it now bakes a
  direct `spell.spell(param=instance_results[key], ...)` call into the source.
  Other shapes fall back to `_construct_spell_instance` unchanged.
- This is the singleton/step-plan path real apps use; the transient executor
  was already inlined.
- Verified: standalone harness — predicate correctness, generated source
  compiles, inlined executor builds correct wired instances, error semantics
  (`MeldExecutionError` + `inner`) preserved, fallback intact, mixed plans OK.
- Known divergence (acceptable): a genuinely missing dependency key raises
  `MeldExecutionError` with message "Error invoking spell" instead of
  "Dependency 'X' missing" — same exception type, `inner` carries the
  `KeyError`; unreachable for a valid topologically-ordered plan.

### Items explicitly NOT to redo
- The **overrides codegen is already shape-inlined**
  (`_append_overrides_construct_inline_source` in `phase12_overrides_executor.py`,
  used across shape lanes 1917–2194, with `_construct_spell_instance_with_overrides`
  kept only as the generic fallback). Do not "inline" it — it is done.
- A cross-process disk persistence layer for the code cache was implemented and
  then deliberately removed by the project owner ("sus for a public library").
  **Do not re-add it.**

---

## 2. Open opportunities (ranked)

### OPP-A — ContextVar-per-conduit: leak + growing-HAMT slowdown  [HIGH]
- Location: `src/melder/aether/conduit/conduit.py:265` (creation),
  `:700-713` (`enter_spellspace`).
- Problem: `Conduit.__init__` creates a uniquely-named `ContextVar` per
  conduit: `ContextVar(f"_spellspace_stack_{self._id}", default=[])`.
  `enter_spellspace` calls `.set()` on it (push and pop). `.set()` writes an
  entry into the calling thread's `Context`, and a `Context` holds a **strong
  reference** to the ContextVar. A worker thread's `Context` lives as long as
  the thread, so every per-conduit ContextVar ever `.set()` on that thread is
  pinned for the thread's lifetime — even after the conduit is `cleanup()`'d.
  On a long-lived server thread doing per-request scopes this grows unbounded.
  Second-order: the thread `Context` is a HAMT; it grows one node per conduit,
  so `.set()`/`.get()` (i.e. `enter_spellspace` itself) gets monotonically
  slower over a run. Plausible cause of the gauntlet's 43% CV / max≈2×min.
- Fix: the spellspace stack must not be a per-conduit ContextVar. Pick by
  required isolation:
  - plain `list` instance attribute — if a conduit's stack is only touched by
    one thread/task at a time (true for a lesser conduit used as a request
    scope). Simplest, GC-clean.
  - `threading.local()` per conduit — per-thread isolation, no Context pinning.
  - one **module-level** `ContextVar` holding a dict keyed by conduit id — only
    if spellspace stacks must propagate across `await` boundaries.
  Decision input needed from owner: does a spellspace stack need to follow
  execution across `await`? If no → plain list.
- Risk: low-moderate; behavior depends on the isolation choice. Verify
  `create_spellspace`/`SpellSpace` semantics aren't relying on ContextVar
  copy-on-fork behavior.

### OPP-B — DevopsIdentity eager registry attach (cost + cross-thread contention)  [HIGH]
- Location: `src/melder/aether/conduit/conduit.py:253-264`.
- Problem: every conduit, lesser included, builds a `DevopsIdentity`, calls
  `attach_registry(self._aetheric_frame.devops_information_registry, ...)`, and
  `_refresh_devops_identity_state()`. Ephemeral request scopes (65k in the
  gauntlet, across 3 threads) churn that frame-wide, shared registry — cost per
  create plus lock contention on one structure across threads.
- Fix: make devops-identity registration **lazy** for lesser conduits — only
  attach to the frame registry when something actually inspects/controls the
  conduit. This does not weaken the `CreationGate` lockdown path (separate
  mechanism — see OPP-C).
- Risk: moderate — confirm nothing assumes a lesser conduit is always present
  in `devops_information_registry` at construction time.

### OPP-C — Lesser-conduit heavyweight init (the 69µs / 5× gauntlet gap)  [HIGH]
- Location: `src/melder/aether/conduit/conduit.py:144` (`Conduit.__init__`),
  reached via `create_lesser_conduit` (`:1557`).
- Problem: a lesser conduit constructs the full normal-conduit machinery —
  measured ~69µs per `create_lesser_conduit()` (dependency-injector scope ≈0µs,
  dishka ≈1µs). In the "real world gauntlet"
  (`benchmarks/testing_other_di/test_real_world_gauntlet.py`) this makes melder
  ~5× slower overall (15.5ms/iter vs 2.9ms dep-injector, 3.1ms dishka). The
  benchmark is fair — it calls real APIs (`create_lesser_conduit`,
  `enter_spellspace`, `cleanup`); the cost is real melder code.
- `__init__` builds, per lesser conduit: id; `DevopsIdentity` + registry attach
  (OPP-B); a per-conduit `ContextVar` (OPP-A); `Creations`; `CreationGate`;
  `_snapshot_split_hook_maps_from_configuration()`; `Meld`;
  `_configure_conduit_state()`; `ConduitWard`.
- Recommended: a dedicated lightweight init path for `conduit_state == lesser`:
  - **Keep, full:** `Creations` (the scope's instance storage — its whole
    purpose); `CreationGate` (lockdown handle — "stop a conduit from anywhere";
    owner explicitly wants this); `Meld` (a lesser conduit resolves spells);
    id.
  - **Make lesser-specific (lighter):** `ConduitWard` — a lesser conduit needs
    only lineage pointers (parent, root, lesser-children list); it cannot
    peer-link or register contracts, so the contract graph / inbound-outbound
    link indices / peer-link policy machinery should not be built. A
    `lesser`-mode ward.
  - **Skip / share:** `_snapshot_split_hook_maps_from_configuration()` — the
    parent already snapshotted the hook maps once; a lesser conduit inherits
    and never mutates config hooks, so it should take a **shared reference** to
    the parent's `_conduit_hooks` / `_meld_hooks`, not a per-conduit copy.
  - Plus OPP-A (plain-list spellspace stack) and OPP-B (lazy devops identity).
- Before writing the exact cut, **read and confirm internals of**:
  `ConduitWard.__init__` (`src/melder/aether/conduit/conduit_ward/conduit_ward.py`)
  — how much is contract-graph machinery cleanly gated behind
  `conduit_type == lesser`; `Conduit._configure_conduit_state()` — what the
  lesser branch does; `Conduit._creations_configuration()` — whether it does
  per-spell pre-allocation. A 30-second cProfile of `create_lesser_conduit()`
  in a tight loop will rank the sub-constructions by cumtime — do that first to
  target the actual hotspots.
- Deeper architectural question for the owner: should a per-request scope be a
  full `Conduit` at all? `enter_spellspace()` is only ~8µs; the 69µs is
  specifically the lesser-conduit (`unique_per_conduit` outer scope).
- Risk: moderate-high — hot, correctness-sensitive. Do it test-gated.

### OPP-D — O(N²) cycle-detection strategies in Phase 4  [MEDIUM]
- Location:
  `src/melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py`
  (`validate`, the `binding_graph` build ~lines 85-114);
  `src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py`
  (`validate`, the `adjacency` build ~lines 71-77).
- Problem: Phase 4 validates every spell; `SpellValidationSystem.validate_spell`
  runs all strategies per spell. Both cycle strategies rebuild the **entire
  spellbook-wide graph** inside each per-spell `validate()` call — only the
  per-spell `root_key` differs. N spells ⇒ the same N-node graph is built N
  times (O(N²)). It dominated conjure-tracemalloc allocations (`adjacency=set()`
  ×255, `_detect_cycles` ×153) though the `validation` phase is only ~1.8ms
  wall-time — so this is mostly an allocation/GC-pressure win, modest on time.
- Confirmed: the `SpellValidationSystem` (hence its strategy instances) is
  shared across all spells in a Phase-4 pass — one `SpellCompilerSystem` per
  pass (`spellbook_creation_system.py:781` and `:832` each create exactly one;
  `spell_compiler_system.py:59` owns one `_spell_validator`). So memoizing the
  graph on the strategy instance is correctly pass-scoped.
- Fix: hoist the graph build out of the per-spell loop. Build it once, memoize
  on the strategy instance, guarded by a cheap **completeness signature** so it
  is correct for both the barrier-gated full conjure AND the interleaved
  post-conjure path (`run_post_conjure_structural_phases` runs phases 1-4 per
  spell sequentially, so a spell's `requirements`/`dependencies` populate
  mid-pass). Suggested signature: count of spells whose requirements are
  present/non-cleaned (binding strategy) and count of spells with non-empty
  `dependencies` (circular strategy) — monotonic during a pass; any change that
  could alter the graph also changes the count; equal count ⇒ identical graph ⇒
  safe reuse. Needs `import threading` + a lock + extended `__slots__` on each
  strategy (`SpellValidationStrategy.__slots__` is the base).
- Risk: low-moderate. Verify the completeness signature with a harness:
  full-conjure path memo must hit every call; interleaved path must rebuild as
  spells complete.

### OPP-E — Spell key recomputation (precompute the immutable key)  [MEDIUM]
- Location: `src/melder/utilities/helpers/general_helpers.py:128`
  (`normalize_frame_key` is `@lru_cache(maxsize=64)`), `:178`
  (`normalize_binding_name` same). `make_spell_key_from_parts` / `normalize_spell_key`
  themselves are uncached.
- Problem: `@lru_cache(maxsize=64)` on `normalize_frame_key` thrashes when a
  graph has >64 distinct frames (each ~per spell type) — near-100% miss +
  eviction, so the cache adds overhead on top of recomputing. Deeper: a spell's
  `(frame_key, bind_key)` is **immutable after bind** (`spellframe`,
  `spell_name`, `binding_name` never change), yet it is recomputed all over —
  `spell.py:394`, `meld.py:1584/1594`, the Phase-4 cycle strategies, contract
  strategies, `compiler_phase_3.py:482`. `(frame_key, bind_key)` appeared as a
  top-20 conjure allocation (~782 tuple builds).
- Fix: compute the canonical `(frame_key, bind_key)` once at bind time, store
  it on the `Spell` object; callers read the attribute instead of recomputing.
  This is precomputing an invariant, not caching. (Cheap, low risk, no
  hot-path surgery — good first task.)
- Risk: low.

### OPP-F — root_blueprints: DAG-build + socket-overlay still per-spell  [MEDIUM, needs profiling first]
- Location: `spell_system_root_blueprint_builder.py` — `_build_single_root_dag`
  (the `DirectedAcyclicWorkGraph` construction: `add_nodes_bulk`,
  `add_dependencies_bulk`, `collect_dependency_ids` topo sort) and
  `_overlay_sockets_and_index` (the socket BFS allocating `SocketRef`s).
- Problem: OPP-1.3 (landed) removed only the *reachability traversal*
  duplication. The DAG construction and socket overlay are still rebuilt for
  every per-spell blueprint, re-doing work for shared subtrees. ~13ms of the
  (post-1.3) 13ms `root_blueprints` phase is here.
- Fix direction: compose bottom-up like 1.3 — but the socket overlay is
  **path-relative** (`param_path_id` differs per blueprint root), so it cannot
  be shared as-is; it is a real rearchitecture, not a hoist.
- **Do not start blind.** First get a profiler breakdown of `_build_single_root_dag`
  DAG-build vs `_overlay_sockets_and_index` inside the `root_blueprints` phase
  to know which dominates; only then design the fix.
- Risk: high (hot structural code).

### OPP-G — Warm-meld layering vs flat competitors  [LOW / architectural]
- Location: `src/melder/aether/conduit/meld/meld.py` (`Meld.meld`, ~335-413).
- Problem: warm singleton resolve is ~0.41µs vs dependency-injector 0.04µs,
  dishka 0.26µs (LITE singleton benchmark, post-warmup). The path —
  `Conduit.meld` → `Meld.meld` → `creation_context._execute_no_hooks_no_overrides_compiled`
  → CC template — is 3-4 call frames; each frame is individually tight (a
  tuple-keyed resolution-cache `.get`, ~6 attr reads, 2 skipped gate bools, the
  template's `owner_creations._creations.get` + return). There is no redundant
  work to delete — the 0.41µs is the *sum of the layers*. dependency-injector
  is 0.04µs because it has one layer (a provider `__call__`).
- Note: in automatic mode the validity/change-control gates are off (two bool
  reads, both fall through) — so the gap is NOT gating.
- Fix direction: only a "direct meld handle" closes it — after a spell is
  resolved once, hand the caller a bound callable that *is*
  `creation_context._execute_no_hooks_no_overrides_compiled` pre-bound with
  `creations`, so a repeat warm meld is one call, skipping `Conduit.meld` /
  `Meld.meld` / the resolution-cache lookup. This is an API/architecture
  addition with its own lifecycle-vs-mutation-invalidation design — owner
  decision, not a mechanical edit. (A `melder-direct-vs-alias` probe already
  exists in the benchmarks — the team is already circling this.)
- Minor sub-item: meld-by-object allocates a fresh 4-tuple resolution-cache key
  (`(spell_name, spell, spellframe, binding_name)`) every call (`meld.py:350`).
  Tens of ns; will not move a 10× gap.
- Reality check: HEAVY-transient benchmark shows melder 1094µs vs dishka 1082µs
  — dead even — because once real constructor work happens between resolves a
  sub-µs dispatch difference vanishes. The warm-resolve gap only dominates a
  synthetic tight loop.
- Risk: high (architecture). Treat as a design proposal, not an optimization
  task.

---

## 3. Suggested order of work

1. OPP-E (precompute spell key) — cheap, low risk, isolated. Warm-up task.
2. OPP-A (ContextVar) — correctness/leak, not just perf; fix regardless.
3. OPP-B + OPP-C (lesser-conduit lightweight init) — the big one for the
   5× gauntlet gap. Profile `create_lesser_conduit` first; read
   `ConduitWard.__init__` / `_configure_conduit_state` / `_creations_configuration`.
4. OPP-D (O(N²) cycle strategies) — modest but clean once the completeness
   signature is verified.
5. OPP-F — only after a profiler breakdown justifies the rearchitecture.
6. OPP-G — owner design decision; not a mechanical task.

## 4. Verification expectations

Every change must keep the 52-test suite green and the benchmark suite at
`errors=0`. For codegen changes (Phase 12), also verify generated source
compiles and exec's to correct instances (a stub-based standalone harness works
— stub the melder enums/exceptions, import the emitter module, run it, exec the
output). For measurement, P-core-pin and report min/p50. The honest before/after
for any change is: same binary, change reverted vs applied, P-core-pinned,
min-of-N.
