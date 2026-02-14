# Meld Paths: Meld, MeldRuntime, MeldEngine (2026-01-26)

## Sources
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`
- `src/melder/aether/conduit/meld/meld_context/meld_context.py`
- `src/melder/spellbook/existence/existence.py`

## Glossary (Local to this doc)
- Occurrence: `(spell_id, path)` where `path` is a tuple of parameter names from root.
- Instance key: `(spell_id, path_or_None)` where `None` means shared instance.
- Shared existence: any existence except `Existence.many`.
- Per-path existence: `Existence.many`.
- Owner creations: the creations container owned by the spell's owner conduit.
- Caller creations: the creations container of the conduit initiating the meld call.

## Meld: Entry Lanes and Branches
### Lane A: Resolve identity
- `meld()` normalizes overrides via `_normalize_spell_override`.
- Resolve spell by:
  - Direct `spell_id` string -> `_resolve_spell_by_id`.
  - Logical lookup key -> `_resolve_spell_by_lookup_key` via `SpellInputUtils`.

### Lane B: Validation / gating
- If `spellbook._spellbook_validation_required`:
  - `_ensure_lineage_resolvable` runs structural phases (1-4) when validity is unknown/gated.
  - Runs conduit-scoped resolution phases (5-7) when resolution validity is unknown/gated.
  - Raises `SpellbookValidationError` when invalid/disabled or still gated/unknown.
  - Change-control dirty root check can raise `MeldExecutionError`.

### Lane C: Hooks vs no hooks
- If hooks enabled (global or per spell):
  - `_comprehensive_meld_with_hooks` fires pre, activation (on create), and post hooks.
- Otherwise:
  - `_meld_without_hooks` runs the minimal instance resolution path.

### Lane D: Instance resolution with locks
`_resolve_instance_with_locks` drives the core reuse/construct logic:
- `Existence.many`:
  - Always constructs (no reuse).
  - Registers only if the spell has disposal methods.
- `Existence.unique_per_conduit` and `Existence.unique_per_spell_space`:
  - Hold creations lock across check -> construct -> register.
  - Reuse if exists; raise on override targeting existing instance.
- Shared existences (`unique`, `unique_per_conduit_cluster`, `unique_per_conduit_lineage`):
  - Hold spell lock; use creations lock only for map access.
  - Reuse if exists; raise on override targeting existing instance.

### Lane E: Spell-type dispatch
`_meld_by_spell_type` picks the construction path:
- Existing creation spell -> return `spell.user_created_object`.
- Class/method/lambda -> build `MeldContext` and run `MeldRuntime.execute`.
- Otherwise -> error.

### Lane F: Registration
`_register_spell` dispatches to:
- `_register_to_creations` for `Creations`.
- `_register_to_lesser_creations` for `LesserCreations`.
Rules:
- `Existence.many` skips registration if no disposal methods.
- `Existence.unique_per_spell_space` requires active spellspace or raises.
- LesserConduits allow per-conduit (and many), and delegate shared lifetimes to parent creations.

## MeldRuntime: Execution Lanes
### Lane A: Preflight gating
- If validation required:
  - System state validity must not be invalid/gated/disabled.
  - Dirty-root change control blocks runtime.
  - `spell.is_broken` and `spell.validated` are enforced.

### Lane B: Snapshot artifacts
- Reads `dependency_graph`, `requirements`, `resolution_frame`.
- Pulls root blueprint phase 5 if present.

### Lane C: Overrides pipeline
- If root blueprint exists:
  - `GraphMutator` applies mutation overrides.
  - `SpellOverrider` computes socket overrides.
  - Failure -> `MeldExecutionError`.
- If no blueprint:
  - Skips graph mutation and socket overrides.

### Lane D: Frame overrides
`_build_frame_overrides` merges:
- Context overrides (including `__args__`).
- Socket overrides that target the root node with single-segment path.

### Lane E: Engine execution + cleanup
- Builds spell lookup for all known spells (owned + contracted).
- Instantiates `MeldEngine` and calls `engine.run()`.
- Always cleans up engine + resolution frame.
- If a factory-style spell returns `None`, raises `MeldExecutionError`.

## MeldEngine: DAG vs Root-Only Lanes
### Lane A: Root-only fallback
- If no blueprint or no ordered nodes:
  - Build root-only instance key.
  - `_resolve_spell_instance` with `_construct_root_only`.
  - Store result in `ResolutionFrame`.

### Lane B: Blueprint-driven execution
1. Build occurrence graph from root path.
2. Extend graph with ordered nodes not in root path.
3. Build execution order (topological, fallback by ordered ids).
4. Detect overrides (socket, contract, root-level).
5. Build instance plan:
   - `Existence.many` -> per-path instance keys.
   - Shared existences -> one instance per spell id, canonical occurrence used for deps.
6. Validate override targets for shared spells (no duplicates).
7. For each node id in execution order, for each instance key:
   - Build contract override payload (if any).
   - Build kwargs:
     - Dependency results from occurrence graph.
     - Socket overrides (path-matched).
     - Contract overrides (may include `__args__`).
   - Construct and resolve via `_resolve_spell_instance`.
   - Store result in `ResolutionFrame`.
8. Return root instance; fallback to root-only if root not found in results.

## Override Semantics
- Root-level overrides live on the `ResolutionFrame` and apply to root spell only.
- Socket overrides are `SocketRef` keyed and can be path-specific for many instances.
- Contract overrides can inject payloads per occurrence.
- Shared instances may only accept one override per parameter and one contract payload.
- Many/per-path instances accept overrides only when `param_path` matches their path.

## Existence and Locking Semantics (Engine)
`_resolve_spell_instance` in engine:
- `Existence.many`: always construct; register when disposal methods exist.
- Per-conduit existences: use caller creations lock across check -> construct -> register.
- Shared existences: use spell lock; creations lock only for map access.
- If caller creations lock is already held and maps align, skip spell lock to avoid inversion.

## SpellSpace Lane
- `Existence.unique_per_spell_space` requires an active spellspace.
- If none or wrong owner, raises `SpellSpaceScopeError`.

## Findings and Refactor Candidates (No code changes)
### Candidates for lane extraction
- `Meld.meld`: split identity resolution + gating + hook lane selection into helpers.
- `Meld._resolve_instance_with_locks`: split by existence class (many/per-conduit/shared).
- `MeldRuntime.execute`: split gating, overrides pipeline, engine invocation, cleanup.
- `MeldEngine.run`: split blueprint path into clear sub-steps (graph, plan, execute).
- `MeldEngine._build_kwargs_for_instance`: split dependency assembly vs override merge.

### Duplication hotspots
- Registration and reuse logic duplicated in `Meld` and `MeldEngine`.
- Creations selection logic duplicated across `Meld` and `MeldEngine`.

### Path labeling suggestions (for future docs and code)
- "Root-only lane" vs "Blueprint lane".
- "Shared existence lane" vs "Per-path lane".
- "Overrides present lane" vs "Overrides absent lane".
- "Hooked meld lane" vs "No-hook lane".
