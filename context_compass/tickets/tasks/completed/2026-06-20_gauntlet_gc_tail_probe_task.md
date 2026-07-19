

# Task: Add GC tail-spike probe to real_world_gauntlet

## Metadata
- Task ID: TASK-2026-06-20-gauntlet-gc-tail-probe
- Story: none (standalone)
- Status: closed (orphan sweep 2026-07-11, melder_0, owner-directed:
  refactor_0 does not exist; the INSTRUMENTATION delivered - the
  off-by-default gc.callbacks probe + GAUNTLET_GC_MODE toggle live in
  test_real_world_gauntlet.py; the 3-mode attribution run was never
  performed, so the ~98ms churn-spike question stays UNKNOWN/dormant -
  the probe is ready whenever anyone cares to run it)
- Owner: cowork
- Agent Name: refactor_0
- Priority: p2
- Created: 2026-06-20T10:37:11Z
- Updated: 2026-06-20T10:37:11Z

## Objective
Attribute the ~98ms per-cycle max spike seen in the melder churn run of
`test_real_world_gauntlet.py` to GC (or rule it out) with direct, measured
evidence, via an opt-in, off-by-default instrument that does not perturb the
baseline numbers and is applied symmetrically to all three libraries.

## Ticket Contract
- ENTRY_GATE: active board row routing to this ticket under agent_name refactor_0.
- EXECUTION_BOUNDARY: `benchmarks/testing_other_di/test_real_world_gauntlet.py`
  only (additive helper + `_run_gauntlet_benchmark` instrumentation). No changes
  to `src/melder`, no changes to the object graph, per-lib ops, or the measured
  code path when the probe is off.
- DEPENDENCIES: mirrors the existing `GcBucketMonitor` pattern in
  `test_persistent_runtime_gauntlet.py`.
- EXIT_GATE: file compiles; probe is off by default; user runs the three modes
  on the no-GIL `.venv_new` build and the spike cause is evidenced.
- FAILURE_ESCALATION: if the probe perturbs baseline numbers or cannot attribute
  the spike, record a CONFLICT/BLOCKER note.

## Scope Boundaries
- In scope: env-gated GC pause recorder (gc.callbacks) + gc disable/freeze
  toggle around the measured loop; one `[lib] gc probe ...` output line.
- Out of scope: any `src/melder` change; any fix (gc.freeze in the runtime,
  threshold tuning) — those are separate, approval-gated tasks.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user approved adding the probe to test the GC-pause thesis.

## Steps / Checklist
- [x] Read harness (`_run_gauntlet_once`, `_run_gauntlet_benchmark`) to place probe.
- [ ] Add `_GcPauseProbe` helper (gc.callbacks, thread-safe totals/max/per-gen).
- [ ] Wrap the measured loop with env-gated probe + GC mode toggle, restore in finally.
- [ ] Syntax-validate (`py_compile`).
- [ ] Hand user run commands for the three modes; interpret their output.

## Deliverables
- Off-by-default GC probe + `GAUNTLET_GC_MODE` (normal|disabled|frozen) toggle in
  `test_real_world_gauntlet.py`.

## Files / Paths Impacted
- benchmarks/testing_other_di/test_real_world_gauntlet.py

## Validation
- Not run (benchmark). The full gauntlet requires the no-GIL `.venv_new` build,
  competitor libs, and ~8 minutes; it cannot be reproduced in the agent sandbox.
- Recommended commands (user-run, on .venv_new):
  - normal+probe: `GAUNTLET_GC_PROBE=1 GAUNTLET_GC_MODE=normal pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -s`
  - gc disabled:  `GAUNTLET_GC_PROBE=1 GAUNTLET_GC_MODE=disabled pytest ... -s`
  - gc frozen:    `GAUNTLET_GC_PROBE=1 GAUNTLET_GC_MODE=frozen pytest ... -s`
- Syntax: `python -m py_compile benchmarks/testing_other_di/test_real_world_gauntlet.py`

## Risks / Rollback Notes
- gc.callbacks adds trivial overhead only when probe is on; off-by-default keeps
  the baseline byte-identical. Rollback = revert the single file.
- GC mode + freeze state is restored per-lib in `finally` so it cannot leak
  across the three-library run in the same process.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from UNKNOWN or HYPOTHESIS.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Notes
- DATETIME: 2026-06-20T10:37:11Z
  TYPE: HYPOTHESIS
  CLAIM: The 98ms churn max is most likely a gen-2 GC pause (heaviest allocator
    of the three, biggest heap to scan), possibly compounded by per-iteration
    thread spawn jitter; not per-cycle teardown (avg teardown ~0.002ms).
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1178-1260
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1438-1441
  IMPACT: If GC, gc.freeze() of the stable runtime graph is a real p-max lever.
  NEXT: implement the off-by-default probe + mode toggle; user runs three modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T10:40:00Z
  TYPE: FACT
  CLAIM: Probe implemented: `_GcPauseProbe` (gc.callbacks, thread-safe) plus
    `GAUNTLET_GC_PROBE` and `GAUNTLET_GC_MODE` (normal|disabled|frozen) wrap the
    measured loop in `_run_gauntlet_benchmark`, restored per-library in finally;
    off-by-default so baseline numbers are unperturbed and the probe applies to
    all three libraries symmetrically. Authoritative file reads complete and
    well-formed end-to-end.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1340-1453
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1568-1602
  IMPACT: Probe ready; the attribution run is user-side on the no-GIL build.
  NEXT: user runs the three modes; compare probe pause_max to cycle max.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T10:40:00Z
  TYPE: RISK
  CLAIM: Independent syntax check NOT obtained in-sandbox. The bash mount is a
    stale/truncated mirror (wc -l=1582, tail cut mid-line at 1583) versus the
    authoritative file-tool view (full through ~1719). py_compile there fails on
    the truncated mirror, not the real file. Validation stays "Not run" pending a
    user-side py_compile.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1580-1602
  IMPACT: Must not claim a passing compile; user confirms syntax on their machine.
  NEXT: user runs `python -m py_compile <file>` (exit 0 = good) before the 8-min run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-20T11:00:00Z
  TYPE: MEASURE
  CLAIM: GC RULED OUT as the churn tail-spike cause (user-run, 5k iters, no-GIL
    3.14t). normal: probe collections=0, pause_max=0.000ms, yet melder cycle
    max=43.4ms. disabled: max=41.99ms (spike persists with GC off). frozen:
    max=40.16ms (the 1 collection / 6.82ms is the explicit pre-freeze collect,
    not a loop event). melder total ~unchanged across modes (13.86/13.98/13.90s)
    -> GC is not a factor in melder churn cost or tail. Incidental: zero
    automatic collections during the loop = deterministic cleanup keeps the GC
    threshold from tripping (supports the cleanup thesis).
  EVIDENCE:
  - user-run terminal output normal/disabled/frozen, 2026-06-20
  IMPACT: tail spike is NOT GC; gc.freeze() is not the lever here.
  NEXT: pursue lock-contention hypothesis (below) via thread sweep + profiler.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T11:00:00Z
  TYPE: HYPOTHESIS
  CLAIM: Tail spike is lock contention / thread serialization on melder's
    shared frame-level state during concurrent scope churn. Evidence: melder
    outer_total max ~24ms while same-cycle create=0.96ms / cleanup=0.24ms are
    sub-ms (time spent stalled mid-cycle, not allocating/tearing down); melder
    threaded-phase max ~30ms vs di 3.3ms / dishka 5.3ms under identical
    per-iteration 3-thread spawn (melder-specific in-cycle stall).
  EVIDENCE:
  - user-run terminal output normal mode, 2026-06-20
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1178-1260
  IMPACT: contention at 3 threads is a risk for the 50-thread concurrency pitch;
    tail may worsen with more threads. This is the axis the product bet rests on.
  NEXT: thread-count sweep (3/10/20/50) + py-spy sampling of a stalled cycle, or
    a lock-acquire timing probe around conduit/spellspace locks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T12:10:00Z
  TYPE: FACT
  CLAIM: "normal" mode genuinely runs with automatic GC enabled -- nothing
    disables it globally. grep of all *.py: src/melder has ZERO
    gc.disable/freeze/set_threshold; the only such calls in the gauntlet file
    are this probe's own mode branches (gc.disable at disabled-mode, gc.collect
    +gc.freeze at frozen-mode), both gated and not run when gc_mode=normal. No
    conftest disables gc. So the prior collections=0 reading was NOT a
    gc-was-off artifact.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1502-1507
  - grep gc.(disable|set_threshold|freeze|set_debug): src/melder = no hits
  IMPACT: removes the strongest "you did it wrong" failure mode for the GC verdict.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T12:12:00Z
  TYPE: FACT
  CLAIM: Added a callback-independent cross-check to the probe: snapshot
    CPython's own per-generation collection counters via gc.get_stats() before
    and after the measured loop, print the delta plus gc.isenabled() alongside
    the probe's callback count. If the gc.callbacks count and the get_stats
    delta disagree, the callback missed events (e.g. worker-thread collections
    under no-GIL) and the GC verdict is re-opened; if both read zero, GC idle is
    confirmed by two independent mechanisms. New helper `_gc_stats_delta_text`
    parses OK in isolation; full-file py_compile still blocked by the stale
    truncated sandbox mirror (cut at line 1588), so user runs py_compile.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1444-1469
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1509-1519
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1551-1558
  IMPACT: turns the GC verdict from "trust one callback" into a two-counter
    agreement check; no src/melder change, off by default.
  NEXT: user py_compiles, re-runs the three modes; compare callback count vs
    get_stats delta per library.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-20T12:40:00Z
  TYPE: MEASURE
  CLAIM: GC DEFINITIVELY RULED OUT -- two independent counters agree. 25k-iter
    normal run, gc_enabled=True, all three libs: probe gc.callbacks count=0 AND
    CPython's own gc.get_stats delta=+0 (g0/g1/g2 all +0). The callback the user
    doubted is corroborated by the interpreter's own tally. Yet melder cycle
    max=63.651ms vs di 6.879ms / dishka 6.976ms on the identical harness. The
    spike is NOT work: melder worst outer cycle=23.887ms while outer_create
    max=1.136ms and outer_cleanup max=0.261ms -> ~22ms is pure mid-cycle STALL.
    Localized to the threaded phase (melder max 41.581ms vs di 6.59 / dishka
    6.61). Rare (melder p99=5.279ms, median 2.552ms ties dishka; total 66.79s ~=
    dishka 66.29s). di/dishka are the control: same per-iter thread spawn, no
    stall -> the stall is melder code under concurrency, not harness/OS/GC.
  EVIDENCE:
  - user-run terminal output 2026-06-20, mode=normal, 25k iters
  IMPACT: closes the GC line for good; confirms a melder-specific, concurrency-
    only, rare tail stall consistent with lock contention on shared locked state.
  NEXT: free thread sweep via DI_GAUNTLET_THREADS=1 then =2 (cap is 1..3, no code
    change). threads=1 = no concurrency = no contention possible: if the 60ms
    spike vanishes at 1 and grows 1->2->3, contention is confirmed; if it
    persists at 1, contention is refuted and the cause is elsewhere.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T13:10:00Z
  TYPE: RAISE
  CLAIM: METHOD GAP owned -- all prior verdicts used order-independent whole-run
    aggregates (median/p95/p99/max/total collections) that CANNOT show
    degradation-over-duration; get_stats was sampled only at endpoints. Added
    per-window time-series instrumentation: GAUNTLET_TREND_WINDOWS=N splits the
    run into N windows, snapshots gc.get_stats() collections + gc.get_count()
    heap pressure AT each window boundary DURING the loop, and reports per-window
    iter med/p99/max, threaded p99/max, gc_coll delta, live counts, and wall
    time after. Logic validated standalone on synthetic drift data (median
    climbs across windows, injected stalls land in the right windows, gc_coll
    stays +0 per window). Off by default; benchmark-only; no src/melder change.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1453-1460 (env knob)
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1535-1546 (loop init)
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1556-1568 (boundary snap)
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1573-1606 (report)
  IMPACT: turns "is it GC" (answered: no) into "does the run drift, for whom,
    and does any signal track it" -- the question the duration moat actually
    needs. Per-window gc_coll also makes the GC ruling-out time-resolved.
  NEXT: user py_compiles + runs GAUNTLET_TREND_WINDOWS=10 (normal+probe);
    read whether di/dishka iter med/wall climb w01->w10 vs melder flatter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-20T14:05:00Z
  TYPE: MEASURE
  CLAIM: Per-turn run (25k iters, normal, no-GIL) resolves the spike at
    per-iteration granularity. GC: turns_with_collection=0/25000 for ALL three;
    every slowest-15 turn reads gc_during=no -> GC not in any slow turn. HEAP:
    gen0_live FLAT first10%==last10% (di 3667, dishka 10007, melder 3283;
    melder min3273/max3283) -> no accumulation/drift for anyone. SHAPE: slow
    turns are bursts of CONSECUTIVE turns, not back-loaded -> no progressive
    degradation in this churn workload. melder worst=63.675ms is TURN 0 (cold
    start, == overall max), after which median ~2.75ms ~= dishka; melder's next
    cluster is turns 4705-4717. dishka bursts ~10786 & ~21024. di max ~5.9ms.
  EVIDENCE:
  - user-run terminal output 2026-06-20 (GAUNTLET_PER_TURN_GC=1)
  IMPACT: closes GC AND heap-accumulation as drift mechanisms for the churn
    benchmark; reframes melder's headline 63ms as one-time warmup, and the
    mid-run bursts as GC-/heap-clean (OS scheduler / allocator jitter, unproven).
    The duration-degradation claim is NOT demonstrated by this workload.
  NEXT: port the per-turn instrument (GC incidence + gen0_live drift) into
    test_persistent_runtime_gauntlet.py -- the workload where competitor
    degradation was actually observed -- to test the moat claim with per-turn
    evidence. Pending user go (separate benchmark file; additive, no src/melder).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Probe is diagnostic only. Confirming the cause does not authorize a runtime fix;
any gc.freeze()/threshold change in `src/melder` is a separate approval-gated
task. User runs the three modes on the no-GIL build; compare probe `pause_max`
to the cycle `max` to confirm/deny GC attribution.
