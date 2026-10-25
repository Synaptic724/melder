# component_patch_codegen_acl_profiles

## Metadata
- Patch ID: codegen_materialize_namespace_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T11:34:22Z
- Updated: 2026-10-25T11:34:22Z
- Ticket: TASK-2026-10-10-refuse-materializing-over-live-modules (D-20), parent
  EPIC-2026-10-25-codegen_room_policy_defects

## Component Purpose and Boundary
- Nexus Descriptor And ACL Managers: the codegen capability ruleset gains the `materialize_modules` operation and
  the compiler projects it onto the compiled surface.

## Before/After Behavior Summary
- Before: no rule names where a frame's room may materialize.
- After: `materialize_modules` allow/deny rules compile to `generation_module_roots` (None = no allow rule) and
  `denied_generation_module_roots`; standard presets declare none.

## Interface Deltas
- FrameACLValidator: capability operation set + condition check (non-empty dotted-legal `module_roots`).
- FrameACLCodegenBuilder: `allow_materialize_module_roots`, `deny_materialize_module_roots`.
- FrameACLCompiler: `_compile_codegen_generation_controls`; CompiledFrameACLAccessSurface: two fields.

## State and Lifecycle Deltas
- Two immutable fields on the surface; cleanup deletes them.

## Failure Mode Deltas
- A malformed `materialize_modules` rule raises ValueError at validation, as an import rule does.

## Dependency and Ordering Constraints
- Both surface clones must forward the fields (D-11 lesson).

## Validation Expectations
- Unit: validator accepts/rejects, builder merges, compiler matrix (none, allow, overlay intersection, deny).

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION: the namespace is an ACL rule (the owner, chat 2026-10-25; architecture_patch).

## Context / Handoff Summary
The generation namespace becomes posture, compiled like import roots.
