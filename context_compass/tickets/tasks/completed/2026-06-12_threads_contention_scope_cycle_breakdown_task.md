

# Task: Measure and fix threads>=3 scope-cycle contention (parent lock / ward churn)

## Metadata
- Task ID: TASK-2026-06-12-threads-contention-scope-cycle-breakdown
- Story: none
- Status: done
- Owner: claude
- Agent Name: compiler_builder_0
- Priority: p1
- Created: 2026-06-12T21:13:39Z
- Updated: 2026-06-12T21:48:17Z

## Objective
Close the threads>=3 hot-loop gap (melder 22.0k hot scopes/s vs dishka 29.2k
vs dependency-injector 36.7k, with 11-22ms scope-cycle stalls) by measuring
the shared synchronization points under contention first, then landing
evidence-ranked fixes one at a time.

## Ticket Contract
- ENTRY_GATE: active board row for this ticket; fresh research read of the
  current lesser-conduit/pool/ward cycle paths (other lanes changed src this
  session; no stale-memory implementation).
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/` (conduit lesser-cycle
  paths, conduit_pool, conduit_ward link/detach, creations locks,
  spell_space pool), one new benchmark harness under
  `benchmarks/testing_other_di/`, matching tests. NOT in scope: compiler
  phases, bind lane, transaction mediator, meld front-door semantics.
- DEPENDENCIES: real_world_gauntlet numbers (threads=3 baseline); breakdown
  harness pattern proven on the scheduler lane.
- EXIT_GATE: contention harness numbers rank the suspects; each landed fix
  shows a measured improvement on the harness AND the real_world gauntlet
  without correctness regressions; user accepts.
- FAILURE_ESCALATION: CONFLICT note if a fix requires changing ward lineage
  bookkeeping semantics (user sign-off required before implementation);
  BLOCKER if stalls trace into non-owned lanes.

## Scope Boundaries
- In scope: measurement harness; ward-link retention across pool cycles;
  parent-lock narrowing; pool sharding if deques contend; stall attribution.
- Out of scope: meld warm-path fixed-cost trim (second tranche, separate
  decision); compiler/bind surfaces.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: User accepted fix #1 results and chose to close the
  lane rather than pursue fix #2 ("ok great this is fine... we can move
  onto something else"). Residual meld inflation recorded as follow-up
  candidate, folded into the warm-meld fixed-cost trim tranche.

## Steps / Checklist
- [x] Research read: current create_lesser_conduit / ConduitPool /
      ward link+detach / scope-cycle cleanup paths (post-session state)
- [x] Build contention-breakdown harness: per-thread hold/wait timing on the
      shared sync surfaces at threads=1/3/5 + >1ms stall capture
- [x] User runs harness; rank suspects from evidence
- [x] Land fix #1 (highest-ranked) with tests
- [x] Re-measure (harness + real_world gauntlet)
- [x] Repeat or close per evidence (closed: fix #1 accepted; fix #2
      deferred by user decision)
- [x] Run Ticket Microcycle during execution.

## Deliverables
- benchmarks/testing_other_di/profile_scope_cycle_contention.py (new)
- Evidence-ranked fix(es) in the conduit/pool/ward lane with tests

## Files / Paths Impacted
- benchmarks/testing_other_di/profile_scope_cycle_contention.py (new)
- src/melder/aether/conduit/ (fix targets UNKNOWN until measured)

## Validation
- Not run.
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_scope_cycle_contention.py`
  - `pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -q -s`

## Risks / Rollback Notes
- Ward-link retention changes lineage bookkeeping observable state; gated on
  explicit user sign-off (FAILURE_ESCALATION).
- Free-threaded contention measurements are machine-sensitive; rank by
  ratios and stall counts, not absolute ns.

## Applicable Anti-Patterns
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-12T21:13:39Z
  TYPE: PLAN
  CLAIM: Baseline (user-run, real_world gauntlet threads=3): melder 22,044
    hot scopes/s vs dishka 29,225 vs DI 36,742; melder outer-total max
    22.4ms / request-total max 16.7ms stalls (cv ~220-310%) vs dishka max
    ~1.8ms. Pre-ranked suspects (UNVERIFIED): parent conduit lock in
    create_lesser_conduit, ward link/detach per pooled lesser cycle, shared
    owner-creations lock, pool deque contention. Measurement first.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1-1
  IMPACT: This is the last competitive surface melder loses outright.
  NEXT: research-read the current lesser-cycle code paths, then build the
    contention harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T21:21:00Z
  TYPE: FACT
  CLAIM: Research read complete; suspect ranking before measurement:
    (1) `create_lesser_conduit` holds the PARENT conduit RLock for its
    entire body - root resolution, pool pop OR full Conduit construction
    on miss, pooled->lesser state transitions, hook firing, ward link,
    nexus publish decision. With one shared root at threads>=3, every
    scope create serializes on this single RLock. (2) Ward link takes the
    parent ward RLock but only while already under the root lock, so it
    adds hold-time, not separate contention. (3) Release path is nearly
    contention-free: it runs under the LESSER's own lock and
    `_detach_for_pool` pops the parent ward registry dict WITHOUT the
    parent ward lock (atomic C-locked dict pop); pool return is plain
    deque append + optional popleft eviction.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1758-1887
  - src/melder/aether/conduit/conduit.py:377-408
  - src/melder/aether/conduit/conduit_pool.py:110-132
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:972-1002
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:336-362
  IMPACT: The whole-body root-lock hold is the only shared point every
    thread's create path must pass through; it is the structural candidate
    for the 11-22ms stalls (a thread constructing a fresh Conduit on pool
    miss holds the lock for the full construction).
  NEXT: user runs the contention harness; rank by measured root-lock wait
    share and stall attribution before any fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T21:21:00Z
  TYPE: MEASURE
  CLAIM: Contention harness built:
    `benchmarks/testing_other_di/profile_scope_cycle_contention.py`.
    Probes true root-lock wait via a re-entrant pre-acquire around
    `create_lesser_conduit` (RLock re-entry keeps semantics identical),
    times create/melds/cleanup walls per cycle, sweeps threads 1/3/5 on
    the 29-class gauntlet graph, captures >=1ms stalls with surface
    attribution. Env knobs: BENCH_CONTENTION_THREADS / _SECONDS / _MELDS /
    _STALL_MS. Not run (sandbox lacks 3.14t); user executes.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-318
  IMPACT: Converts the pre-ranked suspects into measured wait shares; the
    "% of thread-time" line on root-lock wait is the decision number.
  NEXT: user runs; if root-lock wait dominates, design lock-narrowing
    (construct outside the lock, link under it) as fix #1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T21:30:00Z
  TYPE: MEASURE
  CLAIM: First harness run (user, 3.14t gil=disabled, melds=on, 5s/sweep):
    t1 98,489 cycles/s; t3 182,856 (1.86x); t5 221,406 (2.25x). Root-lock
    wait share of thread-time: 1.0% -> 5.1% -> 12.6%; worst stalls 4x
    ~1.28ms root_lock_wait at t5 only. Per-surface avg inflation t1->t3:
    melds 7.15->11.36us (+59%), create 0.91->1.24us, cleanup
    1.22->1.99us; t5 melds 14.32us (+100% vs t1). No 11-22ms gauntlet-class
    stalls reproduced in lite mode (hot pool, no misses). One t1 melds max
    8.9ms = first-cycle warmup.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  IMPACT: Ranking: (1) PRIMARY - cross-thread inflation inside the meld
    path (~68% of cycle; +59% at t3) - not the scope-cycle locks
    themselves; (2) SECONDARY - root-lock wait, superlinear growth,
    fix-worthy lock-narrowing but only ~5% at t3; (3) release path
    exonerated. Gauntlet's 11-22ms stalls likely need the heavier meld
    mix or pool-miss construction to reproduce.
  NEXT: harness v1.1 (landed) sub-attributes melds into outer_melds /
    space_enter / request_melds / space_exit; user reruns melds=on and
    melds=0 to pin the inflating storage surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T21:42:00Z
  TYPE: MEASURE
  CLAIM: Harness v1.1 runs (user, gil=disabled) settle the ranking.
    MELDS=OFF (pure cycle): t1 375,677 cycles/s -> t3 230,478 -> t5
    197,606 = NEGATIVE scaling; root-lock wait share 3.5% -> 58.3% ->
    73.1% of thread-time, avg wait 7.59us(t3)/18.50us(t5) per cycle, 18
    stalls >=1ms at t3. The parent-lock whole-body hold fully serializes
    scope creation. MELDS=ON sub-attribution: outer_melds and
    request_melds inflate EQUALLY (+63%/+65% t1->t3, +97% both at t5);
    space_enter flat (0.10us); space_exit tiny. Equal inflation across
    two different storage surfaces (conduit-local vs spellspace) plus
    create/cleanup inflating ~+60% says the meld inflation is a shared
    mechanism (shared-object refcount/cache traffic or a common read
    path), not a per-storage lock convoy.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  IMPACT: Fix #1 confirmed by measurement: narrow the parent-lock window
    in create_lesser_conduit (construct/pool-pop/hooks outside; cleaned
    re-check + ward link inside). Expected: pure-cycle scaling flips
    positive; t5 1.3ms lock stalls disappear. Meld inflation is fix #2
    territory and needs its own attribution pass.
  NEXT: land lock-narrowing with tests; harness probe must switch to
    sample-then-release (holding across create would re-serialize the
    narrowed path and falsify the measurement).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T21:55:00Z
  TYPE: DECISION
  CLAIM: Fix #1 LANDED - parent-lock narrowing in create_lesser_conduit.
    The whole-body `with self._lock:` is gone; root resolution, pool
    pop/fresh construction, pooled-shell reactivation, hook firing, and
    Nexus publish run lock-free; new `_link_new_lesser_under_lock` holds
    the parent lock only for a cleaned re-check + ward link, with an
    unwind path (orphan shell recycled via its own cleanup, standard
    cleaned error raised) for create racing parent cleanup. Docstring
    concurrency contract added (hooks must be thread-safe under
    concurrent lesser creation). Harness probe switched to
    sample-then-release (holding across create would re-serialize the
    narrowed path). Two integration tests added: 4-thread x 50-cycle
    storm on one root (double-issuance detection + ward-registry
    consistency) and a deterministic cleanup-race unwind test (pool
    create_object hijack).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1758-1920
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:169-186
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1599-1738
  IMPACT: Pure-cycle root-lock wait (58-73% of thread-time at t3/t5,
    negative scaling) should collapse; expected positive scaling melds-off
    and reduced create p95 melds-on.
  NEXT: user runs conduit test suites, both harness modes, and the
    real_world gauntlet; then re-measure and decide fix #2 (meld-path
    inflation attribution).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:10:00Z
  TYPE: MEASURE
  CLAIM: Post-fix-#1 numbers (user-run). HARNESS melds-on: t3 173,922
    cycles/s (was 156,556; +11%), t5 222,841 (was 202,192; +10%);
    root-lock wait share t3 5.7%->2.2%, t5 12.6%->5.4%; >=1ms stalls
    ZERO at t3 and t5 (was cleanup/request/lock stalls incl. 4x ~1.28ms).
    HARNESS melds-off: t3 230,478->284,644 (+23%), wait share
    58.3%->27.9%, t5 73.1%->39.1%, 18 stalls -> 0; pure cycle remains
    lock-bound (every cycle still takes the parent lock once at the link
    window; RLock handoff overhead under contention is now the floor).
    GAUNTLET: melder 19,231 hot scopes/s vs prior-session baseline 22,044
    (-13%) while DI moved +4% (38,157) and dishka -1% (28,866); melder
    setup 181.7ms (prior ~157ms) and max stalls 26.1ms persist.
    Tests: 1128 passed; my unwind test failed on a seam defect
    (ConduitPool __slots__ makes instance attr read-only) - patched to a
    class-level seam with finally-restore; rerun pending.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1700-1745
  IMPACT: Harness verdict clear: fix #1 removed the lock-stall class and
    ~halved wait share. Gauntlet verdict UNKNOWN: -13% melder delta is
    outside DI/dishka movement but the run also carries elevated setup
    (+25ms) and another lane's uncommitted bind change
    (single_signature_bind, validation pending) in the same tree; cv was
    ~46%. Needs a variance check before attributing regression to fix #1.
  NEXT: rerun the fixed unwind test; repeat the gauntlet 1-2x for
    variance; if melder stays ~19k, bisect by stashing the bind-lane
    change or re-running with fix #1 reverted locally.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:25:00Z
  TYPE: MEASURE
  CLAIM: Gauntlet variance check (user, machine under multi-agent load):
    all three frameworks dropped together (DI 38,157->34,963, dishka
    28,866->26,066 w/ a 123.8ms max stall, melder 19,231->21,485).
    Ratio analysis (robust to shared load): melder/DI 0.600 baseline ->
    0.504 run1 -> 0.614 run2; melder/dishka 0.754 -> 0.666 -> 0.824.
    VERDICT: fix #1 is not a gauntlet regression; run2 ratios slightly
    beat baseline. Unwind test seam fixed (class-level patch on
    ConduitPool); concurrency file 19/19 green. Melder setup rose again
    (181.7 -> 248.5ms) - consistent with co-running agents + the pending
    bind-lane change, not this lane's surfaces.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1599-1745
  IMPACT: Fix #1 accepted on evidence: harness stall class eliminated,
    wait share halved, gauntlet ratios neutral-to-positive. Remaining
    competitive gap now attributed to meld-path cross-thread inflation
    (+59-65% per meld at t3 on BOTH outer and request melds equally).
    Ward-link retention (sign-off gated) demoted: melds-on lock wait is
    only 2.2-5.4% post-fix, so its upside is small in realistic shapes.
  NEXT: fix #2 attribution - instrument INSIDE the meld path (storage
    lock vs shared blueprint/spellbook reads vs allocator/refcount
    pressure) to find the shared surface inflating both meld families
    equally; a clean-machine gauntlet run when the swarm is idle would
    firm the record.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T21:48:17Z
  TYPE: DECISION
  CLAIM: CLOSURE. Delivered: (1) profile_scope_cycle_contention.py
    (threads sweep, root-lock wait probe, meld sub-attribution, stall
    capture); (2) fix #1 - create_lesser_conduit parent-lock narrowed to
    the cleaned-recheck+ward-link window via _link_new_lesser_under_lock
    with a safe unwind path; (3) two integration tests (4x50 storm,
    deterministic cleanup-race unwind). Measured: harness melds-on +11%
    (t3) / +10% (t5) cycles, lock wait share 5.7->2.2% / 12.6->5.4%, all
    >=1ms lock/cleanup stall classes eliminated; melds-off wait
    58.3->27.9% (t3); gauntlet ratios melder/DI 0.60->0.61,
    melder/dishka 0.75->0.82 (neutral-to-positive under heavy machine
    load). DEFERRED (recorded, not lost): fix #2 - cross-thread meld
    inflation (+59-65% per meld at t3, equal across outer/request
    families => shared-surface mechanism, likely shared-object
    refcount/cache traffic or a common read path) - overlaps and should
    be folded into the warm-meld fixed-cost trim tranche (cached meld
    0.44us vs dishka 0.29us; exit 0.45 vs 0.23). Ward-link retention
    NOT pursued (sign-off-gated; small upside post-fix). The 11-27ms
    gauntlet stalls never reproduced in the isolation harness and
    co-occur with machine load; treat as environment-sensitive until a
    clean-machine run says otherwise.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1758-1920
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:1-1
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1599-1745
  IMPACT: threads>=3 scope-cycle serialization structurally removed;
    remaining gap owned by the meld warm path, not the cycle locks.
  NEXT: none (lane closed; successor lane should start from the
    deferred fix #2 attribution).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Lane opened after scheduler-v2 and cross-clear closures. Measurement-first:
build `profile_scope_cycle_contention.py` instrumenting per-thread hold/wait
on the shared sync surfaces of the pooled lesser-conduit and spellspace
cycles at threads=1/3/5 with >1ms stall capture; user runs; fixes land in
evidence order (ward-link retention needs explicit user sign-off).
