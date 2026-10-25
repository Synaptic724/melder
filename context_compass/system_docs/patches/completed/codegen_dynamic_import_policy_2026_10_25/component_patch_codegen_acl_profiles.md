# component_patch_codegen_acl_profiles

## Metadata
- Patch ID: codegen_dynamic_import_policy_2026_10_25
- Component: Nexus Descriptor And ACL Managers - `FrameACLCompiler`, `CompiledFrameACLAccessSurface` and the
  codegen name tuples (`src/melder/nexus/acl/`)
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T09:57:25Z
- Updated: 2026-10-25T09:57:25Z

## Component Purpose and Boundary
- Current boundary: `FrameACLCompiler` joins a frame's descriptor truth and ACL configuration into a
  `CompiledFrameACLAccessSurface`. For codegen it compiles the imports-enabled flag, the allowed and denied
  import roots, and `denied_builtin_names` (the union of the preset/precision/override denies, minus the allows,
  plus `__import__` only when imports are off).
  EVIDENCE:
  - src/melder/nexus/acl/frame_acl_compiler.py:558-630
  - src/melder/nexus/acl/frame_acl_compiled_access_surface.py:84-180
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:108-130
- Target boundary: the same, plus a new compiled `static_only_denied_builtin_names` - names the static gates
  refuse but the runtime keeps present - set to `IMPORT_BUILTIN_NAMES` (`('__import__',)`) when imports are on
  and an allow or deny import list applies, else `()`. `IMPORT_BUILTIN_NAMES` lives in the stdlib_import_sets
  leaf module beside the other codegen name tuples, read by the compiler and the runtime builtins strategy, so the
  two cannot drift.

## Before/After Behavior Summary
| posture | imports | import list applies | static_only_denied_builtin_names | denied_builtin_names has __import__ |
|---|---|---|---|---|
| safe | off | no | () | yes (imports off) |
| hybrid | on | yes (allow + deny) | ('__import__',) | no |
| hybrid + precision overlay | on | yes (allow + deny) | ('__import__',) | no |
| permissive | on | yes (allow) | ('__import__',) | no |
| full_access | on | no | () | no |

Only the `static_only_denied_builtin_names` column is new; every other cell is today's behaviour.

## Interface Deltas
- Inputs: none.
- Outputs: `CompiledFrameACLAccessSurface` gains `static_only_denied_builtin_names: Tuple[str, ...]` (sorted,
  default `()`) with an accessor; the compiler sets it from a new static helper over the import posture.
- Error semantics: none in this component; the field feeds the codegen engine's two static gates.

## State and Lifecycle Deltas
- Owned state changes: `CompiledFrameACLAccessSurface` adds one slot `_static_only_denied_builtin_names`,
  initialized in `__init__`, deleted in `cleanup` with the other owned fields.
- Lifecycle/cleanup changes: none beyond the new field's `del`.

## Failure Mode Deltas
- New failure mode: none in this component (the refusals live in the codegen engine's gates).
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. `IMPORT_BUILTIN_NAMES` is added to stdlib_import_sets.py first; the compiler and the builtins strategy both
   read it.
2. The compiled field is added before the engine reads it (component_patch_codegen_internal_engine).

## Validation Expectations
- Test/validation item 1: unit - the compiled `static_only_denied_builtin_names` is `('__import__',)` for
  hybrid/precision/permissive and `()` for full_access and safe.
- Test/validation item 2: unit - `CompiledFrameACLAccessSurface` round-trips and cleans the new field.
- Evidence target 1: tests/unit/melder/aether/test_frame_acl_compiler_contracts.py
- Evidence target 2: tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION: A + B (the owner, chat 2026-10-25; architecture_patch).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none known in this component.
- Next entrypoint: `IMPORT_BUILTIN_NAMES` in stdlib_import_sets.py, then
  `FrameACLCompiler._compile_codegen_builtin_controls`.
