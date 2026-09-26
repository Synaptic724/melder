

# Task: Measure what causes Melder's long-run gauntlet drop (retained state vs process effects)

## Metadata
- Completed: 2026-09-26T08:32:04Z
- Closure Basis: owner directed turn-in 2026-09-26 ("turn in the tickets related to this").
- Summary: 2x2 controls attributed the long-run slowdown to the harness keeping ints allocated by
  exited worker threads (Melder and dishka alike, zero GC); owner chose array('q') storage.
- Task ID: TASK-2026-09-26-measure-melder-long-run-attribution
- Epic: EPIC-2026-09-26-melder-long-run-throughput-truth
- Status: done
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T00:34:00Z
- Updated: 2026-09-26T08:32:04Z

## Objective
Run the gauntlet's Melder cycle under controlled conditions in a CPython 3.14 free-threaded sandbox
copy of the current working tree, and attribute the long-run drop: retained objects/memory per cycle,
fresh-thread churn vs persistent threads, GC pause growth, and the effect of running after the other
two libraries in the same process.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("Make an epic and hunt down the truth"); board row routes here.
- EXECUTION_BOUNDARY: Sandbox copy of src/ and benchmarks/testing_other_di (snapshot taken
  2026-09-26T00:31Z); probe scripts and results under artifacts/melder_long_run_growth_20260926/.
  No src/ edits.
- DEPENDENCIES: T1 source reads (which structures to count); 3.14.0rc2 free-threaded sandbox.
- EXIT_GATE: Each measured cause recorded as MEASURE with method and caveats; attribution stated.
- FAILURE_ESCALATION: BLOCKER if the sandbox cannot run the gauntlet; DECISION_REQUEST if the
  verdict needs owner-machine runs.

## Scope Boundaries
- In scope: object counts, tracemalloc, gc callbacks, per-thread state counts, pool sizes, timing shape.
- Out of scope: absolute throughput claims for the owner's machine; src fixes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Opened under the epic on owner direction 2026-09-26.
- from_state: in_progress
- to_state: review
- transition_reason: Attribution established by controlled 2x2 runs; owner decision and owner-machine
  confirmation pending.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in 2026-09-26; ticket moved to completed.

## Steps / Checklist
- [x] Confirm the sandbox runs the Melder gauntlet lane on the snapshot.
- [x] Measure retained objects per cycle under fresh-thread churn and under persistent threads.
- [x] Measure GC collections/pauses over a long run and whether pauses grow with iterations.
- [ ] Measure Melder alone vs Melder after dependency-injector and dishka in one process (sandbox
      reclaimed mid-run; superseded by per-library A/B controls - see Notes).
- [x] Record attribution and hand exact owner-run commands over.
- [ ] Run Ticket Microcycle during execution.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- MEASURE notes with method, interpreter, cores and caveats.
- Probe scripts and outputs under artifacts/melder_long_run_growth_20260926/.

## Files / Paths Impacted
- artifacts/melder_long_run_growth_20260926/ (new)

## Validation
- Sandbox runs recorded in Notes and artifacts/melder_long_run_growth_20260926/runs/.
- Owner-machine runs: Not run.

## Risks / Rollback Notes
- 3.14.0rc2 on 2 cores differs from the owner's 3.14 on an i9-13900K; counts transfer, speed does not.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Acceptance criteria reviewed with user and confirmed (owner turn-in)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_long_run_growth_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: owner acceptance of the epic verdict

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Long-run attribution of Melder's gauntlet drop.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:34:00Z
  TYPE: FACT
  CLAIM: Sandbox ready: CPython 3.14.0rc2 free-threading build, 2 cores, 7 GB, with pytest 9.1.1,
    dishka 1.10.1, dependency-injector 4.49.1. Snapshot of src/, benchmarks/testing_other_di and
    pyproject.toml taken from the working tree at 2026-09-26T00:31Z (includes uncommitted slot-guard
    changes). The tarball was left at Claude outputs/melder_1_scratch/ in the repo (owner may delete).
  EVIDENCE: pyproject.toml:10-10
  IMPACT: Object-growth measurements can run now; timing is shape-only.
  NEXT: Run the Melder gauntlet lane on the snapshot to confirm it executes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-26T00:40:00Z
  TYPE: MEASURE
  CLAIM: The gauntlet's real Melder lane (test_melder_gauntlet._build_runtime_melder driven by
    test_real_world_gauntlet._run_gauntlet_once, 3 fresh threads per iteration) runs on the sandbox
    snapshot: setup 1.98 s, 200 iterations in 0.89 s (~14.6k scope cycles/s on 2 cores, -X gil=0).
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-305
  IMPACT: Growth probes can reuse the exact harness functions instead of a re-implementation.
  NEXT: Probe retained objects per iteration under fresh-thread churn vs persistent threads.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-26T00:52:00Z
  TYPE: MEASURE
  CLAIM: No retained growth in the gauntlet's Melder lane. Probe (warm 500 iterations, then gc.collect
    and a full gc.get_objects() type census every 2,000 iterations, 10,000 iterations = 650k scope
    cycles): fresh-thread churn (30k threads) GC-tracked objects 98,721 -> 97,226 (flat after 6k),
    sys.getallocatedblocks +314..+332 (flat), RSS flat; persistent 3 threads: objects 98,869 ->
    97,377, blocks +293..+310, RSS flat. Throughput per window flat in both modes (churn 13.8-14.0k
    cycles/s; persistent 30.7-32.3k cycles/s). Only probe-owned objects (Counter, list) grew.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_melder_gauntlet.py:146-205
  IMPACT: A Melder memory leak is ruled out for this lane at the object and allocator level; the
    long-run drop must come from something that grows with iterations outside Melder. Separate
    finding: the same cycles run 2.3x faster on persistent threads than with 3 new threads per
    iteration, so thread churn dominates the harness cost on this box.
  NEXT: Run the full three-library harness long enough to see per-window drift, with the GC probe on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T01:13:00Z
  TYPE: MEASURE
  CLAIM: Full shared harness in the sandbox (100k iterations, GAUNTLET_GC_PROBE=1,
    GAUNTLET_TREND_WINDOWS=10), dependency-injector leg: ZERO garbage collections over 100k iterations
    (gc.callbacks and gc.get_stats agree), gen0 live count 9,034 -> 9,052. Sandbox throughput is
    6,518 hot scopes/s with window wall times varying 73-134 s at constant work, so sandbox timing is
    noise-dominated (2 shared cores, 3 worker threads + churn) and is not used for rate comparisons.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1487-1600
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1370-1467
  IMPACT: dependency-injector's objects are freed by reference counting alone, so the free-threaded
    collector never runs during its leg. Any cost that scales with GC passes cannot touch it. Whether
    Melder's leg triggers collections is the next question.
  NEXT: Read the dishka and Melder legs of the same run for collection counts and pause growth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T01:18:00Z
  TYPE: MEASURE
  CLAIM: A full gc.collect() on 3.14t costs ~22 ns per retained int held in lists, linear in count:
    0 entries 0.4 ms; 0.95M 15.6 ms; 4.75M 68 ms; 9.5M 152 ms; 19M 420 ms (sandbox, 3 samples each).
    The harness keeps 393 ints per iteration per library for the whole leg (3 iteration lists + 65
    cycles x 6 lane metrics) = 39.3M at 100k, freed only when the leg returns. Owner-run corroboration:
    every library's cleanup (which ends in gc.collect() while those lists are still alive) scaled
    1.92-1.95x from 50k to 100k (DI 134.6 -> 262.0 ms, dishka 257.5 -> 495.6 ms, Melder 318.7 ->
    614.3 ms); DI's cleanup is essentially that one pass, so one pass at 100k costs ~260 ms there.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1753-1766
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:745-750
  - benchmarks/testing_other_di/test_melder_gauntlet.py:295-305
  IMPACT: Every automatic collection during a leg gets more expensive as that leg runs, purely from
    the harness's own sample lists. A library that triggers collections pays a cost that grows with
    iteration count; one that never triggers them (DI in the sandbox) pays none.
  NEXT: Get Melder's and dishka's collection counts and pause maxima from the running full harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T07:12:00Z
  TYPE: MEASURE
  CLAIM: Same full-harness sandbox run, dishka leg: also ZERO collections over 100k iterations, yet its
    10k-iteration windows slowed from 61 s to 150 s by window 3 and 178-190 s for windows 6-10 (~3x)
    at identical work; median iteration 5.6 -> 18.4 ms. dependency-injector's windows drifted
    ~74 s -> ~126-134 s over the last three. The sandbox was reclaimed during the Melder leg, so that
    leg has no data. Neither drift can come from GC passes (none ran) or from Melder.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  IMPACT: Long legs of this harness slow down for libraries that never collect, on this machine. The
    candidates are what grows during every leg regardless of library: the ~39M retained sample ints
    (allocated on the 300k short-lived worker threads) and process memory. Run-order and sandbox
    noise stay open as secondary factors.
  NEXT: Controlled run per library: discard samples vs retain them (harness-identical) vs retain
    copies made on the main thread; per-window cycles/s, CPU per cycle, GC counts, RSS.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T07:17:48Z
  TYPE: MEASURE
  CLAIM: Controlled A/B, dishka lane through the harness's own _run_gauntlet_once (40k iterations, 8
    windows, fresh sandbox container). Discarding samples: flat 18.1-19.0k cycles/s, 71-74 us CPU per
    cycle, RSS 45 MB, 0 collections for all 8 windows. Retaining them exactly as the harness does
    (worker-allocated ints extended into run-long lists): 8.3k -> 6.2k -> 5.5k cycles/s and 143 ->
    195 -> 227 us CPU per cycle over the first three windows, RSS 146 -> 343 MB, still 0 collections.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  IMPACT: The harness's sample retention alone makes every cycle progressively more CPU-expensive,
    with no garbage collection involved, and for a library that is not Melder. The long-run drop is a
    property of the measuring harness on free-threaded CPython, not of the library under test.
  NEXT: Finish the Melder discard/retain runs and the main-thread-copy control (same probe).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T07:40:49Z
  TYPE: MEASURE
  CLAIM: Melder lane, same probe (40k iterations, 8 windows), three modes. DISCARD: 13.5-14.4k
    cycles/s, 99-106 us CPU/cycle, RSS 76 MB, 0 collections, flat. RETAIN (harness-identical,
    worker-allocated ints): 7.6k -> 5.9k -> 4.7k ... 4.4k cycles/s, 167 -> 214 -> 275 ... 329 us
    CPU/cycle, RSS 187 -> 938 MB, 0 collections. COPY (identical retained count and RSS growth, but
    each int re-created on the main thread; worker originals freed each iteration): 13.1k, 12.4k,
    11.0k, 10.5k, 12.6k, 14.1k, 13.2k, 14.7k cycles/s, 96-125 us CPU/cycle, 0 collections - no trend.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  - benchmarks/testing_other_di/test_melder_gauntlet.py:146-205
  IMPACT: The slowdown is not heap size and not GC. It needs the retained objects to have been
    allocated by the worker threads that then exit, which the harness does 3x per iteration
    (perf_counter_ns deltas computed on the worker, kept for the whole leg). Melder triggers zero
    collections and its cycle cost is flat when the harness does not keep worker-allocated ints.
  NEXT: Finish the persistent-thread control (retain without thread exit), then write the verdict.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T07:51:20Z
  TYPE: MEASURE
  CLAIM: Persistent-thread control (same lanes, 3 long-lived threads, workers allocate the same
    ints, main thread keeps them exactly as the harness does; 40k iterations, 8 windows). Melder:
    discard 31.6-32.8k cycles/s, 50-53 us CPU/cycle; retain 30.8-32.0k, 51-53 us, RSS 191 -> 956 MB -
    no trend. dishka: discard 42.3-48.6k, 35-40 us; retain 42.1-46.7k, 36-39 us - no trend. dishka
    copy under churn: 15.9k, 13.8k, 13.5k, 12.4k, 14.9k, 15.5k, 15.2k, 15.5k - no sustained trend
    (retain under churn went 8.3k -> 4.4k).
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  IMPACT: Completes the 2x2. Slowdown appears only when BOTH hold: the harness keeps objects that
    worker threads allocated, AND those threads exit (3 per iteration). Keeping the same data without
    thread exit, or with thread exit but main-thread-owned copies, stays flat. Separately, thread
    churn alone roughly doubles CPU per cycle for both libraries versus persistent threads.
  NEXT: Write the attribution verdict; validate the new retention tests in the sandbox.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T08:05:19Z
  TYPE: DECISION
  CLAIM: Attribution: the long-run slowdown is caused by the shared harness, not by Melder. Its
    per-leg sample lists keep ~393 ints per iteration that were allocated on worker threads which
    then exit (3 per iteration); on free-threaded CPython 3.14 that makes each later cycle costlier
    (Melder 167 -> 329 us CPU/cycle; dishka 143 -> 318 us over 40k iterations) with zero collections.
    Discard, main-thread copies, and persistent threads each remove the trend. Mechanism inside
    CPython (per-thread allocator heaps left behind by exited threads) is a HYPOTHESIS: CPython
    source not read. Owner-machine shape (DI/dishka drop early, Melder late) is UNKNOWN until the
    attribution test runs there.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1545-1600
  - context_compass/artifacts/melder_long_run_growth_20260926/README.md:1-40
  IMPACT: Long-run gauntlet numbers for every library are depressed by the harness in proportion to
    run length; 50k vs 100k comparisons measure the harness as much as the libraries.
  NEXT: Owner decision below; owner runs the attribution test on his machine.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T08:05:19Z
  TYPE: DECISION_REQUEST
  CLAIM: Harness fix, not implemented (out of this epic's boundary). Options: (a) have workers keep
    samples in array('q') per lane and extend run-long array('q') storage on the main thread - same
    values, same summaries, no int objects outliving their threads (recommended; smallest change in
    _run_gauntlet_once and _run_gauntlet_benchmark); (b) keep lists but re-create the ints on the main
    thread (measured flat, but ~1.5 GB per leg at 100k); (c) streaming summaries (exact
    count/sum/min/max, approximate percentiles) - changes reported p95/p99 semantics.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1186-1285
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1288-1345
  IMPACT: Without a fix, any gauntlet run long enough to matter penalises libraries by run length and
    thread churn rather than by their own cost.
  NEXT: Owner picks an option; a separate owner-approved ticket implements it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T08:10:44Z
  TYPE: DECISION
  CLAIM: Owner chose option (a) ("yeah fix everything"): array('q') sample storage in the harnesses.
    Implementation routed to TASK-2026-09-26-fix-gauntlet-sample-storage-and-melder-lane-isolation.
  EVIDENCE: context_compass/tickets/tasks/2026-09-26_fix_gauntlet_sample_storage_and_melder_lane_isolation_task.md:1-20
  IMPACT: Closes this task's DECISION_REQUEST.
  NEXT: Implementation proceeds in the fix task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Opened 2026-09-26 under EPIC-2026-09-26-melder-long-run-throughput-truth; review since 2026-09-26T08:05:19Z.
Harness attribution established (2x2 controls); owner decision on a harness fix pending.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
