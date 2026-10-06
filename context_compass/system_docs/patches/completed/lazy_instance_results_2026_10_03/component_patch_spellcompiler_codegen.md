# Component patch: SpellCompiler codegen - site-plan lowering, lazy instance_results (S8)

- Patch id: lazy_instance_results_2026_10_03
- Component: SpellCompiler and Validation Pipeline (site-plan lowering of the generalized and many_only families)
- Owner: fable_0
- Created: 2026-10-03T18:51:39Z

<!-- BEGIN ENTRY: "SitePlanLowering: before and after" -->
## Before
In dict mode the plan body starts with `instance_results = {}`; after every kept step in every context
(top level and each `_miss{i}` body) the emitter appends `instance_results[key{i}] = v{i}`; every miss takes
`instance_results` as a parameter after its store; a generic step calls
`_construct_spell_instance(plan_step=st{i}, instance_results=instance_results)` (or the supplied-values
helper) and the helper reads the step's dependency keys from the dict. A warm creation of a dict-mode root
pays one dict allocation plus one store per step although nothing reads them (misses do not run).

## After
No top allocation, no stores, no dict parameter. Where a generic step is constructed, the emitter writes
`instance_results = {key{p}: v{p}, ...}` for the keys of the (masked) step's `dependency_resolution_order`,
in that order, binding each `key{p}` constant to the provider's instance key, or `instance_results = {}` for
a step that reads nothing (existing object, pure contract payload); the construct call is unchanged.
`_place` adds a generic member's providers (and a generic site's own providers) to its miss's outer values, so
the locals exist in scope. Direct steps are untouched. Cache generation 17.

## Interface deltas
- Private: `_dict_mode` removed; `_miss_arguments(index)` returns `[args?] + v...`; the class contract's
  "Dict mode" bullet rewritten.
- Public: none. Emitted-source shape above.
<!-- END ENTRY: "SitePlanLowering: before and after" -->

<!-- BEGIN ENTRY: "SitePlanLowering: state, failure, ordering, validation" -->
## State and failure deltas
- No new state. A failing miss raises the same errors: the construct helpers see the same values under the
  same keys; a missing key is impossible (`_place` raises at emission).
- Warm path: fewer bytecodes, no dict. Miss path: one small dict literal instead of inheriting the shared
  accumulating dict.

## Dependency and ordering
- Providers precede consumers (family order); `_emit_context` emits children before the guard; the literal is
  emitted immediately before the construct line, after every provider local is bound.

## Validation expectations
- Emitter unit tests: direct-mode source unchanged; dict-mode source has no top allocation, no stores, no dict
  miss parameter, and a literal with exactly the step's keys before each generic construct.
- Differential tests on the harness's dict-mode shapes (ContextRoot, wide8 over existing objects) and on a
  generic step with dependencies inside a miss: same objects, same errors on a failing miss.
- Component test: a real conjure of a root with an existing-object step melds warm and cold.
- Harness re-run: plan delta on the two dict-mode shapes (bar >= 15%).
<!-- END ENTRY: "SitePlanLowering: state, failure, ordering, validation" -->
