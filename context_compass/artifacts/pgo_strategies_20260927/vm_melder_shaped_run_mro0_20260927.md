# PGO codegen composition experiment

melder 0.2.82; Python 3.14.7; GIL disabled; iters=10000 repeats=5 warmup=2000 sample=50 mro_depth=0

## solo (1 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 288 | 4.0 | 1.0 | 1.0 |  |
| pgo_guarded | 104 | 1.0 | 0.0 | 1.0 | -184 ns, -3.0 py, -1.0 C |
| pgo_store | 95 | 1.0 | 0.0 | 1.0 | -193 ns, -3.0 py, -1.0 C |
| pgo_floor | 94 | 1.0 | 0.0 | 1.0 | -194 ns, -3.0 py, -1.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -276 ns, -4.0 py, -1.0 C |

## w1_singleton (2 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 364 | 4.0 | 2.0 | 1.0 |  |
| pgo_guarded | 145 | 1.0 | 0.0 | 1.0 | -219 ns, -3.0 py, -2.0 C |
| pgo_store | 149 | 1.0 | 1.0 | 1.0 | -215 ns, -3.0 py, -1.0 C |
| pgo_floor | 134 | 1.0 | 0.0 | 1.0 | -230 ns, -3.0 py, -2.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -352 ns, -4.0 py, -2.0 C |

## w1_transient (2 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 439 | 5.0 | 1.0 | 2.0 |  |
| pgo_guarded | 235 | 2.0 | 0.0 | 2.0 | -204 ns, -3.0 py, -1.0 C |
| pgo_store | 226 | 2.0 | 0.0 | 2.0 | -214 ns, -3.0 py, -1.0 C |
| pgo_floor | 222 | 2.0 | 0.0 | 2.0 | -218 ns, -3.0 py, -1.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -427 ns, -5.0 py, -1.0 C |

## w2_mixed (3 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 510 | 5.0 | 2.0 | 2.0 |  |
| pgo_guarded | 272 | 2.0 | 0.0 | 2.0 | -238 ns, -3.0 py, -2.0 C |
| pgo_store | 275 | 2.0 | 1.0 | 2.0 | -236 ns, -3.0 py, -1.0 C |
| pgo_floor | 255 | 2.0 | 0.0 | 2.0 | -256 ns, -3.0 py, -2.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -498 ns, -5.0 py, -2.0 C |

## w3_mixed (4 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 563 | 5.0 | 3.0 | 2.0 |  |
| pgo_guarded | 307 | 2.0 | 0.0 | 2.0 | -256 ns, -3.0 py, -3.0 C |
| pgo_store | 315 | 2.0 | 2.0 | 2.0 | -248 ns, -3.0 py, -1.0 C |
| pgo_floor | 285 | 2.0 | 0.0 | 2.0 | -278 ns, -3.0 py, -3.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -551 ns, -5.0 py, -3.0 C |

## w4_mixed (5 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 691 | 6.0 | 3.0 | 3.0 |  |
| pgo_guarded | 419 | 3.0 | 0.0 | 3.0 | -272 ns, -3.0 py, -3.0 C |
| pgo_store | 424 | 3.0 | 2.0 | 3.0 | -267 ns, -3.0 py, -1.0 C |
| pgo_floor | 391 | 3.0 | 0.0 | 3.0 | -300 ns, -3.0 py, -3.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -679 ns, -6.0 py, -3.0 C |

## chain3_mixed (4 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 515 | 5.0 | 2.0 | 2.0 |  |
| pgo_guarded | 272 | 2.0 | 0.0 | 2.0 | -243 ns, -3.0 py, -2.0 C |
| pgo_store | 271 | 2.0 | 1.0 | 2.0 | -244 ns, -3.0 py, -1.0 C |
| pgo_floor | 256 | 2.0 | 0.0 | 2.0 | -259 ns, -3.0 py, -2.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -503 ns, -5.0 py, -2.0 C |

## mixed3s4t (8 classes)

| arm | ns/creation | py calls | C calls | objects | vs real_meld |
| --- | ---: | ---: | ---: | ---: | --- |
| real_meld | 1031 | 8.0 | 4.0 | 5.0 |  |
| pgo_guarded | 731 | 5.0 | 0.0 | 5.0 | -300 ns, -3.0 py, -4.0 C |
| pgo_store | 728 | 5.0 | 3.0 | 5.0 | -303 ns, -3.0 py, -1.0 C |
| pgo_floor | 680 | 5.0 | 0.0 | 5.0 | -351 ns, -3.0 py, -4.0 C |
| noop | 12 | 0.0 | 0.0 | 0.0 | -1018 ns, -8.0 py, -4.0 C |

## Summary: the most an ideal PGO body wins per creation

| composition | real ns | guarded ns | saved ns | saved % | saved py calls | saved C calls | saved per 1000 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| solo | 288 | 104 | 184 | 64% | 3.0 | 1.0 | 0.18 |
| w1_singleton | 364 | 145 | 219 | 60% | 3.0 | 2.0 | 0.22 |
| w1_transient | 439 | 235 | 204 | 46% | 3.0 | 1.0 | 0.20 |
| w2_mixed | 510 | 272 | 238 | 47% | 3.0 | 2.0 | 0.24 |
| w3_mixed | 563 | 307 | 256 | 45% | 3.0 | 3.0 | 0.26 |
| w4_mixed | 691 | 419 | 272 | 39% | 3.0 | 3.0 | 0.27 |
| chain3_mixed | 515 | 272 | 243 | 47% | 3.0 | 2.0 | 0.24 |
| mixed3s4t | 1031 | 731 | 300 | 29% | 3.0 | 4.0 | 0.30 |

## Weighted by Melder's own constructor-width distribution (scanner, 2026-09-27)

| bucket | share | shapes | real ns | guarded ns | saved ns | saved % |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| width 0 | 58% | solo | 288 | 104 | 184 | 64% |
| width 1 | 23% | w1_singleton, w1_transient | 402 | 190 | 212 | 53% |
| width 2 | 8% | w2_mixed | 510 | 272 | 238 | 47% |
| width 3-4 | 9% | w3_mixed, w4_mixed | 627 | 363 | 264 | 42% |
| width 5-8 | 2% | mixed3s4t | 1031 | 731 | 300 | 29% |
| **weighted** | 100% | | 377 | 173 | 204 | 54% |

Weighted: an ideal PGO body saves 204 ns per creation on a codebase shaped like Melder (0.20 ms per 1000 creations, 0.2 s per million).
