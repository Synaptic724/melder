# Borrower validation: observations before production changes

Source: Melder 0.2.40, Python 3.14.7 free-threaded. Production source remains unchanged.

Each case starts a fresh world, melds the provider once during setup, then makes only one final
provider meld after the borrower work. Passive artifact reads do not rebuild runtime state.

| Borrower operations (one and two borrowers tested) | Consumer receives original object | Provider data survives cleanup | Provider plan | Final provider meld |
| --- | --- | --- | --- | --- |
| Late bind only; no validation/meld | Not requested | Yes | Present | Same original object |
| Repeated validate_resolution(refresh_structural=False), then consumer meld | Yes | Yes | Missing | Missing-codegen error |
| Repeated validate_resolution(refresh_structural=True), then consumer meld | Yes | Yes | Missing | Missing-codegen error |
| Consumer meld without explicit validation | Yes | Yes | Missing | Missing-codegen error |

The existing object can still be injected into the consumer while the provider's own compiled lookup
path is broken. These are different observations. Retained data is not evidence that the compiled
artifact remained valid, and missing codegen is not evidence that the provider object was disposed.
refresh_structural=False is not a working bypass in this native experiment.

Eight characterization cases passed while recording these outcomes. The native corrected-contract
suite has 13 cases: six early-prefix controls pass; seven validation/meld/repeated/two-borrower cases
fail with the same missing spell_codegen_creation error, including resolution-only and implicit local
compilation. The earlier two-borrower test setup collision
was corrected by using distinct consumer binding names; it is not counted as a runtime defect.

Evidence:
- experiment_observations.json
- experiments_final.log
- experiments_final.xml
- regressions_discussion_final.log
- regressions_discussion_final.xml

Catch-up paths, ownership chain and original real GraphCache acceptance tests are in the owning
task's Catch-up Read Map. Production repair is paused for owner discussion.
