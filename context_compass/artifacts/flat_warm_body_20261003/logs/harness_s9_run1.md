| shape | variant | ns per creation (plan direct) | vs plain | py calls | C calls |
| --- | --- | ---: | ---: | ---: | ---: |
| worker | plain | 203 |  | 3 | 5 |
| worker | S1 trim registration | 195 | -4% | 3 | 5 |
| worker | S2b unique captures | 160 | -21% | 3 | 4 |
| worker | S4 single-door prologue | 166 | -18% | 3 | 5 |
| worker | S5 batched registration | 119 | -41% | 2 | 2 |
| worker | S6 thread-affine append | 135 | -33% | 2 | 3 |
| worker | S9 owner-store constants | 172 | -15% | 3 | 5 |
| worker | ALL (S8+S4+S9+S2a+S2b+S1) | 173 | -15% | 3 | 5 |
| worker | ALL+S5 (S5 for S1) | 106 | -48% | 2 | 2 |
| worker | reference: conduit.meld("Worker") | 329 | | | |
| worker | S11 key identity: sid0:identical | | | | |
| context_root | plain | 329 |  | 3 | 9 |
| context_root | S1 trim registration | 339 | +3% | 3 | 9 |
| context_root | S2a existing constants | 237 | -28% | 3 | 5 |
| context_root | S2b unique captures | 327 | -1% | 3 | 8 |
| context_root | S4 single-door prologue | 310 | -6% | 3 | 9 |
| context_root | S5 batched registration | 289 | -12% | 2 | 6 |
| context_root | S6 thread-affine append | 287 | -13% | 2 | 7 |
| context_root | S8 lazy instance_results | 316 | -4% | 3 | 9 |
| context_root | S9 owner-store constants | 294 | -10% | 3 | 9 |
| context_root | ALL (S8+S4+S9+S2a+S2b+S1) | 285 | -13% | 3 | 9 |
| context_root | ALL+S5 (S5 for S1) | 226 | -31% | 2 | 6 |
| context_root | reference: conduit.meld("ContextRoot") | 499 | | | |
| context_root | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical | | | | |
| wide8_unique | plain | 469 |  | 3 | 12 |
| wide8_unique | S1 trim registration | 461 | -2% | 3 | 12 |
| wide8_unique | S2b unique captures | 627 | +34% | 3 | 4 |
| wide8_unique | S4 single-door prologue | 447 | -5% | 3 | 12 |
| wide8_unique | S5 batched registration | 423 | -10% | 2 | 9 |
| wide8_unique | S6 thread-affine append | 409 | -13% | 2 | 10 |
| wide8_unique | S9 owner-store constants | 395 | -16% | 3 | 12 |
| wide8_unique | ALL (S8+S4+S9+S2a+S2b+S1) | 381 | -19% | 3 | 12 |
| wide8_unique | ALL+S5 (S5 for S1) | 312 | -33% | 2 | 9 |
| wide8_unique | reference: conduit.meld("Wide8Unique") | 657 | | | |
| wide8_unique | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical, sid5:identical, sid6:identical, sid7:identical | | | | |
| wide8_existing | plain | 441 |  | 3 | 12 |
| wide8_existing | S1 trim registration | 460 | +4% | 3 | 12 |
| wide8_existing | S2a existing constants | 275 | -38% | 3 | 4 |
| wide8_existing | S4 single-door prologue | 452 | +3% | 3 | 12 |
| wide8_existing | S5 batched registration | 398 | -10% | 2 | 9 |
| wide8_existing | S6 thread-affine append | 414 | -6% | 2 | 10 |
| wide8_existing | S8 lazy instance_results | 459 | +4% | 3 | 12 |
| wide8_existing | S9 owner-store constants | 376 | -15% | 3 | 12 |
| wide8_existing | ALL (S8+S4+S9+S2a+S2b+S1) | 370 | -16% | 3 | 12 |
| wide8_existing | ALL+S5 (S5 for S1) | 297 | -33% | 2 | 9 |
| wide8_existing | reference: conduit.meld("Wide8Existing") | 645 | | | |
| wide8_existing | S11 key identity: sid0:identical, sid1:identical, sid2:identical, sid3:identical, sid4:identical, sid5:identical, sid6:identical, sid7:identical | | | | |
| chain8_transient | plain | 512 |  | 10 | 5 |
| chain8_transient | S1 trim registration | 452 | -12% | 10 | 5 |
| chain8_transient | S2b unique captures | 443 | -14% | 10 | 4 |
| chain8_transient | S4 single-door prologue | 442 | -14% | 10 | 5 |
| chain8_transient | S5 batched registration | 437 | -15% | 9 | 2 |
| chain8_transient | S6 thread-affine append | 407 | -21% | 9 | 3 |
| chain8_transient | S9 owner-store constants | 440 | -14% | 10 | 5 |
| chain8_transient | ALL (S8+S4+S9+S2a+S2b+S1) | 454 | -11% | 10 | 5 |
| chain8_transient | ALL+S5 (S5 for S1) | 365 | -29% | 9 | 2 |
| chain8_transient | reference: conduit.meld("Chain8") | 673 | | | |
| chain8_transient | S11 key identity: sid0:identical | | | | |
