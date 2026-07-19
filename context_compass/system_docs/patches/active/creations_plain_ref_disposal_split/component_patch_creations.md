# component_patch_creations

## Metadata
- Patch ID: creations_plain_ref_disposal_split
- Component: creations
- Status: draft
- Owner: codex
- Created: 2026-05-26T22:36:42Z
- Updated: 2026-05-26T22:36:42Z

## Component Purpose and Boundary
- Current boundary:
  `Creations` owns mixed retained storage, disposal stacks, spellspace buckets,
  extract/restore, and pool reset.
- Target boundary:
  `Creations` still owns those responsibilities, but non-disposable retained
  entries are stored as raw refs while disposal-tracked entries keep explicit
  metadata.

## Before/After Behavior Summary
- Before:
  unique-like and spellspace retained entries are universally wrapped in
  `Creation`.
- After:
  non-disposable retained entries store raw refs; only disposal-tracked entries
  use `Creation`.

## Interface Deltas
- Inputs:
  `add_creation(...)` and `register_spellspace_creation(...)` must branch by
  disposal need.
- Outputs:
  extract/restore payloads become generic stored-entry payloads.
- Error semantics:
  unchanged for duplicate keys and invalid bucket shapes.

## State and Lifecycle Deltas
- Owned state changes:
  `_creations` becomes mixed raw-ref vs `Creation` storage by intent, not by
  accident.
- Lifecycle/cleanup changes:
  cleanup and pool reset only explicitly dispose entries enrolled in the
  disposal stacks.

## Failure Mode Deltas
- New failure mode:
  retrieval paths may mis-handle raw refs if not updated consistently.
- Removed failure mode:
  unnecessary wrapper-only cleanup for non-disposable retained entries.
- Changed failure mode:
  transfer restore now has to preserve raw-vs-disposable entry shape.

## Dependency and Ordering Constraints
1. `Creations` must land before `Meld` and generated runtime retrieval edits.
2. extract/restore payload shape must be updated atomically with retrieval.

## Validation Expectations
- Test/validation item 1:
  unique/spellspace add/get/extract/restore paths.
- Evidence target 1:
  direct creations/conduit unit tests.
- Test/validation item 2:
  pool reset still clears retained state correctly.
- Evidence target 2:
  conduit pooling and spellspace tests.

## Unknowns and Open Decisions
- UNKNOWN:
  whether any direct tests assert `Creation` wrapper identity for plain entries.
- DECISION_REQUEST:
  none

## Context / Handoff Summary
- What changed:
  component contract defined
- Remaining risks:
  mixed-shape retrieval consistency
- Next entrypoint:
  `code_description_patch_creations.md`
