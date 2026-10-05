# Four static-strategy micro-shapes - VM 3.14.7t, GIL disabled, GC off during timing, 2026-10-01T01:22:43Z

Directional (2-core VM); 300k iterations per rep, best of 7, two rounds (both shown).

| candidate | shape | ns |
| --- | --- | ---: |
| S22 store lock type | RLock, with-statement | 44-49 |
| S22 | Lock, with-statement | 43-47 |
| S22 | RLock, explicit acquire/release | 30-31 |
| S22 | Lock, explicit acquire/release | 31-32 |
| S10 hit read | `d.get(sid)` + `is None` | 17.6-17.9 |
| S10 | `d[sid]` in try/except (hit) | 13.4-13.7 |
| S10 | `d[sid]` in try/except (MISS, KeyError path) | 70-71 |
| S40 key identity | `d.get(k)`, k is the stored key object | 14.1-15.1 |
| S40 | `d.get(k)`, k equal but a distinct object | 15.8-16.9 |
| S39 constant binding | plan reads constants as namespace globals | 27.6-30.8 |
| S39 | as default arguments (LOAD_FAST) | 29.3-31.1 |
| S39 | as closure cells | 30.6-32.9 |

Readings: RLock vs Lock is a wash on 3.14t (S22 dropped); the with-statement itself costs ~14 ns over explicit
acquire/release (that is the A1 vs A3 gap of the register_many shapes); a subscript hit saves ~4 ns and a miss
costs ~+50 ns (zero-cost exceptions make the KeyError path 70 ns, not microseconds); an identical key object
saves ~2 ns per lookup; globals are already the fastest constant binding on 3.14 (S39 dropped).

Script: static_micro_shapes.py (this folder).
