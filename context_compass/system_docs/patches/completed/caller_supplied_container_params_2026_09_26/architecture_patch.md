# architecture_patch

## Metadata
- Patch ID: caller_supplied_container_params_2026_09_26
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T12:13:41Z
- Updated: 2026-09-26T12:13:41Z

## Patch Scope and Non-Goals
- Objective: Phase 4 stops contradicting Phase 1. A dict, set, frozenset or tuple constructor parameter is
  never injected (Phase 1 classifies it PLAIN, a caller input), so Phase 4 no longer errors on it and conjure
  no longer refuses the spell. typing.Any is not a DI target anywhere in Phase 4, as in Phase 1. The "Melder
  injects collections only as list[T]" hint moves into the REQUIRED_HOLE warning for such parameters.
- Non-goals:
  - No dict/set/tuple collection injection (Phase 1 unchanged).
  - No change to list[T] collection DI, forward-ref warnings, or the other validation strategies.
  - No change to whether data classes may be spells (owner: supply fields through override).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler and Validation Pipeline (Phase-4 strategies) | modify | remove the container error branch; Any exclusion; REQUIRED_HOLE hint | none |

## Interface and Boundary Deltas
- Interface delta: the UNSUPPORTED_COLLECTION_SHAPE issue code is no longer emitted. REQUIRED_HOLE messages for
  dict/set/frozenset/tuple annotations gain one sentence; issue code, severity and details are unchanged.
- Behaviour delta: spells with such parameters (no SpellMap/SpellContract default) now pass Phase 4 and
  conjure; the caller supplies the value at meld (a missing value fails as Python's missing argument).
  list[Any] now draws the existing LIST_ELEMENT_NOT_DI_TARGET warning like list[int].

## Cross-Component Invariants
- Invariant 1: Phase 1 is the single decider of which parameters are injected; Phase-4 strategies judge only
  what Phase 1 decided and never break a spell over a parameter Phase 1 made a caller input.
- Invariant 2: Phase 1 and Phase 4 agree that typing.Any is not a DI target.
- Invariant 3: no spell-id, fingerprint or creation-cache change.

## Migration and Rollout Order
1. AnnotationShapeGuardStrategy: remove the set/frozenset/dict/tuple branch and its helper; Any is not a DI target.
2. RequiredHolesStrategy: container hint in the REQUIRED_HOLE message.
3. Tests that asserted the old refusal now assert a successful conjure and the hint; new regression for
   dict[str, Any] and a supplied container.
4. Promote to src_components, graph, release note; assets rebuilt later by the owner.

## Rollback Strategy
- Rollback trigger: a suite failure attributable to the two strategy files.
- Rollback steps: restore both files and the edited tests.
- Post-rollback verification: unit/component/integration validation suites.

## Validation Expectations and Evidence Plan
- Before: artifacts/annotation_shape_guard_20260926/results/container_guard_before_after.txt (five container
  shapes refuse conjure). After: they conjure, meld with the supplied value, and the REQUIRED_HOLE hint names
  list[T]; unit/component/integration suites green apart from the pre-existing concurrency flake.

## Ticket Coverage Map
- Epic: none
- Story: none
- Tasks: tickets/tasks/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md

## Unknowns and Decision Requests
- UNKNOWN: none.
- DECISION_REQUEST: none open (owner decided the four-part change 2026-09-26).

## Context / Handoff Summary
- What changed: see component_patch_spell_compiler_validation.md.
- What remains: implementation, validation, promotion.
- Next entrypoint: the task ticket's latest Notes NEXT.
