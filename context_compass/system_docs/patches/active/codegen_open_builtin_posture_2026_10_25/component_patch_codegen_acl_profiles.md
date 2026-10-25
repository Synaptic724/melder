# component_patch_codegen_acl_profiles

## Metadata
- Patch ID: codegen_open_builtin_posture_2026_10_25
- Component: Nexus Descriptor And ACL Managers - the standard codegen profiles
  (`src/melder/nexus/acl/configurations/profiles/codegen/`)
- Status: decided (B for hybrid's pathlib)
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T02:10:23Z
- Updated: 2026-10-25T08:06:02Z

## Component Purpose and Boundary
- Current boundary: each preset (safe, hybrid, precision, permissive, full_access) states, in its capability
  ruleset, which imports and builtins room code may use. Safe, hybrid and precision deny the builtins in one shared
  tuple, `SAFE_DENIED_BUILTIN_NAMES` (hybrid and precision alias it), which omits `open`.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:83-99
  - src/melder/nexus/acl/configurations/profiles/codegen/safe_profile.py:106-124
  - src/melder/nexus/acl/frame_acl_compiler.py:600-631
- Target boundary: the same presets; the shared tuple names `open`; each preset's docstring states its file
  posture.

## Before/After Behavior Summary
| posture | `open` (call or name) | `io.open` | `os.open` | pathlib write |
|---|---|---|---|---|
| safe | accepted -> refused | refused, imports off | refused, imports off | refused, imports off |
| hybrid | accepted -> refused | refused, not listed | refused, not listed | accepted -> refused (B) |
| hybrid + precision overlay | accepted -> refused | refused, not listed | refused, not listed | refused, not listed |
| permissive | accepted (documented open) | accepted | accepted | accepted |
| full_access | accepted (documented open) | accepted | accepted | accepted |
"accepted -> refused" is this patch (hybrid's pathlib cell is the owner's B); every other cell is today's
behaviour, pinned by a test (`io`/`os` rows under
hybrid and precision measured at the red run). The `open` and pathlib rows for 0.2.8267 are the recorded probe run
(artifacts/codegen_room_policy_20261025/runs/codegen_probe_0_2_8267_gil0.txt).

## Interface Deltas
- Inputs: none.
- Outputs: the compiled `denied_builtin_names` of safe, hybrid and precision (and of any chain carrying the
  precision overlay) gains "open"; hybrid's compiled `allowed_import_module_roots` loses "pathlib" (B).
- Error semantics: existing texts - "Builtin 'open' is not allowed in this codegen mode." for a call, "Name 'open'
  is not available in the codegen namespace." for a bare reference; at run time `open` is not in `__builtins__`.

## State and Lifecycle Deltas
- Owned state changes: none; the presets are stateless and built per call.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: room code that used `open` under safe, hybrid or precision is refused at validation
  (Breaking; the release note names it); hybrid room code that imports `pathlib` is refused by the import gate
  (Breaking, B).
- Removed failure mode: room code under those postures reading or writing any file the process can reach through
  `open` (D-10), and hybrid code doing so through `pathlib.Path`.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The tuple change and the docstrings land together; the engine default reads the same tuple
   (component_patch_codegen_internal_engine).
2. An explicit frame `builtin_names` allow rule still re-allows `open`; the compiler is unchanged.

## Validation Expectations
- Test/validation item 1: the strict xfail `test_safe_profile_refuses_writing_files` passes without its marker.
- Test/validation item 2: symptom-named tests pin each row of the table above through `validate_codegen` /
  `execute_codegen` on a real room (integration), and the compiled `denied_builtin_names` per preset (unit).
- Evidence target 1: tests/integration/melder/aether/test_codegen_core_boundary_integration.py
- Evidence target 2: tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py

## Unknowns and Open Decisions
- UNKNOWN: none beyond the red run's `io`/`os` messages.
- DECISION: hybrid's `pathlib` - B (the owner, chat 2026-10-25, "focus on B"; architecture_patch).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: room code that used `open` in those rooms (Breaking); hybrid's pathlib route until decided.
- Next entrypoint: `SAFE_DENIED_BUILTIN_NAMES` in stdlib_import_sets.py.
