# Melder creation and override experiment

Python: 3.14.7 free-threading build (main, Sep  1 2026, 14:17:47) [Clang 22.1.3 ]
GIL enabled: False
GC during samples: disabled; repeats: 7

Warm single-thread calls; disk cache disabled. Setup, assertions and explicit GC are outside timing.
Supplied dependencies may change graph work. Python root-only rows exclude all Melder behavior.
No init={} API or runtime optimization is implemented by this experiment.

| Mode | Graph | Case | Median us | Min-max us | Ops/s | % normal speed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| automatic | scalar | normal | 0.267 | 0.262-0.323 | 3,742,028 | 100.0 |
| automatic | scalar | empty_dict | 0.361 | 0.354-0.394 | 2,767,793 | 74.0 |
| automatic | scalar | empty_tuple | 0.532 | 0.522-0.543 | 1,881,268 | 50.3 |
| automatic | scalar | root_one_reused | 0.468 | 0.458-0.552 | 2,136,950 | 57.1 |
| automatic | scalar | root_one_fresh | 0.473 | 0.468-0.481 | 2,112,696 | 56.5 |
| automatic | scalar | root_args_tuple | 0.560 | 0.551-0.573 | 1,784,411 | 47.7 |
| automatic | scalar | python_root_only | 0.105 | 0.103-0.126 | 9,486,529 | 253.5 |
| automatic | shallow | normal | 0.354 | 0.351-0.438 | 2,827,059 | 100.0 |
| automatic | shallow | empty_dict | 0.450 | 0.447-0.555 | 2,221,642 | 78.6 |
| automatic | shallow | empty_tuple | 1.717 | 1.678-2.267 | 582,289 | 20.6 |
| automatic | shallow | root_one_reused | 1.558 | 1.527-1.580 | 641,867 | 22.7 |
| automatic | shallow | root_one_fresh | 1.619 | 1.566-1.673 | 617,555 | 21.8 |
| automatic | shallow | root_all_reused | 2.040 | 2.023-2.272 | 490,141 | 17.3 |
| automatic | shallow | python_root_only | 0.122 | 0.120-0.135 | 8,215,477 | 290.6 |
| automatic | shallow | original_override | 1.599 | 1.572-1.623 | 625,482 | 22.1 |
| automatic | wide | normal | 0.571 | 0.562-0.583 | 1,752,330 | 100.0 |
| automatic | wide | empty_dict | 0.673 | 0.670-0.705 | 1,485,555 | 84.8 |
| automatic | wide | empty_tuple | 2.895 | 2.869-2.919 | 345,457 | 19.7 |
| automatic | wide | root_one_reused | 2.708 | 2.621-3.010 | 369,339 | 21.1 |
| automatic | wide | root_one_fresh | 2.799 | 2.775-3.285 | 357,307 | 20.4 |
| automatic | wide | root_all_reused | 7.048 | 6.930-7.250 | 141,885 | 8.1 |
| automatic | wide | python_root_only | 0.482 | 0.478-0.499 | 2,075,942 | 118.5 |
| automatic | wide | original_override | 2.742 | 2.703-2.832 | 364,748 | 20.8 |
| automatic | diamond | normal | 0.456 | 0.444-0.541 | 2,192,855 | 100.0 |
| automatic | diamond | empty_dict | 0.554 | 0.532-0.587 | 1,806,464 | 82.4 |
| automatic | diamond | empty_tuple | 2.290 | 2.260-2.710 | 436,727 | 19.9 |
| automatic | diamond | root_one_reused | 2.134 | 2.056-2.562 | 468,521 | 21.4 |
| automatic | diamond | root_one_fresh | 2.163 | 2.135-2.454 | 462,316 | 21.1 |
| automatic | diamond | root_all_reused | 2.665 | 2.578-3.105 | 375,183 | 17.1 |
| automatic | diamond | python_root_only | 0.127 | 0.123-0.141 | 7,848,155 | 357.9 |
| automatic | diamond | original_override | 2.219 | 2.170-2.672 | 450,749 | 20.6 |
| automatic | diamond | nested_reused | 2.165 | 2.138-2.632 | 461,996 | 21.1 |
| automatic | diamond | nested_exact | 2.094 | 2.043-2.430 | 477,555 | 21.8 |
| automatic | deep | normal | 25.720 | 25.355-26.269 | 38,880 | 100.0 |
| automatic | deep | empty_dict | 25.756 | 25.083-26.414 | 38,826 | 99.9 |
| automatic | deep | empty_tuple | 110.738 | 109.145-113.244 | 9,030 | 23.2 |
| automatic | deep | root_one_reused | 112.450 | 110.343-114.719 | 8,893 | 22.9 |
| automatic | deep | root_one_fresh | 114.416 | 109.862-124.600 | 8,740 | 22.5 |
| automatic | deep | root_all_reused | 113.746 | 109.981-117.403 | 8,792 | 22.6 |
| automatic | deep | python_root_only | 0.131 | 0.128-0.133 | 7,654,825 | 19688.1 |
| automatic | deep | original_override | 114.953 | 111.095-123.666 | 8,699 | 22.4 |
| automatic | deep | nested_reused | 114.948 | 111.636-118.117 | 8,700 | 22.4 |

Cases rejected by current runtime (not timed):
- automatic/shallow/root_args_tuple: ShallowRootAB.__init__() got multiple values for argument 'a'
- automatic/wide/root_args_tuple: Wide8Root.__init__() got multiple values for argument 'l0'
- automatic/diamond/root_args_tuple: DiamondRoot.__init__() got multiple values for argument 'left'
- automatic/deep/root_args_tuple: Depth9Root.__init__() got multiple values for argument 'left'

Case semantics:
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
