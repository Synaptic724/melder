
---

## Shared real-world gauntlet: one process per library (2026-09-30)

`test_real_world_gauntlet.py` compares dependency-injector, dishka and melder on the same class graph and the
same workload. Its pytest wrapper starts `real_world_gauntlet_gil_runner.py --lib <name>` once per library, so
every library is measured in a fresh interpreter (`-X gil=0` while `REAL_WORLD_GAUNTLET_FORCE_NOGIL` is true).

Why: the runner used to measure all three one after another in one process. On free-threaded CPython 3.14 each
library's run leaves starting and joining threads slower for whatever runs next (200 no-op threads: about 211 µs
in a fresh process, 426-619 µs after one or two libraries), and the gauntlet starts three new threads per
iteration. On a 2-vCPU VM (3.14.7t, dishka 1.10.1, dependency-injector 4.49.1, 3000 iterations, medians of 3
runs), a library measured second or third was 5-12% slower than when it ran first, enough to reorder the three:

| order in one process | dependency-injector | dishka | melder |
| --- | ---: | ---: | ---: |
| dependency-injector, dishka, melder (the old default) | 5009 ms | 4292 ms | 5101 ms |
| melder, dishka, dependency-injector | 5689 ms | 4532 ms | 4507 ms |
| each one first in a fresh process | 5009 ms | 4269 ms | 4507 ms |

Run modes:

- `pytest benchmarks/testing_other_di/test_real_world_gauntlet.py -s`: one process per library. Use this one to
  compare libraries.
- `REAL_WORLD_GAUNTLET_ROUNDS=N` (default 1): measure every library N times, rotating the order each round, then
  print one median line per library. Use it when results vary from run to run.
- `python -X gil=0 benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py --lib melder`: one library by
  hand.
- `python -X gil=0 benchmarks/testing_other_di/real_world_gauntlet_gil_runner.py`: all three in one process, the
  old layout. Kept to reproduce earlier baselines; its numbers depend on the order.

`GAUNTLET_PER_TURN_CSV=1` still writes `real_world_gauntlet_per_turn<suffix>.csv`. Written by the
one-process-per-library wrapper, it has a trailing `Round` column.
