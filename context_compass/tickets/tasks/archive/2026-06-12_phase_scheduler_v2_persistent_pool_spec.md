# Task: PhaseScheduler v2 — Persistent Pool, Latch Barriers, Chunking, Phase Fusion (Spec)

## Metadata
- Task ID: TASK-2026-06-12-phase-scheduler-v2
- Status: spec_review
- Owner: user
- Created: 2026-06-12
- Depends on:
  - Existing revert note in `phase_scheduler.py` (~L535): inline workers==1
    execution is forbidden; "the correct shape is a persistent
    scheduler-lifetime worker, not inline execution." This spec is that shape.

## Measured context
- Cold conjure (29 classes, workers=1): ~25ms; warm cache full-hit: ~11.5ms
  (phases 8-11 ≈ 14ms of cold conjure).
- Persistent shallow_all threads=10: melder setup 262.6ms vs dishka 37.5ms.
- Earlier profile: ~60% of warm conjure is thread spawn/join coordination.
- Per conjure today: 3 scheduler lifecycles (structural 1-4, foundational 5-7,
  plan 8-11) x workers (default 5) = 15 thread spawns + 15 sentinel/joins.
  Every meld-time lazy revalidation pays another full lifecycle.
- Unit shape: one UnitOfWork per spell per phase. 29-spell graph ≈ 320
  Future+RLock objects per conjure, 11 barrier waits over per-unit futures,
  units average ~150µs (sync cost is the same order as the work).

## Cross-spell read map (evidence)
Derived from `spell_compiler/phases/compiler_phase_*.py`:
- Phase 1 (requirements): no spellbook-wide reads. Per-spell independent.
- Phase 2 (symbolic graph): no spellbook-wide reads. Per-spell independent.
- Phase 3 (local frame/DAG): `_iter_all_spells` over live `_spell_id_pool`
  at 4 sites. FRAME-GLOBAL; hard barrier before and after.
- Phase 4 (validation): no spellbook-wide reads in the phase file; strategy
  internals read bind-time-static metadata (e.g., duplicate-name scans), not
  concurrently mutated phase artifacts. Per-spell parallel, barrier after.
- Phases 5/6/7: `run_frame_wide` + pool reads + change control. FRAME-GLOBAL
  group; keep current structure.
- Phases 8/9/10/11: no spellbook-wide reads; each consumes the same spell's
  prior artifact (root blueprint -> occurrence analysis -> model -> plan ->
  creation). Per-spell independent ACROSS the whole sequence.
- Residual verification before D lands: full read of phase 2 and phase 8
  `run()` bodies to confirm no shared mutable args are threaded through
  factories. (Initial grep clean; final check is part of implementation.)

## Design

### A. Persistent worker pool (lifecycle inversion)
1. The pool becomes scheduler-lifetime and the scheduler becomes
   Spellbook-lifetime: one `PhaseScheduler` owned by the Spellbook, created
   lazily on first phase run, cleaned in Spellbook cleanup (sentinels +
   joins move from per-conjure to per-spellbook teardown).
2. `SpellbookCreationSystem` stops constructing per-group schedulers; all
   three conjure groups and every revalidation borrow the owned scheduler.
   `phase_scheduler_cls` patch-point seams stay intact.
3. Runs become the disposable thing: each `run_all_phases` call gets a fresh
   per-run `CancellationEventSignal`; phase registry is per-run (registered,
   executed, cleared). Public registration/run API shape preserved.
4. Worker loop: blocking `queue.get()` (no 100ms poll). Workers exit on
   sentinel only. Workers stop reading scheduler-level cancel state; their
   only cancellation involvement is the per-unit cancel event already
   carried by UnitOfWork. The control thread (caller) keeps sole ownership
   of barrier timeout / external-cancel responses, satisfying the revert
   note's control contract.

### B. Latch barriers (build what is consumed)
1. Per-phase countdown latch: `remaining` counter + one `threading.Event` +
   lock-guarded error list. Workers decrement after each unit; the last
   decrement sets the event. Control thread waits on ONE event with the
   barrier timeout instead of `concurrent.futures.wait()` over N futures.
2. UnitOfWork keeps its Future surface (result()/exception() inspection
   contract unchanged for callers) but: the per-instance RLock leaves the
   execution hot path (a unit is built by the control thread, executed by
   exactly one worker, inspected only after the barrier — thread confinement
   by construction; documented, mirroring the spellspace lane rationale).
3. Timeout / external cancel semantics preserved exactly: latch timeout =>
   trip run cancel signal, set_exception on undone units, raise
   PhaseTimeoutError; unit failure => fail-fast at latch, cancel run,
   set_exception pending, raise PhaseExecutionError.

### C. Chunked dispatch (batch, not stream)
1. `_build_per_spell_phase_units` partitions spells into at most `workers`
   chunks; one UnitOfWork per chunk. Inside a chunk, per-spell callables run
   sequentially with per-spell error capture `(spell_id, exc)`; a chunk
   failure carries the full per-spell error payload so PhaseExecutionError
   attribution stays per-spell.
2. 29-spell graph: 11 phases x <=5 chunks ≈ 55 units/conjure instead of
   ~320; queue handoffs and wakeups drop proportionally.

### D. Phase fusion (delete barriers the data contract does not require)
1. Fuse 1->2 per spell: one unit runs requirements then symbolic graph for
   one spell. One barrier deleted.
2. Keep: barrier -> 3 (frame-global) -> barrier -> 4 (per-spell parallel)
   -> barrier. The 3|4 boundary stays for now (strategy internals read other
   spells' static metadata; safe but not fusion-proven).
3. Keep 5-7 frame-wide structure unchanged.
4. Fuse 8->9->10->11 per spell: one unit runs the whole plan sequence for
   one spell. Three barriers deleted; the dominant cold-conjure group
   (~14ms) becomes embarrassingly parallel per spell. Existing eligibility
   gates (`_is_spell_plan_phase_eligible`, existing-creation bypass) wrap
   the fused unit unchanged.
5. Failure semantics: a spell failing mid-sequence skips its own remaining
   fused steps; the group still fail-fasts the run via the cancel signal and
   raises PhaseExecutionError. (Slightly better isolation than today, where
   a phase-9 failure also cancels other spells' 10/11 work mid-flight.)

## Tradeoffs / risks (stated, not hidden)
- Idle cost: `workers` parked threads per live Spellbook (blocking get; zero
  CPU). Teardown churn moves to Spellbook cleanup. Acceptable for the
  per-spellbook model; revisit frame-level sharing only if multi-spellbook
  density becomes a real workload.
- Abandoned-unit semantics on timeout match today's behavior (thread may
  stay busy past abandonment); a stuck unit now occupies a pooled worker for
  the next run instead of leaking a dying thread. Run-id stamping on units
  keeps stale completions from touching newer latches.
- Chunking changes intra-phase failure timing (later spells in a failed
  chunk see the cancel event at their pre-run check); cross-spell ordering
  inside one phase was never contractual.

## Validation plan
- Unit (tests/unit/.../synchronization/): pool persistence across runs;
  per-run cancel isolation (run N cancel does not poison run N+1); latch
  timeout raises PhaseTimeoutError with pending set_exception; chunk error
  attribution carries per-spell payloads; sentinel-only shutdown; cleanup
  idempotence.
- Component: conjure artifact equivalence fused-vs-unfused on a mixed-graph
  spellbook (artifact identity checks per spell); revalidation reuses the
  same pool (thread ids stable across runs).
- Integration: existing conjure/meld integration suites must pass unchanged.
- Benchmarks (user-run): profile_bind_conjure_cycle.py cold/warm at
  workers=1 and 5; persistent shallow_all setup column at threads=10;
  real_world gauntlet setup. Targets: cold conjure setup meaningfully below
  29ms at workers=5; threads=10 setup moving toward the dishka 37ms class.
  Measured results: Not run.

## Rollout order
1. A+B together (pure scheduler + creation-system borrow path), all tests.
2. C (chunking) — mechanical once B's latch carries error payloads.
3. D (fusion) — after the residual phase-2/8 body verification; compiler
   agent gets a heads-up since phases are his lane (scheduler consumes, he
   produces; fusion only changes the consumption grouping, not phase code).
4. User runs benchmarks; numbers decide whether adaptive worker count
   (workers = f(spell count)) is worth a follow-up.

## Implementation status (2026-06-12)
All four steps landed in one pass (user-approved). Files:
`phase_latch.py` (new), `phase_scheduler.py` (rewrite), `unit_of_work.py`
(+`run_for_scheduler`), `spellbook.py` (owned scheduler slot + lazy accessor
+ cleanup-first teardown), `spellbook_creation_system.py` (borrow path,
chunk helpers, fused `requirements_symbolic` + `plan_group` factories).

Deviations from spec, with rationale:
1. Run-id stamping was replaced by a stronger mechanism: every queued item
   carries its own `(unit, latch)` pair, so an abandoned run's stragglers
   physically cannot reach a newer run's barrier. No id comparison needed.
2. A contract-preserving post-scan of stored unit exceptions was added on
   clean latch completion: the historical barrier collected exceptions from
   DONE futures (covers units handed in pre-failed); workers skip done
   units, so the latch alone would silently succeed for that case.
3. Phase-2/8 residual verification completed before fusion landed: phase 2
   reads only the same spell's `artifact._requirements` and "does not
   mutate the Spell"; phase 8's `spellbook`/`spell_system_states` params
   are documented unused compatibility arguments.
4. Behavior note: `cancel()` issued BETWEEN runs is forgotten when the next
   run installs its fresh scope (the one-shot scheduler had no
   between-runs state, so no existing contract is broken).
5. Chunk failure raises the FIRST failing spell's original exception
   unchanged (no wrapper type), preserving exception-type matching for
   upstream consumers; the chunk unit's metadata carries the spell-id list
   for attribution.

Validation: unit suites updated/added (scheduler v2 persistence/isolation/
clearing/teardown, latch, run_for_scheduler, chunk helpers). Execution of
the suites and all benchmarks: Not run.
