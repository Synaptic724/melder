# S6 validation index (generated from the run logs by scripts/s6_validation_index.py)

Story tests, red before the change and green after (pytest -q; discard, owner-stamp unit, integration):
- runs/s6_red_gil0.txt:153-153  31 failed, 11 passed in 3.63s
- runs/s6_red_gil1.txt:161-161  31 failed, 11 passed, 1 warning in 3.60s
- runs/s6_green_gil0.txt:2-2  42 passed in 3.60s
- runs/s6_green_gil1.txt:10-10  42 passed, 1 warning in 3.30s

Transfer suites (pytest -q):
- runs/s6_transfer_unit_gil0.txt:13-13  846 passed in 9.80s
- runs/s6_transfer_unit_gil1.txt:13-13  846 passed in 9.29s
- runs/s6_transfer_component_gil0.txt:2-2  69 passed in 24.09s
- runs/s6_transfer_component_gil1.txt:2-2  69 passed in 23.73s
- runs/s6_transfer_integration_gil0.txt:3-3  135 passed in 43.81s
- runs/s6_transfer_integration_gil1.txt:3-3  135 passed in 41.31s

Whole tree (pytest -q):
- runs/s6_unit_aether_spellbook_gil0.txt:98-98  6981 passed in 58.75s
- runs/s6_unit_aether_spellbook_gil1.txt:98-98  6981 passed in 59.38s

Whole tree, resumable shards (scripts/resumable_pytest_shard.py, pytest -v part logs; unit-rest, component and experiments id lists are S5's, S6 adds no tests there):
- s6_unit_rest_gil0: 2518 ids (s6_unit_rest_ids.txt); outcomes {'PASSED': 2508, 'SKIPPED': 3, 'XFAIL': 7}; 2 part logs
- s6_unit_rest_gil1: 2518 ids (s6_unit_rest_ids.txt); outcomes {'PASSED': 2508, 'SKIPPED': 3, 'XFAIL': 7}; 2 part logs
- s6_component_gil0: 2411 ids (s6_component_ids.txt); outcomes {'PASSED': 2387, 'XFAIL': 1, 'SKIPPED': 23}; 2 part logs
- s6_component_gil1: 2411 ids (s6_component_ids.txt); outcomes {'PASSED': 2387, 'XFAIL': 1, 'SKIPPED': 23}; 2 part logs
- s6_integration_gil0: 2150 ids (s6_integration_ids.txt); outcomes {'PASSED': 2137, 'XFAIL': 9, 'XPASS': 2, 'SKIPPED': 2}; 10 part logs
- s6_integration_gil1: 2150 ids (s6_integration_ids.txt); outcomes {'PASSED': 2137, 'XFAIL': 9, 'XPASS': 2, 'SKIPPED': 2}; 9 part logs
- s6_experiments_gil0: 254 ids (s6_experiments_ids.txt); outcomes {'PASSED': 250, 'SKIPPED': 4}; 1 part logs
- s6_experiments_gil1: 254 ids (s6_experiments_ids.txt); outcomes {'PASSED': 250, 'SKIPPED': 4}; 1 part logs

Probe (probes/probe_s6_managed_transfer.py, gil1), before and after the change:
- runs/s6_probe_managed_transfer_before_gil1.txt:1-1  A move (default), active member only
- runs/s6_probe_managed_transfer_before_gil1.txt:5-5  spell owner store is target's: True
- runs/s6_probe_managed_transfer_before_gil1.txt:8-8  B move with a version parked after conjure, then a notch to it on the target
- runs/s6_probe_managed_transfer_before_gil1.txt:9-9  parked owner store is owner's before: True pool: True
- runs/s6_probe_managed_transfer_before_gil1.txt:10-10  parked pool in target store: True in owner store: False
- runs/s6_probe_managed_transfer_before_gil1.txt:11-11  parked owner store after: owner's = True target's = False owner conduit id = target: True
- runs/s6_probe_managed_transfer_before_gil1.txt:12-12  meld after notch raised: MeldExecutionError [MELD] Execution failed for spell 'Session' (1d3b6678cc89c02d7ee8225b3518d6b7e1653dfe762cae8b24e498f14b1af
- runs/s6_probe_managed_transfer_before_gil1.txt:13-13  C no move
- runs/s6_probe_managed_transfer_before_gil1.txt:18-18  D failed transfer, move
- runs/s6_probe_managed_transfer_before_gil1.txt:20-20  transfer raised: RuntimeError forced failure after the creations step
- runs/s6_probe_managed_transfer_before_gil1.txt:24-24  spell owner store: owner's = False target's = True
- runs/s6_probe_managed_transfer_before_gil1.txt:25-25  owner meld/release after rollback raised: MeldExecutionError [MELD] Execution failed for spell 'Session' (ae7b4bdc357620626af54e846d0272e1f41ddc4e6baf
- runs/s6_probe_managed_transfer_before_gil1.txt:26-26  E failed transfer, no move
- runs/s6_probe_managed_transfer_before_gil1.txt:28-28  transfer raised: RuntimeError forced failure after the creations step
- runs/s6_probe_managed_transfer_before_gil1.txt:32-32  spell owner store: owner's = False target's = True
- runs/s6_probe_managed_transfer_before_gil1.txt:33-33  owner meld after rollback: new object
- runs/s6_probe_managed_transfer_before_gil1.txt:34-34  owner meld/release after rollback raised: ValueError Session is managed by 2 pools: spell_id=ae7b4bdc357620626af54e846d0272e1f41ddc4e6baf3a75fc0301b3a
- runs/s6_probe_managed_transfer_before_gil1.txt:35-35  F unique: failed transfer (move), then a meld on the owner
- runs/s6_probe_managed_transfer_before_gil1.txt:36-36  transfer raised: RuntimeError
- runs/s6_probe_managed_transfer_before_gil1.txt:37-37  spell owner store: owner's = False target's = True
- runs/s6_probe_managed_transfer_before_gil1.txt:38-38  owner store holds the first object: True
- runs/s6_probe_managed_transfer_before_gil1.txt:39-39  owner meld returns the first object: False | target store holds an object: True
- runs/s6_probe_managed_transfer_before_gil1.txt:40-40  G unique: version parked after conjure, moved, notched in on the target
- runs/s6_probe_managed_transfer_before_gil1.txt:41-41  object stored in: owner store = True target store = False
- runs/s6_probe_managed_transfer_after_gil1.txt:5-5  A move (default), active member only
- runs/s6_probe_managed_transfer_after_gil1.txt:9-9  spell owner store is target's: True
- runs/s6_probe_managed_transfer_after_gil1.txt:12-12  B move with a version parked after conjure, then a notch to it on the target
- runs/s6_probe_managed_transfer_after_gil1.txt:13-13  parked owner store is owner's before: True pool: True
- runs/s6_probe_managed_transfer_after_gil1.txt:14-14  parked pool in target store: True in owner store: False
- runs/s6_probe_managed_transfer_after_gil1.txt:15-15  parked owner store after: owner's = False target's = True owner conduit id = target: True
- runs/s6_probe_managed_transfer_after_gil1.txt:16-16  meld after notch: Session from target pool: 1
- runs/s6_probe_managed_transfer_after_gil1.txt:17-17  C no move
- runs/s6_probe_managed_transfer_after_gil1.txt:22-22  D failed transfer, move
- runs/s6_probe_managed_transfer_after_gil1.txt:24-24  transfer raised: RuntimeError forced failure after the creations step
- runs/s6_probe_managed_transfer_after_gil1.txt:28-28  spell owner store: owner's = True target's = False
- runs/s6_probe_managed_transfer_after_gil1.txt:29-29  owner meld after rollback: reused
- runs/s6_probe_managed_transfer_after_gil1.txt:31-31  E failed transfer, no move
- runs/s6_probe_managed_transfer_after_gil1.txt:33-33  transfer raised: RuntimeError forced failure after the creations step
- runs/s6_probe_managed_transfer_after_gil1.txt:37-37  spell owner store: owner's = True target's = False
- runs/s6_probe_managed_transfer_after_gil1.txt:38-38  owner meld after rollback: reused
- runs/s6_probe_managed_transfer_after_gil1.txt:40-40  F unique: failed transfer (move), then a meld on the owner
- runs/s6_probe_managed_transfer_after_gil1.txt:41-41  transfer raised: RuntimeError
- runs/s6_probe_managed_transfer_after_gil1.txt:42-42  spell owner store: owner's = True target's = False
- runs/s6_probe_managed_transfer_after_gil1.txt:43-43  owner store holds the first object: True
- runs/s6_probe_managed_transfer_after_gil1.txt:44-44  owner meld returns the first object: True | target store holds an object: False
- runs/s6_probe_managed_transfer_after_gil1.txt:45-45  G unique: version parked after conjure, moved, notched in on the target
- runs/s6_probe_managed_transfer_after_gil1.txt:46-46  object stored in: owner store = False target store = True

Not run, by scope: no emission capture (S6 changes no codegen file, so no emitted plan can move) and
no benchmark (S6 changes no meld path; the transfer is a cold control-plane operation).
