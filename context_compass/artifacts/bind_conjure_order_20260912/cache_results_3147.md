# Cached dynamic bind/conjure order comparison on Python 3.14.7

The late-bind path does not reuse saved execution payloads. A warm bundle avoids rewrites,
but its five spells still compile. Bind-before-conjure loads all five saved payloads.

## Median complete workflow (milliseconds)

| Disk cache | Bind -> conjure -> meld | Conjure -> bind -> meld | Latter / former |
| --- | ---: | ---: | ---: |
| disabled | 3.7073 | 7.3165 | 1.974x |
| cold | 4.6749 | 10.9569 | 2.344x |
| warm | 3.7521 | 7.7653 | 2.070x |

## Stage breakdown (milliseconds)

| Cache | Order | Bind five | Conjure | First meld five | Total p10-p90 |
| --- | --- | ---: | ---: | ---: | ---: |
| disabled | Bind -> conjure -> meld | 1.0768 | 2.4779 | 0.1108 | 3.2407-4.2091 |
| disabled | Conjure -> bind -> meld | 1.7835 | 0.3620 | 5.1401 | 6.6540-8.1731 |
| cold | Bind -> conjure -> meld | 1.0737 | 3.4382 | 0.1271 | 4.2934-5.0600 |
| cold | Conjure -> bind -> meld | 1.7968 | 0.5870 | 8.5319 | 10.3054-11.8349 |
| warm | Bind -> conjure -> meld | 1.0692 | 2.5484 | 0.0761 | 3.2577-4.1802 |
| warm | Conjure -> bind -> meld | 1.7887 | 0.6757 | 5.2365 | 7.1842-8.5020 |

Stage and total medians are computed independently; medians need not add exactly.

## Interpretation

- Bind -> conjure -> meld: warm uses 19.7% less median time than cold; +1.2% versus cache disabled.
- Conjure -> bind -> meld: warm uses 29.1% less median time than cold; +6.1% versus cache disabled.
- A warm cache improves over building and writing a cold cache. It gives no meaningful total
  speedup over disabling disk caching for this small five-independent-class workload.
- Conjure still performs phases 1-7. A full hit skips phases 8-11 and publishes cached contexts;
  first meld includes lazy hydration. Those savings compete with bundle loading overhead.
- An empty conjure still loads the cache file, but has no live spells to match. Later binds
  never hydrate those payloads. Existing IDs only suppress payload export and bundle writes.
- This does not generalize to larger dependency graphs, other existence modes or bulk binds.

## Independent diagnostic call counts

| Cache | Order | Payload reads | Cached context publications | Target plan compiles | Bundle writes |
| --- | --- | ---: | ---: | ---: | ---: |
| disabled | Bind -> conjure -> meld | 0 | 0 | 0 | 0 |
| disabled | Conjure -> bind -> meld | 0 | 0 | 5 | 0 |
| cold | Bind -> conjure -> meld | 0 | 0 | 0 | 1 |
| cold | Conjure -> bind -> meld | 0 | 0 | 5 | 5 |
| warm | Bind -> conjure -> meld | 5 | 5 | 0 | 0 |
| warm | Conjure -> bind -> meld | 0 | 0 | 5 | 0 |

All nine diagnostic passes agree. These are call-through spy runs after measurement;
their timings are discarded. Target plan counts refer to the late-bind local path;
zero does not imply that no conduit-wide plan compilation happened on a cold conjure.
No deferred fallback compilation was observed in any diagnostic case.

## First meld of each object (microseconds)

| Cache | Order | Object 1 | Object 2 | Object 3 | Object 4 | Object 5 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| disabled | Bind -> conjure -> meld | 46.40 | 18.80 | 15.30 | 14.30 | 14.40 |
| disabled | Conjure -> bind -> meld | 1914.55 | 885.70 | 797.45 | 770.40 | 772.80 |
| cold | Bind -> conjure -> meld | 56.90 | 20.60 | 16.70 | 15.60 | 15.40 |
| cold | Conjure -> bind -> meld | 2532.80 | 1592.20 | 1492.50 | 1456.10 | 1445.80 |
| warm | Bind -> conjure -> meld | 37.70 | 11.50 | 9.00 | 8.30 | 8.30 |
| warm | Conjure -> bind -> meld | 1926.70 | 914.05 | 822.10 | 805.75 | 792.35 |

## Repetition stability

| Cache | Process | Bind-first total ms | Conjure-first total ms | Ratio |
| --- | ---: | ---: | ---: | ---: |
| disabled | 1 | 3.7141 | 7.3041 | 1.967x |
| disabled | 2 | 3.6665 | 7.3378 | 2.001x |
| disabled | 3 | 3.7309 | 7.3108 | 1.960x |
| cold | 1 | 4.6816 | 11.0031 | 2.350x |
| cold | 2 | 4.6886 | 11.0669 | 2.360x |
| cold | 3 | 4.6466 | 10.8001 | 2.324x |
| warm | 1 | 3.7548 | 7.7316 | 2.059x |
| warm | 2 | 3.7060 | 7.6906 | 2.075x |
| warm | 3 | 3.7683 | 7.9357 | 2.106x |

## Method and evidence

- Three fresh processes per mode; 20 warm-up pairs plus 200 measured pairs per process:
  600 samples per order per mode, 3,600 measured workflows total.
- Same five classes, individual binds, Existence.unique, returned spell IDs, dynamic posture,
  default five compiler workers, recording off, Nexus publication off and GC enabled.
- AB/BA sample order alternates. Mode order rotates across repetitions. Processes run serially.
- Every cycle owns a fresh book/frame/root. Warm files are seeded by the same order in separate
  task-owned folders. Cold means absent Melder cache, not cold OS/filesystem page caches.
- Setup, cache deletion/seeding, assertions, repeated instance reads and teardown are untimed.
  Conjure/bind/first-meld cache I/O remains inside the corresponding workflow timer.
- All object types/values, repeated-instance identity and frame cleanup checks passed.
- Raw samples: cache_{disabled,cold,warm}_3147_run_{1,2,3}.json. Pilots are excluded.
- No runtime source edits. Git revision and source status are captured in every run.
- See environment_and_stall.md for the uv migration and bounded profiler reproduction.

## Reproduce

Run from the repository root in PowerShell; repeat with each cache mode and unique run ID:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:MELDER_BIND_ORDER_CACHE_SPEEDTEST = '1'
$env:MELDER_BIND_ORDER_CACHE_MODE = 'warm'
$env:MELDER_BIND_ORDER_SAMPLES = '200'
$env:MELDER_BIND_ORDER_WARMUPS = '20'
$env:MELDER_BIND_ORDER_RUN_ID = 'cache_warm_3147_run_1'
& '.venv_new/Scripts/python.exe' -m pytest tests/experimentation/test_dynamic_bind_conjure_order_cache_speed_experiment.py::test_dynamic_bind_conjure_order_cache_speed --confcutdir=tests/experimentation -p no:cacheprovider -o addopts= -q -s
```

Rebuild this report with `.venv_new/Scripts/python.exe context_compass/artifacts/bind_conjure_order_20260912/aggregate_cache_results.py`.
