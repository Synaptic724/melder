# component_patch_nexus_acl_managers

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Nexus Descriptor And ACL Managers
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:58:40Z
- Updated: 2026-09-26T09:58:40Z

## Component Purpose and Boundary
- Current boundary: the ACL compiler, the set compatibility validator, the profile builder and the configuration chain
  annotate their collaborators; `src/melder/nexus/acl/`.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: 21 annotation owners in four modules named types no scope bound, even under `TYPE_CHECKING`:
  `FrameACLRuleSet` and `FrameACLViewProfile` were never imported, `IFrameACLProfileBuilder` does not
  exist anywhere, and `frame_acl_configuration_chain.py` used `Any` without importing it.
- After: `TYPE_CHECKING` imports of `FrameACLProfileBuilder`, `FrameACLRuleSet` and `FrameACLViewProfile`
  in `frame_acl_compiler.py`, of `FrameACLProfileBuilder` and `FrameACLRuleSet` in
  `frame_acl_set_compatibility_validator.py`, of `FrameACLRuleSet` in `frame_acl_profile_builder.py`;
  `IFrameACLProfileBuilder` becomes the concrete `FrameACLProfileBuilder` (the object the manager
  injects); `Any` joins the `typing` import of `frame_acl_configuration_chain.py`.

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
- Guard: `tests/unit/melder/test_annotation_integrity.py` library static and dynamic passes report zero
  findings for these modules.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (owner approved the audit fixes 2026-09-26).

## Context / Handoff Summary
- What changed: annotation-only fixes found by the annotation integrity audit.
- Remaining risks: none known; the concrete type matches the injected object.
- Next entrypoint: architecture_patch.md.
