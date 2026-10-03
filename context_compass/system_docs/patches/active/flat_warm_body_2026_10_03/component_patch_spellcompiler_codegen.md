# Component patch: SpellCompiler and Validation Pipeline - site-plan lowering, shared-site read

- Patch id: flat_warm_body_2026_10_03
- Owner: fable_0
- Created: 2026-10-03T21:41:39Z

<!-- BEGIN ENTRY: "Shared-site read: before and after" -->
## Before
Every shared site reads its store on every creation: `c{i} = <route>` then `v{i} = c{i}._creations.get(sid{i})`,
where the route is `spells[i]._owner_creations` for `unique` (a global tuple index and a slot read) and
`meld._conduit_creations` / `meld._spellspace_creations` / `meld._root_creations` /
`meld._cluster_creations.resolved_store()` for the other shared existences.

## After
For a `unique` site whose provider is owned by an automatic conduit (`not spell._dynamic_environment`) and has
an owner store, `c{i}` is bound in the plan namespace to `spell._owner_creations` at emission and the alias
line is not emitted; the hit line, the miss call and the miss body are unchanged. Every other site, and every
site in dynamic posture, emits today's line.

## State and failure deltas
- None. The store object is fixed for the life of an automatic conduit; its dict is read per creation.

## Dependency and ordering
- Emission happens at hydration (first meld), after `define_conduit_into_spells` stamped ownership, on both the
  cold path and a cache full hit (rows -> live steps -> emit).

## Validation expectations
- Unit: automatic unique site -> no alias line, `c{i}` in the namespace, same instance published and reused;
  dynamic unique site -> the line is present and `c{i}` absent; unowned provider -> the line is present; a
  per-conduit site is unchanged.
- Component: real conjures - automatic Worker over a unique Service melds the same Service twice and its normal
  plan source has no alias line; the same world on a cache full hit behaves the same; a dynamic world's plan
  keeps the line.
<!-- END ENTRY: "Shared-site read: before and after" -->
