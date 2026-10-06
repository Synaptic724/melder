# Owner run: shared gauntlet, one process per library, 30000 iterations (chat paste, 2026-09-30)

Source: the pytest output the owner pasted in chat on 2026-09-30 (Windows, PyCharm runner, started 7:24 a.m.,
134.83 s), the first run of the one-process-per-library wrapper at 0.2.8212. Config: gil=disabled, iterations=30000,
threads=3, request_scopes=10, worker_a_scopes=25, worker_b_scopes=30. Values copied from the pasted lines (ms).

| library | setup | total | avg | median | p95 | p99 | max | threaded avg | bootstrap avg | hot_scopes/s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dependency-injector | 39.960 | 38350.20 | 1.278 | 1.270 | 1.486 | 1.684 | 2.849 | 1.016 | 0.012 | 50,847 |
| dishka | 57.925 | 31965.24 | 1.066 | 1.064 | 1.302 | 1.468 | 4.198 | 0.806 | 0.014 | 61,004 |
| melder | 349.213 | 36607.86 | 1.220 | 1.216 | 1.520 | 1.702 | 10.209 | 0.925 | 0.019 | 53,267 |

Per lane: outer_total avg / request_total avg (ms) and active / wall cycles per second.

| library | request lane | worker_a lane | worker_b lane |
| --- | --- | --- | --- |
| dependency-injector | 0.039 / 0.028; 35,321 / 9,841 | 0.023 / 0.017; 59,551 / 24,604 | 0.022 / 0.016; 63,044 / 29,524 |
| dishka | 0.018 / 0.011; 90,801 / 12,414 | 0.012 / 0.007; 142,175 / 31,035 | 0.012 / 0.008; 125,234 / 37,242 |
| melder | 0.019 / 0.010; 98,735 / 10,806 | 0.014 / 0.007; 135,960 / 27,016 | 0.013 / 0.007; 139,759 / 32,419 |

Scope create/cleanup averages, all lanes combined: dishka outer 0.001 / 0.000, request 0.001 / 0.001; melder outer
0.002 / 0.002, request 0.001 / 0.001 (dependency-injector has no timed teardown).

Derived, melder minus dishka per iteration: total +0.154 ms (+14.5%); threaded phase +0.119; bootstrap +0.005;
the rest of the iteration (thread creation and start before the barrier, bookkeeping) +0.030. hot_scopes/s ratio
melder/dishka 0.873. Inside the request window melder is ahead on the request and worker_b lanes (active cycles/s
1.087x and 1.116x) and behind on worker_a (0.956x). The 3-decimal ms resolution makes the 1-2 us per-cycle scope
differences approximate.
