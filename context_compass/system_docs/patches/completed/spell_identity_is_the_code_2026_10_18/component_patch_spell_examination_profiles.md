# Component patch: Spell Examination Profiles - fingerprint-only fields removed (spell_identity_is_the_code_2026_10_18)

## Metadata
- Patch ID: spell_identity_is_the_code_2026_10_18
- Component: Spell Examination Profiles - `CallableParameterBindingSummary.default_fingerprint_repr`,
  `CallableBindingProfile.fingerprint_repr`, `InstanceBindingProfile.fingerprint_repr`,
  `OtherBindingProfile.fingerprint_repr`
  (`src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py:234-536`)
  and their builders `BindingProfileStrategy._build_callable_profile`, `_build_instance_profile` and
  `_build_other_profile` (`.../strategies/binding_profile_strategy.py:193-301`)
- Status: approved - the owner's word to land S1 (2026-10-18T15:01:53Z) approves it with its recommendation:
  the fields are removed
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T13:21:00Z
- Updated: 2026-10-18T15:40:03Z

## Component Purpose and Boundary
- Current boundary: at every bind the strategy computes `InspectorUtility.stable_repr(...)` - the full repr with
  memory addresses removed - of each callable, each callable parameter's default, each existing object and each other
  object, and stores it as `fingerprint_repr` / `default_fingerprint_repr` beside the truncated display text
  (`repr_string`, `default_repr`). Their one reader is the fingerprint (`Bind._fingerprint_repr_text`,
  `Bind._fingerprint_default_text`; searched: src/melder).
- Target boundary: the four fields, their constructor keywords, their cleanup deletions and the `stable_repr` calls
  that fill them are removed. The display fields stay; `InspectorUtility.stable_repr` stays, because SpellCodeDigest
  uses it for a target with no Python-visible state and for an object of an installed third-party class
  (decision B; code-description patch).

## Before/After Behavior Summary
- Before: one or two full reprs per callable and per object at bind, kept on the profile for its life.
- After: none of them. Nothing else reads the fields, so no published payload, record or Nexus view changes.

## Interface Deltas
- Inputs: the constructor keywords `fingerprint_repr` (three profile classes) and `default_fingerprint_repr`
  (the parameter summary) are removed - internal API.
- Outputs: the profiles no longer carry the two attributes.
- Error semantics: unchanged.

## State and Lifecycle Deltas
- Owned state changes: four slots removed; `cleanup` deletes the fields that remain.
- Lifecycle/cleanup changes: none beyond that.

## Failure Mode Deltas
- New failure mode: none. Removed failure mode: none. Changed failure mode: none.

## Dependency and Ordering Constraints
1. Lands with the Binding Pipeline patch, which removes the fields' only reader.

## Validation Expectations
- `tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py` (four
  references today) asserts the display fields and no fingerprint field.
- The callable, instance and other profiles still build for a TYPE_CHECKING-only annotation, a default rendering an
  address and a broken `__repr__` (the existing tests of those cases keep passing).

## Unknowns and Open Decisions
- UNKNOWN: none in the code paths read.
- DECIDED (the owner's word to land S1, 2026-10-18): the fields are removed, as recommended - a field nothing
  reads is a second, stale description of identity.

## Context / Handoff Summary
- What changed: nothing in `src/`.
- Remaining risks: none known.
- Next entrypoint:
  `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:BindingProfileStrategy._build_callable_profile`.
