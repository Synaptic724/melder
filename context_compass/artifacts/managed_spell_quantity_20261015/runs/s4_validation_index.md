# S4 validation index (generated from the run logs; one summary line per log)

- runs/s4_red_gil0.txt:182-182  8 failed, 88 passed, 5 errors in 3.28s
- runs/s4_green_new_gil0.txt:4-4  197 passed in 3.80s
- runs/s4_green_new_gil1.txt:12-12  197 passed, 1 warning in 3.98s
- runs/s4_unit_aether_spellbook_gil0.txt:97-97  6874 passed in 35.97s
- runs/s4_unit_aether_spellbook_gil1.txt:105-105  6874 passed, 1 warning in 35.35s
- runs/s4_unit_rest_gil0.txt:36-36  2508 passed, 3 skipped, 7 xfailed in 126.78s (0:02:06)
- runs/s4_unit_rest_gil1.txt:44-44  2508 passed, 3 skipped, 7 xfailed, 1 warning in 130.47s (0:02:10)
- runs/s4_component_spellbook_gil0.txt:13-13  819 passed in 93.28s (0:01:33)
- runs/s4_component_spellbook_gil1.txt:21-21  819 passed, 1 warning in 110.18s (0:01:50)
- runs/s4_component_rest_gil0.txt:23-23  1545 passed, 23 skipped, 1 xfailed in 53.87s
- runs/s4_component_rest_gil1.txt:31-31  1545 passed, 23 skipped, 1 xfailed, 1 warning in 62.10s (0:01:02)
- runs/s4_integration_aether_gil0.txt:12-12  785 passed, 5 xfailed in 103.45s (0:01:43)
- runs/s4_integration_aether_gil1.txt:20-20  785 passed, 5 xfailed, 1 warning in 94.74s (0:01:34)
- runs/s4_integration_conduit_spellbook_mr_live_gil0.txt:15-15  1003 passed, 2 skipped, 1 xfailed, 2 xpassed in 35.75s
- runs/s4_integration_conduit_spellbook_mr_live_gil1.txt:23-23  1003 passed, 2 skipped, 1 xfailed, 2 xpassed, 1 warning in 32.31s
- runs/s4_integration_multithreading_gil0.txt:2-2  54 passed in 124.17s (0:02:04)
- runs/s4_integration_multithreading_gil1.txt:10-10  54 passed, 1 warning in 113.71s (0:01:53)
- runs/s4_docstring_recheck_gil0.txt:7-7  401 passed, 1 skipped in 53.39s

Resumable shards (scripts/resumable_pytest_shard.py; ids in s4_integration_crystallizer_ids.txt and
s4_experiments_ids.txt; per-part -v logs s4_integration_crystallizer_gil{0,1}_partNN.txt and
s4_experiments_gil{0,1}_part00.txt):
- runs/s4_resumable_summary.txt:1-1  crystallizer integration gil0 (tests/integration/melder/crystallizer, collected ids /tmp/m0_mq/s4_crys_all_ids.txt):
- runs/s4_resumable_summary.txt:2-2  COMPLETE: 279 ids; outcomes {'PASSED': 276, 'XFAIL': 3}
- runs/s4_resumable_summary.txt:3-3  crystallizer integration gil1:
- runs/s4_resumable_summary.txt:4-4  COMPLETE: 279 ids; outcomes {'PASSED': 276, 'XFAIL': 3}
- runs/s4_resumable_summary.txt:5-5  experimentation + experiments + tests/tests gil0:
- runs/s4_resumable_summary.txt:6-6  COMPLETE: 254 ids; outcomes {'PASSED': 250, 'SKIPPED': 4}
- runs/s4_resumable_summary.txt:7-7  experimentation + experiments + tests/tests gil1:
- runs/s4_resumable_summary.txt:8-8  COMPLETE: 254 ids; outcomes {'PASSED': 250, 'SKIPPED': 4}

Routing probe (probes/probe_release_routing_cost.py, 200,000 cycles x 7 rounds):
- runs/s4_probe_release_routing_gil0.txt:1-1  python 3.14.7 gil=disabled melder=0.2.8243 cycles=200000 rounds=7
- runs/s4_probe_release_routing_gil0.txt:2-2  A put_back                         min    65.9 ns  median    68.2 ns  routing +   0.0 (min) +   0.0 (median)
- runs/s4_probe_release_routing_gil0.txt:3-3  B registry.release                 min   117.0 ns  median   121.2 ns  routing +  51.1 (min) +  53.1 (median)
- runs/s4_probe_release_routing_gil0.txt:4-4  C ReleaseManagedSpell().release    min   210.3 ns  median   212.4 ns  routing + 144.4 (min) + 144.2 (median)
- runs/s4_probe_release_routing_gil1.txt:1-1  python 3.14.7 gil=enabled melder=0.2.8243 cycles=200000 rounds=7
- runs/s4_probe_release_routing_gil1.txt:2-2  A put_back                         min    68.2 ns  median    69.3 ns  routing +   0.0 (min) +   0.0 (median)
- runs/s4_probe_release_routing_gil1.txt:3-3  B registry.release                 min   117.8 ns  median   119.4 ns  routing +  49.6 (min) +  50.2 (median)
- runs/s4_probe_release_routing_gil1.txt:4-4  C ReleaseManagedSpell().release    min   204.6 ns  median   207.1 ns  routing + 136.5 (min) + 137.9 (median)

Singleton call cost (probes/probe_singleton_call_cost.py, 200,000 calls x 7 rounds, two passes per factory):
- runs/s4_probe_singleton_call_gil0.txt:1-1  python 3.14.7 gil=disabled melder=0.2.8243 calls=200000 rounds=7
- runs/s4_probe_singleton_call_gil0.txt:2-2  Aether()               min   70.0 ns  median   71.8 ns
- runs/s4_probe_singleton_call_gil0.txt:3-3  ReleaseManagedSpell()  min   69.3 ns  median   70.2 ns
- runs/s4_probe_singleton_call_gil0.txt:4-4  Aether()               min   68.9 ns  median   69.4 ns
- runs/s4_probe_singleton_call_gil0.txt:5-5  ReleaseManagedSpell()  min   69.7 ns  median   70.3 ns
- runs/s4_probe_singleton_call_gil1.txt:1-1  python 3.14.7 gil=enabled melder=0.2.8243 calls=200000 rounds=7
- runs/s4_probe_singleton_call_gil1.txt:2-2  Aether()               min   69.7 ns  median   71.8 ns
- runs/s4_probe_singleton_call_gil1.txt:3-3  ReleaseManagedSpell()  min   70.2 ns  median   71.1 ns
- runs/s4_probe_singleton_call_gil1.txt:4-4  Aether()               min   68.4 ns  median   68.9 ns
- runs/s4_probe_singleton_call_gil1.txt:5-5  ReleaseManagedSpell()  min   69.7 ns  median   70.9 ns
