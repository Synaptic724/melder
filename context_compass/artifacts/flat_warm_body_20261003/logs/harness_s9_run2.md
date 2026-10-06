| shape | variant | ns per creation (plan direct) | vs plain | py calls | C calls |
| --- | --- | ---: | ---: | ---: | ---: |
| worker | plain | 203 |  | 3 | 5 |
| worker | S1 trim registration | 190 | -6% | 3 | 5 |
| worker | S2b unique captures | 161 | -21% | 3 | 4 |
| worker | S4 single-door prologue | 165 | -19% | 3 | 5 |
| worker | S5 batched registration | 120 | -41% | 2 | 2 |
| worker | S6 thread-affine append | 137 | -33% | 2 | 3 |
| worker | S9 owner-store constants | 170 | -16% | 3 | 5 |
| worker | ALL (S8+S4+S9+S2a+S2b+S1) | 175 | -14% | 3 | 5 |
| worker | ALL+S5 (S5 for S1) | 110 | -46% | 2 | 2 |
| worker | reference: conduit.meld("Worker") | 345 | | | |
| worker | S11 key identity: sid0:identical | | | | |
| context_root | plain | 320 |  | 3 | 9 |
| context_root | S1 trim registration | 350 | +10% | 3 | 9 |
| context_root | S2a existing constants | 231 | -28% | 3 | 5 |
| context_root | S2b unique captures | 314 | -2% | 3 | 8 |
| context_root | S4 single-door prologue | 318 | -0% | 3 | 9 |
| context_root | S5 batched registration | 270 | -16% | 2 | 6 |
| context_root | S6 thread-affine append | 272 | -15% | 2 | 7 |
| context_root | S8 lazy instance_results | 323 | +1% | 3 | 9 |
| context_root | S9 owner-store constants | 282 | -12% | 3 | 9 |
| context_root | ALL (S8+S4+S9+S2a+S2b+S1) | 284 | -11% | 3 | 9 |
| context_root | ALL+S5 (S5 for S1) | 230 | -28% | 2 | 6 |
| context_root | reference: conduit.meld("ContextRoot") | 489 | | | |
| context_root | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical | | | | |
| wide8_unique | plain | 437 |  | 3 | 12 |
| wide8_unique | S1 trim registration | 467 | +7% | 3 | 12 |
| wide8_unique | S2b unique captures | 357 | -18% | 3 | 4 |
| wide8_unique | S4 single-door prologue | 441 | +1% | 3 | 12 |
| wide8_unique | S5 batched registration | 405 | -7% | 2 | 9 |
| wide8_unique | S6 thread-affine append | 400 | -8% | 2 | 10 |
| wide8_unique | S9 owner-store constants | 370 | -15% | 3 | 12 |
| wide8_unique | ALL (S8+S4+S9+S2a+S2b+S1) | 387 | -11% | 3 | 12 |
| wide8_unique | ALL+S5 (S5 for S1) | 312 | -29% | 2 | 9 |
| wide8_unique | reference: conduit.meld("Wide8Unique") | 651 | | | |
| wide8_unique | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical, sid5:identical, sid6:identical, sid7:identical | | | | |
| wide8_existing | plain | 468 |  | 3 | 12 |
| wide8_existing | S1 trim registration | 565 | +21% | 3 | 12 |
| wide8_existing | S2a existing constants | 308 | -34% | 3 | 4 |
| wide8_existing | S4 single-door prologue | 499 | +7% | 3 | 12 |
| wide8_existing | S5 batched registration | 423 | -10% | 2 | 9 |
| wide8_existing | S6 thread-affine append | 415 | -11% | 2 | 10 |
| wide8_existing | S8 lazy instance_results | 496 | +6% | 3 | 12 |
| wide8_existing | S9 owner-store constants | 389 | -17% | 3 | 12 |
| wide8_existing | ALL (S8+S4+S9+S2a+S2b+S1) | 363 | -22% | 3 | 12 |
| wide8_existing | ALL+S5 (S5 for S1) | 312 | -33% | 2 | 9 |
| wide8_existing | reference: conduit.meld("Wide8Existing") | 643 | | | |
| wide8_existing | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical, sid5:identical, sid6:identical, sid7:identical | | | | |
| chain8_transient | plain | 534 |  | 10 | 5 |
| chain8_transient | S1 trim registration | 454 | -15% | 10 | 5 |
| chain8_transient | S2b unique captures | 441 | -17% | 10 | 4 |
| chain8_transient | S4 single-door prologue | 444 | -17% | 10 | 5 |
| chain8_transient | S5 batched registration | 423 | -21% | 9 | 2 |
| chain8_transient | S6 thread-affine append | 393 | -26% | 9 | 3 |
| chain8_transient | S9 owner-store constants | 427 | -20% | 10 | 5 |
| chain8_transient | ALL (S8+S4+S9+S2a+S2b+S1) | 440 | -18% | 10 | 5 |
| chain8_transient | ALL+S5 (S5 for S1) | 350 | -35% | 9 | 2 |
| chain8_transient | reference: conduit.meld("Chain8") | 653 | | | |
| chain8_transient | S11 key identity: sid0:identical | | | | |
