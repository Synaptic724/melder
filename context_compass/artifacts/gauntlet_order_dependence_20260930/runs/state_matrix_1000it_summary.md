# State-probe matrix, 1000 iterations, 3 threads, -X gil=0, VM (2 vCPU), 2 interleaved rounds

Source: runs/state_matrix_1000it.jsonl (order_probe.py --state-probe via run_matrix.py, seeds 1 and 2).
`before` = state measured just before the library started, in the same process.

## Thread start+join median before a library, by what ran before it (us)

| ran before | samples | median of medians | range |
| --- | --- | --- | --- |
| (fresh process) | 18 | 211 | 207-239 |
| dependency-injector | 4 | 426 | 417-442 |
| dishka | 4 | 576 | 573-605 |
| melder | 4 | 488 | 477-495 |
| dependency-injector then dishka | 2 | 593 | 586-599 |
| dependency-injector then melder | 2 | 605 | 602-609 |
| dishka then dependency-injector | 2 | 502 | 496-507 |
| dishka then melder | 2 | 619 | 617-620 |
| melder then dependency-injector | 2 | 479 | 470-487 |
| melder then dishka | 2 | 530 | 499-561 |

GC-tracked objects owned by a thread other than the main thread, before every library: [0]

## Loop total by position (ms, 1000 iterations)

| library | position 1 (alone or first) | position 2 | position 3 |
| --- | --- | --- | --- |
| dependency-injector | n=6 median 1652 (1621-1757) | n=4 median 1774 (1765-1907) | n=4 median 1807 (1770-1857) |
| dishka | n=6 median 1410 (1393-1460) | n=4 median 1429 (1357-1561) | n=4 median 1438 (1400-1548) |
| melder | n=6 median 1524 (1511-1556) | n=4 median 1662 (1637-1695) | n=4 median 1677 (1644-1817) |

## Threaded phase average per iteration by position (ms)

| library | position 1 | position 2 | position 3 |
| --- | --- | --- | --- |
| dependency-injector | median 1.407 (1.377-1.477) | median 1.516 (1.493-1.633) | median 1.540 (1.507-1.585) |
| dishka | median 1.160 (1.150-1.206) | median 1.176 (1.100-1.260) | median 1.179 (1.139-1.254) |
| melder | median 1.256 (1.245-1.271) | median 1.390 (1.370-1.409) | median 1.406 (1.374-1.488) |

## Collections during each library's call (includes the one gc.collect() in its cleanup)

- dependency-injector position 1: [2, 2, 2, 2, 2, 2]
- dependency-injector position 2: [1, 1, 1, 1]
- dependency-injector position 3: [1, 1, 1, 1]
- dishka position 1: [2, 2, 2, 2, 2, 2]
- dishka position 2: [1, 1, 1, 1]
- dishka position 3: [1, 1, 1, 1]
- melder position 1: [5, 5, 5, 5, 5, 5]
- melder position 2: [2, 2, 3, 3]
- melder position 3: [2, 2, 2, 2]
