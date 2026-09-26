# component_patch_binding_pipeline

## Metadata
- Patch ID: stable_callable_spell_ids_2026_09_26
- Component: Binding Pipeline (Bind, Spell, SpellIndex)
- Status: active
- Owner: user (writer: melder_1)
- Created: 2026-09-26T10:42:41Z
- Updated: 2026-09-26T11:04:31Z

## Component Purpose and Boundary
- Current boundary: Bind.sha256_profile turns a binding profile plus binding metadata into the spell id.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: callable, instance and other branches hash repr_string and each default_repr as displayed, so
  ids of 10 of 14 measured shapes change every process.
- After: those branches hash fingerprint_repr / default_fingerprint_repr; when a profile lacks them the
  display text is used with " at 0x<hex>" removed. The callable signature text and the class
  init_signature text are hashed with addresses removed as well, because str(signature) renders default
  reprs (found during implementation: a class with an object() default was process-local). Prefix,
  metadata parts and part order unchanged.

## Interface Deltas
- Inputs/outputs: none (same signature, same hex digest shape).
- Behaviour: affected ids (including classes with address-rendering constructor defaults) change once
  to process-stable values; already-stable ids do not move.

## State and Lifecycle Deltas
- None.

## Failure Mode Deltas
- Removed: per-process id drift for affected spells (cache misses, bundle growth, repeated MutationResearch
  declarations).
- Changed: two distinct objects with identical fingerprint inputs and identical binding metadata now share
  an id; Spellbook's existing collision checks reject the second bind (it already shared the lookup key).

## Dependency and Ordering Constraints
1. Profiles/strategy first; this consumes their fields.

## Validation Expectations
- Unit: address-only differences give equal ids; content differences still differ; fallback path.
- Component: separately defined, content-identical functions/instances/methods/partials get equal ids;
  a fresh process reproduces the ids.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (owner approved option 1).

## Context / Handoff Summary
- What changed: address-free fingerprint inputs.
- Remaining risks: none known.
- Next entrypoint: architecture_patch.md.
