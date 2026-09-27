# component_patch_spell_compiler

## Metadata
- Patch ID: unresolved_input_sockets_2026_09_26
- Component: SpellCompiler and Validation Pipeline (Phases 3, 4, 8, 9) and SpellSystemStates watcher
- Status: draft for owner review

## Before
- Phase 3 `_resolve_single_by_annotation` raises RuntimeError "no DI candidate found" when no class spell
  matches the annotation. The phase aborts conjure (PhaseExecutionError) and late binds into a dynamic
  root fail at transaction commit.
  EVIDENCE: src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-513
- `_build_local_topology` marks a socket OVERRIDE_REQUIRED only when a non-resolvable definition was
  selected (non-empty references). EVIDENCE: compiler_phase_3.py:693-768
- The watcher registers OVERRIDE_REQUIRED and NORMAL collection sockets by frame key.
  EVIDENCE: src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1390
- Injection turns OVERRIDE_REQUIRED sockets into "override_required" sources; exporters append position,
  kind and references for that kind.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:216-278
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:860-945
- Phase-4 required_holes warns for PLAIN holes and OVERRIDE_REQUIRED sockets; warnings are stored, not logged.

## After
- `SocketKind.UNRESOLVED_INPUT` (appended): "a single typed dependency no registered spell provides;
  the constructing call supplies it."
- `_resolve_single_by_annotation` returns an empty mapping when there are no candidates at all (the
  two-candidate RuntimeError is unchanged). Its docstring states the new contract.
- `_build_local_frame_dag` records `(param_name, position)` in an `unresolved` set when a
  `SINGLE_BY_ANNOTATION` dependency resolves to nothing; `_build_local_topology` assigns
  UNRESOLVED_INPUT to those keys (after the existing OVERRIDE_REQUIRED rule, which cannot overlap because
  that rule needs a selected definition) and computes `dependency_key` for them as for NORMAL.
- `_extract_collection_frame_keys` also registers UNRESOLVED_INPUT sockets (dependency_key frame).
- Injection adds an "unresolved_input" source per UNRESOLVED_INPUT socket: no dependency keys,
  override_key = param name, position and parameter_kind retained. Planners need no change: sources with an
  override_key already become override targets and are omitted unless supplied.
- Both exporters (`build_injection_instance_rows` and the signature-row builder) append
  (position, parameter_kind) for kind "unresolved_input".
- required_holes emits code "UNRESOLVED_INPUT" (warning) with parameter, position, kind and expected key.
  binding_resolution_cycle skips UNRESOLVED_INPUT sockets as it skips OVERRIDE_REQUIRED.

## Interface Deltas
- Internal only (SocketKind member, param source kind, row suffix). No public signature changes here.

## State / Failure Deltas
- Conjure succeeds for a consumer with unresolved inputs; validity is not gated by them.
- A matching bind later marks the consumer dependency-changed; its next meld re-runs structural phases
  and the socket becomes NORMAL. The Phase-8 graph-shape rows include socket kind values, so the
  occurrence signature changes and cached plans for that root rebuild.

## Dependency / Ordering
- SocketKind first; Phase 3 and consumers in the same change. No persisted value of existing members moves.

## Validation Expectations
- Unit: zero candidates -> UNRESOLVED_INPUT with dependency_key; one -> NORMAL; two -> RuntimeError;
  non-resolvable definition present -> OVERRIDE_REQUIRED unchanged; non-resolvable root unchanged.
- Unit: injection source and exporter rows for the new kind; required_holes warning; cycle skip.
- Component: dynamic world, bind a provider after conjure, next meld injects the provider.
