# component_patch_conduit_runtime

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Conduit Runtime (Normal and Lesser)
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:12:40Z

## Component Purpose and Boundary
- Current boundary: `Conduit._resolve_peer_conduit_for_contract_hooks` (private) resolves the peer
  conduit passed to contract hooks.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: parameters annotated `conduit: "Conduit" | None, conduit_id: str | None`. Evaluating
  `"Conduit" | None` raises TypeError (str has no `|` with None), so no annotation format can read
  the method (the only such annotation among 7,689 Melder callables); under eager evaluation it
  would have failed at import.
- After: `conduit: Optional[Conduit], conduit_id: Optional[str]` - unquoted self-reference, valid on
  3.14 (evaluated on read, after the class exists) and already used elsewhere in the class.

## Interface Deltas
- Inputs/outputs: none (annotation only; runtime never evaluates it).
- Error semantics: none.

## State and Lifecycle Deltas
- None.

## Failure Mode Deltas
- Removed failure mode: TypeError when any tool reads this method's annotations.

## Dependency and Ordering Constraints
1. None.

## Validation Expectations
- Regression: `test_protocol_crafter_mirrors_melder_conduit`; invalid-annotation probe reports 0.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (owner confirmed the unquoted form 2026-09-26).

## Context / Handoff Summary
- What changed: one annotation.
- Remaining risks: none.
- Next entrypoint: architecture_patch.md.
