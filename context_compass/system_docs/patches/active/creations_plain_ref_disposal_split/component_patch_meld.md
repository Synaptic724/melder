# component_patch_meld

## Metadata
- Patch ID: creations_plain_ref_disposal_split
- Component: meld
- Status: draft
- Owner: codex
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-05-26T22:36:42Z

## Component Purpose and Boundary
- Current boundary:
  `Meld` resolves spell identity, enforces gating, and reads retained entries as
  `Creation` wrappers.
- Target boundary:
  `Meld` keeps the same resolution/gating role but accepts raw retained refs
  for non-disposable entries.

## Before/After Behavior Summary
- Before:
  retrieval paths use `creation.value` and `isinstance(..., Creation)`.
- After:
  retrieval paths accept raw refs or `Creation` wrappers without changing spell
  identity or gating behavior.

## Interface Deltas
- Inputs:
  retained-entry lookup results may now be raw objects.
- Outputs:
  returned runtime object is unchanged.
- Error semantics:
  still raise when an expected retained entry is missing.

## State and Lifecycle Deltas
- Owned state changes:
  none
- Lifecycle/cleanup changes:
  none beyond accepting the new storage model.

## Failure Mode Deltas
- New failure mode:
  inconsistent unwrapping if one lookup path is missed.
- Removed failure mode:
  unnecessary hard dependency on universal `Creation` storage.
- Changed failure mode:
  none intended.

## Dependency and Ordering Constraints
1. Requires `Creations` storage split first.
2. Must stay aligned with generated creation-context runtime lookup code.

## Validation Expectations
- Test/validation item 1:
  `meld_existing_spell`, live-creation probe, and normal meld reuse.
- Evidence target 1:
  meld/conduit unit tests.

## Unknowns and Open Decisions
- UNKNOWN:
  none
- DECISION_REQUEST:
  none

## Context / Handoff Summary
- What changed:
  Meld storage expectation shift is bounded to retrieval.
- Remaining risks:
  missed lookup branches.
- Next entrypoint:
  `component_patch_creation_runtime_codegen.md`
