# Owner runs of test_real_world_gauntlet (chat paste, 2026-09-30)

Source: three pytest outputs the owner pasted in chat on 2026-09-30 with the question "its weird when I reorder
this benchmark it changes". Windows, PyCharm pytest runner (`-s --log-cli-level=INFO`), first run started 5:53 a.m.
All three ran in the order dependency-injector -> dishka -> melder: each library prints its result as soon as it
finishes, so the printed order is the execution order. No reordered run was pasted.
Config, all runs: gil=disabled, setup_singletons=5, iterations=5000, threads=3, request_scopes=10,
worker_a_scopes=25, worker_b_scopes=30. Extracted verbatim from the pasted lines (ms).

| run | library | setup | total | avg | median | p95 | p99 | max | threaded avg | cleanup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | dependency-injector | 41.081 | 6632.33 | 1.326 | 1.329 | 1.520 | 1.708 | 2.714 | 1.053 | 5.512 |
| 1 | dishka | 38.311 | 5627.48 | 1.125 | 1.147 | 1.334 | 1.518 | 3.889 | 0.871 | 4.866 |
| 1 | melder | 316.787 | 6454.26 | 1.291 | 1.335 | 1.517 | 1.657 | 10.369 | 1.031 | 17.077 |
| 2 | dependency-injector | 89.499 | 7028.75 | 1.406 | 1.380 | 1.747 | 2.176 | 3.450 | 1.105 | 5.491 |
| 2 | dishka | 39.598 | 5733.32 | 1.147 | 1.171 | 1.353 | 1.458 | 3.545 | 0.876 | 5.551 |
| 2 | melder | 344.921 | 6783.97 | 1.357 | 1.391 | 1.599 | 1.787 | 10.883 | 1.055 | 18.064 |
| 3 | dependency-injector | 41.713 | 6823.98 | 1.365 | 1.348 | 1.609 | 2.189 | 2.622 | 1.074 | 6.087 |
| 3 | dishka | 41.929 | 5904.00 | 1.181 | 1.196 | 1.419 | 1.660 | 3.739 | 0.889 | 6.657 |
| 3 | melder | 365.669 | 7040.97 | 1.408 | 1.441 | 1.687 | 1.990 | 10.942 | 1.075 | 20.286 |

Same-order spread across the three runs (max/min - 1): dependency-injector 6.0%, dishka 4.9%, melder 9.1%.
Melder's per-iteration max (10.4-10.9 ms) is 3-4x the others' (2.6-3.9 ms) in every run.
