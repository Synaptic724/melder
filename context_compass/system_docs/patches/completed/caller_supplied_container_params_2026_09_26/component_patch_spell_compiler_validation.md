# component_patch_spell_compiler_validation

## Metadata
- Patch ID: caller_supplied_container_params_2026_09_26
- Component: SpellCompiler and Validation Pipeline (Phase-4 validation strategies)
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T12:13:41Z
- Updated: 2026-09-26T12:13:41Z

## Component Purpose and Boundary
- Current boundary: Phase-4 strategies read Phase-1 requirements and emit issues; any error marks the spell
  broken and conjure raises SpellbookValidationError.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: AnnotationShapeGuardStrategy emitted UNSUPPORTED_COLLECTION_SHAPE (error) for a set, frozenset, dict
  or tuple parameter whose arguments looked injectable (any non-builtins class, typing.Any included), even
  though Phase 1 had classified it PLAIN; RequiredHolesStrategy warned REQUIRED_HOLE on the same parameter.
- After: the guard judges only list[T] and forward-ref shapes; its DI-target check returns False for
  typing.Any. REQUIRED_HOLE for a default-less set/frozenset/dict/tuple parameter adds: Melder injects
  collections only as list[T], so this parameter is always supplied by the caller.

## Interface Deltas
- Inputs/outputs: UNSUPPORTED_COLLECTION_SHAPE retired; REQUIRED_HOLE message text extended for containers.

## State and Lifecycle Deltas
- None.

## Failure Mode Deltas
- Removed: conjure refusal for spells with caller-supplied container parameters.
- Unchanged: a meld that does not supply a required container fails in the constructor call.

## Dependency and Ordering Constraints
1. Guard change and hint land together so the hint is never lost.

## Validation Expectations
- Unit: guard emits nothing for set/dict/tuple parameters; Any not a DI target; list[Any] warns; REQUIRED_HOLE
  hint present for containers and absent for scalars.
- Component/integration: container spells conjure; supplied container reaches the constructor.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: container guard removed, Any aligned, hint moved to REQUIRED_HOLE.
- Remaining risks: users who relied on conjure failing for set[T] now see a warning instead.
- Next entrypoint: architecture_patch.md.
