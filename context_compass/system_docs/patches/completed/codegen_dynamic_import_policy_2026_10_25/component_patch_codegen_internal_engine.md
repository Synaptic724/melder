# component_patch_codegen_internal_engine

## Metadata
- Patch ID: codegen_dynamic_import_policy_2026_10_25
- Component: Codegen Internal Engine - the validation strategies, `CodegenNamespaceConfiguration`,
  `CodegenBuiltinsStrategy` and `CodegenSystem` default posture
  (`src/melder/nexus/rift/codegen_system/`)
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T09:57:25Z
- Updated: 2026-10-25T09:57:25Z

## Component Purpose and Boundary
- Current boundary: the builtin gate refuses a Call whose func is a Name in `denied_builtin_names`; name
  resolution admits every builtin not in `denied_builtin_names`; the builtins strategy builds the runtime
  `__builtins__` as `vars(builtins)` minus `denied_builtin_names`; the import gate checks import
  statements' roots; `CodegenSystem._build_default_namespace_configuration` builds the no-projection posture.
  EVIDENCE:
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:103-127
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:244-265
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:100-109
  - src/melder/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:67-235
  - src/melder/nexus/rift/codegen_system/codegen_system.py:407-483
- Target boundary: `CodegenNamespaceConfiguration` carries `static_only_denied_builtin_names`; A reads
  `denied_builtin_names | static_only_denied_builtin_names` in the builtin gate and name resolution; B keeps the
  builtins strategy stripping `denied_builtin_names` only, then wraps `__import__` when imports are on and a
  list applies; the default posture threads the new field (`()` with no projection - imports off there).

## Before/After Behavior Summary
- Before: under hybrid/precision/permissive, `__import__('subprocess')` is accepted at validation and the
  runtime `__import__` loads any root.
- After: under those postures the call and a bare `__import__` reference are refused at validation, and the
  runtime `__import__` is a wrapper that refuses a denied/unlisted root (ImportError naming it) and delegates an
  allowed root; import statements of allowed roots still work. full_access is unchanged (no list). safe is
  unchanged (`__import__` already denied, imports off).

## Interface Deltas
- Inputs: `CodegenNamespaceConfiguration.__init__` and `create_default` gain
  `static_only_denied_builtin_names: Tuple[str, ...] = tuple()`; a read-only accessor returns it.
- Outputs: the two static gates' allowed/denied name computation; B's runtime `__builtins__['__import__']`.
- Error semantics: builtin gate "Builtin '__import__' is not allowed in this codegen mode." (call); name
  resolution "Name '__import__' is not available in the codegen namespace." (reference); B at run time
  "Import root '<root>' is not allowed in this codegen mode." (ImportError).

## State and Lifecycle Deltas
- Owned state changes: `CodegenNamespaceConfiguration` adds one slot `_static_only_denied_builtin_names`,
  initialized in `__init__`, deleted in `cleanup`.
- Lifecycle/cleanup changes: none beyond the new field's `del`.

## Failure Mode Deltas
- New failure mode: room code that used `__import__` under a listed posture is refused at validation (Breaking);
  a denied/unlisted import reaching B's wrapper at run time raises ImportError naming the root.
- Removed failure mode: room code under a listed posture loading a denied or unlisted root through `__import__`.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Reads the compiled `static_only_denied_builtin_names` (component_patch_codegen_acl_profiles) and
   `IMPORT_BUILTIN_NAMES` for B's wrapper install condition.
2. A's two gates and B's wrapper land together; a static-only name with no runtime wrapper would deny
   `__import__` references while import statements still call the unguarded real import.

## Validation Expectations
- Test/validation item 1: unit - the builtin gate refuses a `__import__` call and name resolution refuses a bare
  `__import__` reference when `static_only_denied_builtin_names` carries it; both accept it when it does not.
- Test/validation item 2: unit - the builtins strategy keeps `__import__` present and, with a list, installs a
  wrapper that refuses a denied root (ImportError) and delegates an allowed root; unit - the default posture
  carries `()` for the field.
- Evidence target 1: tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py
- Evidence target 2: tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py,
  tests/unit/melder/aether/test_codegen_system_unit_matrix.py

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION: A + B (the owner, chat 2026-10-25; architecture_patch).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: an allowed import's wrapper cost (measured in validation).
- Next entrypoint: `CodegenBuiltinsStrategy.build_namespace_entries` and the two static strategies.
