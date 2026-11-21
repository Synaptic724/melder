# code_description_patch_codegen_name_resolution

## Metadata
- Patch ID: codegen_room_contract_2026_11_21
- Component: `CodegenNameResolutionStrategy` binding collectors
- Status: implemented at 0.2.8311-0.2.8313; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-21T22:16:54Z
- Updated: 2026-11-21T23:30:00Z
- Trigger: a changed policy gate (what codegen validation accepts)

## Control Flow Commitments
- `_collect_locally_assigned_names` walks the tree once and adds, besides `ast.Name` in Store context:
  `ast.ExceptHandler.name`, `ast.MatchAs.name` and `ast.MatchStar.name` when not None, and
  `ast.MatchMapping.rest` when not None. `except*` handlers are `ast.ExceptHandler` nodes under `ast.TryStar`.
- `_collect_local_parameter_names` adds the names of `ast.TypeVar`, `ast.ParamSpec` and `ast.TypeVarTuple` beside
  `ast.arg`: PEP 695 type parameters of functions, classes and `type` aliases.
- `validate` is unchanged: it unions the collectors with the exposed, always-allowed and builtin names, then refuses
  the first `ast.Name` load outside that set.

## Edge and Error Semantics
- `case _` and `[*_]` carry `None` and add nothing; `_` stays refused unless the code binds it some other way.
- A name bound only in one function still passes in another; the runtime NameError covers that case, as for every
  other binding form today.

## Invariants and Idempotency
- The collectors are pure functions of the tree; the strategy keeps no state between calls.

## Explicit Non-Goals
- No scope analysis; no change to the builtin, import, attribute or reflection strategies.
