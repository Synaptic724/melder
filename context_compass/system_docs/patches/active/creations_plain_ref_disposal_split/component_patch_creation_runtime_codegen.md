# component_patch_creation_runtime_codegen

## Metadata
- Patch ID: creations_plain_ref_disposal_split
- Component: creation_runtime_codegen
- Status: draft
- Owner: codex
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-05-26T22:36:42Z

## Component Purpose and Boundary
- Current boundary:
  generated creation-runtime lanes assume retained lookup returns
  `Creation.value`.
- Target boundary:
  generated lanes continue to use direct storage access where intended, but must
  accept raw refs for non-disposable entries.

## Before/After Behavior Summary
- Before:
  emitted no-overrides and overrides routes assume `creation.value`.
- After:
  emitted routes unwrap conditionally or use helpers that support raw refs and
  `Creation`.

## Interface Deltas
- Inputs:
  retained-entry lookups may return raw refs.
- Outputs:
  runtime object result is unchanged.
- Error semantics:
  unchanged for missing spellspace or missing retained entry.

## State and Lifecycle Deltas
- Owned state changes:
  none
- Lifecycle/cleanup changes:
  none

## Failure Mode Deltas
- New failure mode:
  generated source could keep one stale `creation.value` assumption.
- Removed failure mode:
  unnecessary universal wrapper dependence.
- Changed failure mode:
  none intended.

## Dependency and Ordering Constraints
1. Align with `Creations` storage split.
2. Keep phase12 registration semantics unchanged.

## Validation Expectations
- Test/validation item 1:
  no-overrides and overrides execution routes for unique/shared/spellspace.
- Evidence target 1:
  conduit/meld runtime tests.

## Unknowns and Open Decisions
- UNKNOWN:
  none
- DECISION_REQUEST:
  none

## Context / Handoff Summary
- What changed:
  generated runtime path boundary defined
- Remaining risks:
  missed emitted branch
- Next entrypoint:
  `code_description_patch_creations.md`
