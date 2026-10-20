# S5 validation index (generated from the run logs by scripts/s5_validation_index.py)

Story tests (pytest -q):
- runs/s5_green_unit_gil1.txt:5-5  223 passed in 10.03s
- runs/s5_green_unit_gil0.txt:5-5  223 passed in 10.25s
- runs/s5_green_component_gil1.txt:2-2  23 passed in 11.67s
- runs/s5_green_component_gil0.txt:2-2  23 passed in 10.68s
- runs/s5_green_integration_gil1.txt:2-2  7 passed in 39.33s
- runs/s5_green_integration_gil0.txt:2-2  7 passed in 37.75s

Whole tree (pytest -q):
- runs/s5_unit_aether_spellbook_gil0.txt:98-98  6951 passed in 58.42s
- runs/s5_unit_aether_spellbook_gil1.txt:98-98  6951 passed in 57.71s

Whole tree, resumable shards (scripts/resumable_pytest_shard.py, pytest -v part logs):
- s5_unit_rest_gil0: 2518 ids (s5_unit_rest_ids.txt); outcomes {'PASSED': 2508, 'SKIPPED': 3, 'XFAIL': 7}; parts s5_unit_rest_gil0_part00.txt, s5_unit_rest_gil0_part01.txt
- s5_unit_rest_gil1: 2518 ids (s5_unit_rest_ids.txt); outcomes {'PASSED': 2508, 'SKIPPED': 3, 'XFAIL': 7}; parts s5_unit_rest_gil1_part00.txt
- s5_component_gil0: 2411 ids (s5_component_ids.txt); outcomes {'PASSED': 2387, 'XFAIL': 1, 'SKIPPED': 23}; parts s5_component_gil0_part00.txt
- s5_component_gil1: 2411 ids (s5_component_ids.txt); outcomes {'PASSED': 2387, 'XFAIL': 1, 'SKIPPED': 23}; parts s5_component_gil1_part00.txt
- s5_integration_gil0: 2138 ids (s5_integration_ids.txt); outcomes {'PASSED': 2125, 'XFAIL': 9, 'XPASS': 2, 'SKIPPED': 2}; parts s5_integration_gil0_part00.txt, s5_integration_gil0_part01.txt, s5_integration_gil0_part02.txt, s5_integration_gil0_part03.txt, s5_integration_gil0_part04.txt
- s5_integration_gil1: 2138 ids (s5_integration_ids.txt); outcomes {'PASSED': 2125, 'XFAIL': 9, 'XPASS': 2, 'SKIPPED': 2}; parts s5_integration_gil1_part00.txt, s5_integration_gil1_part01.txt, s5_integration_gil1_part02.txt, s5_integration_gil1_part03.txt, s5_integration_gil1_part04.txt
- s5_experiments_gil0: 254 ids (s5_experiments_ids.txt); outcomes {'PASSED': 250, 'SKIPPED': 4}; parts s5_experiments_gil0_part00.txt
- s5_experiments_gil1: 254 ids (s5_experiments_ids.txt); outcomes {'PASSED': 250, 'SKIPPED': 4}; parts s5_experiments_gil1_part00.txt

Emission gate:
- runs/s5_emission_diff.txt:1-1  S5 emission diff: before = 0.2.8244 tree (s5_emission_before_0_2_8244.json.gz), after = working tree with S5
- runs/s5_emission_diff.txt:2-2  entries before=4461 after=4461
- runs/s5_emission_diff.txt:3-3  only before=0 only after=0 changed=0
- runs/s5_emission_diff.txt:4-4  error entries before=30 after=30 same keys=True
- runs/s5_emission_diff.txt:5-5  entries by family: {'door': 42, 'harness': 5, 't1': 3456, 't2': 750, 't3': 120, 't4': 72, 't5': 16}
- runs/s5_emission_diff.txt:6-6  RESULT: IDENTICAL

Warm lease-cycle benchmark (probes/probe_s5_warm_lease_cycle.py, 200,000 cycles x 7 rounds):
- runs/s5_bench_warm_lease_cycle_gil0.txt:1-1  python 3.14.7 gil=disabled melder=0.2.8244 cycles=200000 rounds=7
- runs/s5_bench_warm_lease_cycle_gil0.txt:2-2  A managed direct             min    312.9 ns  median    321.5 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:3-3  B many direct                min    211.9 ns  median    217.2 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:4-4  C unique direct              min    165.6 ns  median    167.2 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:5-5  D many holder of managed     min    363.8 ns  median    371.7 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:6-6  E many holder of many        min    268.1 ns  median    274.3 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:7-7  F managed direct, dynamic    min    727.8 ns  median    741.8 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:8-8  G many direct, dynamic       min    614.4 ns  median    622.8 ns
- runs/s5_bench_warm_lease_cycle_gil0.txt:9-9  pools after the run: [('Worker', 1, 1), ('DynWorker', 1, 1)]
- runs/s5_bench_warm_lease_cycle_gil1.txt:1-1  python 3.14.7 gil=enabled melder=0.2.8244 cycles=200000 rounds=7
- runs/s5_bench_warm_lease_cycle_gil1.txt:2-2  A managed direct             min    311.4 ns  median    319.7 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:3-3  B many direct                min    211.7 ns  median    214.3 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:4-4  C unique direct              min    168.1 ns  median    171.0 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:5-5  D many holder of managed     min    363.8 ns  median    366.3 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:6-6  E many holder of many        min    263.0 ns  median    266.5 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:7-7  F managed direct, dynamic    min    734.1 ns  median    743.6 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:8-8  G many direct, dynamic       min    603.3 ns  median    610.8 ns
- runs/s5_bench_warm_lease_cycle_gil1.txt:9-9  pools after the run: [('Worker', 1, 1), ('DynWorker', 1, 1)]
