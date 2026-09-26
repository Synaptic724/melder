# Component Patch: override melds run per-key-set plans (SpellCompiler codegen creation, S3)

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Component: SpellCompiler and Validation Pipeline (Phase-11 codegen creation: many_only and generalized
  override lanes); Meld Resolution Runtime unchanged (same CreationContext slots and doors)
- Task: TASK-2026-09-26-build-site-plan-lowering
- Status: active
- Created: 2026-09-26T12:36:15Z

## Before
- An override meld runs `execute_with_overrides(meld, overrides)` built by the family finalize step (fresh
  conjure) or hydrator (cache hit): split the payload, resolve keys through the path-expanded targeting
  table on every call, key an executor by the resulting socket shape, and run ONE step list that builds
  every instance of the root graph, then substitutes supplied values at their sockets.
- Supplied dependencies and everything only they need are still built (design v2 row 1); `override=()`
  runs at about 20% of normal (row 2); root positional payloads over DI-injected parameters raise "got
  multiple values" (row 6); a PATH through a collection hits one member (row 8).

## After
- New `SitePlanOverrideRuntime` (shared_assets/site_plan_override_runtime.py) replaces the many_only and
  generalized `execute_with_overrides`. All three families are manifest-first, so fresh conjures and cache
  hits both build it in the family hydrator (`many_only_hydrator._hydrate_overrides_runtime`,
  `generalized_hydrator._hydrate_overrides_runtime`); the finalize steps are not in any live pipeline
  (corrected 2026-09-26T12:51:34Z). Its inputs are the root spell, the manifest's no-overrides step rows
  hydrated by the family's own row hydration, the inner no-overrides executor and the live Phase-3
  topologies.
- Per call: `plan = plans.get(tuple(overrides))`, compiled on first use of a key set, then `plan(meld, ov)`.
  The empty key set delegates to the inner no-overrides executor (normal speed).
- Plan compile (once per key set): site graph from the steps and topologies; `OverrideKeyResolver` (S1)
  gives winners, P1 cuts, positional placements and equal-rank conflicts; demand walks from the root and
  skips overridden parameters; the lowering emits straight-line code for the demanded steps only, in the
  steps' existing providers-first order (site_plan_lowering.py).
- Key errors keep today's texts, wrapped as `MeldExecutionError("Failed to apply overrides.")`, and are not
  cached. Equal-rank conflicts: identity, then `==` for plain scalars, otherwise the same wrapped error.
- Shared steps with a winning override raise today's "spell instance that already exists" error when
  stored (P2); the door's root refusal is unchanged. Registration, slot guards, Spell locks, disposal
  registration and store routing per existence are emitted as the live generalized manifest lowering emits
  them (generalized_manifest_no_overrides_compiler).
- Steps with a contract payload or contract positional payload construct through the family's generic
  helper (their dependencies are built as today), so contract values keep a single source.
- `__args__` of length N supplies the root's first N positional parameters and cuts their dependencies; a
  plan is compiled per arity; a non-list/tuple `__args__` raises today's error.

## Interface / State Deltas
- No public API change. CreationContext slots and door compilers unchanged.
- The overrides lane payload in the manifests is no longer read; it stays in the bundle until the old
  emitters are retired (then cache generation 14).
- Plans live on the runtime object captured by the override door; a FIFO cap (256 key sets) bounds key sets
  generated at run time.

## Behavior Deltas
- B1, B5, B7, B8 and B3 (design v2). Construction order of the remaining steps is unchanged (providers
  first); B2 stays with the normal lane (S2).

## Validation Expectations
- Existing override suites (component meld_overrides, meld_overrides_deep, integration overrides,
  resolution matrices, unresolved inputs, non-resolvable overrides, contracts) unchanged except documented
  B-changes; new tests for B1/B5/B7/B8 and constructor counts; override throughput via the owner's
  test_overrides_all.py graphs and the override performance experiment, 3.14t and GIL.

## Rollback
- Restore the two hydrator `_hydrate_overrides_runtime` functions; the new modules are then unused.
