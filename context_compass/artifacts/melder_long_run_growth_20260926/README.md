# Melder long-run gauntlet drop: evidence pack (2026-09-26)

**Status: harness fixed on owner approval the same day - see "After the fix" at the end.**

Owner question: Melder's shared-gauntlet throughput held from 5k to 50k iterations
(23,787 -> 23,200 hot scopes/s) and fell to 20,304 at 100k. Is Melder leaking?

Tickets:
- `tickets/epics/2026-09-26_melder_long_run_throughput_truth_epic.md`
- `tickets/tasks/2026-09-26_investigate_melder_long_run_growth_task.md` (source verdict, tests)
- `tickets/tasks/2026-09-26_measure_melder_long_run_attribution_task.md` (measurements)

Environment for every run here: sandbox copy of the working tree taken 2026-09-26T00:31Z,
CPython 3.14.0rc2 free-threaded (`-X gil=0`), 2 cores, 7-8 GB. Object and memory counts
transfer to other machines; absolute speeds do not.

## Verdict

1. **Melder does not leak on this path.** Over 650k scope cycles and 30k fresh threads the
   count of GC-tracked objects and allocated blocks stays flat (`probe_growth.py`), in source
   every per-cycle structure is bounded or symmetric (task T1 notes), and the new tests
   `test_melder_long_run_retention.py` assert it, with a negative control showing a 10-object
   per-iteration leak is caught.
2. **Melder triggers no garbage collections in this lane** (0 in every 40k-iteration run).
   Neither do dishka or dependency-injector.
3. **The long-run slowdown comes from the measuring harness.** `_run_gauntlet_benchmark` keeps
   every per-cycle `perf_counter_ns` delta for the whole leg (393 ints per iteration, 39.3M at
   100k). Those ints are created on the three worker threads that each iteration starts and
   then exits. On free-threaded CPython, retaining objects allocated by threads that have
   exited makes every later cycle progressively more CPU-expensive. Same effect for dishka.

## The controls (40k iterations, 8 windows of 5k)

Scope cycles/s, first window -> last window:

| lane   | threads    | discard samples | retain (harness-identical) | copy (same data, main-thread ints) |
|--------|------------|-----------------|----------------------------|------------------------------------|
| melder | fresh x3   | 13.7k -> 13.5k  | 7.6k -> 4.4k               | 13.1k -> 14.7k (no trend)          |
| dishka | fresh x3   | 18.3k -> 18.1k  | 8.3k -> 4.4k               | 15.9k -> 15.5k (no trend)          |
| melder | persistent | 31.6k -> 32.6k  | 31.5k -> 31.6k             | -                                  |
| dishka | persistent | 43.6k -> 45.1k  | 43.1k -> 44.3k             | -                                  |

CPU per cycle for melder fresh/retain rose 167 -> 329 us while discard held 99-106 us and copy
held 96-125 us. The copy mode keeps exactly as many ints and grows RSS as much as retain
(187 -> 947 MB versus 187 -> 938 MB), so heap size is not the cause. Zero collections in every run, so GC
is not the cause either. Only the combination "objects allocated by worker threads" plus
"those threads exit" degrades.

Supporting measurements:
- `probe_gc_pass_cost.py`: one `gc.collect()` costs ~22 ns per retained int (19M -> ~420 ms).
  The script's per-iteration entry arithmetic is approximate; the reported entry counts are
  exact. Owner-run corroboration: every library's cleanup (ends in `gc.collect()` with the
  lists alive) scaled 1.92-1.95x from 50k to 100k.
- `runA_full_100k_probe.log`: full three-library harness, 100k, GC probe and 10 trend windows.
  dependency-injector and dishka legs: 0 collections; dishka's windows slowed ~3x (61 s ->
  185 s per 10k iterations). The sandbox was reclaimed during the Melder leg.
- `probe_cyclic_garbage.py`: 3,000 Melder cycles with `DEBUG_SAVEALL` leave 0 cyclic garbage.

## What is still UNKNOWN

- The exact CPython mechanism. Consistent with free-threaded CPython's per-thread mimalloc
  heaps (pages still holding live objects when their thread exits are abandoned and later
  reclaimed by other threads), but the CPython source was not read. HYPOTHESIS only.
- Why the owner's i9/Windows shape differs by library (DI and dishka dropped 5k -> 50k and
  held; Melder held and dropped at 100k). The attribution test answers this on his machine.

## Reproduce

Owner-runnable, from the repository root:

```
python -X gil=0 -m pytest benchmarks/testing_other_di/test_melder_long_run_retention.py -q -s
```

Attribution (three modes, minutes each; PowerShell):

```
$env:MELDER_LONG_RUN_ATTRIBUTION = "1"
$env:MELDER_LONG_RUN_ATTRIBUTION_ITERS = "50000"
$env:MELDER_LONG_RUN_ATTRIBUTION_LIB = "melder"   # or dishka / dependency-injector
python -X gil=0 -m pytest benchmarks/testing_other_di/test_melder_long_run_retention.py -q -s -k attribution
```

The `probes/` scripts are the sandbox originals and hard-code sandbox paths; they are kept as
the exact record of what was run, not as tools.

## After the fix (owner-approved, 2026-09-26)

Applied by `patch_gauntlet_harness.py` (kept here as the exact record; it refuses to run on files
that changed):

- `test_real_world_gauntlet.py` and `melder_gauntlet_support.py`: each iteration's samples stay
  plain lists; run-long accumulation and the combined lists are `array("q")`
  (`_new_lane_metric_storage` / `new_lane_metric_storage`). Values and summaries are unchanged;
  no worker-created int object outlives its iteration.
- The shared gauntlet's own Melder builder was broken (`configure_aether_frame` froze the
  configuration before `set_property` ran), which is why it had been borrowing the Melder-only
  builder. It now uses exactly the Melder-only settings (one phase-scheduler worker, no frame
  posture overrides) and `_build_ops("melder")` calls it, so the two benchmarks are separate code.
- `test_gauntlet_melder_lane_parity.py` fails if the two lanes' setup calls, conjured spells,
  class graphs, lane sizes or per-variant melds ever differ, and proves the shared gauntlet no
  longer calls the Melder-only builder.

Fixed harness, same sandbox, 40k iterations, `_run_gauntlet_benchmark` with 8 trend windows
(`runs/runD_fixed_*.log`), wall seconds per 5k iterations:

| lane   | w1   | w2   | w3   | w4   | w5   | w6   | w7   | w8   | hot scopes/s | GC |
|--------|------|------|------|------|------|------|------|------|--------------|----|
| melder | 23.5 | 23.8 | 22.9 | 21.4 | 22.2 | 21.4 | 21.9 | 23.0 | 14,945       | 0  |
| dishka | 18.4 | 17.2 | 17.0 | 16.8 | 16.4 | 17.2 | 16.6 | 17.1 | 19,827       | 0  |

Before the fix the same harness storage degraded to ~4.4k cycles/s for both by 40k iterations.
Long-run numbers taken before the fix carried the harness penalty and are not comparable with
numbers taken after it.
