# component_patch_spell_examination_profiles

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Spell Examination Profiles
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:12:40Z

## Component Purpose and Boundary
- Current boundary: `BindingProfileStrategy` builds the bind-time profile whose `init_signature`
  (classes) and `signature` (callables) text feeds `Bind.sha256_profile`; `ClassInspector` and
  `MethodInspector` build the detailed-profile payloads.
- Target boundary: unchanged; rendering goes through `SignatureReflection`.

## Before/After Behavior Summary
- Before:
  - Bind-time text was `str()` of a FORWARDREF signature; an unresolved name rendered as
    `ForwardRef('Decimal', owner=<function C.__init__ at 0x...>)`, so the spell id changed per process.
  - `SpellExaminer.create_profile(spell, "detailed")` raised NameError at
    `ClassInspector._header` (get_annotations eval_str=True) and in the member/method signature reads.
- After:
  - Bind-time text is `str(SignatureReflection.stabilize_signature(...))`: identical wherever the
    signature had no owner-bearing ForwardRef, deterministic otherwise. The cached
    `init_signature_object` stays the FORWARDREF signature.
  - ClassInspector: `_class_annotations` evaluates with eval_str first and on NameError returns
    `SignatureReflection.class_annotations(c)`; member signatures use `display_signature`.
  - MethodInspector: `_fill_signature` uses `display_signature`.

## Interface Deltas
- Inputs: none changed.
- Outputs: previously failing profiles now complete; unresolved names appear as source text
  (`'Decimal'`, `'Optional[Decimal]'`). Spell ids change only for spells whose bind text carried an
  owner-bearing ForwardRef (they were random per process before).
- Error semantics: NameError from unavailable names no longer escapes profile building.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- Removed failure mode: NameError in detailed profile completion; per-process spell ids for classes
  and callables whose annotations name TYPE_CHECKING-only types (callables remain per-process for the
  separate `repr()` reason, not fixed here).
- New/changed failure mode: none.

## Dependency and Ordering Constraints
1. Depends on SignatureReflection (utilities helpers component patch).
2. The requirements finder keeps borrowing `init_signature_object` unchanged.

## Validation Expectations
- Regressions: `test_bind_fingerprint_text_is_address_free_for_type_checking_annotations`,
  `test_detailed_profile_of_spell_with_type_checking_annotations`.
- Existing suites for binding profiles, inspectors and future-annotation cases pass unchanged.
- Cross-process id probe: identical ids for the TYPE_CHECKING-annotated class.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: deterministic bind text; detailed profiles no longer raise.
- Remaining risks: binding-profile `annotations` still clear to `{}` on an unresolved name (separate).
- Next entrypoint: architecture_patch.md.
