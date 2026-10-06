| shape | variant | ns per creation (plan direct) | vs plain | py calls | C calls |
| --- | --- | ---: | ---: | ---: | ---: |
| worker | plain | 203 |  | 3 | 5 |
| worker | S1 trim registration | 193 | -5% | 3 | 5 |
| worker | S2b unique captures | 159 | -22% | 3 | 4 |
| worker | S4 single-door prologue | 169 | -17% | 3 | 5 |
| worker | S5 batched registration | 118 | -42% | 2 | 2 |
| worker | S6 thread-affine append | 139 | -32% | 2 | 3 |
| worker | S9 owner-store constants | 167 | -18% | 3 | 5 |
| worker | ALL (S8+S4+S9+S2a+S2b+S1) | 173 | -15% | 3 | 5 |
| worker | ALL+S5 (S5 for S1) | 113 | -44% | 2 | 2 |
| worker | reference: conduit.meld("Worker") | 342 | | | |
| worker | S11 key identity: sid0:identical | | | | |
| context_root | plain | 337 |  | 3 | 9 |
| context_root | S1 trim registration | 330 | -2% | 3 | 9 |
| context_root | S2a existing constants | 231 | -31% | 3 | 5 |
| context_root | S2b unique captures | 384 | +14% | 3 | 8 |
| context_root | S4 single-door prologue | 325 | -4% | 3 | 9 |
| context_root | S5 batched registration | 354 | +5% | 2 | 6 |
| context_root | S6 thread-affine append | 355 | +5% | 2 | 7 |
| context_root | S8 lazy instance_results | 396 | +18% | 3 | 9 |
| context_root | S9 owner-store constants | 335 | -1% | 3 | 9 |
| context_root | ALL (S8+S4+S9+S2a+S2b+S1) | 306 | -9% | 3 | 9 |
| context_root | ALL+S5 (S5 for S1) | 212 | -37% | 2 | 6 |
| context_root | reference: conduit.meld("ContextRoot") | 490 | | | |
| context_root | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical | | | | |
| wide8_unique | plain | 423 |  | 3 | 12 |
| wide8_unique | S1 trim registration | 432 | +2% | 3 | 12 |
| wide8_unique | S2b unique captures | 342 | -19% | 3 | 4 |
| wide8_unique | S4 single-door prologue | 412 | -3% | 3 | 12 |
| wide8_unique | S5 batched registration | 371 | -12% | 2 | 9 |
| wide8_unique | S6 thread-affine append | 401 | -5% | 2 | 10 |
| wide8_unique | S9 owner-store constants | 386 | -9% | 3 | 12 |
| wide8_unique | ALL (S8+S4+S9+S2a+S2b+S1) | 378 | -11% | 3 | 12 |
| wide8_unique | ALL+S5 (S5 for S1) | 313 | -26% | 2 | 9 |
| wide8_unique | reference: conduit.meld("Wide8Unique") | 634 | | | |
| wide8_unique | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical, sid5:identical, sid6:identical, sid7:identical | | | | |
| wide8_existing | plain | 433 |  | 3 | 12 |
| wide8_existing | S1 trim registration | 466 | +8% | 3 | 12 |
| wide8_existing | S2a existing constants | 270 | -38% | 3 | 4 |
| wide8_existing | S4 single-door prologue | 454 | +5% | 3 | 12 |
| wide8_existing | S5 batched registration | 400 | -8% | 2 | 9 |
| wide8_existing | S6 thread-affine append | 412 | -5% | 2 | 10 |
| wide8_existing | S8 lazy instance_results | 462 | +7% | 3 | 12 |
| wide8_existing | S9 owner-store constants | 383 | -12% | 3 | 12 |
| wide8_existing | ALL (S8+S4+S9+S2a+S2b+S1) | 372 | -14% | 3 | 12 |
| wide8_existing | ALL+S5 (S5 for S1) | 303 | -30% | 2 | 9 |
| wide8_existing | reference: conduit.meld("Wide8Existing") | 646 | | | |
| wide8_existing | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical, sid5:identical, sid6:identical, sid7:identical | | | | |
| chain8_transient | plain | 530 |  | 10 | 5 |
| chain8_transient | S1 trim registration | 448 | -15% | 10 | 5 |
| chain8_transient | S2b unique captures | 440 | -17% | 10 | 4 |
| chain8_transient | S4 single-door prologue | 436 | -18% | 10 | 5 |
| chain8_transient | S5 batched registration | 404 | -24% | 9 | 2 |
| chain8_transient | S6 thread-affine append | 388 | -27% | 9 | 3 |
| chain8_transient | S9 owner-store constants | 442 | -17% | 10 | 5 |
| chain8_transient | ALL (S8+S4+S9+S2a+S2b+S1) | 431 | -19% | 10 | 5 |
| chain8_transient | ALL+S5 (S5 for S1) | 353 | -33% | 9 | 2 |
| chain8_transient | reference: conduit.meld("Chain8") | 632 | | | |
| chain8_transient | S11 key identity: sid0:identical | | | | |
