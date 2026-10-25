# component_patch_aetheric_frame_services

## Metadata
- Patch ID: index_keeps_its_first_binding_2026_10_25
- Component: AethericFrame Services (the frame's LookupContainer)
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T09:13:34Z
- Updated: 2026-10-25T09:13:34Z

## Component Purpose and Boundary
- Current boundary: the frame's LookupContainer keeps one active spell_id per address, `claim` refusing a second
  spell; `update` sets an address to a spell_id unconditionally (the notch's repoint) and `release` /
  `release_by_spell_id` drop it. AethericFrame wraps each call.
- Target boundary: a fifth writer, `repoint`, moves an address only from the spell the caller expects, so a notch can
  move its index's claim without ever taking another spell's. `update` stays for setting a claim back to a recorded
  value (`Spellbook._restore_binding_key`).

## Before/After Behavior Summary
- Before: the notch's `update` overwrote whichever spell held the address.
- After: `repoint(key, spell_id, *, from_spell_id)` is one compare-and-set under the container's lock. The address is
  set to `spell_id` when it is free, held by `from_spell_id`, or already held by `spell_id`; the previous holder's
  reverse entry goes. Otherwise nothing changes and the holder's spell_id is returned. `AethericFrame.repoint_lookup`
  delegates.

## Interface Deltas
- Inputs: `LookupContainer.repoint(key: Tuple[str, str], spell_id: str, *, from_spell_id: Optional[str])`;
  `AethericFrame.repoint_lookup(key, spell_id, *, from_spell_id)`.
- Outputs: `Optional[str]`: None when the address now names `spell_id`; the holder's spell_id when it was refused.
- Error semantics: none raised; the caller decides what a refusal means (the notch raises).

## State and Lifecycle Deltas
- Owned state changes: none; the forward and reverse maps stay in lockstep, as every writer keeps them.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none here.
- Removed failure mode: none here; the notch's overwrite closes in Spellbook Core.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The container's lock stays a leaf, non-reentrant: `repoint` calls no other method while holding it.
2. Callers hold the Book lock around it, as they held it around `update`; no lock-order edge is added.

## Validation Expectations
- tests/unit/melder/aether/test_lookup_container_repoint.py: a free address claimed; an address moved from the expected
  spell with the reverse map; an address another spell holds refused with the holder returned and both maps unchanged
  (with `from_spell_id` None too); a repoint to the holder itself a no-op.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: the compare-and-set and its frame wrapper.
- Remaining risks: none known.
- Next entrypoint: `LookupContainer.repoint`.
