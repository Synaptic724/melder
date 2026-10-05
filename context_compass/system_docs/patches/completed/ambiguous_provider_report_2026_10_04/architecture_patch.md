# Architecture patch: ambiguous providers are reported, not thrown (ambiguous_provider_report_2026_10_04)

<!-- BEGIN ENTRY: "Objective and non-goals" -->
## Objective and non-goals
- Objective: a single typed constructor parameter that two or more resolvable spells provide is refused by the
  readable conjure report (`SpellbookValidationError`, code `AMBIGUOUS_PROVIDER`) naming the parameter, the
  annotation, each candidate with its address and the two remedies - instead of a Phase-3 `RuntimeError`.
- Non-goals: no warning path (owner ruling 2026-10-04); no change to what matches (the 0.2.8222 kind rule); no
  change to planning or caching.
<!-- END ENTRY: "Objective and non-goals" -->

<!-- BEGIN ENTRY: "Changed components and interface deltas" -->
## Changed components and interface deltas
- `dag/socket_kind.py`: new member `AMBIGUOUS_INPUT`.
- `phases/compiler_phase_3.py`: `_resolve_single_by_annotation` returns every matching candidate instead of
  raising; `_build_local_frame_dag` records >1 candidates as `socket_ambiguous`; `_build_local_topology` marks
  the socket `AMBIGUOUS_INPUT` with the candidates as `referenced_spell_ids` and keeps its `dependency_key`.
- `validation/strategies/ambiguous_provider_strategy.py` (new): `AmbiguousProviderStrategy`, registered in
  `SpellValidationSystem`, emits one `AMBIGUOUS_PROVIDER` error per such socket.
- `spell_system_states._extract_collection_frame_keys` and `BindingResolutionCycleStrategy` treat the new kind
  like `UNRESOLVED_INPUT` (watched by frame key; no resolution edge).
<!-- END ENTRY: "Changed components and interface deltas" -->

<!-- BEGIN ENTRY: "Invariants, migration, rollback" -->
## Invariants, migration, rollback
- Invariant: a broken spell never plans, so no executor, site plan or cache row can carry the new kind; the cache
  generation does not move.
- Invariant: the refusal keeps its timing - conjure for automatic worlds, the first meld (meld-time validation gate)
  for a consumer late-bound into a dynamic world.
- Migration: none for users; tests pinning the RuntimeError text move to the report text.
- Rollback: revert source and tests together.
<!-- END ENTRY: "Invariants, migration, rollback" -->
