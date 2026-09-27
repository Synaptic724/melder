# component_patch_meld_runtime

## Metadata
- Patch ID: shared_context_rebuild_2026_09_26
- Component: Meld Resolution Runtime (Meld, ConduitMeld, SpellSpaceMeld)
- Status: active
- Updated: 2026-09-26T13:58:21Z

## Before
- Doors read the spell's CreationContext (lock-free warm read, or the factory cold path), then called
  `CreationContext.execute*`, which admitted the spell-index ticket inside execution. A reader could therefore
  hold a context that a concurrent rebuild cleaned, or build from the plan gap.
- Producers `_ensure_lineage_resolvable` (structural 1-4), `_ensure_resolution_resolvable` (5-11) and
  `_ensure_runtime_resolution_ready` (deferred 8-11) ran their phases under `spell._lock` only.

## After
- Doors: when `target_spell._creation_gate` is set (dynamic), both lanes call `Meld._execute_admitted`: admit
  the ticket, recheck `resolution_required` (release, run the deferred path, re-admit), read the context (warm
  read inlined, cold path through the spell), call the executor slot directly, unregister in finally. Automatic
  spells keep the existing lane unchanged, including the fast-door memo.
- Producers enter `Meld._rebuild_window(spell)` (CreationContextRebuild over the spell; no-op without a gate)
  before `spell._lock`.

## Interface Deltas
- Private: `Meld._rebuild_window(spell) -> AbstractContextManager[object]`,
  `Meld._execute_admitted(spell, creation_gate, override_map, with_created) -> Any`.
- `CreationContext.execute` / `execute_no_hooks` keep their ticketed behaviour for direct callers; doors no
  longer route dynamic melds through them (no double admission).

## State and Failure Deltas
- Every admission is released exactly once, on success or failure; an executor error propagates unchanged.
- A closed (frozen) gate parks the dynamic meld before it reads the context; a terminally closed gate raises.

## Dependency and Ordering
- Validation and producers run before admission. Window before spell lock (see architecture patch).

## Validation Expectations
- Unit (test_concrete_meld_subclasses.py): one ticket held through execution (both doors), park before
  reading while frozen, ticket released on executor failure, hooks lane admits once and reports created,
  deferred recheck without a held ticket, window is a no-op without a gate and freezes with one.
- Component: September deterministic regression; in-flight reader drained before Phase 5.
- Integration: concurrency file incl. the two-cluster test, 40-run loop.
