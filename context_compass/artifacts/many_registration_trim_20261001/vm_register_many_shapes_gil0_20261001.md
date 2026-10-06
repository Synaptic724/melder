# register_many candidate shapes - VM 3.14.7t, GIL disabled, GC off during timing, 2026-10-01T01:05:30Z

Directional (2-core VM). Stand-in store with the real RLock; 200k registrations per rep, best of 7, two rounds.

| shape | ns/registration |
| --- | ---: |
| today: add_many_creations(key, item, has_disposal_methods=True, disposal_methods=dm) -> _append_many_locked | 204-207 |
| A1: register_many(key, item, dm), with-lock, cleaned check, one get, first-use record, append | 104-111 |
| A2: A1 plus `type(bucket) is not list` check on an existing bucket | 115-126 |
| A3: A1 with explicit acquire/try/finally/release instead of the with statement | 99-100 |

Script: register_many_shapes.py (this folder). Run:
`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -X gil=0 register_many_shapes.py`
