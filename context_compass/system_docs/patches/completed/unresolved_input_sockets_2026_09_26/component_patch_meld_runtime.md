# component_patch_meld_runtime

## Metadata
- Patch ID: unresolved_input_sockets_2026_09_26
- Component: Meld Resolution Runtime (codegen creation executors), custom exceptions, CachingSystem
- Status: draft for owner review

## Before
- A missing required input fails at Python argument binding. Generalized and many_only executors wrap it
  as MeldExecutionError "Error invoking spell 'X'" chained from the TypeError; solo executors let the raw
  TypeError propagate. Nothing names the dependency or the override key.
  EVIDENCE: artifacts/missing_dependency_sockets_20260926/probe_required_today_314t.json
- Failure sites:
  - generalized_no_overrides: `_raise_meld_construction_error` (603-617), `_construct_spell_instance`
    (1252-1320), one emitted except block (~1707)
  - generalized_overrides: three emitted except blocks (1650-1735), `_invoke_spell_with_kwargs` (3031-3095),
    which the hydrated manifest override runtime reaches through generalized_runtime_library
  - many_only_no_overrides: `_raise_meld_construction_error` (689-703), `_construct_spell_instance`,
    one emitted except block (~1318)
  - many_only_overrides: three emitted except blocks (1660-1712), `_invoke_spell_with_kwargs` (2683-2745)
  - generalized_manifest_no_overrides: emitted block calls the generalized helper (628-643)
  - solo no-override / override: direct `call_target(...)`, no try

## After
- New `UnresolvedInputError(MeldExecutionError)` in
  `src/melder/utilities/custom_exceptions/unresolved_input_error.py`, exported from `melder`.
  Extra slots: `expected_type` (display name from the Phase-1 annotation; the socket's lowercased frame key
  is used only for watching) and `unresolved_params` (tuple of names).
  `node_id`/`param_name` carry the consumer id and first missing parameter.
- One failure-path helper, `UnresolvedInputError.from_failed_construction(spell, exc, supplied_names,
  supplied_positional_count) -> Optional[UnresolvedInputError]`: reads the spell's local topology, collects
  UNRESOLVED_INPUT sockets not covered by the supplied names or positional count, and returns the error
  (or None). It runs only after a constructor call has already raised.
- Every generalized/many_only failure site calls it first and raises the result `from exc`; otherwise the
  existing MeldExecutionError is raised unchanged. No-override sites pass `supplied_names=()`.
- Solo executors: only when the spell has UNRESOLVED_INPUT sockets (decided at compile time) the call is
  wrapped in `try/except TypeError`; an unresolved miss raises the new error, anything else re-raises the
  original exception unchanged (solo keeps raw propagation).
- CachingSystem generation 11 ("unresolved_input_sockets") retires executors emitted before this change.
- Marked INTERIM: once the demand-driven build plan (design S3/S4) exists, the plan decides this error
  directly and these failure-path hooks are removed.

## Interface Deltas
- Public additive exception. Message form:
  "Task.work_callable expects <type>, but nothing registered provides it and this meld did not supply it.
  Supply it with override={'work_callable': ...} when melding Task, a path key ending in '>work_callable'
  (or '**work_callable') when Task is built as a dependency, or bind a provider for <type>."

## State / Failure Deltas
- Missing unresolved input: UnresolvedInputError (a MeldExecutionError) in every family, including solo.
- Reused stored object: no constructor call, no error. Other constructor failures: unchanged.

## Validation Expectations
- Component, per family (solo, many_only, generalized, cache-hydrated manifest): supplied root, supplied
  by path, supplied by broadcast, missing at root, missing nested, missing but consumer reused,
  constructor raising an unrelated TypeError with the input supplied (generic error preserved).
- Integration: cache generation history includes 11.
