# PGO codegen composition experiment

melder 0.2.82; Python 3.14.7; GIL disabled; iters=20000 repeats=5 warmup=2000 sample=50

## solo (1 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 291 | 4.0 | 1.0 | 1.0 |  |
| pgo_guarded | 108 | 1.0 | 0.0 | 1.0 | -183 ns, -3.0 py, -1.0 C |
| pgo_store | 109 | 1.0 | 0.0 | 1.0 | -182 ns, -3.0 py, -1.0 C |
| pgo_floor | 111 | 1.0 | 0.0 | 1.0 | -180 ns, -3.0 py, -1.0 C |
| noop | 14 | 0.0 | 0.0 | 0.0 | -277 ns, -4.0 py, -1.0 C |
| real_meld @ 2 threads | 1073 ns/creation/thread | | | | 1,863,354 creations/s |
| pgo_guarded @ 2 threads | 310 ns/creation/thread | | | | 6,447,889 creations/s |

## wide8_transient (9 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 1469 | 12.0 | 1.0 | 9.0 |  |
| pgo_guarded | 1114 | 9.0 | 0.0 | 9.0 | -354 ns, -3.0 py, -1.0 C |
| pgo_store | 1079 | 9.0 | 0.0 | 9.0 | -390 ns, -3.0 py, -1.0 C |
| pgo_floor | 1093 | 9.0 | 0.0 | 9.0 | -375 ns, -3.0 py, -1.0 C |
| noop | 13 | 0.0 | 0.0 | 0.0 | -1456 ns, -12.0 py, -1.0 C |
| real_meld @ 2 threads | 4286 ns/creation/thread | | | | 466,654 creations/s |
| pgo_guarded @ 2 threads | 3285 ns/creation/thread | | | | 608,832 creations/s |

## wide8_singleton (9 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 866 | 4.0 | 9.0 | 1.0 |  |
| pgo_guarded | 433 | 1.0 | 0.0 | 1.0 | -433 ns, -3.0 py, -9.0 C |
| pgo_store | 501 | 1.0 | 8.0 | 1.0 | -364 ns, -3.0 py, -1.0 C |
| pgo_floor | 380 | 1.0 | 0.0 | 1.0 | -486 ns, -3.0 py, -9.0 C |
| noop | 15 | 0.0 | 0.0 | 0.0 | -851 ns, -4.0 py, -9.0 C |
| real_meld @ 2 threads | 3516 ns/creation/thread | | | | 568,763 creations/s |
| pgo_guarded @ 2 threads | 1665 ns/creation/thread | | | | 1,201,001 creations/s |

## wide16_transient (17 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 2732 | 20.0 | 1.0 | 17.0 |  |
| pgo_guarded | 2355 | 17.0 | 0.0 | 17.0 | -377 ns, -3.0 py, -1.0 C |
| pgo_store | 2296 | 17.0 | 0.0 | 17.0 | -436 ns, -3.0 py, -1.0 C |
| pgo_floor | 2294 | 17.0 | 0.0 | 17.0 | -438 ns, -3.0 py, -1.0 C |
| noop | 13 | 0.0 | 0.0 | 0.0 | -2720 ns, -20.0 py, -1.0 C |
| real_meld @ 2 threads | 7891 ns/creation/thread | | | | 253,468 creations/s |
| pgo_guarded @ 2 threads | 6795 ns/creation/thread | | | | 294,331 creations/s |

## chain8_transient (9 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 1687 | 12.0 | 1.0 | 9.0 |  |
| pgo_guarded | 1148 | 9.0 | 0.0 | 9.0 | -540 ns, -3.0 py, -1.0 C |
| pgo_store | 1135 | 9.0 | 0.0 | 9.0 | -552 ns, -3.0 py, -1.0 C |
| pgo_floor | 1130 | 9.0 | 0.0 | 9.0 | -558 ns, -3.0 py, -1.0 C |
| noop | 13 | 0.0 | 0.0 | 0.0 | -1675 ns, -12.0 py, -1.0 C |
| real_meld @ 2 threads | 4199 ns/creation/thread | | | | 476,290 creations/s |
| pgo_guarded @ 2 threads | 3015 ns/creation/thread | | | | 663,342 creations/s |

## chain8_singleton (9 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 380 | 4.0 | 2.0 | 1.0 |  |
| pgo_guarded | 187 | 1.0 | 0.0 | 1.0 | -193 ns, -3.0 py, -2.0 C |
| pgo_store | 151 | 1.0 | 1.0 | 1.0 | -229 ns, -3.0 py, -1.0 C |
| pgo_floor | 133 | 1.0 | 0.0 | 1.0 | -247 ns, -3.0 py, -2.0 C |
| noop | 13 | 0.0 | 0.0 | 0.0 | -367 ns, -4.0 py, -2.0 C |
| real_meld @ 2 threads | 1377 ns/creation/thread | | | | 1,452,583 creations/s |
| pgo_guarded @ 2 threads | 727 ns/creation/thread | | | | 2,752,187 creations/s |

## diamond (4 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 680 | 6.0 | 2.0 | 3.0 |  |
| pgo_guarded | 431 | 3.0 | 0.0 | 3.0 | -249 ns, -3.0 py, -2.0 C |
| pgo_store | 453 | 3.0 | 2.0 | 3.0 | -227 ns, -3.0 py, -0.0 C |
| pgo_floor | 415 | 3.0 | 0.0 | 3.0 | -265 ns, -3.0 py, -2.0 C |
| noop | 13 | 0.0 | 0.0 | 0.0 | -667 ns, -6.0 py, -2.0 C |
| real_meld @ 2 threads | 2266 ns/creation/thread | | | | 882,591 creations/s |
| pgo_guarded @ 2 threads | 1353 ns/creation/thread | | | | 1,478,518 creations/s |

## mixed3s4t (8 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 1082 | 8.0 | 4.0 | 5.0 |  |
| pgo_guarded | 732 | 5.0 | 0.0 | 5.0 | -349 ns, -3.0 py, -4.0 C |
| pgo_store | 730 | 5.0 | 3.0 | 5.0 | -352 ns, -3.0 py, -1.0 C |
| pgo_floor | 674 | 5.0 | 0.0 | 5.0 | -407 ns, -3.0 py, -4.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -1070 ns, -8.0 py, -4.0 C |
| real_meld @ 2 threads | 3503 ns/creation/thread | | | | 571,018 creations/s |
| pgo_guarded @ 2 threads | 2212 ns/creation/thread | | | | 904,186 creations/s |

## chain6_alternating (7 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 518 | 5.0 | 2.0 | 2.0 |  |
| pgo_guarded | 289 | 2.0 | 0.0 | 2.0 | -229 ns, -3.0 py, -2.0 C |
| pgo_store | 275 | 2.0 | 1.0 | 2.0 | -243 ns, -3.0 py, -1.0 C |
| pgo_floor | 256 | 2.0 | 0.0 | 2.0 | -261 ns, -3.0 py, -2.0 C |
| noop | 13 | 0.0 | 0.0 | 0.0 | -505 ns, -5.0 py, -2.0 C |
| real_meld @ 2 threads | 1824 ns/creation/thread | | | | 1,096,387 creations/s |
| pgo_guarded @ 2 threads | 927 ns/creation/thread | | | | 2,156,579 creations/s |

## diamond_transient (4 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 960 | 8.0 | 1.0 | 5.0 |  |
| pgo_guarded | 704 | 5.0 | 0.0 | 5.0 | -257 ns, -3.0 py, -1.0 C |
| pgo_store | 620 | 5.0 | 0.0 | 5.0 | -341 ns, -3.0 py, -1.0 C |
| pgo_floor | 716 | 5.0 | 0.0 | 5.0 | -245 ns, -3.0 py, -1.0 C |
| noop | 14 | 0.0 | 0.0 | 0.0 | -946 ns, -8.0 py, -1.0 C |
| real_meld @ 2 threads | 2603 ns/creation/thread | | | | 768,375 creations/s |
| pgo_guarded @ 2 threads | 1856 ns/creation/thread | | | | 1,077,431 creations/s |

## Summary: the most an ideal PGO body wins per creation

| composition | real ns | guarded ns | saved ns | saved % | saved py calls | saved C calls | saved per 1000 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| solo | 291 | 108 | 183 | 63% | 3.0 | 1.0 | 0.18 |
| wide8_transient | 1469 | 1114 | 354 | 24% | 3.0 | 1.0 | 0.35 |
| wide8_singleton | 866 | 433 | 433 | 50% | 3.0 | 9.0 | 0.43 |
| wide16_transient | 2732 | 2355 | 377 | 14% | 3.0 | 1.0 | 0.38 |
| chain8_transient | 1687 | 1148 | 540 | 32% | 3.0 | 1.0 | 0.54 |
| chain8_singleton | 380 | 187 | 193 | 51% | 3.0 | 2.0 | 0.19 |
| diamond | 680 | 431 | 249 | 37% | 3.0 | 2.0 | 0.25 |
| mixed3s4t | 1082 | 732 | 349 | 32% | 3.0 | 4.0 | 0.35 |
| chain6_alternating | 518 | 289 | 229 | 44% | 3.0 | 2.0 | 0.23 |
| diamond_transient | 960 | 704 | 257 | 27% | 3.0 | 1.0 | 0.26 |
