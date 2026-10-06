

# Task: Find why the real-world gauntlet's numbers change when the library order changes

## Metadata
- Task ID: TASK-2026-09-30-investigate-gauntlet-order-dependence
- Story: none; standalone investigation of the benchmark harness (read-only until the owner picks a fix)
- Related lane: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md (melder_2; same gauntlet)
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-30T12:03:51Z
- Updated: 2026-09-30T15:40:12Z
- Completed: 2026-09-30T15:40:12Z
- Closure Basis: owner turn-in in chat (2026-09-30) of every finished lane: "yeah turn in the [lanes] you
  finished please, go ahead".
- Summary: The shared gauntlet ran dependency-injector, dishka and Melder one after another in one free-threaded
  process, and each run left thread start/exit slower for the next (a later slot ran 5-12% slower in the VM),
  so the order changed the ranking. Owner-picked option 1: the pytest wrapper runs each library in its own
  process (runner --lib), prints medians over REAL_WORLD_GAUNTLET_ROUNDS rotated rounds, and the runner with
  no arguments keeps the old layout; 14 contract tests. Benchmark-only; no source changed.

## Objective
Owner report (chat, 2026-09-30): "its weird when I reorder this benchmark it changes can you look into this?",
with three pasted runs of `benchmarks/testing_other_di/test_real_world_gauntlet.py`, all in the order
dependency-injector -> dishka -> melder (transcribed in the artifact `owner_runs_20260930.md`). Find, with
measurements, why a library's result depends on where it sits in the run order; separate that effect from
same-order run-to-run noise; recommend a harness change that makes the three-way comparison order-independent.
No src change. A harness change only after the owner confirms it.

## Ticket Contract
- ENTRY_GATE: this ticket's board row routes here; the harness structure is noted before any probe runs.
- EXECUTION_BOUNDARY: read-only in `benchmarks/testing_other_di/` (the runner, `test_real_world_gauntlet.py`,
  `melder_gauntlet_support.py`) and in `src/` where a builder's state matters. Probe scripts and logs go under
  `artifacts/gauntlet_order_dependence_20260930/`; runs happen in the VM mirror of the tree. No edit to `src/`,
  `tests/` or the benchmark files without the owner's confirmation and a NOTICE to melder_2.
- DEPENDENCIES: melder_2's gauntlet_runtime_speed lane (same harness); the closed tickets
  `tickets/tasks/completed/2026-09-27_persistent_gauntlet_fairness_review_task.md` and
  `tickets/tasks/completed/2026-09-26_attribute_gauntlet_tail_spikes_task.md`.
- EXIT_GATE: the order effect's cause stated as FACT/MEASURE with run tables (per order, repeated), the
  same-order noise band stated, a DECISION_REQUEST naming the recommended harness change; status review.
- FAILURE_ESCALATION: BLOCKER if the VM cannot run all three libraries; DECISION_REQUEST before any harness edit;
  CONFLICT if a finding contradicts the fairness review's conclusions.

## Scope Boundaries
- In scope: state one library leaves for the next inside one process (heap and GC state, allocator, caches,
  threads, imports), process warmup, CPU/thermal drift, noise; per-order measurements; a harness recommendation.
- Out of scope: Melder src changes; making any library faster; runs on the owner's Windows machine (the VM is
  measured; the owner may re-run a probe there).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: option 1 implemented and validated (2026-09-30T12:51:46Z): isolation tests red before, green after;
  wrapper, runner modes and CSV checked in the VM; LLM/asset checks OK. Earlier: draft -> in_progress
  (12:03:51Z), in_progress -> review (12:26:39Z), review -> in_progress on the owner's pick (12:39:02Z).
- from_state: review
- to_state: done
- transition_reason: (2026-09-30T15:40:12Z) owner turn-in in chat; option 1 accepted as built, with the owner's own
  30,000-iteration default kept.

## Steps / Checklist
- [x] Note the harness structure (runner order, one child process, per-library build/measure/cleanup).
- [x] Read `_run_gauntlet_benchmark`, the three builders' cleanup, `_run_gauntlet_once` and the GC probe; note
      what state survives from one library to the next.
- [x] Confirm the VM environment runs all three libraries.
- [x] Measure: each library first vs last in one process (repeated), and each alone in a fresh process.
- [x] Measure the heap/GC state entering each library.
- [x] Note the cause (MEASURE/FACT) and the same-order noise band.
- [x] DECISION_REQUEST with the recommended harness change.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.
- [x] On the owner's pick: NOTICE to melder_2, implement the harness change, verify isolated numbers.

## Deliverables
- Evidence-backed notes: cause, measurements, noise band, recommendation.
- Probe scripts and run logs under `artifacts/gauntlet_order_dependence_20260930/`.
- Option 1 as picked by the owner: the shared gauntlet measures every library in its own process.

## Files / Paths Impacted
- benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py (`--lib`, `--round`, `--result-json`)
- benchmarks/testing_other_di/test_real_world_gauntlet.py (isolation helpers, per-turn CSV helpers, wrapper)
- benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py (new, 14 contract tests)
- benchmarks/testing_other_di/benchmarks.md (section on the run modes and the order bias)
- llm_support/ (regenerated: "other" corpus)

## Validation
- Ran (VM, 3.14.7t, -X gil=0): the unmodified runner once at 300 iterations; order_probe.py over the full order
  matrix (2 state-probe rounds at 1000 iterations, 3 plain rounds at 3000); mech_probe.py (6 scenarios x 3,
  plus 2 long runs).
- After the change: the 14 isolation tests (red on the pre-change files, green after); the pytest wrapper at
  300/200/3000 iterations with 1-3 rounds and the CSV on; the runner's all-in-one and --lib modes; LLM
  bundles and build assets --check OK. On the owner's Windows machine: Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py -q`
  - `pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -s` (add REAL_WORLD_GAUNTLET_ROUNDS=3 for
    medians)

## Risks / Rollback Notes
- The VM has 2 cores against the owner's machine: absolute numbers differ; only the order effect's direction
  and size carry over, and the owner may need to confirm on Windows.
- A harness change breaks comparability with older baselines; any change keeps a way to reproduce the old
  layout.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No causal claim from a single run: an order claim needs repeats and the same-order noise band beside it.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_order_dependence_20260930/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the owner's turn-in of this ticket.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-30T12:03:51Z
  TYPE: MEASURE
  CLAIM: The owner's three pasted runs all ran dependency-injector -> dishka -> melder (config: gil=disabled,
    5000 iterations, 3 threads). Same-order spread (max/min - 1) is already 6.0% for dependency-injector, 4.9% for
    dishka and 9.1% for melder (melder 6454 -> 6784 -> 7041 ms), and every library slowed from run 1 to run 3.
    Melder's per-iteration max is 10.4-10.9 ms in every run against 2.6-3.9 ms for the others; melder setup is
    317-366 ms against about 40 ms. No reordered run was pasted, so the order effect itself is not yet measured.
  EVIDENCE: context_compass/artifacts/gauntlet_order_dependence_20260930/owner_runs_20260930.md:1-23
  IMPACT: Any order effect must be shown larger than this noise band before it is called an effect.
  NEXT: Note the harness structure from the runner and the pytest entry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T12:03:51Z
  TYPE: FACT
  CLAIM: The gauntlet runs all three libraries back to back in ONE child process, in the fixed order
    dependency-injector, dishka, melder. `test_real_world_gauntlet` spawns `real_world_gauntlet_gil_runner.py` once
    (`-X gil=0` when forced) and waits for it; the runner's `main()` loops over that tuple, calling
    `_run_gauntlet_benchmark(lib, cfg)` and printing each result before the next library starts. Reordering the
    tuple therefore changes what each library inherits from the ones that ran before it in the same interpreter
    (heap, allocator and GC state, imports, a warm CPU), not only its place on the clock.
  EVIDENCE:
  - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py:23-34
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:2197-2234
  IMPACT: The three totals are not independent samples; whatever a library leaves behind is charged to the
    libraries after it.
  NEXT: Read `_run_gauntlet_benchmark` whole and the three builders' cleanup; list what survives a library.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T12:06:30Z
  TYPE: FACT
  CLAIM: What one library leaves for the next inside the runner's process (read whole: the benchmark driver, the
    iteration, the three builders' setup and cleanup).
    - Setup is `_build_ops` + `spawn_singletons`. Each builder imports its own library inside itself
      (`pytest.importorskip`, `from melder.aether...`), so a library's import always lands in its own setup,
      whatever its position.
    - The loop runs `cfg.iterations` calls of `_run_gauntlet_once`, and each call starts one NEW thread per lane
      (3 at the default config) behind a barrier and joins them: 15,000 short-lived threads per library at 5,000
      iterations.
    - `finally` restores the GC posture, then calls `ops.cleanup()`; its time is printed as `cleanup=` and is not
      in the totals.
    - Inherited by the next library: every module imported so far; for dependency-injector and dishka, nothing
      they own once cleanup reset/closed the container, `gc.collect()` ran and `ops` went out of scope (whether
      every object built on their worker threads is freed is UNKNOWN); for Melder, a NEW `Aether()` with its six
      hosted roots, which cleanup constructs right after the reset and which lives to the end of the process; and
      whatever allocator and heap state 15,000 exited threads left behind.
    - Nothing isolates one library from the next except the GC posture restore.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1757-2066
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1460-1559
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:788-793
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1017-1019
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1067-1079
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1254-1262
  IMPACT: What ran before can change a library's measured loop only through process state: the imports, the
    live Aether that Melder leaves, the heap and allocator, the GC's counters and thresholds.
  NEXT: Record the candidate mechanisms, then plan the measurement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T12:06:30Z
  TYPE: HYPOTHESIS
  CLAIM: Candidate mechanisms, ranked by prior evidence:
    - H1, process-wide thread-exit cost. The tail task measured on 3.14t that a short-lived thread's exit+join
      grows with live objects allocated by threads that have already exited (bare interpreter 98-100 us; 650 us
      after one worker left 100k live instances; 4.2 ms at 300k) and that it differs by library world (DI
      338-347 us, dishka 500-514, Melder 659-677). The gauntlet pays that cost 3 times per iteration, so any
      worker-thread objects an earlier library leaves alive would slow every later library. The harness itself
      already hit this once (worker-thread int objects kept in lists, 2-2.5x slower over 40k iterations).
    - H2, heap and GC state: a library that runs after Melder does so with Melder's package and a live Aether in
      the heap. The tail task saw no collection fire inside the loop in the default order; other orders are
      unmeasured.
    - H3, warm-up and drift: the first library pays first-touch page faults and CPU ramp-up; later ones pay any
      thermal drift. The owner's same-order runs spread 5-9% and all three libraries slowed from run 1 to run 3,
      which is drift that no order explains.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-26_attribute_gauntlet_tail_spikes_task.md:314-345
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:523-550
  - context_compass/artifacts/gauntlet_order_dependence_20260930/owner_runs_20260930.md:22-23
  IMPACT: H1 predicts that a later position costs more per iteration, by an amount set by what the earlier
    library left alive, and that the extra shows up in the threaded phase, not in the timed scope cycles. H3
    predicts a position effect that does not depend on which library came before.
  NEXT: Measure (PLAN below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T12:06:30Z
  TYPE: PLAN
  CLAIM: Measurement in the device VM, no tree edit:
    1. Check the VM mirror's harness matches the device tree and that the 3.14t environment has dishka and
       dependency_injector.
    2. An order driver (artifact) that imports the harness module and calls `_run_gauntlet_benchmark` for a
       given order in one fresh `-X gil=0` process: all six orders plus each library alone, interleaved,
       repeated, at reduced iterations (DI_GAUNTLET_ITERS=1500, 3 threads).
    3. Before each library the driver records: the median start+join of 200 no-op threads (H1's cost directly),
       the count of GC-tracked objects and of those whose owning thread is not the main thread (H1's cause),
       gc.get_count() and the collections the loop triggers (H2).
    4. Tabulate each library's total and threaded phase by position against its spread at a fixed position.
  EVIDENCE: benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py:23-34
  IMPACT: Separates an order effect from noise and names the state behind it, with numbers.
  NEXT: Step 1.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-30T12:12:08Z
  TYPE: MEASURE
  CLAIM: Setup done and a first smoke run (one process, order melder then dishka, 100 iterations, `-X gil=0`,
    3.14.7t in the VM with dishka 1.10.1 and dependency-injector 4.49.1 - the owner's versions - in a separate
    venv) already shows inherited state. Before melder (fresh process): 52,139 GC objects, none owned by another
    thread, 200 no-op thread start+join median 211 us. Before dishka, right after melder's run and cleanup:
    92,629 GC objects, still none owned by an exited thread, and the same thread cycle takes 755 us (3.6x).
    So a library that runs after Melder starts every thread at a much higher cost, and the residue is not a
    GC-tracked object left by a worker thread. One run only: the matrix below decides.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/smoke_melder_then_dishka.jsonl:1-2
  - context_compass/artifacts/gauntlet_order_dependence_20260930/order_probe.py:79-150
  IMPACT: Supports H1 in the owner's likely reorder (Melder moved earlier): the gauntlet starts 3 threads per
    iteration, so a later library would pay that difference on every iteration.
  NEXT: Run the state-probe matrix (all six orders plus singles) to see which library leaves what, then plain
    timing rounds for the per-position totals.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T12:15:32Z
  TYPE: MEASURE
  CLAIM: State-probe matrix (all six orders plus each library alone, 2 interleaved rounds, 1000 iterations, 3
    threads, VM): EVERY library leaves the process slower at starting threads, and the libraries that run later
    pay for it.
    - 200 no-op thread start+join, median before a library: fresh process 211 us (207-239); after
      dependency-injector 426; after Melder 488; after dishka 576; after two libraries 479-619.
    - Before every library, 0 GC-tracked objects are owned by a thread other than the main thread, and the object
      count is back near the fresh count after DI or dishka (46-50k against 52k; about 93k after Melder, which
      leaves its package and a new Aether). Collections during a call are the cleanup's own plus one to four
      during setup imports at position 1, so none fire in the measured loop. The residue is neither worker-owned
      objects nor the GC. (Corrected 12:29Z: first text credited the position-1 extras to Melder's import only.)
    - Loop total by position, medians (1000 iterations): dependency-injector 1652 -> 1774 -> 1807 ms (+7-9%),
      Melder 1524 -> 1662 -> 1677 ms (+9-10%), dishka 1410 -> 1429 -> 1438 ms (+1-2%, inside its range). The
      extra is in the threaded phase (DI 1.407 -> 1.516-1.540 ms per iteration, Melder 1.256 -> 1.390-1.406,
      dishka 1.160 -> 1.176-1.179). At position 1 each library's spread is 3-8%, so the DI and Melder shifts
      are larger than that noise.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/state_matrix_1000it_summary.md:1-49
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/state_matrix_1000it.jsonl:1-42
  - context_compass/artifacts/gauntlet_order_dependence_20260930/run_matrix.py:1-85
  IMPACT: This is the reorder effect: whatever runs later inherits a slower thread start/exit from the libraries
    before it, and the gauntlet starts 3 threads per iteration. In the owner's order (DI, dishka, Melder) Melder
    always runs last, so its total carries DI's and dishka's residue; DI always runs clean. The precise CPython
    mechanism is UNKNOWN (likely the free-threaded allocator's pages from exited threads).
  NEXT: Plain timing rounds without the probe at 3000 iterations for per-position totals, then one bare-CPython
    probe (no DI library) to show the residue comes from thread churn itself.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T12:22:44Z
  TYPE: MEASURE
  CLAIM: Plain order matrix without the state probe (3000 iterations, 3 threads, -X gil=0, VM; all six orders plus
    each library alone, 3 interleaved rounds, a fresh process per configuration). Loop totals, medians:
    - Melder: 4507 ms first or alone (4311-4550) -> 5060 second, 5058 third: +12%. Threaded phase 1.235 ->
      1.41 ms per iteration.
    - dependency-injector: 5009 (4911-5140) -> 5243 second (+5%) -> 5605 third (+12%).
    - dishka: 4269 (4081-4401) -> 4525 second (+6%) -> 4568 third (+7%).
    Every shift sits in the threaded phase. Melder's and DI's exceed their position-1 spread (4311-4550 and
    4911-5140, about 5%); dishka's (+6-7%) is about the size of its spread (4081-4401, 8%), so it is the weakest.
    The order flips the ranking: in the owner's order (DI, dishka, Melder) the medians are DI 5009, dishka 4292,
    Melder 5101, so Melder looks slowest; reversed (Melder, dishka, DI) they are Melder 4507, dishka 4532, DI
    5689, so Melder ties dishka and DI looks slowest. First in a fresh process (alone or first of three): dishka
    4269, Melder 4507 (+6%), DI 5009 (+17%). (Corrected 12:28Z: the first text said every shift exceeded its
    spread and called position 1 "alone".)
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/plain_matrix_3000it_summary.md:1-48
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/plain_matrix_3000it.jsonl:1-63
  IMPACT: The owner's observation is reproduced and sized: in the shared runner a library's result depends on
    which libraries ran before it, by up to about 12% on the VM, enough to reorder the three. The owner's order
    always charges Melder with the other two's residue and never charges DI. Only one-library-per-process runs are
    comparable.
  NEXT: Bare-CPython probe (no DI library) to show where the residue comes from, then the DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-30T12:25:49Z
  TYPE: MEASURE
  CLAIM: Where the residue comes from, with no DI library loaded (bare 3.14t, mech_probe.py: 3000 waves of 3
    threads started together and joined, then the median start+join of 200 no-op threads; 3 runs each):
    - no churn: 204-209 us before, 206-209 after;
    - threads that do nothing: 205-225 -> 208-296 (inconsistent);
    - threads that build and drop 2,000 small objects: 204-218 -> 255-262 (+40-50 us, and it stays);
    - objects handed to the next wave, so they outlive their thread: 240-278 while alive, 218-228 after they are
      dropped;
    - 20 objects per thread kept alive (180k): 290-366, back to 190-261 once dropped;
    - 50 interned strings per thread (immortal on 3.14t): 307-327, permanently.
    A library run adds more than any of these (+210 to +365 us after its cleanup). Interned strings grow by
    +4.9k (DI), +5.9k (dishka) and +28.7k (Melder, mostly its import on the main thread) per run, which does not
    track the residue (dishka leaves the most), so immortal strings are not the main cause. Collections per call
    are identical at 1000 and 3000 iterations, so no collection fires inside the loops.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/mech_probe.py:1-148
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/mech_probe_round1.txt:1-6
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/mech_probe_rounds2_3_and_long.txt:1-14
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/interned_singles_1000it.jsonl:1-6
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/plain_matrix_3000it.jsonl:1-63
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/state_matrix_1000it_summary.md:39-49
  IMPACT: The residue is a property of free-threaded CPython's short-lived threads, and it grows with what those
    threads allocated. It survives every library's cleanup and is not a leak in dependency-injector, dishka or
    Melder (0 worker-owned GC objects remain). The exact allocator mechanism stays UNKNOWN (likely mimalloc pages
    left by exited threads). No library-side fix removes it; only the harness can isolate it.
  NEXT: DECISION_REQUEST: how the harness should isolate libraries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T12:26:19Z
  TYPE: DECISION_REQUEST
  CLAIM: How should the harness isolate the libraries? The answer so far: the runner measures all three in one
    process; free-threaded CPython keeps a slower thread start/exit after each library's run (+210 to +365 us per
    thread on the VM, not a leak, survives cleanup), and the gauntlet starts 3 threads per iteration, so a later
    library's loop runs 5-12% slower. Options (all benchmark-only: no src change, no notch):
    1. RECOMMENDED - one fresh process per library. The runner gains a single-library mode (--lib NAME);
       test_real_world_gauntlet starts it once per library, in the printed order, and streams each output. An
       optional REAL_WORLD_GAUNTLET_ROUNDS=N repeats the three N times, rotating the order, and prints per-library
       medians, which also answers the owner's 5-9% run-to-run spread. The current all-in-one mode stays for
       reproducing old baselines, documented as order-biased. Cost: two more interpreter starts (about 1 s each);
       the per-turn CSV gets one file per library (library name in the file name). Removes the bias: every library
       is measured as it is alone.
    2. Same process, order rotated over N rounds and averaged. Smaller change, but every number keeps some residue
       and each library's number mixes positions; it spreads the bias instead of removing it.
    3. A persistent pool of 3 worker threads per library instead of 3 new threads per iteration. Removes most of
       the thread-lifecycle cost from all numbers, and most of the order effect with it, but it changes what the
       gauntlet measures and breaks comparison with every earlier baseline. Can be combined with 1 later.
    Files for option 1: benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py,
    benchmarks/testing_other_di/test_real_world_gauntlet.py (the test and the per-turn CSV name only) and
    benchmarks/testing_other_di/benchmarks.md; a NOTICE to melder_2 first, whose lane measures the same gauntlet.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/plain_matrix_3000it_summary.md:1-48
  - context_compass/artifacts/gauntlet_order_dependence_20260930/runs/state_matrix_1000it_summary.md:1-49
  - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py:23-34
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:2197-2234
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:2069-2115
  IMPACT: Until the harness isolates libraries, the shared gauntlet's three-way ranking depends on the order in
    the runner's tuple; in the current order Melder is always charged with the other two's residue.
  NEXT: The owner picks an option; on option 1, send the NOTICE to melder_2, then implement and verify that each
    library's isolated number matches its position-1 number from the matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T12:39:02Z
  TYPE: DECISION
  CLAIM: Owner (chat, 2026-09-30): "do the most recommended thing please" - option 1 of the DECISION_REQUEST:
    one fresh process per library in the shared gauntlet. Benchmark-only: no src change, no notch, no release note.
  EVIDENCE: context_compass/tickets/tasks/completed/2026-09-30_investigate_gauntlet_order_dependence_task.md:349-381
  IMPACT: Reopens the ticket for implementation within the files the request named; melder_0 becomes the only
    writer of them until turn-in (NOTICE to melder_2 first).
  NEXT: PLAN note with the exact symbols, then the NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T12:39:02Z
  TYPE: PLAN
  CLAIM: Implementation (mapped to option 1):
    - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py: `main(argv)` parses `--lib NAME`, `--round N`
      and `--result-json PATH`. With `--lib` it runs that one library, prints its result and, when a parent asked
      for it, writes a JSON payload (with its per-turn rows) instead of the CSV. Without arguments it runs all three
      in one process exactly as today, after one printed line saying those numbers depend on the order.
    - benchmarks/testing_other_di/test_real_world_gauntlet.py: pure helpers `_gauntlet_libraries`,
      `_gauntlet_rounds` (REAL_WORLD_GAUNTLET_ROUNDS, default 1), `_isolated_order` (order rotated per round),
      `_result_payload`, `_isolated_median_lines`; the per-turn CSV gets its env/path in two helpers and an
      isolated writer that adds a trailing Round column (the all-in-one CSV keeps its columns);
      `_run_isolated_library`; `test_real_world_gauntlet` starts the runner once per library and round in its
      own process, prints each output as it finishes, fails naming library and round, prints medians when
      rounds > 1, then writes the combined CSV.
    - New benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py: fast contract tests for those
      helpers and the runner's --lib mode (a few iterations); the role requires tests with a change, so it is
      added beside the named files and reported.
    - benchmarks/testing_other_di/benchmarks.md: a section on the run modes and the measured order bias.
    - Validation in the VM mirror: the new tests; the wrapper at a few hundred iterations with 1 and 2 rounds and
      the CSV on; the all-in-one runner; isolated 3000-iteration numbers against the matrix's position-1 medians.
    - Last: LLM bundles rebuilt (benchmarks are in the "other" corpus) and both --check runs.
  EVIDENCE:
  - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py:1-38
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:2069-2234
  - llm_support/_builder.py:61-99
  IMPACT: Every library is measured in a fresh process, so its number no longer depends on the others; the old
    layout stays reproducible.
  NEXT: NOTICE to melder_2, then edit the runner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T12:46:23Z
  TYPE: DECISION
  CLAIM: Implemented option 1 (benchmark-only; applied by a script that keeps each file's line endings; pre-change
    copies and SHA-256 under before/):
    - The runner gained a module docstring and `main(argv)`: `--lib NAME` runs one library in its process and,
      with `--result-json`, hands back `_result_payload` JSON instead of writing the CSV; `--round` is recorded in
      the payload; `--round`/`--result-json` without `--lib`, an unknown name, or a round < 1 are usage errors
      (exit 2). No arguments runs all three in one process as before, after one line saying those numbers depend
      on the order.
    - test_real_world_gauntlet.py: `_gauntlet_libraries`, `_gauntlet_rounds` and `_isolated_order` beside
      `_build_ops`; the per-turn CSV split into `_per_turn_csv_enabled/_path/_header/_row`, with
      `_maybe_write_per_turn_csv` unchanged in behaviour and `_write_isolated_per_turn_csv` adding a trailing
      Round column; `_result_payload`, `_isolated_median_lines` and `_run_isolated_library`; the pytest wrapper
      now starts one process per library and round, prints each as it finishes, names library and round on
      failure, prints medians for rounds > 1 and writes the CSV last. `_build_ops`, `_run_gauntlet_once` and
      `_run_gauntlet_benchmark` are untouched, so the measured loop is the same code.
    - New test_real_world_gauntlet_isolation.py: 14 contract tests. Against the pre-change files all 14 fail
      (missing helpers; the old runner printed all three libraries for `--lib dishka`); against the change all
      14 pass (0.97 s).
    - benchmarks.md: a section on the modes and the measured order bias.
  EVIDENCE:
  - benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py:1-171
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1392-1454
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:2136-2264
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:2346-2515
  - benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py:1-336
  - benchmarks/testing_other_di/benchmarks.md:139-172
  - context_compass/artifacts/gauntlet_order_dependence_20260930/isolation_patch/apply_isolation.py:1-87
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/isolation_tests_red_before.log:1-15
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/isolation_tests_green_after.log:1-15
  IMPACT: The wrapper no longer lets one library's run change another's numbers; the old layout stays one
    command away.
  NEXT: Validate the wrapper itself in the VM (1 and 2 rounds, CSV on), the all-in-one runner, and isolated
    3000-iteration numbers against the matrix's position-1 medians.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T12:49:50Z
  TYPE: MEASURE
  CLAIM: Validation in the VM mirror (3.14.7t, -X gil=0; the wrapper run through pytest):
    - 1 round, 300 iterations: three processes, each printing only its own library; passed in 2.8 s.
    - 2 rounds, 200 iterations, CSV on: round 2 ran dishka, melder, dependency-injector (rotated); one median line
      per library; the CSV has one header, the trailing Round column and 1200 rows (200 x 3 x 2).
    - Runner with no arguments: the order line, then the three libraries in one process as before; its CSV keeps
      the old 7 columns (600 rows). `--lib melder` by hand and `--help` work.
    - 3 rounds, 3000 iterations: medians DI 5064 ms (4924-5763), dishka 4461 (4459-4726), Melder 4746
      (4741-4763). Melder's three runs sat in slots 3, 2 and 1 of their rounds and differ by 0.5%, against +12%
      for a later slot in one process. DI's 5763 and dishka's 4726 came together at the end of round 3 (DI's
      max 14.5 ms), host noise rather than order.
    - Paired control at the same time: the isolated probe's single-library processes gave Melder 4735/4579,
      dishka 4503/5001, DI 5273/5198 around the wrapper's 4725/4450/5613, so the wrapper measures what a fresh
      process measures. The VM was noisier than during the matrix, which is also why these medians sit 1-5%
      above the matrix's position-1 medians.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/wrapper_2rounds_csv_200it.log:1-17
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/runner_all_in_one_200it.log:1-5
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/runner_help.txt:1-16
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/wrapper_3rounds_3000it.log:1-22
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/control_probe_vs_wrapper_3000it.log:1-9
  IMPACT: The change does what the owner picked: a library's slot no longer moves its number, the old layout is
    still available, and the CSV keeps working in both modes. On Windows the new mode is Not run.
  NEXT: Rebuild the LLM bundles (benchmarks sit in the "other" corpus) and run both --check commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-30T12:51:46Z
  TYPE: MEASURE
  CLAIM: Last step done: the LLM bundles were rebuilt with --include-untracked (only the "other" corpus moved:
    380 files, as benchmarks live there; src and tests unchanged) and both checks print only OK lines -
    LLM src/tests/other OK; build assets _agent_documentation, _bind_guard and _system_documents current at
    0.2.8212. No src, docs or release_docs file changed, so no notch and no release-note entry. No
    .git/index.lock was left.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/llm_build.log:1-4
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/llm_check.log:1-3
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/assets_check.log:1-3
  IMPACT: The change set is complete and the repository checks are green; the ticket goes to review.
  NEXT: Owner review; on acceptance, turn in (closure summary, completed/, board anchors, artifacts retained).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-30T15:08:50Z
  TYPE: FACT
  CLAIM: The owner raised the shared gauntlet's default iteration count from 5,000 to 30,000
    (`_GauntletConfig.from_env`, DI_GAUNTLET_ITERS) in the device tree at 2026-09-30T13:24:27Z, after this lane
    landed; it is the only difference from the landed file. Notes above that speak of the default (for example
    15,000 exited threads per run) describe the 5,000 default in force when they were measured.
  EVIDENCE: benchmarks/testing_other_di/test_real_world_gauntlet.py:462-462
  IMPACT: Turn-in treats the file as landed plus the owner's edit; nothing to change back.
  NEXT: Owner review, then turn-in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-30T15:40:12Z
  TYPE: DECISION
  CLAIM: The owner turned this lane in (chat, 2026-09-30, every finished lane): option 1 stays as built - one
    process per library in the pytest wrapper, rotated rounds with medians, the old one-process layout behind
    the runner's no-argument mode - together with the owner's own DI_GAUNTLET_ITERS default of 30,000. The
    sole-writer claim on the runner, test_real_world_gauntlet.py, test_real_world_gauntlet_isolation.py and
    benchmarks.md (M0-123) is released to melder_2 by NOTICE M0-126. The artifacts stay as reference.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-30_investigate_gauntlet_order_dependence_task.md:382-510
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:462-462
  IMPACT: The owner's default edit moved the LLM "other" corpus (LLM --check: STALE other source fingerprint
    moved; src and tests OK), so that bundle is rebuilt as the last step of this turn-in pass.
    Correction: the 12:39:02Z DECISION note cited the DECISION_REQUEST as 328-360, nine lines too early
    (the ticket grew above it after it was written); it now names the note's real range.
  NEXT: Rebuild the LLM bundles and run the LLM and asset checks after every closure in this pass.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-30T15:49:07Z
  TYPE: MEASURE
  CLAIM: Last step of the turn-in pass: the LLM bundles were rebuilt with --include-untracked. Only the "other"
    corpus was written (380 files; its source fingerprint had moved with the owner's DI_GAUNTLET_ITERS edit);
    src and tests were unchanged. Both checks then print only OK lines: LLM src, tests and other; build assets
    _agent_documentation, _bind_guard and _system_documents current at 0.2.8212. No .git/index.lock was left.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/llm_check_turnin_before.log:1-6
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/llm_build_turnin.log:1-4
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/llm_check_turnin.log:1-3
  - context_compass/artifacts/gauntlet_order_dependence_20260930/validation/assets_check_turnin.log:1-3
  IMPACT: The repository checks are green after the turn-in; the closed tickets and boards are outside what
    the bundles and assets read.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Closed 2026-09-30T15:40:12Z on the owner's turn-in. Cause: the runner measured dependency-injector,
dishka and Melder one after another in one free-threaded process; each library's run left thread start/exit
slower (200 no-op threads: 211 us fresh, 426-619 us after one or two libraries), so a later library ran 5-12%
slower in the VM and the order flipped the ranking. Fix (option 1): the pytest wrapper starts the runner once
per library (--lib) and prints medians over REAL_WORLD_GAUNTLET_ROUNDS rotated rounds; the runner without
arguments keeps the old one-process layout; 14 contract tests. The owner's DI_GAUNTLET_ITERS default of 30,000
stays. No src change. melder_0's sole-writer claim (M0-123) is released by NOTICE M0-126; artifacts retained as
reference.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
