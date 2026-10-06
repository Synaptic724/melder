# many registration split (VM, 3.14t GIL off) - run 1 (2026-09-27T22:58Z, inline harness)

| registration shape | ns per creation (VM) |
| --- | ---: |
| today: add_many_creations (disposal) | 384 |
| today: add_many_creations (no disposal) | 185 |
| RLock enter/exit alone | 67 |
| Lock enter/exit alone | 65 |
| trimmed A: per-key methods, one RLock, one append | 120 |
| trimmed B: lock-free append after first use | 63 |

# run 2 (2026-09-27T23:31Z, tests/experimentation/many_registration_split_experiment.py against a real Creations store)

| registration shape | ns per creation (VM) |
| --- | ---: |
| today: add_many_creations(sid, item, has_disposal_methods=True, disposal_methods=dm) | 305 |
| today: add_many_creations(sid, item) (no disposal) | 151 |
| today: _append_many_locked direct, no lock, disposal (the dict/list work alone) | 264 |
| RLock enter/exit alone | 57 |
| Lock enter/exit alone | 56 |
| trimmed A: per-key methods, RLock kept, one append | 103 |
| trimmed B: double-checked first use, lock-free append after | 62 |
| list.append alone | 39 |
