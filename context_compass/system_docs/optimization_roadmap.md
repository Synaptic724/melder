# Melder Performance Roadmap — Top 20 Opportunities

Working doc. Where things stand and the ranked list of what's left.

## Current standing

Gauntlet, gil-disabled, 3-thread, 1000 iters (the honest number):
- melder **2.97ms/iter**, dishka 1.45ms, dependency-injector 1.28ms
- melder is **~2.0× dishka, ~2.3× dep-injector** (down from ~4-5× before pooling)
- tail is still bad: gauntlet max 16ms vs median 2.97ms; `request-scope cleanup` CV up to 1192%

## Done already
- ContextVar-per-conduit leak — fixed
- Conduit + spellspace **pooling** — done; killed `Conduit.__init__` and ULID minting from the hot path (was ~12%)
- Phase-12 source-keyed compile cache; Phase-5 reachability hoist; no-overrides constructor inline — done

## How to read the profiles
The cProfile runs are ~⅓ module-import + conjure noise. Use them for **call counts and
relative ranking**, not absolute µs. For real timing use the gil-disabled
non-cProfile gauntlet, P-core-pinned, min/p50.

---

## TIER 1 — the big remaining levers

### 1. The seal / warm-resolve object cache  ★ highest value
A warm meld descends `Conduit.meld → Meld.meld → CreationContext → Creations →
CreationGate`, costing ~217k `RLock` enter/exit + ~102k `check_cleaned` per run.
A version-stamped seal at the front door returns a cached instance before
descending — flattening the warm path to one dict get + an epoch compare.
Closes most of the median 2× gap. Invalidate by bumping a per-conduit epoch on
bind/mutate/cleanup; `existing_creation` spells are sealable at bind.
Impact: large. Risk: medium (correctness — stale entry must self-invalidate).

### 2. De-scope the `TransactionMediator` from scope create/cleanup  ★ the tail
The 20ms spikes / CV 435-532% are contention, not work — pooling proved it
(construction is gone, tail remains). Lineage `link` during `create_lesser_conduit`
routes through the mediator's broad lock; 3 threads serialize on it. Fix: give
lesser-conduit linking a narrow local path, or shrink the mediator's lock to the
commit only. Impact: kills p99/p99.9 latency cliffs. Risk: medium.

### 3. Lock elision on the warm read path
A warm singleton resolve is `creations._creations.get(spell_id)` — a `dict.get`,
atomic on free-threaded Python, **needs no lock**. Only the cold
construct-and-register path needs the double-checked lock. Audit which of the
~217k RLock ops are hit-path vs construct-path; delete the hit-path ones.
Impact: medium-large. Risk: low (targeted).

### 4. One lock per executor run, not per step
The Phase-12 step executor takes `creations._lock` per unique-ish step. For a
graph of N steps in one creations container that's N acquire/release. Take it
once around the executor body instead. Impact: cuts a large share of the RLock
churn. Risk: low-medium (lock held slightly longer per meld — fine, melds are short).

---

## TIER 2 — solid mid-tier wins

### 5. Hoist `get_active_spellspace`
`creations.get_active_spellspace` / `spell_space_thread_state.get_active` — 17,916
calls each. Re-resolved ~3× per spellspace-scoped step (existence check ×2 +
register) when it's constant within a meld. Resolve once per executor run, pass
it down. Cheap rider on the seal work. Impact: small-medium. Risk: low.

### 6. Elide the `Creation` wrapper for disposal-less objects
Every registered instance is wrapped in a `Creation` (carrying disposal
metadata); `creation.value` is read 27,773×. For objects with no disposal
methods the wrapper is pure overhead — an allocation + an indirection per
resolve. Store the bare object; wrap only when disposal metadata exists.
Impact: medium. Risk: low-medium (touches the read path everywhere).

### 7. Optimize the pool reset path
Post-pooling, scope cost flipped: `create` ~0.008ms but `cleanup`/reset ~0.021ms
— reset is now the bigger half. `reset_non_spellspace_for_pool` + disposing the
prior occupant's per-conduit objects. Profile the reset; trim what a clean
checkout doesn't need. Impact: medium. Risk: low.

### 8. Collapse the meld front door
`Conduit.meld → Meld.meld` is two frames of pure dispatch before any work. A
resolved direct handle (a bound callable the caller keeps) skips both for
repeat melds. Pairs with the seal. Impact: small-medium. Risk: medium (API).

### 9. Verify and fix 3-thread scaling
Off-GIL, melder's throughput should scale ~3× with 3 threads. Run 1- vs
3-thread; if it doesn't scale, find the shared lock (devops registry, gate
controller, transaction mediator). Same root as #2. Impact: potentially large
on multi-thread. Risk: investigative.

### 10. Lazy / lighter `DevopsIdentity`
`DevopsIdentity.__init__` was 3,257 calls (per conduit *and* per spellspace) +
a frame-wide registry attach — cross-thread contention on a shared registry.
Make registration lazy (attach only when something inspects the conduit).
Impact: medium (helps #2's contention too). Risk: medium.

### 11. Share hook maps in lesser conduits
`_snapshot_split_hook_maps_from_configuration` copies hook maps per conduit. A
lesser conduit inherits and never mutates them — take a shared reference to the
parent's maps instead of copying. Impact: small. Risk: low.

### 12. Lightweight `ConduitWard` for lesser conduits
A lesser conduit needs only lineage pointers (parent, root, children); it can't
peer-link or register contracts, so the contract graph / link indices / policy
machinery are dead weight. A `lesser`-mode ward — smaller object, faster pool
reset. Impact: small-medium. Risk: medium.

---

## TIER 3 — conjure-time, smaller, or long-term

### 13. Compose `root_blueprints` DAG-build + socket-overlay
The reachability hoist (done) removed the traversal duplication; the DAG
construction and the path-relative socket overlay are still rebuilt per spell —
~13ms of the conjure `root_blueprints` phase. Profile DAG-build vs
socket-overlay first; the socket overlay is path-relative so composing it is
real surgery. Impact: medium (conjure). Risk: high.

### 14. Hoist the Phase-4 O(N²) cycle strategies
`binding_resolution_cycle_strategy` and `circular_dependency_strategy` rebuild
the whole-spellbook graph inside a per-spell `validate()` — N spells → N builds.
Hoist to once per validation pass (completeness-count guard for correctness).
Impact: small (the `validation` phase is ~1.8ms), mostly allocation/GC. Risk: low.

### 15. Precompute each spell's canonical key at bind
`(frame_key, bind_key)` is immutable after bind but recomputed all over;
`normalize_frame_key`'s `@lru_cache(maxsize=64)` thrashes on high-cardinality
frames. Compute the key once at bind, store on the Spell. Impact: small. Risk: low.

### 16. Faster codegen-signature hashing
`serialize_codegen_signature_part` uses `pickle.dumps` (2,125 calls) feeding
SHA-256 (`HASH.update` 6,774). pickle is slow; use a cheaper deterministic
serialization for signature parts. Conjure-time. Impact: small. Risk: low.

### 17. Share the resolution cache (frame/spellbook scope)
`_input_resolution_cache` / `_spell_id_resolution_cache` are per-`Meld`; fresh
conduits re-resolve. For *by-id* melds this is negligible (resolution is a dict
lookup). For *by-object/by-frame* melds it's heavier (tuple-key build + the
multi-input resolver) — sharing helps those workloads, not the gauntlet.
Impact: workload-dependent. Risk: low (also a memory tidy-up).

### 18. Treat conjure/setup latency as a tracked number
melder setup ~208ms vs competitors ~50ms — the AOT cost. One-time for a static
app, but it's the re-conjure cost in the agentic mutation loop. Items 13-16
feed this; track the aggregate so it doesn't regress.

### 19. Counter for internal, non-durable ids
ULID is the right call where the embedded timestamp is a feature (spells,
conduits — keep it). But purely-internal transaction/creation ids that are
never inspected for time could use `next(itertools.count())` (atomic, ~50×
cheaper). Low priority — pooling already removed the worst ULID churn. Listed
for completeness.

### 20. Composable sub-executors  — long-term, measure first
Root executors calling shared per-node sub-executors so a dependency in many
graphs shares compiled code. Genuine compile-dedup + finer incremental, but it
reintroduces inter-step call overhead — it trades runtime speed (melder's
deep-graph edge) for compile-time savings. Prototype behind the existing
route-dispatch flag and benchmark; do **not** rewrite the executor codegen
blind. Impact: uncertain. Risk: high.

---

## Suggested order

1. **Seal (#1)** — the median 2× gap; do it with #3, #4, #5 folded in (they're
   the same hot path).
2. **TransactionMediator (#2)** + #9 + #10 — the tail and multi-thread scaling.
3. #6, #7 — meld read path and pool reset.
4. #8, #11, #12 — diminishing but cheap.
5. Tier 3 as conjure latency warrants.

After #1-#5, re-profile the hot loop *in isolation* (no import/conjure noise)
and re-rank — the board will have shifted again. Honest projection: #1-#5 put
melder around ~1.5-2.0ms (≈1.3-1.5× dishka); parity is a stretch that needs the
seal to absorb essentially all warm melds.
