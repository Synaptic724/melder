# component_patch_conduit_ward_and_contracts

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: ConduitWard and Contracts
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:12:40Z

## Component Purpose and Boundary
- Current boundary: `ConduitWard._get_spell_contract_keys` collects canonical SpellContract keys from
  a spell's call-signature defaults (best effort; empty set when the signature is uninspectable).
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: VALUE-format read; a TYPE_CHECKING-only annotation raised NameError (only TypeError and
  ValueError are caught). No `src/` caller exists today; unit tests exercise it.
- After: `inspect.signature(call_target, annotation_format=Format.FORWARDREF)`, mirroring
  `Meld._iter_spell_contract_defaults`.

## Interface Deltas
- Inputs/outputs: none changed.
- Error semantics: NameError no longer escapes; TypeError/ValueError still yield an empty set.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- Removed failure mode: NameError for TYPE_CHECKING-annotated consumers.
- New/changed failure mode: none.

## Dependency and Ordering Constraints
1. None.

## Validation Expectations
- Regression: `test_conduit_ward_contract_keys_read_through_type_checking_annotations`.
- Existing `test_get_spell_contract_keys_*` cases pass unchanged.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: read format plus a docstring contract line.
- Remaining risks: none.
- Next entrypoint: architecture_patch.md.
