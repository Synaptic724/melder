# Fast-Path Benchmark Summary (2026-01-26)

## Sources
- `benchmarks/testing_other_di/optimistic/test_optimistic_meld_plan.py` (optimistic plan micro-benchmark; synthetic)
- `benchmarks/testing_other_di/test_conduit_integration_perf_deep_graphs.py` (melder deep graph runtime)
- `benchmarks/testing_other_di/test_deep_other_di.py` (other DI baselines)

## Notes
- Conjure and cleanup timings omitted (focus on meld execution).
- Units: ms for milliseconds, us for microseconds.
- Optimistic plan results are synthetic: no validation, no overrides, tight loop.

## Optimistic Plan Execution (Synthetic)
| Depth | Iterations | Avg ms | Avg us |
| --- | --- | --- | --- |
| 3 | 200000 | 0.001345 | 1.345 |
| 5 | 100000 | 0.002397 | 2.397 |
| 9 | 50000 | 0.004453 | 4.453 |

## Depth 9 Comparison: Optimistic Melder vs DI Baselines

Note: optimistic plan is a synthetic floor and not a direct apples-to-apples
match for the runtime baselines.

| System | Scenario | Avg root (ms) |
| --- | --- | --- |
| melder (optimistic) | plan execution (synthetic) | 0.004453 |
| melder | depth9 many avg root | 9.712 |
| dependency-injector | depth9 many avg root | 0.118 |
| lagom | depth9 many avg root | 0.211 |
| injector | depth9 many avg root | 7.430 |
| dishka | depth9 many avg root | 0.107 |

## Cold Root Resolve by Depth (meld_root_cold, ms)
| System | d3 | d5 | d7 | d9 |
| --- | --- | --- | --- | --- |
| melder | 0.439 | 0.833 | 2.197 | 7.575 |
| dependency-injector | 0.038 | 0.039 | 0.052 | 0.063 |
| lagom | 0.083 | 0.064 | 0.072 | 0.140 |
| injector | 0.136 | 0.215 | 0.305 | 0.361 |
| dishka | 0.203 | 0.302 | 0.414 | 0.596 |

## Depth 9 Unique Root Resolve (ms/us)
| System | Cold ms | Warm us |
| --- | --- | --- |
| melder | 8.534 | 7.10 |
| dependency-injector | 0.047 | 0.20 |
| lagom | 0.129 | 0.40 |
| injector | 0.428 | 1.90 |
| dishka | 0.513 | 1.40 |

## Depth 9 Many (new graph each call) Avg Root (ms)
| System | Avg meld root ms |
| --- | --- |
| melder | 9.712 |
| dependency-injector | 0.118 |
| lagom | 0.211 |
| injector | 7.430 |
| dishka | 0.107 |

## Spellspace Depth 3 (unique per spellspace)
| System | Cold in space ms | Warm avg us | Per-spellspace cold avg ms |
| --- | --- | --- | --- |
| melder | 0.389 | 1.33 | 0.258 |
| dependency-injector | 0.014 | 0.05 | 0.014 |
| lagom | 0.010 | 0.18 | 0.012 |
| injector | 0.098 | 1.14 | 0.069 |
| dishka | 0.234 | 0.26 | 0.004 |

## Depth 9 Many with Cached Leaves (iters=200)
| System | Cold ms | Avg meld root ms |
| --- | --- | --- |
| melder | 8.893 | 8.956 |
| dependency-injector | 0.115 | 0.081 |
| lagom | 0.238 | 0.180 |
| injector | 5.033 | 5.025 |
| dishka | 0.541 | 0.071 |

## Mixed Workload (iters=200, spellspace_cycles=10)
| System | Avg step ms | Avg spellspace cycle ms |
| --- | --- | --- |
| melder | 7.101 | 0.339 |
| dependency-injector | 0.055 | 0.016 |
| lagom | 0.115 | 0.016 |
| injector | 4.175 | 0.091 |
| dishka | 0.058 | 0.023 |

## Cycle Depth 9 Unique Per Container/Conduit (cycles=10)
| System | Avg meld root ms |
| --- | --- |
| melder | 9.239 |
| dependency-injector | 0.041 |
| lagom | 0.126 |
| injector | 0.376 |
| dishka | 0.548 |

## Spellspace Depth 9 (spaces=50)
| System | Avg cycle ms |
| --- | --- |
| melder | 9.155 |
| dependency-injector | 0.048 |
| lagom | 0.270 |
| injector | 0.289 |
| dishka | 0.019 |
