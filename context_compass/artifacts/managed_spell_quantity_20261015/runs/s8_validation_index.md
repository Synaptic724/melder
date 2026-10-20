# S8 validation index (generated from the run logs by scripts/s8_validation_index.py)

Story tests, red on 0.2.8247 and green after the change (pytest -q; the new unit and integration files,
the cache-schema test, the lowering's managed tests):
- runs/s8_red_gil0.txt:1442-1442  37 failed, 71 passed in 8.87s
- runs/s8_green_new_gil0.txt:3-3  108 passed in 7.49s
- runs/s8_green_new_gil1.txt:11-11  108 passed, 1 warning in 7.60s

Whole tree (pytest -q):
- runs/s8_unit_aether_spellbook_gil0.txt:99-99  7035 passed in 40.78s
- runs/s8_unit_aether_spellbook_gil1.txt:107-107  7035 passed, 1 warning in 35.78s

Whole tree, resumable shards (scripts/resumable_pytest_shard.py, pytest -v part logs; id lists collected on the changed tree):
- s8_unit_rest_gil0: 2518 ids (s8_unit_rest_ids.txt); outcomes {'PASSED': 2508, 'SKIPPED': 3, 'XFAIL': 7}; 1 part logs
- s8_unit_rest_gil1: 2518 ids (s8_unit_rest_ids.txt); outcomes {'PASSED': 2508, 'SKIPPED': 3, 'XFAIL': 7}; 1 part logs
- s8_component_gil0: 2420 ids (s8_component_ids.txt); outcomes {'PASSED': 2396, 'XFAIL': 1, 'SKIPPED': 23}; 2 part logs
- s8_component_gil1: 2420 ids (s8_component_ids.txt); outcomes {'PASSED': 2396, 'XFAIL': 1, 'SKIPPED': 23}; 2 part logs
- s8_integration_gil0: 2178 ids (s8_integration_ids.txt); outcomes {'PASSED': 2165, 'XFAIL': 9, 'XPASS': 2, 'SKIPPED': 2}; 6 part logs
- s8_integration_gil1: 2178 ids (s8_integration_ids.txt); outcomes {'PASSED': 2165, 'XFAIL': 9, 'XPASS': 2, 'SKIPPED': 2}; 10 part logs
- s8_experiments_gil0: 254 ids (s8_experiments_ids.txt); outcomes {'PASSED': 250, 'SKIPPED': 4}; 1 part logs
- s8_experiments_gil1: 254 ids (s8_experiments_ids.txt); outcomes {'PASSED': 250, 'SKIPPED': 4}; 1 part logs

ManagedSpellLease as built (pytest -q: its unit file, the release registry, the managed component and two integration files):
- runs/s8_lease_suites_gil0.txt:3-3  94 passed in 32.15s
- runs/s8_lease_suites_gil1.txt:11-11  94 passed, 1 warning in 30.90s

Probes:
- runs/s8_owner_questions_after_gil0.txt:2-2  unique                   parked BEFORE conjure: stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:3-3  unique                   parked AFTER conjure:  stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:4-4  unique_per_conduit       parked BEFORE conjure: stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:5-5  unique_per_conduit       parked AFTER conjure:  stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:6-6  many                     parked BEFORE conjure: stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:7-7  many                     parked AFTER conjure:  stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:8-8  managed_spell_quantity   parked BEFORE conjure: stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:9-9  managed_spell_quantity   parked AFTER conjure:  stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:10-10  unique                   parked BEFORE conjure, conjure stamps parked (probe-only patch): stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:11-11  unique_per_conduit       parked BEFORE conjure, conjure stamps parked (probe-only patch): stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:12-12  many                     parked BEFORE conjure, conjure stamps parked (probe-only patch): stamped before notch=True; meld works -> ServiceB
- runs/s8_owner_questions_after_gil0.txt:13-13  managed_spell_quantity   parked BEFORE conjure, conjure stamps parked (probe-only patch): stamped before notch=True; meld works -> ServiceB
- runs/s8_managed_spell_lease_gil0.txt:1-1  PASS with-exit: inside count/idle/out=(1, 0, 1), after=(1, 1), reused=True, resets=[1]
- runs/s8_managed_spell_lease_gil0.txt:2-2  PASS with-exception: propagated='boom', count/idle after the block=(1, 1)
- runs/s8_managed_spell_lease_gil0.txt:3-3  PASS ReleaseManagedSpell().managed(obj): same object=True, released=True, idle=1
- runs/s8_managed_spell_lease_gil0.txt:4-4  PASS release-once: idle=1, resets=1, object raises after=True, with on a released lease raises=True
- runs/s8_managed_spell_lease_gil0.txt:5-5  PASS limited_quantity(1): second with-lease reuses the first object=True, built=1
- runs/s8_managed_spell_lease_gil0.txt:6-6  PASS release after root teardown: "The pool of managed spell 'Parser' was torn down with its root conduit; the object is your", released=True
- runs/s8_managed_spell_lease_gil0.txt:7-7  PASS managed_spell_meld of a unique spell: "managed_spell_meld leases a managed spell; 'Other' is unique. Meld it with meld("
- runs/s8_managed_spell_lease_gil0.txt:8-8  PASS a version staged before conjure, notched in, leased with `with`: count/idle=(1, 1)
- runs/s8_managed_spell_lease_gil0.txt:9-9  8 of 8 cases pass
- runs/s8_managed_spell_lease_gil1.txt:1-1  PASS with-exit: inside count/idle/out=(1, 0, 1), after=(1, 1), reused=True, resets=[1]
- runs/s8_managed_spell_lease_gil1.txt:2-2  PASS with-exception: propagated='boom', count/idle after the block=(1, 1)
- runs/s8_managed_spell_lease_gil1.txt:3-3  PASS ReleaseManagedSpell().managed(obj): same object=True, released=True, idle=1
- runs/s8_managed_spell_lease_gil1.txt:4-4  PASS release-once: idle=1, resets=1, object raises after=True, with on a released lease raises=True
- runs/s8_managed_spell_lease_gil1.txt:5-5  PASS limited_quantity(1): second with-lease reuses the first object=True, built=1
- runs/s8_managed_spell_lease_gil1.txt:6-6  PASS release after root teardown: "The pool of managed spell 'Parser' was torn down with its root conduit; the object is your", released=True
- runs/s8_managed_spell_lease_gil1.txt:7-7  PASS managed_spell_meld of a unique spell: "managed_spell_meld leases a managed spell; 'Other' is unique. Meld it with meld("
- runs/s8_managed_spell_lease_gil1.txt:8-8  PASS a version staged before conjure, notched in, leased with `with`: count/idle=(1, 1)
- runs/s8_managed_spell_lease_gil1.txt:9-9  8 of 8 cases pass
- runs/s8_existing_object_teardown_gil0.txt:1-1  notch=False: meld -> v1; v2 in store before notch=False, after meld=False; closed at teardown=[]
- runs/s8_existing_object_teardown_gil0.txt:2-2  notch=True: meld -> v2; v2 in store before notch=False, after meld=False; closed at teardown=[]

Not run, by scope: no emission capture - the lowering's change is the text of a runtime helper the plans
call (`_raise_missing_managed_pool`, bound into a plan's namespace), not code they contain, and no other
emitting code changed; no benchmark - the change is on conjure's cold path. Hosted CI and coverage: the
owner's.
