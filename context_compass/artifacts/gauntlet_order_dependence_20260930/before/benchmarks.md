# DI Deep Benchmark Comparison (Melder vs 4 libraries)

**Source:** timings you pasted from your two test runs (other DI: `test_deep_other_di.py`; Melder: `test_conduit_integration_perf_deep_graphs.py`).

**Units:** unless stated otherwise, times are **milliseconds (ms)**. Warm cache hits are shown in **microseconds (µs)**.

---

## Conjure scaling + cold root resolve (depth 3/5/7/9)

| System              | d3 conjure (ms) | d3 cold (ms) | d5 conjure (ms) | d5 cold (ms) | d7 conjure (ms) | d7 cold (ms) | d9 conjure (ms) | d9 cold (ms) |
| ------------------- | --------------: | -----------: | --------------: | -----------: | --------------: | -----------: | --------------: | -----------: |
| dependency-injector |           4.518 |        0.041 |           0.203 |        0.040 |           0.265 |        0.055 |           0.299 |        0.070 |
| lagom               |           7.925 |        0.093 |           0.240 |        0.068 |           0.301 |        0.083 |           0.373 |        0.138 |
| injector            |           2.646 |        0.157 |           0.525 |        0.251 |           0.375 |        0.323 |           0.425 |        0.367 |
| dishka              |           0.412 |        0.209 |           0.444 |        0.323 |           0.570 |        0.614 |           0.653 |        0.535 |
| **melder**          |      **97.824** |    **0.667** |      **90.473** |    **1.234** |      **90.546** |    **2.222** |     **204.445** |    **7.911** |

---

## Depth 9 unique (cold + warm)

**Units:** conjure/cold = **ms**, warm = **µs**

| System              | conjure (ms) | cold root (ms) | warm root (µs) |
| ------------------- | -----------: | -------------: | -------------: |
| dependency-injector |        0.256 |          0.045 |           0.20 |
| lagom               |        0.283 |          0.125 |           0.40 |
| injector            |        0.371 |          0.427 |           2.00 |
| dishka              |        0.682 |          0.542 |           1.80 |
| **melder**          |  **212.330** |      **8.246** |      **23.50** |

---

## Depth 9 many (new graph each call)

**Units:** **ms** (avg over 250)

| System              | avg meld root (ms) |
| ------------------- | -----------------: |
| dependency-injector |              0.120 |
| lagom               |              0.250 |
| injector            |              7.584 |
| dishka              |              0.104 |
| **melder**          |         **12.470** |

---

## Spellspace depth 3 (unique per spellspace)

**Units:** cold/per-space = **ms**, warm avg = **µs**

| System              | cold in space (ms) | warm avg (µs) | per-spellspace cold avg (ms) |
| ------------------- | -----------------: | ------------: | ---------------------------: |
| dependency-injector |              0.015 |          0.05 |                        0.014 |
| lagom               |              0.011 |          0.17 |                        0.012 |
| injector            |              0.099 |          1.16 |                        0.072 |
| dishka              |              0.321 |          0.25 |                        0.004 |
| **melder**          |          **0.699** |      **7.11** |                    **0.267** |

---

## Depth 9 many with cached leaves + cleanup

**Units:** **ms**

| System              | cold root (ms) | avg root (ms) | cleanup (ms) |
| ------------------- | -------------: | ------------: | -----------: |
| dependency-injector |          0.113 |         0.079 |        5.199 |
| lagom               |          0.252 |         0.184 |        5.208 |
| injector            |          5.191 |         5.319 |        4.859 |
| dishka              |          0.578 |         0.069 |        4.871 |
| **melder**          |     **11.375** |    **11.844** |   **14.537** |

---

## Mixed workload

**Units:** **ms** (iters=200, spellspace_cycles=10)

| System              | avg step (ms) | avg spellspace cycle (ms) | cleanup (ms) |
| ------------------- | ------------: | ------------------------: | -----------: |
| dependency-injector |         0.057 |                     0.023 |        8.266 |
| lagom               |         0.120 |                     0.025 |        8.866 |
| injector            |         4.391 |                     0.095 |        5.101 |
| dishka              |         0.055 |                     0.028 |        5.116 |
| **melder**          |     **6.550** |                 **0.325** |   **14.749** |

---

## Cycle test (build → resolve → cleanup)

**Units:** **ms** (avg over 10)

| System              | avg conjure (ms) | avg meld root (ms) | avg cleanup (ms) |
| ------------------- | ---------------: | -----------------: | ---------------: |
| dependency-injector |            0.284 |              0.045 |            3.828 |
| lagom               |            0.324 |              0.133 |            3.774 |
| injector            |            0.409 |              0.390 |            3.702 |
| dishka              |            0.673 |              0.561 |            4.070 |
| **melder**          |      **207.651** |          **8.084** |        **1.818** |

---

## Spellspace depth 9 (avg cycle)

**Units:** **ms** (spaces=50)

| System              | avg cycle (ms) |
| ------------------- | -------------: |
| dependency-injector |          0.047 |
| lagom               |          0.255 |
| injector            |          0.321 |
| dishka              |          0.018 |
| **melder**          |      **8.014** |

---

## Codegen Delta Runner Matrix (2026-02-08)

Use the repeatable runner to capture cold/warm gates plus route matrix samples:

```bash
python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 9 --warmup-count 1
```

The report now includes:
- `gate_report`:
  cold compile vs warm/mixed ratios.
- `route_matrix_report`:
  per-route warm ratios vs cold for:
  - `warm_root_ns`
  - `warm_spellspace_ns`
  - `warm_override_root_args_ns`
  - `warm_override_targeted_ns`
  - `warm_mixed_ns`
- `route_matrix_baseline_delta_report` (when `--baseline-path` is provided):
  per-route regression ratios against a baseline report.
