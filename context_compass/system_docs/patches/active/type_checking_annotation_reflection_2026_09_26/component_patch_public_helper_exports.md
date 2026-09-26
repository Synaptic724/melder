# component_patch_public_helper_exports

## Metadata
- Patch ID: type_checking_annotation_reflection_2026_09_26
- Component: Packaged Hardcopy Documents And Public Helper Exports (ProtocolCrafter Utility)
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T09:12:40Z
- Updated: 2026-09-26T09:12:40Z

## Component Purpose and Boundary
- Current boundary: `ProtocolCrafter.craft_protocol_code(...)` mirrors a live class into protocol
  source by reflecting class annotations, properties and method signatures.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: `_collect_attributes` read class `__annotations__`, `_render_signature` and
  `_get_property_annotation` read VALUE-format signatures; any TYPE_CHECKING-only name raised
  NameError, including on Melder's own `Spellbook` and `Conduit`.
- After: all three read `Format.FORWARDREF`; `_render_annotation` renders an owner-bearing ForwardRef
  as the quoted name (`"Decimal"`), matching how class names are rendered. Typing's ownerless
  ForwardRefs keep today's rendering.

## Interface Deltas
- Inputs: none changed.
- Outputs: protocol text for previously failing classes; unchanged text for others.
- Error semantics: NameError from unavailable names no longer escapes.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- Removed failure mode: NameError when mirroring TYPE_CHECKING-annotated classes.
- New/changed failure mode: none.

## Dependency and Ordering Constraints
1. `ProtocolCrafter(Conduit)` also needs the Conduit Runtime annotation fix (conduit patch).

## Validation Expectations
- Regressions: `test_protocol_crafter_mirrors_class_with_type_checking_annotations`,
  `test_protocol_crafter_mirrors_melder_conduit`.
- Existing `test_protocol_crafter.py` passes unchanged.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (quoted-generic `Any` rendering is a separate, recorded finding).

## Context / Handoff Summary
- What changed: FORWARDREF reads plus one render branch.
- Remaining risks: none.
- Next entrypoint: architecture_patch.md.
