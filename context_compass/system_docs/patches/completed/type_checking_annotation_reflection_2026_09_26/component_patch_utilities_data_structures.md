# component_patch_utilities_data_structures

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Utilities data structures (WeakConcurrentDict)
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:58:40Z
- Updated: 2026-09-26T09:58:40Z

## Component Purpose and Boundary
- Current boundary: the `__or__`, `__ior__` and `__ror__` operators of
  `src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py`.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: `other: "WeakConcurrentDict[_K, _V]" | Mapping[_K, _V] | Iterable[Tuple[_K, _V]]`. The string
  operand evaluated only because `Mapping` is `typing.Mapping`; with `collections.abc.Mapping` (also
  imported in the module) all three would raise TypeError, and the form breaks the no-`|`, no-quotes rules.
- After: `other: Union[WeakConcurrentDict[_K, _V], Mapping[_K, _V], Iterable[Tuple[_K, _V]]]`.

## Interface Deltas
- Inputs/outputs: none. Annotation-only: the runtime never evaluates these annotations.
- Error semantics: none at runtime.

## State and Lifecycle Deltas
- None.

## Failure Mode Deltas
- Removed failure mode: any VALUE-format read of the listed owners (`inspect.signature`,
  `typing.get_type_hints`, ProtocolCrafter, SpellExaminer detailed profiles) no longer raises.
- New failure mode: none. No runtime import is added; every new import is under `TYPE_CHECKING`.

## Dependency and Ordering Constraints
1. None. `TYPE_CHECKING` imports add no import-time edge, so no cycle can form.

## Validation Expectations
- Guard: no STRING_IN_UNION finding; existing WeakConcurrentDict unit tests unchanged.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (owner approved the audit fixes 2026-09-26).

## Context / Handoff Summary
- What changed: annotation-only fixes found by the annotation integrity audit.
- Remaining risks: none.
- Next entrypoint: architecture_patch.md.
