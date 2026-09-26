# Code Description Patch: key-set plan compile and emission

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Component: shared_assets/site_plan_override_runtime.py, shared_assets/site_plan_lowering.py
- Task: TASK-2026-09-26-build-site-plan-lowering
- Created: 2026-09-26T12:36:15Z

## Trigger Justification
New per-key-set compile pipeline, emitted locking/registration and per-call dispatch on the free-threaded
hot path.

## Control-Flow Description
1. Dispatch: `keys = tuple(ov)`; `plan = plans.get(keys)`; on a miss compile under the runtime's compile
   lock (cold path, no user code) and store (FIFO cap); call. `ov` None runs the inner no-overrides executor.
2. Compile keys: if `"__args__"` is a key, return an arity dispatcher (per-call: `args = ov["__args__"]`;
   None -> arity 0; list/tuple -> len; else today's error) that compiles one plan per arity on first use.
3. Plan for (keys, arity): build/reuse the site graph (steps + topologies; built once per runtime); resolve
   keys; empty non-args key set with arity 0 -> the inner no-overrides executor.
4. Demand: from the root site, follow dependency sites of every parameter that has no winning operand.
   Steps whose instance key is not demanded are dropped.
5. Operand per (step, parameter): winning key -> `ov[key]` (or `args[i]`); else dependency locals
   (collection -> list, one non-collection -> value, several -> list, zero-member required collection -> []).
   Steps with a contract payload are not direct calls (step 6).
6. Emit per kept step, in step order:
   - many: direct call `v = t(<operands>)` (positional while legal, then keywords); disposal-bearing many
     registers with `add_many_creations` on the innermost scope store.
   - shared: route by existence to its store; hit (`_creations.get`) -> reuse (or P2 raise if it carries a
     winning override); miss -> slot guard (per-conduit, spellspace, cluster, lineage; Spell lock for
     `unique` with the lock hint), recheck, construct, publish (`_creations[sid] = v` without disposal,
     `add_creation` with disposal), as the manifest lowering does.
   - steps that are not a plain callable call (existing creation, non-callable spell, contract payload,
     contract positional override, a parameter that cannot be passed in order) construct through the
     generic helper; with supplied values the overridden parameters are masked out and the values applied
     last.
   - constructor failures go through `_raise_meld_construction_error` with the supplied names/positional
     count of that call.
7. Conflicts: one guard per equal-rank pair, before any construction.

## Edge/Error Semantics
- Key validation errors: today's RuntimeError/ValueError texts, wrapped `MeldExecutionError("Failed to apply
  overrides.")` with the root spell id/name; not cached; retried on the next call.
- P2 and root refusal messages unchanged; unresolved inputs keep the interim failure-path conversion (S4).

## Invariants and Idempotency
- Operands depend on the key set only (P3). No new locks; hits are lock-free reads.
- A plan is `def _site_plan_executor(meld, ov)` exec'd into its own namespace; its constants (spells, ids,
  helpers) are globals of that namespace, never default arguments, so a call copies nothing per constant
  (S2a, 2026-09-26: the empty-key-set plan runs at 98-102% of the inner no-overrides executor on 3.14t and
  GIL). No namespace name is assigned in the plan body.
- Concurrent first compiles of one key set produce equivalent plans; the dict write is a single store.

## Explicit Non-Goals
- Consumer-first shared misses (B2) and the normal lane switch (S2); unresolved inputs decided in the plan
  (S4); Phase-5 overlay retirement (S5).
