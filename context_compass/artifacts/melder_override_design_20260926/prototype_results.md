# Design v2 prototype: results (E1-E4)

Date: 2026-09-26. Author: melder_0. Task: tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md.
Design: design_v2.md. Production unchanged: every run used a VM copy of src/ (synced 2026-09-26T10:56Z,
0.2.54 plus today's changes), automatic mode, disk caching off. Builds: CPython 3.14.7 free-threaded
(3.14t) and 3.14.7 with the GIL.

## How the prototype works (E1)

`v2_prototype.py` builds the site graph from a live, conjured root spell (its Phase-9 model and Phase-10
steps), compiles one plan per key set, and swaps the spell's `CreationContext` executor slots at run time
(`SlotSwitch`). Public `Conduit.meld` calls then run the v2 plans; switching back restores today's
executors. It supports `many` and `unique_per_conduit` sites with a `many` root; PATH, `*`, `**` and root
positional keys; P1 cuts, P2 errors, P3 static operands, the E1 conflict guard, and unresolved inputs
decided in the plan. Timings interleave current and v2 samples in one world, 7 repeats of about 30 ms.

## Headline

- **Construction.** Supplied branches are never built. Example: supplying 3 of 5 dependencies builds 3
  objects instead of 6; supplying both halves of a 511-node tree builds 1 instead of 511.
- **Override speed.** Root-key overrides run at 76-106% of today's normal meld on the small graphs (today:
  9-25%). On the deep graph, a deep-path override is within 3-6% of normal and supplying a subtree beats
  normal (185-190% for one half, 50-58x for both halves).
- **Normal speed.** Normal melds are equal or faster, 36-38% faster where a stored shared object has
  children. One regression to explain: deep normal is 2-5% slower.
- **Semantics.** 40 calls across 7 graphs, today vs v2 in fresh worlds. Every difference is one of the
  predicted changes B1-B7. Results are identical on 3.14t and GIL.
- **Threads.** 200 rounds of 8 threads each through nested shared misses: one construction per slot,
  identical shared instances, no deadlock, on both builds.

## E3: behavior and constructor counts

Constructor counts per call. Full rows, including result structure, are in `prototype_results_0254/e3_*.json`.

| Graph | Call | Today | v2 | Note |
| --- | --- | --- | --- | --- |
| many_shallow `Root(a: A, b: B)` | `{"a"}` | A, B, Root | B, Root | B1 |
| many_shallow | `{"a", "b"}` | A, B, Root | Root | B1 |
| many_shallow | `(x,)` and `(x, y)` | error: multiple values for 'a' | works | B5 |
| many_shallow | `{"nosuch"}` | Failed to apply overrides | same error | unchanged |
| epic_five `Consumer(a..e)` | `{"a", "b", "c"}` | 6 objects | 3 objects | B1 (epic example) |
| tree4 (15 objects) | `{"left"}` | 15 | 8 | B1 |
| tree4 | `{"left", "right"}` | 15 | 1 | B1 |
| tree4 | `{"**left"}` | 15 | 4 | B1: every `left` is supplied, so only the right spine is built |
| gen_mixed `Root(a, s: S)`, `S(x: X)` shared | normal, S stored | A, Root, X | A, Root | B2: X no longer built under a stored S |
| gen_mixed | `{"s"}`, S stored | A, Root, X | A, Root | B1 |
| gen_mixed | `{"s>x"}`, S stored | X, then P2 error | A, then P2 error | P2 kept; both build one object first |
| gen_mixed | `{"s>x"}` on a cold world | A, Root, S, X | A, Root, S | Both give S the supplied x; only today builds X |
| gen_mixed | `{"s"}` on a cold world | A, Root, S, X (S stored) | A, Root (S not built) | B1 side effect |
| gen_diamond (S shared under L and R) | `{"l"}`, S stored | L, R, Root, X | R, Root | B1 + B2 |
| gen_diamond | `{"*s"}` | "matched 2 sockets" | same error | UNIQUE rule kept via path counts |
| p3_alias `Root(p: P, q: Q)`, D shared under both | `{"p": obj, "p>d>x": v}` | P built; D.x = v (leaks into q's D) | P not built; D.x default | B3: the Codex leak is fixed |
| p3_alias | `{"q>d>x"}`, `{"p>d>x"}` cold | D.x = v | D.x = v | same result; X not built in v2 |
| p3_alias | `{"p>d>x"}`, D stored | P2 error | P2 error | P2 kept |
| unresolved `Task(work: Package)` | none | A built, then UnresolvedInputError | UnresolvedInputError, nothing built | B6 |
| unresolved | `{"t": obj}` | Task built anyway: UnresolvedInputError | works | B1: a supplied Task is no longer constructed |

Two `same_result=False` rows in the JSON (`{"*a"}` and `{"**a"}` on many_shallow) differ only in object
numbering: earlier positional calls succeed in v2 and fail today, so the numbering shifts. The structures
are the same.

## E2: throughput (percent of today's normal meld; higher is faster)

Medians through public `Conduit.meld`. "Today" is the existing executor; the Python lower bound is a direct
constructor call with supplied inputs.

| Graph | Case | Today 3.14t | v2 3.14t | Today GIL | v2 GIL |
| --- | --- | ---: | ---: | ---: | ---: |
| shallow | normal | 100% (0.361 us) | 106% | 100% (0.319 us) | 107% |
| shallow | one root key | 25% | 77% | 24% | 76% |
| shallow | all root keys | 18% | 81% | 18% | 79% |
| shallow | positional `(a, b)` | error | 62% | error | 58% |
| shallow | `override=()` | 22% | 57% | 21% | 54% |
| wide | normal | 100% (0.581 us) | 105% | 100% (0.558 us) | 102% |
| wide | one root key | 22% | 83% | 25% | 84% |
| wide | all 8 root keys | 9% | 97% | 9% | 106% |
| wide | `override=()` | 21% | 67% | 23% | 65% |
| diamond | normal | 100% (0.454 us) | 107% | 100% (0.413 us) | 101% |
| diamond | one root key | 22% | 88% | 24% | 88% |
| diamond | `**leaf` | 21% | 83% | 22% | 80% |
| diamond | `left>leaf` | 22% | 82% | 24% | 78% |
| deep (511 objects) | normal | 100% (25.5 us) | 98% | 100% (20.1 us) | 95% |
| deep | 8-level path to one leaf | 23% | 97% | 22% | 94% |
| deep | one root key (half the tree) | 23% | 190% | 22% | 185% |
| deep | both root keys | 23% | 5780% (0.44 us) | 22% | 4998% (0.40 us) |
| deep | `override=()` | 23% | 97% | 22% | 93% |
| shared_mixed (S stored, S has a child) | normal | 100% (1.107 us) | 136% | 100% (1.004 us) | 138% |
| shared_mixed | one root key | 43% | 134% | 43% | 137% |
| shared_mixed | S supplied | 43% | 117% | 42% | 118% |
| shared_mixed | `override=()` | 41% | 100% | 40% | 97% |

The shared_mixed classes count constructions under a lock, so their constructors are heavier than the
benchmark classes. That is why supplying S (and building A instead of reading S from the store) looks
slower than supplying A.

## Where the remaining gap on small graphs is

Direct measurements on shallow (3.14t), in ns per call:

| Path | ns |
| --- | ---: |
| Public normal meld (fast door) | 334 |
| v2 normal plan called directly | 134 |
| Public override meld, one root key | 452 |
| v2 dispatcher called directly | 187 |
| v2 plan for that key set called directly | 111 |
| `plans.get(tuple(ov))` alone | 60 |

The plan itself is cheaper than the normal plan (one fewer constructor). The 118 ns gap to a normal meld
is outside the plan: the public override path skips the warm fast door that normal melds take (about 65 ns
more), and dispatch costs about 76 ns. Two follow-ups would close most of it: an override fast door
keyed like the normal one, and cheaper dispatch. Neither changes the design.

`override=()` stays at 54-67% on small graphs. Normalization builds `{"__args__": []}`, and the prototype
adds an arity wrapper call. Keying plans by (keys, arity) in the dispatcher would remove the wrapper.

Deep normal is 2-5% slower than today's normal. The cause is UNKNOWN: candidates are the consumer-first
emission order (versus today's providers-first order) and call layout. This belongs to S2's parity gate.

## E4: threads

`Root(p: P)`, `P(q: Q)`, `Q(x: X)` with P and Q `unique_per_conduit` and slow constructors (0.2 ms sleep),
plus `Root2(q: Q)`. Each round takes a fresh lesser conduit (empty stores). Eight threads start on a
barrier: four meld Root (nested misses: P's guard, then Q's), two meld Root2 (Q only) and two meld Root
with `{"p": obj}` (nothing shared demanded).

| Build | Variant | Rounds | Failures | Median round | Max round |
| --- | --- | ---: | ---: | ---: | ---: |
| 3.14t | today | 200 | 0 | 3.41 ms | 10.11 ms |
| 3.14t | v2 | 200 | 0 | 3.35 ms | 8.29 ms |
| GIL | today | 200 | 0 | 0.93 ms | 1.43 ms |
| GIL | v2 | 200 | 0 | 1.04 ms | 1.48 ms |

A failure is any error, P or Q built more than once, differing P or Q instances, or a thread alive after
20 s. A spy run (`prototype_e4_slot_check.py`) confirmed the v2 plans served the threads (120 normal-plan
calls in 20 rounds, one compiled key set `("p",)`). This checks correctness under contention. It does not
measure the cost of holding a shared guard while children are built at scale (R2).

## Compile cost (3.14t, prototype)

| Graph | Sites | Site graph | Normal plan | One key-set plan | Normal source lines |
| --- | ---: | ---: | ---: | ---: | ---: |
| shallow | 3 | 0.06 ms | 0.08 ms | 0.07 ms | 15 |
| wide | 9 | 0.13 ms | 0.16 ms | 0.16 ms | 39 |
| diamond | 5 | 0.09 ms | 0.12 ms | 0.10 ms | 23 |
| deep | 511 | 5.15 ms | 8.45 ms | 4.27 ms | 2047 |

The prototype reads signatures with `inspect`. Production would read the Phase-3 topology.

## Not covered by the prototype

- Other shared existences (`unique` with the Spell lock, lineage, cluster, spell space), collections,
  contract payloads, callable and existing-object spells, disposal registration on shared publish.
- Dynamic mode (CreationGate), the hooks lane, the SpellSpace door, persistence and cache generation 12.
- The per-call cell for a shared site demanded from two different misses.
- Lock hold-time cost at scale (R2).

## Reproduction

From the repository root of a src/tests copy, with `v2_prototype.py` and `v2_experiment.py` next to it and
`PYTHONPATH=src:.`:

```text
python v2_experiment.py correctness e3.json
python v2_experiment.py timing {shallow|wide|diamond|deep|shared_mixed} e2_<graph>.json
python v2_experiment.py threads 200 e4.json
python prototype_compile_cost.py
python prototype_door_breakdown.py
python prototype_e4_slot_check.py
```
