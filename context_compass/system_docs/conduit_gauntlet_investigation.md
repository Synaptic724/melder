# Conduit & Real-World Gauntlet — Bug & Slowness Investigation Guide

A standalone investigation guide for a fresh agent. No prior conversation
context assumed. Scope is deliberately narrow: **`Conduit` lifecycle and the
real-world gauntlet benchmark only.** Ignore Phase-12 / codegen work.

Goal: (1) the confirmed bugs and slow spots, with evidence; (2) the suspects
that still need reading, with exactly what to look for; (3) a repeatable
methodology to discover the rest; (4) a fix plan.

All paths are relative to repo root. `src/melder/aether/conduit/conduit.py` is
referred to below as **`conduit.py`**.

---

## 0. Environment warnings (read before touching anything)

- **File corruption:** the working tree has had runs of trailing NUL bytes
  appended to `.py` files by the edit tooling. Before editing any file, check
  `open(p,'rb').read().count(0)`; if non-zero and the NULs are a pure trailing
  run, strip them (content before the run is intact).
- **CRLF:** working tree is CRLF, `HEAD` is LF. Keep edits CRLF. Use
  `git diff --ignore-cr-at-eol`.
- **Measurement:** hybrid-core Intel (P + E cores). Pin to P-cores
  (`benchmarks/p_core_affinity/p_core_affinity.py`), report min/p50 not mean.
- **The melder test suite needs `ulid` + the project venv** — run it on the dev
  box, not in an analysis sandbox.

---

## 1. The gauntlet — what it is and what the numbers say

File: `benchmarks/testing_other_di/test_real_world_gauntlet.py` (~1539 lines).

It models a "real world" workload: a few app singletons, a bootstrap fan-out,
then 3 threads each repeatedly creating and tearing down **scopes** —
an *outer* scope and an inner *request* scope — and resolving objects in them.
65,000 hot scope cycles per run, 1000 iterations.

### 1.1 How melder is driven (the harness is fair — it calls real APIs)

`_build_runtime_melder` (line 916) and `_run_in_lesser_and_spellspace`
(line 967). Per scope cycle, for melder:

1. `lesser = conduit.create_lesser_conduit()`  — the **outer scope**
2. `lesser.meld(...)` ×2                        — resolve outer-scoped objects
3. `request_cm = lesser.enter_spellspace(); space = request_cm.__enter__()` — the **request scope**
4. `space.meld(...)` several times
5. `request_cm.__exit__(...)`                   — request-scope teardown
6. `lesser.cleanup()`                           — outer-scope teardown

No fabricated overhead — these are genuine melder APIs, timed honestly. The one
modeling choice: melder's "outer scope" maps to a **lesser `Conduit`**, because
`unique_per_conduit`-scoped services require a real conduit to scope to. That's
melder's existence model, so the mapping is legitimate.

### 1.2 The numbers (last run)

| metric                    | melder    | dependency-injector | dishka   |
|---------------------------|-----------|---------------------|----------|
| gauntlet total avg/iter   | 15.56ms   | 2.89ms              | 3.10ms   |
| setup                     | 220.9ms   | 21.1ms              | 41.7ms   |
| outer-scope **create**    | 0.069ms   | ~0.000ms            | 0.001ms  |
| outer-scope cleanup       | 0.027ms   | ~0.000ms            | ~0.000ms |
| outer-scope whole-cycle   | 0.163ms   | 0.016ms             | 0.011ms  |
| request-scope create      | 0.008ms   | ~0.000ms            | 0.001ms  |
| request-scope cleanup     | 0.004ms   | ~0.000ms            | ~0.000ms |
| hot_scopes/s              | 4,178     | 22,484              | 20,994   |
| CV (run-to-run)           | 9.7%      | 6.8%                | 11.2%    |

Melder is **~5× slower overall**. The single dominant line is **outer-scope
create = 69µs** — that is one `create_lesser_conduit()` call. ×65,000 ≈ 4.5s of
the 15.5s. `cleanup()` at 27µs adds ~1.8s more. `enter_spellspace` (8µs) is much
cheaper by comparison — so the request-scope path is *not* the problem; the
**lesser-conduit** path is.

### 1.3 CRITICAL measurement contamination — the GIL artifact

The gauntlet config line reports **`gil=enabled`**. Melder is built to run on
free-threaded (no-GIL) Python; that is a core design premise. But the gauntlet
imports `dependency_injector`, a C extension that has **not** declared no-GIL
safety, so importing it **forces the GIL back on for the whole process**. (You
will see `RuntimeWarning: the GIL has been enabled to load module
'dependency_injector.providers'` in other benchmark runs.)

Consequences:
- Melder's 3-thread gauntlet runs **GIL-serialized**. Its free-threading
  advantage is nullified — by a co-loaded competitor, not by its own code.
- Any cross-thread contention numbers (and the variance) are GIL-flavoured.

**Action:** run the melder gauntlet **in isolation** — a variant that imports
only melder, on a real free-threaded interpreter, GIL off — to get a true
picture. The current cross-framework gauntlet cannot measure melder's threading
honestly. Treat the 5× as "melder GIL-on vs competitors GIL-on"; the no-GIL
number is unknown and must be measured separately.

---

## 2. Confirmed issues in `conduit.py` (evidence included)

### BUG-1 — per-conduit `ContextVar` leak (this is a correctness bug, not just slow)

- `conduit.py:265` — `Conduit.__init__` builds a **uniquely-named** ContextVar
  per conduit: `self._spellspace_stack = ContextVar(f"_spellspace_stack_{self._id}", default=[])`.
- `conduit.py:700-713` — `enter_spellspace` calls `.set()` on it (push, and
  again on pop).
- Mechanism: `.set()` writes an entry into the **calling thread's `Context`**,
  and a `Context` holds a *strong reference* to the ContextVar. A worker
  thread's `Context` lives as long as the thread. So every per-conduit
  ContextVar ever `.set()` on a thread is pinned for that thread's lifetime —
  **even after `cleanup()`**. `_cleanup_lesser_conduit` does `del self._spellspace_stack`
  (`conduit.py:404`), which only drops the *conduit's* reference; the thread
  `Context` still pins it. Cleanup **cannot** fix this.
- Impact: on the gauntlet, the 3 worker Contexts accumulate ~tens of thousands
  of dead `(ContextVar, [])` entries. On a long-lived server thread doing
  per-request scopes it grows **unbounded**. Second-order: a thread `Context` is
  a HAMT; every `.set()` enlarges it, so `enter_spellspace` gets monotonically
  slower over a run — a likely contributor to the variance.
- This is a real bug. Fix it independent of any perf work — see §5.

### SLOW-1 — `DevopsIdentity` eager attach to a frame-wide registry

- `conduit.py:253-264` — every conduit (lesser included) builds a
  `DevopsIdentity`, calls `attach_registry(self._aetheric_frame.devops_information_registry, ...)`,
  then `_refresh_devops_identity_state()`.
- The `devops_information_registry` is **frame-wide and shared across the
  gauntlet's 3 threads**. 65k ephemeral scopes ⇒ 65k attach/detach churn on one
  shared structure ⇒ per-create cost + cross-thread contention. Strong
  candidate for the 43%-CV / `outer_create max ≈ 3.6ms` tail.
- `_cleanup_lesser_conduit` does call `self._transaction_identity.cleanup()`
  (`conduit.py:402`) — see SUSPECT-D: confirm that actually *detaches* from the
  registry, or this is a second leak.

### SLOW-2 — a lesser conduit constructs the full normal-conduit runtime

- `conduit.py:144` `Conduit.__init__`; reached via `create_lesser_conduit`
  (`conduit.py:1557`). Per lesser conduit it builds: id; `DevopsIdentity` +
  registry attach (SLOW-1); the per-conduit `ContextVar` (BUG-1);
  `Creations` (`_creations_configuration`, `conduit.py:1180`); `CreationGate`
  (`_create_gate_for_current_root`, `conduit.py:1271`); split hook maps
  (`_snapshot_split_hook_maps_from_configuration`, `conduit.py:941`);
  `Meld`; `_configure_conduit_state`; `ConduitWard`.
- Measured 69µs. "Construct an object + wire a few pointers" should be low
  single-digit µs. The lesser conduit is paying normal-conduit construction
  cost.

### NOT the gauntlet hotspot (do not chase these *for the gauntlet*)

- `_configure_conduit_state()` (`conduit.py:865`): for `lesser` it only nulls
  the name. Trivial. (The expensive branch — `_add_root_conduit` +
  `_add_spells_to_aether` — is `normal`-only.)
- `_snapshot_split_hook_maps_from_configuration()` (`conduit.py:941`): copies
  hook lists — but the gauntlet configures **no hooks**, so `get_hooks` returns
  empties and this is near-free *in this benchmark*. It is still wasteful in
  principle (a lesser conduit should share the parent's maps by reference, not
  copy) — fix it, but know it is not the 69µs here.

---

## 3. Unconfirmed suspects — read these, here is exactly what to look for

The 69µs is spread across the constructors below. **Profile first** (§4.1) to
rank them, then read the top ones with these questions:

- **SUSPECT-A — `Meld.__init__`** (`src/melder/aether/conduit/meld/meld.py`).
  Look for: any per-spell work (does it iterate the spellbook? pre-build
  per-spell `CreationContext` or caches?). It *should* just store references
  and start empty caches. If it walks all spells, that is O(spells) per lesser
  conduit.

- **SUSPECT-B — `ConduitWard.__init__`**
  (`src/melder/aether/conduit/conduit_ward/conduit_ward.py`). Look for: how much
  is contract-graph machinery (contract map, inbound/outbound link indices,
  policy objects) vs. the few lineage pointers a lesser conduit actually needs
  (parent, root, lesser-children list). A lesser conduit cannot peer-link or
  register contracts, so the contract-graph machinery is dead weight for it.
  Identify what can be gated behind `conduit_type == lesser`.

- **SUSPECT-C — `CreationGateController.create_conduit_gate`** (find the
  controller class; `conduit.py:1271` calls it). Look for: is gate registration
  O(1), or O(conduits) / O(roots)? Does it take a lock on a shared controller
  structure (cross-thread contention in the 3-thread gauntlet)? The
  `CreationGate` itself is wanted (lockdown handle) — the question is
  registration cost.

- **SUSPECT-D — `DevopsIdentity` internals + `.cleanup()`** (find the class;
  `conduit.py:253` constructs it). Look for: (1) what `attach_registry` and
  `_refresh_devops_identity_state` cost; (2) **does `DevopsIdentity.cleanup()`
  detach from `devops_information_registry`?** If it does not, the registry
  grows with every conduit ever created — a second leak on top of BUG-1.

- **SUSPECT-E — `Creations.__init__`** (`src/melder/aether/conduit/creations/creations.py`;
  `conduit.py:1196` constructs it). Look for: per-existence-category dict
  pre-allocation or any per-spell work. Probably light; confirm.

---

## 4. Discovery methodology — how to find what this guide does not list

### 4.1 Profile `create_lesser_conduit` + `cleanup` (do this first)

On the dev box, in the project venv:

```python
import cProfile, pstats
# build a conjured root conduit `conduit` exactly as the gauntlet does
def loop():
    for _ in range(20000):
        lesser = conduit.create_lesser_conduit()
        lesser.cleanup()
cProfile.run("loop()", "lesser.prof")
pstats.Stats("lesser.prof").sort_stats("cumtime").print_stats(30)
```

Read the output top-down: `Conduit.__init__` → which callee dominates `cumtime`.
That ranks SUSPECT-A..E precisely. Repeat with `tottime` sort to find tight
self-time hot spots. This converts "it is slow" into a concrete ranked list.

### 4.2 `__init__` ↔ `cleanup` symmetry audit (catches leaks)

The gauntlet creating/destroying 65k conduits is a cleanup-correctness stress
test. **Every registration / attach in `__init__` must have a matching detach
in `_cleanup_lesser_conduit`.** Build this table and verify each row:

| `__init__` does                              | `_cleanup_lesser_conduit` reverses it? |
|----------------------------------------------|----------------------------------------|
| `DevopsIdentity.attach_registry(...)`         | `_transaction_identity.cleanup()` — **verify it detaches** (SUSPECT-D) |
| `ContextVar(...)` + later `.set()`            | **NO — cannot** (BUG-1); thread Context pins it |
| `controller.create_conduit_gate(...)`         | `controller.unregister_conduit_gate(id)` — present (`conduit.py:368`) |
| `CreationGate` created                        | `_creation_gate.cleanup()` — present |
| `Meld(...)`                                   | `_meld.cleanup()` — present |
| `ConduitWard(...)`                            | `_conduit_ward.cleanup()` — present |
| `Creations(...)`                              | `_creations.cleanup()` — present |
| `_publish_conduit_record_to_nexus()` (only if nexus publish enabled) | `_remove_conduit_record_from_nexus()` — present |
| spellspaces entered                           | `_cleanup_spellspaces()` — present |

Anything that does not reverse cleanly is a leak. Today the known unrecoverable
one is the ContextVar; SUSPECT-D (devops registry) is unverified.

### 4.3 Leak hunt — measure it directly

```python
import gc, tracemalloc
tracemalloc.start()
# baseline
gc.collect(); before = len(gc.get_objects())
for _ in range(20000):
    lesser = conduit.create_lesser_conduit(); lesser.cleanup()
gc.collect(); after = len(gc.get_objects())
print("net objects retained:", after - before)            # should be ~0
print(tracemalloc.take_snapshot().statistics("lineno")[:25])
```

If `after - before` is large, something is retained per conduit. To confirm the
ContextVar specifically, count them: `sum(1 for o in gc.get_objects()
if type(o).__name__ == "ContextVar")` before and after — it will climb by ~1
per conduit that called `enter_spellspace`. Use `gc.get_referrers(...)` on a
leaked object to see what pins it (expect a `Context`).

### 4.4 Re-measure without the GIL artifact

Run a melder-only gauntlet variant (no `dependency_injector` import anywhere in
the process) on a free-threaded build with the GIL off. Compare 1-thread vs
3-thread scaling — that is the only honest read of melder's threaded behavior.
If 3-thread throughput does not scale ~3×, look for shared-structure contention
(prime suspects: the frame-wide `devops_information_registry` in SLOW-1, and the
`CreationGateController` in SUSPECT-C).

### 4.5 Variance / tail

`outer_create` p99 ≈ 0.15ms but `max` ≈ 3.6ms — a long tail. After core-pinning
(removes E-core noise), residual tail points at lock contention or a structure
that grows. Check: the shared devops registry, the gate controller, and the
growing thread-Context HAMT (BUG-1).

---

## 5. Fix plan

### FIX-1 — kill the ContextVar leak (BUG-1) — highest priority, do regardless

Replace the per-conduit `ContextVar` (`conduit.py:265`). Choose by the
isolation actually required for the spellspace stack — **decide with the
owner**: does a spellspace stack need to follow execution across `await`?
- No, and a conduit's stack is only touched by one thread/task at a time
  (true for a lesser conduit used as a request scope) → plain `list` instance
  attribute. Simplest; GC-clean.
- Per-thread isolation, no async propagation → `threading.local()` per conduit
  (these GC normally — no Context pinning).
- Must propagate across `await` → **one module-level** `ContextVar` holding a
  dict keyed by conduit id; delete the conduit's key in `cleanup()`. The
  module-level ContextVar is created once at import and never leaks.
Note: `Creations` is constructed with `spellspace_stack=self._spellspace_stack`
(`conduit.py:1198`) — whatever you pick, update that call and any `Creations`
code that treats it as a ContextVar.

### FIX-2 — lazy devops identity for lesser conduits (SLOW-1)

Do not eagerly `attach_registry` an ephemeral lesser conduit to the frame-wide
`devops_information_registry`. Attach lazily — only when something actually
inspects/controls the conduit. This does not weaken the `CreationGate` lockdown
(separate mechanism — keep that). Confirm SUSPECT-D first so you also fix the
detach side if needed.

### FIX-3 — a lightweight lesser-conduit init path (SLOW-2)

Gate `Conduit.__init__` on `conduit_state == lesser`:
- **Keep, full:** `Creations` (the scope's instance store — its purpose);
  `CreationGate` (lockdown handle — owner wants this); `Meld` (a lesser conduit
  resolves spells); id.
- **Lighter:** `ConduitWard` — build only lineage pointers for a lesser
  conduit; skip the contract graph / link indices / peer-link policy (gate
  behind `conduit_type == lesser` per SUSPECT-B findings).
- **Share, do not copy:** hook maps — a lesser conduit should take a shared
  reference to the parent's already-snapshotted `_conduit_hooks` /
  `_meld_hooks` rather than re-running `_snapshot_split_hook_maps_from_configuration`.
- Plus FIX-1 (plain stack) and FIX-2 (lazy devops).

Sequence each sub-fix against the §4.1 profile so you spend effort where the
cumtime actually is. Re-run the profile after each.

### Deeper question for the owner

Should a per-request scope be a full `Conduit` at all? `enter_spellspace()` is
~8µs; the 69µs is specifically the lesser conduit. If many real workloads need
per-request scoping, a scope primitive lighter than a full conduit may be the
real answer — that is an architecture decision, not a mechanical fix.

---

## 6. Verification

- Every change keeps the 52-test suite green and the gauntlet at `errors=0`.
- After FIX-1, run §4.3 — net retained objects must be ~0 and the ContextVar
  count must stop climbing.
- Re-profile (§4.1) after each fix; re-run the gauntlet **P-core-pinned** and,
  for threaded numbers, **GIL-off in isolation** (§4.4).
- Honest before/after = same binary, change reverted vs applied, pinned,
  min-of-N.
