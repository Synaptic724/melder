# component_patch_utilities_helpers

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Utilities helpers (SignatureReflection, Package)
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:12:40Z

## Component Purpose and Boundary
- Current boundary: `Package` wraps a callable; `describe()` renders its signature and the
  `signature` property builds a bound-arguments namespace.
- Target boundary: adds `SignatureReflection` (`src/melder/utilities/helpers/signature_reflection.py`),
  the single place Melder turns signatures/annotations with unavailable names into renderable values.

## Before/After Behavior Summary
- Before: `Package.describe()` and `Package.signature` raise NameError for a callable annotated with a
  TYPE_CHECKING-only name (VALUE-format read).
- After: `describe()` uses `SignatureReflection.display_signature` (VALUE when it succeeds, otherwise
  FORWARDREF with owner-bearing ForwardRefs replaced by source text); `signature` reads FORWARDREF
  (it only needs the signature to exist).
- SignatureReflection API: `display_signature(target)`, `stabilize_signature(signature, target)`,
  `class_annotations(cls)`, `contains_unresolved_name(annotation)`.

## Interface Deltas
- Inputs: none changed.
- Outputs: `describe()` text for previously failing callables, e.g.
  `price: 'Optional[Decimal]' = None`; unchanged text for all others.
- Error semantics: NameError from unavailable names no longer escapes; TypeError/ValueError for
  callables without a signature are unchanged.

## State and Lifecycle Deltas
- Owned state changes: none. SignatureReflection is stateless (`__slots__ = ()`).
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: NameError in `Package.describe()` / `Package.signature`.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. SignatureReflection imports only the standard library (`inspect`, `annotationlib`, `typing`).
2. Package imports SignatureReflection; no new cycle (both under `melder.utilities.helpers`).

## Validation Expectations
- Unit: `tests/unit/melder/utilities/helpers/test_signature_reflection.py` (14 contracts).
- Regression: `test_package_describe_renders_type_checking_annotation`.
- Equivalence: display_signature equals VALUE on every Melder callable where VALUE succeeds.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: new stateless helper; Package reads/renders through it.
- Remaining risks: STRING-format text of a dataclass-generated `__init__` can show synthetic names
  when a nested annotation is unresolved (deterministic, rare).
- Next entrypoint: architecture_patch.md.
