# Architecture patch: many_child_follows_holder_2026_10_14

## Metadata
- Patch ID: many_child_follows_holder_2026_10_14
- Status: completed - landed 0.2.8235 and promoted to src_architecture, src_components and tests_components (2026-10-14)
- Owner: user (rule); melder_1 (synaptic_python_developer) (patch)
- Tickets: EPIC-2026-10-14-many_child_follows_holder; TASK-2026-10-14-fix_many_child_follows_holder

## Objective
Apply the owner's rule (2026-10-14): a slotted holder's `many` children belong to whatever owns the holder. The site
plan builds a holder's `many` child inside the holder's first build (`_miss{i}`) but registered a disposal-bearing
child in the meld's innermost scope (`many_store`: the spellspace store, else the melding conduit's store), while the
holder is published to its own store `c{i}`. When that scope ends before the holder's owner, the child's disposal
runs under a live holder. Proven on 0.2.8234 for `unique`, `unique_per_conduit`, lineage and cluster holders,
automatic and dynamic, by TASK-2026-10-14-prove_many_child_registration_bug. The opt-in singleton specializer also
builds and records an unused child on every warm meld of a `many` root over a captured `unique` holder.

## Non-goals
- Purge semantics: purging a holder disposes the holder only; its children wait for its store's teardown (open).
- Ownership transfer moving a holder's children (open); managed_spell_quantity pools (separate epic).
- No public API change, no warm-path change, no record or cache format change, no cache generation bump.

## Changed components
| component | change | rationale |
| --- | --- | --- |
| SpellCompiler codegen: site-plan lowering | a `many` step built inside `_miss{i}` registers in `c{i}` | the child belongs to its holder's owner |
| SpellCompiler codegen: generalized hydrator | the specializer declines a graph where a `many` row feeds a non-`many` row | a straight-line body cannot build a child only on its holder's miss |
| Meld Resolution Runtime (docs) | store-selection and live-creation probe text | a holder's children now sit with the holder's owner |

## Invariants
1. A `many` step placed inside a shared site's `_miss{i}` registers in `c{i}`, the store the site publishes to: the
   spell-owning conduit's store for `unique`, `meld._conduit_creations` for `unique_per_conduit`,
   `meld._spellspace_creations` for `unique_per_spell_space`, `meld._root_creations` for lineage, the elected
   leader's store for cluster.
2. A `many` step placed at the plan's top level (the children of a `many` root, the root itself) registers in the
   meld's innermost scope, unchanged.
3. Children are built and registered before the site's build guard is taken; `register_many` stays a leaf under the
   store lock. No lock and no lock-order edge is added.
4. Warm paths are unchanged: every line outside the misses is emitted exactly as before.
5. The singleton specializer declines (keeps the plain door) a graph in which any `many` row is a dependency of a
   non-`many` row; every other graph specializes as before.
6. A child is disposed exactly once - when its holder's owner's store is disposed (or by an explicit purge) - never
   when a narrower melding scope ends.

## Interface deltas
- Internal: `SitePlanEmission._emit_many(index, step, indent, lines, store)`; `_emit_context` registers top-level
  children through `many_store` and a miss's children through `c{i}`; `_emit_miss` no longer emits the innermost-scope
  prologue. New pure helper `rows_feed_many_into_non_many_step(rows)` beside `select_specializable_step_indexes`,
  called by `_install_specializing_door`.
- Behaviour: where a shared site's disposal-bearing `many` children are recorded, hence when they are disposed; a
  scope's live-creation probe for a `many` spell no longer counts children whose holder another store owns.
- Persisted: none. Generalized and many_only cache packages carry manifest rows, and plans are emitted from them at
  hydration, so 0.2.8234 bundles hydrate into the fixed plans (and the release field cold-resets them across the
  notch anyway).

## Migration order
Red tests on 0.2.8234 -> this patch -> src -> the updated unit test -> new tests green (GIL off and on) -> full tree
-> component docs -> architecture doc and indexes -> graph -> notch 0.2.8235 and release note -> patch archived ->
assets and llm_support last.

## Rollback
Revert `site_plan_lowering.py`, `generalized_hydrator.py`, `generalized_manifest_no_overrides_compiler.py` and the
test changes. Nothing persisted depends on the change.

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1, 6 | component: 7 routes (scope end leaves the child open; the owner's end disposes it once) and store ownership for 9 cases; nested and override routes; integration: borrower and cluster member |
| 2 | existing many-registration tests (a `many` root and its `many` children stay in the innermost scope) |
| 3 | unit: a miss takes its guard only after its children; the store lock is a leaf (existing) |
| 4 | emitted plan sources diffed before and after for representative shapes |
| 5 | component: the specializer test (one child built and recorded); existing specializer install tests |
