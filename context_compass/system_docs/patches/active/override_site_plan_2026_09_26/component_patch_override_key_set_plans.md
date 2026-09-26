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
- B1, B5, B7, B8 and B3 (design v2). B2 (S2b-1, 2026-09-26): a stored shared site's children are not built;
  they are built just before their shared site, inside its miss, only when it is missing (providers still
  precede consumers). For normal melds see the S2b-2 section.

## Validation Expectations
- Existing override suites (component meld_overrides, meld_overrides_deep, integration overrides,
  resolution matrices, unresolved inputs, non-resolvable overrides, contracts) unchanged except documented
  B-changes; new tests for B1/B5/B7/B8 and constructor counts; override throughput via the owner's
  test_overrides_all.py graphs and the override performance experiment, 3.14t and GIL.

## Rollback
- Restore the two hydrator `_hydrate_overrides_runtime` functions; the new modules are then unused.

## S2b-2: normal melds on the same runtime (2026-09-26)

### Before
- Normal melds run the family's inner executor from the old emitters: generalized `hydrate_no_overrides_executor`
  (unrolled transient source for all-many non-registering graphs, else straight-line step source) and many_only
  `compile_no_overrides_codegen_creation_executor`. Every warm meld builds every transient site, including the
  children of stored shared sites. The generalized override runtime and its site graph are built at the first
  override meld; many_only builds its runtime at hydration.

### After
- Both hydrators build `SitePlanOverrideRuntime` at hydration (first meld). The runtime builds the site graph and
  compiles the empty-key-set plan in normal mode (`def _site_plan_executor(meld)`), exposed as `execute_normal`;
  the hydrators install it as the inner no-overrides executor under the same route-keyed doors (the fast-transient
  door flag is unchanged). `override=None` and payloads with no winning key run the same plan. The generalized
  override door reuses that runtime (one site graph per root). The opt-in singleton specializer keeps its body
  from the old emitter; its generic and deopt target is the plan. Solo-family roots are unchanged.

### Interface / State Deltas
- `SitePlanOverrideRuntime(steps, root_spell, root_instance_key)` takes no inner executor and exposes
  `execute_normal`. `SitePlanLowering.emit(..., normal_mode=True)` requires an empty resolution and arity 0.
- One site graph and step set per hydrated root, kept for override key sets. Manifests are unchanged, so there is
  no cache generation.

### Behavior Deltas
- B2 on normal melds: a warm normal meld no longer builds the children of a stored shared site (R4: those children
  are built just before their shared site, only when it is missing). Results are unchanged.
- The first meld of a root also builds its site graph (about 2 ms on a 511-site graph).

### Validation Expectations
- Parity gate (design S2): s2b2_parity.py, normal throughput at or above today on 3.14t and GIL (met
  2026-09-26T17:07:50Z); all suites on both builds; a normal-meld B2 component test, fresh and cached.

### Rollback
- Restore the hydrators' inner-executor construction; the old emitters stay in the tree until S2b-3.

## S4a: unresolved inputs decided in the plan (2026-09-26)

### Before
- A plan (normal or override) calls a constructor without an unresolved input; the call raises TypeError and the
  family's failure path converts it (`UnresolvedInputError.from_failed_construction`), so the error arrives after
  the consumer's dependencies were built, chained from the TypeError.

### After
- The lowering knows each kept site's UNRESOLVED_INPUT parameters without a winning key and raises
  `UnresolvedInputError` before anything under that consumer is built: at the plan top for top-level many sites,
  at the top of a shared site's miss for its many children and itself. Message, fields and type are unchanged;
  there is no TypeError cause. A stored consumer never demands the input. Solo roots and OVERRIDE_REQUIRED
  sockets are unchanged.

### Interface / State Deltas
- `UnresolvedInputError.for_unsupplied(spell, names)` (new classmethod; shares the message builder with
  `from_failed_construction`, which stays for the solo guard and the old emitters). `SitePlanRuntimeHelpers`
  gains `raise_unresolved_input`. No cache change (plans are built at hydration).

### Behavior Deltas
- B6 for the many_only and generalized families: nothing under the consumer is constructed, and `__cause__` is
  None instead of the binding TypeError.

### Validation Expectations
- Unit: raise before any construction, supplied key builds, stored consumer never demands, raise inside a shared
  miss before its children. Component: the unresolved-input suite per family (cause changes for plan families).
  All suites on 3.14t and GIL.

### Rollback
- Drop the emitted raises; the failure-path hook still converts constructor TypeErrors.

