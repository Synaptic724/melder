# Melder creation and override experiment

Python: 3.14.7 free-threading build (main, Sep  1 2026, 14:18:33) [MSC v.1944 64 bit (AMD64)]
GIL enabled: False
GC during samples: disabled; repeats: 7

Warm single-thread calls; disk cache disabled. Setup, assertions and explicit GC are outside timing.
Supplied dependencies may change graph work. Python root-only rows exclude all Melder behavior.
No init={} API or runtime optimization is implemented by this experiment.

| Mode | Graph | Case | Median us | Min-max us | Ops/s | % normal speed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| dynamic | solo | normal | 0.717 | 0.690-0.751 | 1,394,754 | 100.0 |
| dynamic | solo | empty_dict | 0.760 | 0.734-1.084 | 1,315,794 | 94.3 |
| dynamic | solo | empty_tuple | 1.046 | 1.031-1.071 | 956,057 | 68.5 |
| dynamic | solo | python_root_only | 0.100 | 0.098-0.102 | 9,980,538 | 715.6 |
| dynamic | scalar | normal | 0.725 | 0.714-0.738 | 1,379,430 | 100.0 |
| dynamic | scalar | empty_dict | 0.759 | 0.747-0.775 | 1,317,788 | 95.5 |
| dynamic | scalar | empty_tuple | 1.068 | 1.047-1.143 | 936,339 | 67.9 |
| dynamic | scalar | root_one_reused | 0.959 | 0.950-1.002 | 1,042,665 | 75.6 |
| dynamic | scalar | root_one_fresh | 0.996 | 0.976-1.132 | 1,003,653 | 72.8 |
| dynamic | scalar | root_args_tuple | 1.098 | 1.064-1.126 | 910,696 | 66.0 |
| dynamic | scalar | python_root_only | 0.158 | 0.154-0.169 | 6,342,522 | 459.8 |
| dynamic | shallow | normal | 0.867 | 0.859-1.079 | 1,153,979 | 100.0 |
| dynamic | shallow | empty_dict | 0.898 | 0.881-0.927 | 1,114,039 | 96.5 |
| dynamic | shallow | empty_tuple | 2.620 | 2.551-2.990 | 381,705 | 33.1 |
| dynamic | shallow | root_one_reused | 2.349 | 2.327-2.947 | 425,788 | 36.9 |
| dynamic | shallow | root_one_fresh | 2.370 | 2.339-5.054 | 421,981 | 36.6 |
| dynamic | shallow | root_all_reused | 3.018 | 2.954-6.305 | 331,398 | 28.7 |
| dynamic | shallow | python_root_only | 0.179 | 0.176-0.226 | 5,598,722 | 485.2 |
| dynamic | shallow | original_override | 2.401 | 2.376-2.672 | 416,521 | 36.1 |
| dynamic | wide | normal | 1.203 | 1.191-1.227 | 830,974 | 100.0 |
| dynamic | wide | empty_dict | 1.233 | 1.202-1.246 | 811,241 | 97.6 |
| dynamic | wide | empty_tuple | 4.203 | 4.128-4.404 | 237,932 | 28.6 |
| dynamic | wide | root_one_reused | 3.978 | 3.877-4.069 | 251,377 | 30.3 |
| dynamic | wide | root_one_fresh | 3.906 | 3.806-4.029 | 256,032 | 30.8 |
| dynamic | wide | root_all_reused | 9.866 | 9.653-10.038 | 101,356 | 12.2 |
| dynamic | wide | python_root_only | 0.534 | 0.524-0.539 | 1,873,713 | 225.5 |
| dynamic | wide | original_override | 3.924 | 3.818-3.950 | 254,835 | 30.7 |
| dynamic | diamond | normal | 1.008 | 0.980-1.027 | 992,478 | 100.0 |
| dynamic | diamond | empty_dict | 1.053 | 1.019-1.062 | 949,917 | 95.7 |
| dynamic | diamond | empty_tuple | 3.353 | 3.263-3.433 | 298,198 | 30.0 |
| dynamic | diamond | root_one_reused | 3.083 | 2.994-3.229 | 324,328 | 32.7 |
| dynamic | diamond | root_one_fresh | 3.109 | 3.087-3.168 | 321,686 | 32.4 |
| dynamic | diamond | root_all_reused | 3.782 | 3.733-3.845 | 264,380 | 26.6 |
| dynamic | diamond | python_root_only | 0.176 | 0.173-0.179 | 5,685,040 | 572.8 |
| dynamic | diamond | original_override | 3.302 | 3.249-3.414 | 302,835 | 30.5 |
| dynamic | diamond | nested_reused | 3.250 | 3.194-3.334 | 307,649 | 31.0 |
| dynamic | diamond | nested_exact | 3.095 | 3.050-3.163 | 323,105 | 32.6 |
| dynamic | deep | normal | 33.197 | 32.749-33.514 | 30,123 | 100.0 |
| dynamic | deep | empty_dict | 33.108 | 32.717-33.459 | 30,204 | 100.3 |
| dynamic | deep | empty_tuple | 155.758 | 153.389-157.772 | 6,420 | 21.3 |
| dynamic | deep | root_one_reused | 155.222 | 152.727-224.164 | 6,442 | 21.4 |
| dynamic | deep | root_one_fresh | 154.560 | 154.016-158.705 | 6,470 | 21.5 |
| dynamic | deep | root_all_reused | 158.209 | 155.198-169.484 | 6,321 | 21.0 |
| dynamic | deep | python_root_only | 0.210 | 0.207-0.217 | 4,767,578 | 15827.1 |
| dynamic | deep | original_override | 159.083 | 155.435-165.162 | 6,286 | 20.9 |
| dynamic | deep | nested_reused | 159.081 | 154.844-162.810 | 6,286 | 20.9 |

Cases rejected by current runtime (not timed):
- dynamic/shallow/root_args_tuple: ShallowRootAB.__init__() got multiple values for argument 'a'
- dynamic/wide/root_args_tuple: Wide8Root.__init__() got multiple values for argument 'l0'
- dynamic/diamond/root_args_tuple: DiamondRoot.__init__() got multiple values for argument 'left'
- dynamic/deep/root_args_tuple: Depth9Root.__init__() got multiple values for argument 'left'

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
