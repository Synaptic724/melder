# Melder creation and override experiment

Python: 3.14.7 free-threading build (main, Sep  1 2026, 14:18:33) [MSC v.1944 64 bit (AMD64)]
GIL enabled: False
GC during samples: disabled; repeats: 7

Warm single-thread calls; disk cache disabled. Setup, assertions and explicit GC are outside timing.
Supplied dependencies may change graph work. Python root-only rows exclude all Melder behavior.
No init={} API or runtime optimization is implemented by this experiment.

| Mode | Graph | Case | Median us | Min-max us | Ops/s | % normal speed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| automatic | solo | normal | 0.378 | 0.373-0.417 | 2,644,996 | 100.0 |
| automatic | solo | empty_dict | 0.508 | 0.499-0.521 | 1,967,450 | 74.4 |
| automatic | solo | empty_tuple | 0.735 | 0.719-0.759 | 1,360,309 | 51.4 |
| automatic | solo | python_root_only | 0.101 | 0.097-0.112 | 9,910,999 | 374.7 |
| automatic | scalar | normal | 0.390 | 0.382-0.477 | 2,560,994 | 100.0 |
| automatic | scalar | empty_dict | 0.516 | 0.509-0.648 | 1,937,208 | 75.6 |
| automatic | scalar | empty_tuple | 0.756 | 0.731-0.984 | 1,322,061 | 51.6 |
| automatic | scalar | root_one_reused | 0.648 | 0.646-0.691 | 1,543,108 | 60.3 |
| automatic | scalar | root_one_fresh | 0.681 | 0.672-0.812 | 1,467,422 | 57.3 |
| automatic | scalar | root_args_tuple | 0.759 | 0.745-1.038 | 1,318,066 | 51.5 |
| automatic | scalar | python_root_only | 0.157 | 0.152-0.158 | 6,388,573 | 249.5 |
| automatic | shallow | normal | 0.505 | 0.503-0.550 | 1,979,408 | 100.0 |
| automatic | shallow | empty_dict | 0.649 | 0.631-0.707 | 1,539,725 | 77.8 |
| automatic | shallow | empty_tuple | 2.221 | 2.181-2.436 | 450,312 | 22.7 |
| automatic | shallow | root_one_reused | 2.005 | 1.975-2.218 | 498,709 | 25.2 |
| automatic | shallow | root_one_fresh | 2.060 | 2.012-2.226 | 485,486 | 24.5 |
| automatic | shallow | root_all_reused | 2.611 | 2.584-3.230 | 383,050 | 19.4 |
| automatic | shallow | python_root_only | 0.173 | 0.170-0.183 | 5,774,084 | 291.7 |
| automatic | shallow | original_override | 2.055 | 2.023-2.566 | 486,510 | 24.6 |
| automatic | wide | normal | 0.821 | 0.812-0.981 | 1,217,861 | 100.0 |
| automatic | wide | empty_dict | 0.949 | 0.937-1.131 | 1,053,499 | 86.5 |
| automatic | wide | empty_tuple | 3.760 | 3.719-3.976 | 265,955 | 21.8 |
| automatic | wide | root_one_reused | 3.476 | 3.382-3.681 | 287,720 | 23.6 |
| automatic | wide | root_one_fresh | 3.509 | 3.420-4.303 | 284,969 | 23.4 |
| automatic | wide | root_all_reused | 9.517 | 9.288-9.864 | 105,072 | 8.6 |
| automatic | wide | python_root_only | 0.530 | 0.522-0.548 | 1,886,574 | 154.9 |
| automatic | wide | original_override | 3.516 | 3.407-4.323 | 284,435 | 23.4 |
| automatic | diamond | normal | 0.619 | 0.615-0.657 | 1,616,360 | 100.0 |
| automatic | diamond | empty_dict | 0.771 | 0.762-0.797 | 1,297,537 | 80.3 |
| automatic | diamond | empty_tuple | 2.952 | 2.875-3.058 | 338,755 | 21.0 |
| automatic | diamond | root_one_reused | 2.688 | 2.677-2.778 | 372,005 | 23.0 |
| automatic | diamond | root_one_fresh | 2.738 | 2.714-2.764 | 365,190 | 22.6 |
| automatic | diamond | root_all_reused | 3.338 | 3.303-3.378 | 299,552 | 18.5 |
| automatic | diamond | python_root_only | 0.173 | 0.171-0.178 | 5,769,496 | 356.9 |
| automatic | diamond | original_override | 2.901 | 2.841-2.972 | 344,717 | 21.3 |
| automatic | diamond | nested_reused | 2.836 | 2.787-2.867 | 352,589 | 21.8 |
| automatic | diamond | nested_exact | 2.692 | 2.654-2.748 | 371,410 | 23.0 |
| automatic | deep | normal | 31.983 | 31.865-32.720 | 31,266 | 100.0 |
| automatic | deep | empty_dict | 32.247 | 31.955-33.033 | 31,010 | 99.2 |
| automatic | deep | empty_tuple | 153.695 | 153.082-157.116 | 6,506 | 20.8 |
| automatic | deep | root_one_reused | 152.579 | 151.968-158.904 | 6,554 | 21.0 |
| automatic | deep | root_one_fresh | 153.688 | 152.047-155.743 | 6,507 | 20.8 |
| automatic | deep | root_all_reused | 156.433 | 153.277-158.999 | 6,392 | 20.4 |
| automatic | deep | python_root_only | 0.205 | 0.203-0.216 | 4,867,038 | 15566.4 |
| automatic | deep | original_override | 156.884 | 155.084-160.666 | 6,374 | 20.4 |
| automatic | deep | nested_reused | 154.574 | 152.062-160.015 | 6,469 | 20.7 |

Cases rejected by current runtime (not timed):
- automatic/shallow/root_args_tuple: ShallowRootAB.__init__() got multiple values for argument 'a'
- automatic/wide/root_args_tuple: Wide8Root.__init__() got multiple values for argument 'l0'
- automatic/diamond/root_args_tuple: DiamondRoot.__init__() got multiple values for argument 'left'
- automatic/deep/root_args_tuple: Depth9Root.__init__() got multiple values for argument 'left'

Case semantics:
- solo/normal: Full transient graph; no overrides.
- solo/empty_dict: Same graph; fresh empty dict.
- solo/empty_tuple: Same graph; empty positional input.
- solo/python_root_only: Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.
- scalar/normal: Full transient graph; no overrides.
- scalar/empty_dict: Same graph; fresh empty dict.
- scalar/empty_tuple: Same graph; empty positional input.
- scalar/root_one_reused: One supplied root argument; payload and value reused.
- scalar/root_one_fresh: Same root argument; one fresh dict per call, matching the original benchmark.
- scalar/root_args_tuple: All root arguments supplied positionally; public normalization remains timed.
- scalar/python_root_only: Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.
- shallow/normal: Full transient graph; no overrides.
- shallow/empty_dict: Same graph; fresh empty dict.
- shallow/empty_tuple: Same graph; empty positional input.
- shallow/root_one_reused: One supplied root argument; payload and value reused.
- shallow/root_one_fresh: Same root argument; one fresh dict per call, matching the original benchmark.
- shallow/root_all_reused: All direct root arguments supplied; retained graph values reused.
- shallow/python_root_only: Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.
- shallow/original_override: Original override workload: a; fresh mapping and precreated replacement.
- wide/normal: Full transient graph; no overrides.
- wide/empty_dict: Same graph; fresh empty dict.
- wide/empty_tuple: Same graph; empty positional input.
- wide/root_one_reused: One supplied root argument; payload and value reused.
- wide/root_one_fresh: Same root argument; one fresh dict per call, matching the original benchmark.
- wide/root_all_reused: All direct root arguments supplied; retained graph values reused.
- wide/python_root_only: Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.
- wide/original_override: Original override workload: l0; fresh mapping and precreated replacement.
- diamond/normal: Full transient graph; no overrides.
- diamond/empty_dict: Same graph; fresh empty dict.
- diamond/empty_tuple: Same graph; empty positional input.
- diamond/root_one_reused: One supplied root argument; payload and value reused.
- diamond/root_one_fresh: Same root argument; one fresh dict per call, matching the original benchmark.
- diamond/root_all_reused: All direct root arguments supplied; retained graph values reused.
- diamond/python_root_only: Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.
- diamond/original_override: Original override workload: **leaf; fresh mapping and precreated replacement.
- diamond/nested_reused: Same nested selector **leaf; payload reused.
- diamond/nested_exact: One exact nested leaf; the right branch remains normally constructed.
- deep/normal: Full transient graph; no overrides.
- deep/empty_dict: Same graph; fresh empty dict.
- deep/empty_tuple: Same graph; empty positional input.
- deep/root_one_reused: One supplied root argument; payload and value reused.
- deep/root_one_fresh: Same root argument; one fresh dict per call, matching the original benchmark.
- deep/root_all_reused: All direct root arguments supplied; retained graph values reused.
- deep/python_root_only: Lower bound: Python root constructor only, supplied dependencies; no Melder semantics.
- deep/original_override: Original override workload: left>left>left>left>left>left>left>left; fresh mapping and precreated replacement.
- deep/nested_reused: Same nested selector left>left>left>left>left>left>left>left; payload reused.
