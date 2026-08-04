# Adaptive (Profile-Guided) DI Optimizer — Design

- Status: draft / design-only (no implementation without explicit signoff + patch-framework gating)
- Author lane: compiler_strategy_0
- Created: 2026-06-13
- Updated: 2026-06-13 (added §11 storage mechanism + §12 consolidated build checklist)
- Scope: opt-in, config-gated adaptive specialization of meld runtime executors

---

## 1. Idea (in one line)

An opt-in mode that **observes real resolution behavior over a process's lifetime**, then
**re-emits leaner meld executors biased to the observed common case**, guarded so that a
wrong guess only costs speed (deopt to the generic path), never correctness.

This is profile-guided optimization / speculative specialization with deoptimization — the
JIT / inline-cache playbook (cf. CPython PEP 659's specializing adaptive interpreter, V8 ICs),
applied at the **DI-resolution layer** the interpreter's specializer cannot see into.

Property the design must preserve (non-negotiable):
> A wrong speculation is a **slow path**, never a wrong result.

---

## 2. Key finding: most of the machinery already exists

The runtime already ships a monomorphic **inline cache with generation-guard deopt** — the
fast-meld-door lane. We are *extending* it, not building a JIT from scratch.

Evidence (current `src/melder`):

- `aether/conduit/meld/conduit_meld.py:~196-245` — `self._fast_meld_doors` caches
  `(door_spell, captured_context, fast_creations, captured_epoch)` per spell id, with a
  live-read guard ladder:
  - `not self._meld_hooks`
  - `door_spell._door_epoch == captured_epoch`   (generation guard)
  - `door_spell._creation_context is captured_context`  (context-identity guard)
  - `not self._spellbook._spellbook_validation_required`
  - on any miss → fall through to the normal lane, which rebuilds the entry in place.
- `aether/spellbook/spell.py:369` — `self._door_epoch: int = 0`; bumped at `:573` (hook gate
  change) and `:592` (`_cleanup_creation_context`, covers context clear + switch reset).
- `aether/conduit/meld/meld.py:631`, `aether/spellbook/spellbook_creation_system.py:944` —
  additional `_door_epoch += 1` invalidation chokepoints (conjure/rebuild path).
- The executor slot (`captured_context._no_overrides_executor`) is **re-read live per hit**,
  never captured — because phase-11 hydration hot-swaps the slot cold→hot on first execution
  (`creation_context.py` self-replacing slot contract). That hot-swap is also our **install
  primitive** for a re-specialized executor.
- nogil note: the guard ladder was deliberately collapsed to one int-compare to cut
  shared-line traffic ("2.6x/4.2x pure-door inflation at threads=3/5") — so the guard cost is
  already nogil-tuned.

Net: generation guard ✅, deopt ✅, hot-swap install ✅, cache entry store ✅, nogil-tuned
guard ✅. All present and proven.

---

## 3. What the optimizer adds (the novel work)

1. **Config flag (opt-in).** New typed property on `SpellbookConfiguration`
   (`available_properties` registry + fluent setter), default **off**. The warmup/profiling
   tax means short-lived processes should never pay it; long-lived runtimes (FasterAPI
   servers, persistent runtime) amortize it to nothing — that is exactly where the EV lives.
2. **Profiler / interceptor.** While enabled, record per-call-site resolution outcomes:
   for each dependency socket of each emitted lane, did it resolve to a **reused** store
   instance or a **freshly constructed** one, and how stably (count + last-seen). This is the
   only genuinely new always-on cost; it runs during the learning window.
3. **Specialization decision.** After N stable observations, choose a biased fast body:
   - dep observed **always-absent / always-constructed** (`many`/transient) → emit
     direct-construct, drop the reuse-lookup machinery (this is the *sound* slice — a fresh
     object has no shared state to race on).
   - dep observed **always-present** (shared lifetime) → emit a direct store/closure read —
     **only if** the guard problem in §4 is solved for that case.
4. **Re-emit + install.** Reuse the codegen-creation compiler infra to build the specialized
   executor; install it by hot-swapping the context slot and bumping `_door_epoch` so existing
   `_fast_meld_doors` entries deopt and re-capture the new lane.
5. **Extended guard ladder.** See §4 — the one real new correctness problem.

---

## 4. Correctness centerpiece: guard coverage

The existing `_door_epoch` guards **structural** invalidation of the *consumer* spell's door
(hooks, context rebuild, conjure, mutation). It does **not** cover the truth of a *profiled
assumption about a dependency*.

Concrete gap: speculate "dep B is present in store S". `_door_epoch` of the consumer A does
not bump when B's **instance** is cleared from S by a *different* scope's cleanup (e.g.
`Creations.clear_all` / `reset_for_pool` on B's owner scope). So an A-fast-body that assumes
"B present" can read a now-empty slot with A's epoch unchanged → **stale read** → wrong result.
That violates the non-negotiable property.

Three candidate guards (pick per assumption class; cost vs soundness):

| option | guard | sound against | cost | gap |
|---|---|---|---|---|
| A. multi-spell epoch | also capture `B._door_epoch`; compare | B door rebuild / mutation / context clear | +1 int compare | does **not** cover B store-clear (clear_all doesn't bump B's door epoch today) |
| B. store generation | add a generation counter to `Creations`; bump on add/clear; capture+compare | B store mutation incl. clear | +1 int compare + new counter on hot store ops | new field on a hot path; needs nogil-safe bump/read |
| C. cheap presence-confirm | one `creations.get_creation(B_id) is not None` | everything (re-reads live) | one dict-get (still ≪ full resolution) | not "zero check", but cheapest sound option |

Likely answer is a **hybrid keyed by existence class**:
- transient/`many` deps (`always-absent`): **no extra guard** — direct construct is
  unconditionally sound (no shared state).
- shared-lifetime deps whose lifecycle is structurally tied to the consumer's door: **option A**
  (multi-spell epoch), free and sound.
- shared-lifetime deps that can be cleared independently: **option C** (presence-confirm) until/
  unless **option B** (store generation) is judged worth a counter on the hot store ops.

This table is the actual design decision and the thing to pressure-test before any code.

---

## 5. nogil considerations

- Guard reads must stay live single-int compares (match existing lane discipline); avoid adding
  multi-field guards that re-introduce shared-line traffic the current design fought off.
- Any new counter (option B) needs a defined visibility/ordering story under free-threading:
  cleared-instance write must *happen-before* a guard that could observe staleness, or the
  guard must be the authoritative live read (option C is trivially correct here).
- Cache **install** races: two threads re-specializing the same door concurrently — funnel
  through the existing context-replacement chokepoint (`_cleanup_creation_context` bumps epoch),
  so last-writer-wins + epoch bump deopts the losers. Reuse, don't reinvent.
- Profiler writes (counters) are per-call-site shared state; use the cheapest correct counter
  (relaxed increments are fine — profiling is advisory, never a correctness input).

---

## 6. Scope, risk, rollout

- It is a **subsystem**, not a tweak: profiler + specialization policy + re-emit + extended
  guard. But it rides existing primitives (epoch, hot-swap, fast-door cache), so it's tractable.
- **Default off.** Behind the config flag. A regression in the optimizer cannot touch
  default-path users.
- Shared-worktree discipline: build it as **additive** code paths gated by the flag; do not
  mutate the default fast-lane semantics. Profiler and specialized bodies live in new modules.
- Warmup tax is the JIT warmup; acceptable and opt-in.

---

## 7. Validation plan (benchmarking-first)

Before committing to build:
1. Pick a representative graph (the 29-class gauntlet + a shallow-pure-DI-heavy synthetic).
2. Hand-write one specialized fast body for a known "dep always present" case + its option-A/C
   guard.
3. Micro-bench: current fast-meld-door lane vs the speculated lane, single-thread and at
   threads=3/5 (the nogil contention regime), on the real free-threaded interpreter.
4. Decision gate: the speculated lane must beat the current fast lane by a margin that clears
   profiler-warmup amortization at a realistic reuse count. If it doesn't, the guard cost ate
   the win and we stop.

All numbers come from the user's 3.14t target (sandbox is 3.10, melder won't import there).

---

## 8. Open questions (for review)

1. Guard policy per existence class — confirm the §4 hybrid, or pick one uniform guard.
2. Is a `Creations` store-generation counter (option B) acceptable on the hot store ops, or do
   we cap ambitions at options A + C?
3. Profiling granularity: per spell, per (spell, conduit), or per dependency socket? Finer =
   better specialization, more memory + more counters.
4. Specialization trigger threshold + hysteresis (avoid thrash between specialize/deopt).
5. Does the optimizer specialize only no-overrides lanes first (the dominant hot path), with
   overrides lanes left generic?

---

## 9. Explicit gates

- This document is **design only**. No source edits to the meld/codegen/cache machinery without:
  - explicit user signoff on the §4 guard policy, and
  - patch-framework artifacts (system-impacting: touches meld doors + codegen emit + config),
  - default-off flag so the change is non-invasive to existing users and the other worktree lanes.

---

## 10. Converged Architecture & Implementation Plan

This section supersedes the high-level sketch above where they differ; it records the design
the owner and compiler_strategy_0 converged on in session.

### 10.1 Scope refinement
- **Primary target: the singleton (non-`many`) reuse path.** Singletons are the common shape
  *because* users want reuse, so the hot reuse-lookup is where the cycles are. The transient/
  `many` direct-construct case is *sound but low-value* (a transient already just constructs) —
  deprioritized. The value and the difficulty live in the same place: the singleton-present
  speculation needs the careful guard.
- The optimizer is a **runtime feedback loop that feeds the existing processor (phase 9)**, not
  a new conjure phase. No "phase 12" in the scheduler.

### 10.2 The runtime record (the linchpin)
- A **marshal-safe spell-behavior snapshot** emitted at runtime. Designed once, does triple
  duty: (a) the **decoupling interface** between the observe half and the codegen half, (b) the
  **profile artifact** the profile strategies fold, (c) the **cache payload** later.
- It MUST be a frozen snapshot, never a live reference, so the processor fuses a stable view and
  the feedback cycle cannot become a moving-target / oscillation problem.

### 10.3 Non-intrusive integration — the optimizer doors
- New `OptimizerConduitMeld` / `OptimizerSpellSpaceMeld`: subclass the default doors and **fully
  override only the hot `meld()` entry** to weave in observation; inherit every cold helper
  unchanged. The default `ConduitMeld` / `SpellSpaceMeld` are **never touched or subclassed into
  overhead**.
- **Construction-time selection** by the config flag (read ONCE when the conduit builds its
  door), never a per-meld branch. This is the only thing that *guarantees* zero-overhead-when-off
  (a runtime flag read is itself nogil shared-line traffic on a path tuned to avoid exactly that).
- **Differential test (non-negotiable):** same workload through both doors → identical results
  (instance identity, registration, disposal, error behavior). Locks the invariant that the
  optimizer changes *speed only, never results*, and catches duplication drift immediately.

### 10.4 Component inventory (converged)
NEW unless marked REUSED.
1. Config flag + tuning knobs (threshold, hysteresis, max-specializations, granularity).
2. Optimizer meld doors (observation; construction-selected).
3. Runtime record (marshal-safe snapshot) + a thread-safe profile store.
4. **Profile strategy registry** — `ProfileStrategy` contract + `ProfileStrategyBuilder`,
   mirroring the existing strategy-builder pattern. Pluggable observation/analysis
   (DependencyPresence, CallFrequency, ScopeStability, ...). This is where new optimization
   *ideas* plug in.
5. Profile-aware **processor strategy** (phase 9) that loads the record and fits specialization
   candidates onto `SpellCodegenModel` — a second input alongside the analyzer graph.
6. Specialization **trigger/policy** (threshold + hysteresis → convergence, no thrash).
7. **Speculative codegen family** (`strategies/speculative/`: strategy/state/steps/compilers/
   manifest/hydration + discovery + planner) — mirrors solo/generalized; *also* the "new family
   outside generalized/many/solo."
8. **Guard infrastructure**: guard emitters (close-over instance + `_door_epoch` compare +
   deopt-to-generalized) AND the one hard task — completing `_door_epoch` coverage so EVERY
   instance-clear/replace path bumps the epoch (audit + extend the existing invalidation protocol).
9. Install / deopt — REUSED: hot-swap the context executor slot + bump `_door_epoch`; deopt to
   the generalized body on guard miss.
10. Persistence — REUSED machinery, DEFERRED: speculative manifest emitted as a **new manifest
    family the existing cache already carries** (like solo/many_only), runtime-upserted via
    `upsert_spell_payload`. No cache-internals change. The runtime snapshot is the profile
    payload.
11. Diagnostics — surface what got specialized, guard hit/miss, deopt counts, reasons (likely via
    the dev-ops information registry). A PGO system you can't see into can't be trusted or tuned.

### 10.5 Correctness invariants
- The optimizer changes **speed only, never results** (enforced by the differential test).
- Singleton guard = close-over instance + `B._door_epoch == captured_B_epoch`; one int compare;
  deopt to the generalized resolve on miss. Sound under nogil (worst case: both threads deopt to
  the locked resolve).
- The epoch must be a **complete** invalidation signal for the dependency *instance* (§4 gap:
  store-clear without an epoch bump). Closing that is the core correctness work.
- Feedback-cycle convergence guaranteed by snapshot fusion + trigger hysteresis.

### 10.6 Staged iterative build (the plan spine)
Each stage is independently valuable, independently testable, default-OFF, additive, and
**parkable**. The default path stays byte-for-byte unchanged throughout.

- **Stage 0 — Decider (~1 day, no core edits).** Hand-roll one singleton guarded no-overrides
  body + its epoch guard; throwaway micro-bench vs the generalized resolve at threads=1/3/5 on
  the 3.14t target. **GATE: it must beat the existing path by a margin clearing warmup.** If not,
  STOP — the ticket stays parked and we spent a day, not two weeks.
- **Stage 1 — Record + optimizer doors.** Define the marshal-safe runtime record; build the
  optimizer doors (observation only, no specialization). Measure learning-window overhead.
- **Stage 2 — Processor fusion + profile strategies.** Profile-aware processor strategy loads the
  record; `ProfileStrategy` registry folds it into model candidates. Verify the enriched model
  carries the right candidates. No codegen yet.
- **Stage 3 — Speculative family + guard.** Emit the guarded bodies; complete `_door_epoch`
  instance-clear coverage; manual respecialize trigger. **GATE: correctness — deopt matrix
  (mutation / transfer / cleanup / store-clear, concurrent) + the differential test pass.**
- **Stage 4 — Closed loop.** Automatic trigger (threshold + hysteresis) + hot-swap install.
  **GATE: measured end-to-end speedup on a long-lived reuse workload; default path unaffected.**
- **Stage 5 — Persistence + diagnostics (the only stage near caching).** Speculative manifest as
  a new sibling cache family (runtime upsert); diagnostics surface. Skippable if long-lived
  processes make cross-restart warm-start unnecessary.

### 10.7 Governance / worktree discipline
- Default OFF; additive modules only; default doors and cache internals untouched.
- Stages 3+ are system-impacting → require patch-framework artifacts + owner signoff on the §4
  guard policy before any edit lands.
- The differential test and the deopt matrix are non-negotiable gates for any stage that emits or
  installs a speculated body.

### 10.8 Decisions needed from owner (per gate)
- §4 guard policy (per-existence-class hybrid) — before Stage 3.
- Profiling granularity (spell / spell+conduit / dep-socket) — before Stage 2.
- Trigger threshold + hysteresis values — before Stage 4.
- Whether to build Stage 5 persistence at all (skippable for long-lived processes).

---

## 11. Storage mechanism: the `__optimizations__` cache (Stage 5 concretized)

Concretizes the Stage-5 persistence sketch in §10.10. The earlier note ("a new manifest family the
existing static bundle carries") is **refined** to a **physically separate optimization cache**, for
clean separation and a tidy two-tier lookup. Still additive; the static cache internals are untouched.

### 11.1 Physical layout
- A **second `CachingSystem` instance** rooted at a sibling `__optimizations__/` tree
  (`__melder_cache__/__optimizations__/<frame>/<conduit>.<suffix>`), reusing the existing class
  unchanged — no new cache engine.
- **One bundle file per conduit**, mirroring the static layout (`cache_root / frame / conduit`).
- The static bundle stays byte-for-byte as-is. Lookup is **two-tier**: optimization cache first
  (when the optimizer is ON), static bundle as the floor/fallback.

### 11.2 Manifest shape (polymorphic)
- Payload is **nested**: `spell_id -> { variation_sha256 -> speculative_manifest }`.
- `spell_id` tier = **free source-invalidation**: `spell_id` is already a sha256 source fingerprint,
  so a binding/source change mints a new id and orphans all stale variations.
- `variation_sha256` tier = **polymorphic inline caching**: one specialized body per observed shape.
  The hash is over the **specialization signature** — the profile facts that produced the body (which
  deps were observed present/absent, the existence classes, the chosen guard set). Identical observed
  shapes reuse one entry; a genuinely different shape mints a new variation.
- Entries are **value-only / marshal-safe** (dataclass value-only rule): ids, hashes, existence tags,
  guard descriptors, and the marshalled code payload — never live objects.

### 11.3 Polymorphism cap (megamorphic fallback)
- A spell's variation map is **capped at K** (default ~4, V8-style). On the K+1th distinct shape, stop
  specializing that spell and **pin the generalized executor**.
- Hitting the cap is a correct outcome ("too polymorphic to speculate"), not a failure. It keeps the
  cache **bounded** and learning **convergent** instead of megamorphic blow-up.

### 11.4 In-memory marker (the "already done" check)
- A per-process set of `(spell_id, variation_sha256)` already specialized = both the **dedup** (don't
  re-specialize/re-write a known shape) and the fast **"already optimized this"** check.
- Same two-level pattern the runtime already uses: in-memory hot + disk persistent (cf.
  `_fast_meld_doors`). The marker bounds write work to the **specialization count**, not the meld count.

### 11.5 Write / flush cadence
- **Write** to the in-memory manifest per **new specialization** (cheap, lock-guarded). Already-warm
  shapes hit the marker and write nothing.
- **Flush** to disk on a cadence, **never per meld**: flush when `dirty_count >= flush_every_n`
  (configurable) **OR** on shutdown/`atexit` **OR** after `T` seconds dirty — whichever first. All three
  are **no-ops when clean**.
- Count **new specializations** (dirty events), not raw melds, so the cadence **self-quiesces**: once
  learning converges, `dirty_count` stops advancing and flushes stop. The shutdown + time backstops
  catch the tail so the last sub-`flush_every_n` specializations are not lost.

### 11.6 Concurrency / lock isolation (nogil)
- Optimization-cache writes take **their own lock** and stay **out of the meld read path** and **out of
  the Transaction Admission Plane** (readers/meld never enter that plane — `src_components.md`:
  Transaction Admission Plane). The learning run may be slow; the default and warm read paths must not be.
- The write lock is only ever contended by concurrent **new** specializations (bounded, rare once warm),
  never by hot reads.

### 11.7 Warm-start (consume on the next run)
- On the following run with the optimizer ON, load the conduit's `__optimizations__` bundle; for a
  melding spell, match the observed shape's signature -> `variation_sha256` -> install that speculated
  body as the executor (epoch-guarded, hot-swap install per §10.9).
- No match, or a guard deopt at runtime, -> fall to the generalized body and re-profile. The cache is an
  accelerator, never an authority.

### 11.8 Relationship to §10 and open knobs
- Refines §10.10 (persistence) and is the substance of **Stage 5** (§10.6). Still the only stage near
  caching; still **skippable** for long-lived single-run processes (warm in-memory suffices).
- Open values for owner: **K** (polymorphism cap), **flush_every_n**, **T** (time backstop).
- Unchanged invariant: speed-only, never results. A stale/mismatched variation deopts; it cannot return
  a wrong instance.

---

## 12. Consolidated build checklist & current status (durable recall)

Single-glance map of the whole effort, its stages, and where it sits today.

**Identity.** Opt-in PGO specialization of the singleton-reuse meld tail. = **trim #2** on the active
ticket (warm-tail singleton specialization, epoch-invalidated). Default OFF, additive, parkable.

**New doors (locked decision).** `optimizer_conduit_meld` + `optimizer_spellspace_meld`, selected at
**construction time**, not a runtime branch. Existing `conduit_meld` / `spellspace_meld` untouched.
OFF -> current doors, zero added cost.

**Stages (from §10.6, storage in §11):**
- Stage 0 — Decider micro-bench on 3.14t. GO/NO-GO gate. **NOT STARTED — this is the immediate next move.**
- Stage 1 — Runtime record + optimizer doors (observe only).
- Stage 2 — Processor fusion + `ProfileStrategy` registry.
- Stage 3 — Speculative codegen family + guard ladder + `_door_epoch` instance-clear coverage (the one
  hard correctness task). GATE: deopt matrix + differential test.
- Stage 4 — Closed loop (auto trigger + hot-swap install). GATE: measured end-to-end speedup.
- Stage 5 — Persistence (§11 `__optimizations__` cache) + diagnostics. Skippable.

**Decisions owed before edits (§10.8 + §11.8):** §4 guard policy (before Stage 3); profiling
granularity (before Stage 2); trigger threshold + hysteresis (before Stage 4); K / flush_every_n / T
(Stage 5); whether to build Stage 5 at all.

**Always-on constraints.** Additive only; cache internals untouched; default-OFF/opt-in; raise before
touching the tuned caching; thread-safety paramount (3.14t nogil); wrong speculation = slower never
wrong; no build/trim from hypothesis (owner runs benchmarks on the 3.14t target).

**Cross-references.**
- Active ticket: `tickets/tasks/2026-06-13_executor_construction_lane_trim_task.md`
  (trim #1 landed; trim #2 = this, design-gated).
- Future-direction story:
  `tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md`.
- Parked adjacent: `tickets/tasks/2026-06-13_skip_dead_overrides_plan_build_task.md`.

**Immediate next action.** Stage 0 decider micro-bench — hand-roll one singleton-guarded body + epoch
guard, micro-bench vs the generalized resolve at threads 1/3/5 on the 3.14t target. Nothing else gets
built until that number clears warmup amortization.
