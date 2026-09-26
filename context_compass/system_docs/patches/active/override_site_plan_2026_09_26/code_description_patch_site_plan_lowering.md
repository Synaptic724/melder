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
   lock (cold path, no user code) and store (FIFO cap); call. `ov` None runs the normal plan (step 9).
2. Compile keys: if `"__args__"` is a key, return an arity dispatcher (per-call: `args = ov["__args__"]`;
   None -> arity 0; list/tuple -> len; else today's error) that compiles one plan per arity on first use.
3. Plan for (keys, arity): build/reuse the site graph (steps + topologies; built once per runtime); resolve
   keys; a key set with no winning operand -> the normal plan (step 9).
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
8. Placement (S2b-1, 2026-09-26; design L1/L3): kept steps are placed consumers before providers. The root is
   top level. A many site lives where its one consumer is built: inside the consumer's miss when the consumer
   is shared, otherwise at the consumer's own place. A shared site lives at the lowest context common to all its
   consumers. A shared site that carries a winning override is pinned to top level. Each shared site emits an
   inline hit read at its place and an out-of-line `_miss{i}(meld, ov, c{i}, ...)`: the sites placed inside it in
   step order, then build guard, recheck (P2 when pinned), construction, publication, `return v{i}`. Values from
   outer contexts arrive as arguments; dict mode passes `instance_results`; `many_store` is recomputed in each
   function that registers a disposal-bearing many.
9. Normal plan (S2b-2, 2026-09-26): at construction the runtime builds the site graph, resolves the empty key
   set and emits it with `normal_mode=True`: the plan is `def _site_plan_executor(meld)` and every miss drops
   `ov` from its parameters and calls (nothing reads it without winners). It is compiled through the code cache,
   exposed as `execute_normal`, installed by both hydrators as the inner no-overrides executor and used as the
   runtime's fallback. `normal_mode` with winners, conflicts or arity raises RuntimeError. Site-graph build errors
   surface unwrapped at hydration (first meld).

## Edge/Error Semantics
- Key validation errors: today's RuntimeError/ValueError texts, wrapped `MeldExecutionError("Failed to apply
  overrides.")` with the root spell id/name; not cached; retried on the next call.
- P2 and root refusal messages unchanged; unresolved inputs keep the interim failure-path conversion (S4).
- Pinning keeps P2 exact: a shared site with a winning override is always visited, so a rule on a stored site
  still raises even when the site's consumer is itself stored, and an unstored one is still built and
  published with the value.
- A stored shared site's children are not built (B2): constructors under it run only in its miss. Sibling
  construction order changes accordingly; providers still precede their consumers.

## Invariants and Idempotency
- Operands depend on the key set only (P3). No new locks; hits are lock-free reads.
- A plan is `def _site_plan_executor(meld, ov)` exec'd into its own namespace; its constants (spells, ids,
  helpers) are globals of that namespace, never default arguments, so a call copies nothing per constant
  (S2a, 2026-09-26: the empty-key-set plan runs at 98-102% of the inner no-overrides executor on 3.14t and
  GIL). No namespace name is assigned in the plan body.
- Concurrent first compiles of one key set produce equivalent plans; the dict write is a single store.
- A miss builds its children before taking its own guard, so a plan holds at most one build lock at a time, only
  across that site's recheck, construction and publication, as the straight-line lowering does; no user
  constructor runs under another site's build lock. Warm hits take no lock. Design L3's guard across children
  (risk R2) was dropped on 2026-09-26: it failed the pinned lock-order harness case per_conduit-root-meld-override.
  A cold race may build and drop the loser's children, as before.

## Explicit Non-Goals
- Retiring the old normal emitters (S2b-3); unresolved inputs decided in the plan (S4); Phase-5 overlay
  retirement (S5).
- A per-call cell for a site demanded only from misses of two different shared parents (design L1): such a
  site is placed at their common context instead, which never builds more than the straight-line form did.
