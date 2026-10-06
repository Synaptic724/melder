# PGO codegen composition experiment

melder 0.2.82; Python 3.14.7; GIL disabled; iters=10000 repeats=5 warmup=2000 sample=50 mro_depth=2

## solo (1 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 450 | 6.0 | 1.0 | 1.0 |  |
| pgo_guarded | 262 | 3.0 | 0.0 | 1.0 | -188 ns, -3.0 py, -1.0 C |
| pgo_store | 252 | 3.0 | 0.0 | 1.0 | -198 ns, -3.0 py, -1.0 C |
| pgo_floor | 252 | 3.0 | 0.0 | 1.0 | -199 ns, -3.0 py, -1.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -438 ns, -6.0 py, -1.0 C |

## w1_singleton (2 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 534 | 6.0 | 2.0 | 1.0 |  |
| pgo_guarded | 304 | 3.0 | 0.0 | 1.0 | -230 ns, -3.0 py, -2.0 C |
| pgo_store | 305 | 3.0 | 1.0 | 1.0 | -229 ns, -3.0 py, -1.0 C |
| pgo_floor | 284 | 3.0 | 0.0 | 1.0 | -249 ns, -3.0 py, -2.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -522 ns, -6.0 py, -2.0 C |

## w1_transient (2 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 766 | 9.0 | 1.0 | 2.0 |  |
| pgo_guarded | 554 | 6.0 | 0.0 | 2.0 | -211 ns, -3.0 py, -1.0 C |
| pgo_store | 545 | 6.0 | 0.0 | 2.0 | -220 ns, -3.0 py, -1.0 C |
| pgo_floor | 552 | 6.0 | 0.0 | 2.0 | -214 ns, -3.0 py, -1.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -753 ns, -9.0 py, -1.0 C |

## w2_mixed (3 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 839 | 9.0 | 2.0 | 2.0 |  |
| pgo_guarded | 581 | 6.0 | 0.0 | 2.0 | -258 ns, -3.0 py, -2.0 C |
| pgo_store | 598 | 6.0 | 1.0 | 2.0 | -240 ns, -3.0 py, -1.0 C |
| pgo_floor | 565 | 6.0 | 0.0 | 2.0 | -274 ns, -3.0 py, -2.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -827 ns, -9.0 py, -2.0 C |

## w3_mixed (4 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 896 | 9.0 | 3.0 | 2.0 |  |
| pgo_guarded | 630 | 6.0 | 0.0 | 2.0 | -266 ns, -3.0 py, -3.0 C |
| pgo_store | 628 | 6.0 | 2.0 | 2.0 | -268 ns, -3.0 py, -1.0 C |
| pgo_floor | 597 | 6.0 | 0.0 | 2.0 | -299 ns, -3.0 py, -3.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -884 ns, -9.0 py, -3.0 C |

## w4_mixed (5 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 1193 | 12.0 | 3.0 | 3.0 |  |
| pgo_guarded | 908 | 9.0 | 0.0 | 3.0 | -285 ns, -3.0 py, -3.0 C |
| pgo_store | 929 | 9.0 | 2.0 | 3.0 | -264 ns, -3.0 py, -1.0 C |
| pgo_floor | 880 | 9.0 | 0.0 | 3.0 | -313 ns, -3.0 py, -3.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -1181 ns, -12.0 py, -3.0 C |

## chain3_mixed (4 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 859 | 9.0 | 2.0 | 2.0 |  |
| pgo_guarded | 610 | 6.0 | 0.0 | 2.0 | -249 ns, -3.0 py, -2.0 C |
| pgo_store | 612 | 6.0 | 1.0 | 2.0 | -247 ns, -3.0 py, -1.0 C |
| pgo_floor | 599 | 6.0 | 0.0 | 2.0 | -260 ns, -3.0 py, -2.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -846 ns, -9.0 py, -2.0 C |

## mixed3s4t (8 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 1902 | 18.0 | 4.0 | 5.0 |  |
| pgo_guarded | 1547 | 15.0 | 0.0 | 5.0 | -355 ns, -3.0 py, -4.0 C |
| pgo_store | 1571 | 15.0 | 3.0 | 5.0 | -331 ns, -3.0 py, -1.0 C |
| pgo_floor | 1513 | 15.0 | 0.0 | 5.0 | -389 ns, -3.0 py, -4.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -1890 ns, -18.0 py, -4.0 C |

## Summary: the most an ideal PGO body wins per creation

| composition | real ns | guarded ns | saved ns | saved % | saved py calls | saved C calls | saved per 1000 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| solo | 450 | 262 | 188 | 42% | 3.0 | 1.0 | 0.19 |
| w1_singleton | 534 | 304 | 230 | 43% | 3.0 | 2.0 | 0.23 |
| w1_transient | 766 | 554 | 211 | 28% | 3.0 | 1.0 | 0.21 |
| w2_mixed | 839 | 581 | 258 | 31% | 3.0 | 2.0 | 0.26 |
| w3_mixed | 896 | 630 | 266 | 30% | 3.0 | 3.0 | 0.27 |
| w4_mixed | 1193 | 908 | 285 | 24% | 3.0 | 3.0 | 0.28 |
| chain3_mixed | 859 | 610 | 249 | 29% | 3.0 | 2.0 | 0.25 |
| mixed3s4t | 1902 | 1547 | 355 | 19% | 3.0 | 4.0 | 0.36 |

## Weighted by Melder's own constructor-width distribution (scanner, 2026-09-27)

| bucket | share | shapes | real ns | guarded ns | saved ns | saved % |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| width 0 | 58% | solo | 450 | 262 | 188 | 42% |
| width 1 | 23% | w1_singleton, w1_transient | 650 | 429 | 220 | 34% |
| width 2 | 8% | w2_mixed | 839 | 581 | 258 | 31% |
| width 3-4 | 9% | w3_mixed, w4_mixed | 1044 | 769 | 275 | 26% |
| width 5-8 | 2% | mixed3s4t | 1902 | 1547 | 355 | 19% |
| **weighted** | 100% | | 610 | 397 | 212 | 35% |

Weighted: an ideal PGO body saves 212 ns per creation on a codebase shaped like Melder (0.21 ms per 1000 creations, 0.2 s per million).
