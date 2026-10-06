# Component patch: SpellCompiler and Validation Pipeline - Phase 3 annotation matching

- Patch id: annotation_address_matching_2026_10_03
- Owner: fable_0
- Created: 2026-10-03T19:25:31Z

<!-- BEGIN ENTRY: "Phase 3 matching: before and after" -->
## Before
`_matches_annotation`: a string annotation matches `spell_name`, a string frame or a class frame's `__name__`;
an object annotation matches `spell.spell is annotation` or `spellframe is / == annotation`. The pass-scoped
index buckets by those strings and by `id()` of the bound object and the frame, and is disabled (scan
fallback) when any pool object carries a custom `__eq__`. Consequences: an existing object (`spell.spell` is
the instance) never matches a class-object annotation; the same binding resolves under a `TYPE_CHECKING`
string and fails under a runtime class; a concrete class used as a frame resolves as if it were the type.

## After
One rule: `key = normalize_frame_key(annotation)`; a spell is a candidate when `key` equals its address frame
key or its type key (`normalize_frame_key(spell_name)`), subject to the unchanged `binding_name` filter and
the METHOD/LAMBDA exclusion under `require_class_spell`. The index buckets each spell under its (one or two)
keys; lookups read one bucket; the eq-risky gate and the unused frame buckets are gone. `_eq_safe_object`
remains as the structural snapshot's rule.

## State and failure deltas
- No new state. Ambiguity raises as before (`RuntimeError`, "multiple DI candidates"). An unmatched single
  socket is still an UNRESOLVED_INPUT.

## Dependency and ordering
- Candidate order is still `_spell_id_pool` insertion order (the index keeps positions and the first-position/
  last-object dict semantics).

## Validation expectations
- Unit: the parametrized matcher cases rewritten as key cases (type, frame, string, binding mismatch, method
  exclusion); new cases: an instance matched by its class object and by its class name (parity); a concrete
  class frame matched by name; the index path equals the scan path for those.
- Component: a Worker over a bare existing Service melds through a real conjure; the harness builds its
  existing-object shapes with bare bindings.
<!-- END ENTRY: "Phase 3 matching: before and after" -->
