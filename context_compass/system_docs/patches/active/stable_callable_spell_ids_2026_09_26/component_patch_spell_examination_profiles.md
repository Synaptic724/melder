# component_patch_spell_examination_profiles

## Metadata
- Patch ID: stable_callable_spell_ids_2026_09_26
- Component: Spell Examination Profiles (binding profiles, BindingProfileStrategy, InspectorUtility)
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T10:42:41Z
- Updated: 2026-09-26T10:42:41Z

## Component Purpose and Boundary
- Current boundary: BindingProfileStrategy builds shallow binding profiles; repr_string and parameter
  default_repr come from InspectorUtility.safe_repr (repr() truncated at 120 characters).
- Target boundary: unchanged; the profiles also carry the text the fingerprint hashes.

## Before/After Behavior Summary
- Before: the only repr text on a profile is the display text, which embeds "at 0x..." for functions,
  methods, partials, callable instances, default-repr instances and object() defaults, and is truncated.
- After: InspectorUtility.stable_repr(obj) returns the full repr() with every " at 0x<hex>" removed (never
  raises; same placeholder as safe_repr on failure). The strategy stores it as fingerprint_repr on
  callable/instance/other profiles and as default_fingerprint_repr on each parameter summary with a default.
  repr_string and default_repr (display) are unchanged.

## Interface Deltas
- Inputs: new keyword-optional constructor arguments (default None) on the three profile classes and a
  fifth positional-optional argument on CallableParameterBindingSummary.
- Outputs: the new attributes; None when a caller did not supply them.
- Error semantics: none new.

## State and Lifecycle Deltas
- Owned state: one str/None slot per profile (deleted in cleanup like the other slots); the parameter
  summary gains one slot.

## Failure Mode Deltas
- Removed: none directly (consumed by Bind).
- New: none. stable_repr calls repr() once more per bound object at bind time.

## Dependency and Ordering Constraints
1. Must land with Bind.sha256_profile consuming the fields.

## Validation Expectations
- Unit: stable_repr on function, lambda, bound method, partial, default-repr object, custom repr, failing
  repr, long repr (not truncated).

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: address-free fingerprint text beside the display text.
- Remaining risks: none known.
- Next entrypoint: architecture_patch.md.
