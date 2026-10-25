# component_patch_codegen_internal_engine

## Metadata
- Patch ID: codegen_open_builtin_posture_2026_10_25
- Component: Codegen Internal Engine - `CodegenSystem` default namespace posture
  (`src/melder/nexus/rift/codegen_system/codegen_system.py`)
- Status: draft
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T02:10:23Z
- Updated: 2026-10-25T02:10:23Z

## Component Purpose and Boundary
- Current boundary: when the owning Rift has no codegen projection for the frame a request names,
  `_try_get_codegen_projection` returns None (it swallows the AttributeError, KeyError and ValueError the lookup
  raises - `Rift._get_required_frame_projection_set` raises ValueError for a frame the room holds no projection
  for) and `_build_default_namespace_configuration` builds a default posture: imports off, no reflection, dunder
  access or recursive codegen, and a literal denied-builtin tuple equal to `__import__` plus today's safe tuple.
  The request then validates and runs under it; the public `CodegenCommandSystem.execute_codegen` reaches this
  with any frame name the room has no projection for. So the default is the safe posture kept by hand, and it
  allows `open` like safe does today.
  EVIDENCE:
  - src/melder/nexus/rift/codegen_system/codegen_system.py:362-402
  - src/melder/nexus/rift/codegen_system/codegen_system.py:404-475
  - src/melder/nexus/rift/codegen_system/codegen_system.py:510-537
  - src/melder/nexus/rift/rift.py:683-700
  - src/melder/nexus/rift/command_system/codegen_command_system.py:669-737
- Target boundary: the default posture's denied builtins are `("__import__",) + SAFE_DENIED_BUILTIN_NAMES`; the
  rest of the default posture is unchanged.

## Before/After Behavior Summary
- Before: a request naming a frame without a projection runs under a hand-kept copy of the safe deny list plus
  `__import__`; `open` is available.
- After: the same request denies `__import__` and everything safe denies, `open` included, and follows the safe
  tuple when it changes.

## Interface Deltas
- Inputs: none.
- Outputs: the no-projection `CodegenNamespaceConfiguration.denied_builtin_names` gains "open".
- Error semantics: the builtin gate's and name resolution's existing texts, as under safe.

## State and Lifecycle Deltas
- Owned state changes: none (a value read per request).
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none beyond the Breaking `open` refusal.
- Removed failure mode: code reaching `open` by naming a frame the room holds no projection for.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Reads the codegen profiles' `SAFE_DENIED_BUILTIN_NAMES` (component_patch_codegen_acl_profiles), a leaf module.
2. Whether a request without a projection should run at all is not changed here (out of D-10's scope).

## Validation Expectations
- Test/validation item 1: unit - with no projection the default posture's denied builtins are exactly
  `__import__` plus the safe tuple, `open` among them.
- Test/validation item 2: integration - `execute_codegen` naming a frame the room has no projection for refuses
  `open` and writes nothing.
- Evidence target 1: tests/unit/melder/aether/test_codegen_system_unit_matrix.py
- Evidence target 2: tests/integration/melder/aether/test_codegen_core_boundary_integration.py

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (the D2 posture covers it: the default is the safe posture).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none known.
- Next entrypoint: `CodegenSystem._build_default_namespace_configuration`.
