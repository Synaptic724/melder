# Architecture patch: Creations runs every disposal method and reports every failure (2026-09-27)

Patch id: creations_disposal_failures_2026_09_27. Ticket:
tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md. Owner direction in chat, 2026-09-27:
collect the error of every disposal-method failure and emit it.

## Scope and non-goals
Objective: one failing disposal method no longer stops an object's teardown, and every failure reaches the caller
with its original exception attached.
- Every declared disposal method of an object runs, in declared order, even after an earlier one raised.
- Each failing method yields one error; the error keeps the original exception as its cause.
- Reporting a failure never depends on the failing object's own `__str__`.
Non-goals:
- No change to disposal order (reverse creation order across and within buckets; declared order within an object).
- No change to which objects are disposed, to purge authority, or to locking.
- No change to how Conduit and SpellSpace handle the group they receive (Conduit logs it; others raise it).

## Changed components
| component | change | component patch |
| --- | --- | --- |
| Creations and SpellSpace | per-method failures, chained errors, safe text | component_patch_creations_and_spellspace.md |

## Interface and boundary deltas
- Public: none in signature. `Creations.cleanup`, `clear_all`, `reset_for_pool` and `purge` still raise one
  `ExceptionGroup`; it now holds one `RuntimeError` per failing METHOD (before: at most one per object). Each carries
  `__cause__` = the exception the method raised (before: none).
- The refused late publication (`add_creation`/`add_many_creations` on a cleaned store) still raises RuntimeError;
  with several failing methods its cause is an ExceptionGroup of them (one failure: that error, as before).
- Private: `_attempt_cleanup` returns `List[Exception]` (empty on success) instead of `Optional[Exception]`.

## Cross-component invariants
- Declared order within an object and reverse creation order across objects are unchanged.
- An object with no failing method produces no error; a scope with no failure raises nothing.
- A disposal failure never prevents the disposal of another object, including when the object's `__str__` raises.

## Migration and rollout order
1. Tests that fail on 0.2.79: skipped later methods, lost cause, failing `__str__` aborting the rest (cleanup,
   clear_all, purge), refused publication with several failures; public-path integration test.
2. `_attempt_cleanup` and its four call sites; docstrings.
3. Update the tests that pinned the old posture (the 2026-08-07 regression test, two private-helper tests).
4. Canonical docs, index, graph descriptor, release note, 0.01 notch, build assets and LLM bundles.

## Rollback
Revert the change set as one unit.

## Validation and evidence plan
| change | validation |
| --- | --- |
| later methods run | unit (cleanup, purge many bucket) and integration (real conduit teardown) |
| one error per failing method | unit: two failing methods give two errors, in declared order |
| chained cause | unit: `__cause__` is the original exception instance |
| safe object text | unit: failing `__str__` on a failing object; cleanup and clear_all still dispose the rest |
| refused publication | unit: two failing methods chain an ExceptionGroup of two |

## Ticket coverage map
One task: tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md.

## Unknowns and decision requests
- None open.
