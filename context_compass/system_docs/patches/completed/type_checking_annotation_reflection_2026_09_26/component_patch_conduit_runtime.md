# component_patch_conduit_runtime

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Conduit Runtime (Normal and Lesser)
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:57:44Z

## Component Purpose and Boundary
- Current boundary: `Conduit._resolve_peer_conduit_for_contract_hooks` (private) resolves the peer
  conduit passed to contract hooks.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: parameters annotated `conduit: "Conduit" | None, conduit_id: str | None`. Evaluating
  `"Conduit" | None` raises TypeError (str has no `|` with None), so no annotation format can read
  the method (the only such annotation among 7,689 Melder callables); under eager evaluation it
  would have failed at import.
- After (owner edit, applied directly; this lane made no conduit.py change): `conduit:
  Optional["Conduit"], conduit_id: str | None) -> Optional["Conduit"]`. The string now sits inside
  `Optional[...]`, which typing turns into a ForwardRef, so every annotation format reads it.
- Open for the owner (not changed here): `str | None` is a PEP 604 union, which the repository typing
  rules forbid; the quoted self-reference could be unquoted on 3.14.

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
- DECISION_REQUEST: none (owner applied the fix directly 2026-09-26).

## Context / Handoff Summary
- What changed: one annotation (owner edit).
- Remaining risks: none.
- Next entrypoint: architecture_patch.md.
