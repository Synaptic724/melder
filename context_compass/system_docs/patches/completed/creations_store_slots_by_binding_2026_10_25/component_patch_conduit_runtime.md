# component_patch_conduit_runtime

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: Conduit Runtime (Normal and Lesser) (`src/melder/aether/conduit/conduit.py`)
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Component Purpose and Boundary
- Current boundary: `Conduit._register_to_creations(spell, instance)` files an existing-object spell's object in the
  conduit's store under `spell.spell_id` (conjure and post-conjure binds call it).
- Target boundary: the same verb filing under `spell.store_key`. melder_1 holds conduit.py for
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (docstrings); this lane edits only this method, after
  melder_1's OK.

## Before/After Behavior Summary
- Before: the object is filed by spell_id.
- After: the object is filed by store key, on its spell_id's shelf, so purge, the probes and teardown treat it as
  every other slot; the docstring names the key.

## Interface Deltas
- Inputs: none.
- Outputs: none.
- Error semantics: unchanged (RuntimeError for an existence other than `unique`; `add_creation`'s ValueError for a
  key already filed).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none.
- Changed failure mode: an existing object bound again under another binding (after `cleanup_spell`) while its first
  filing is alive is filed under both keys and disposed with each binding's list when the store ends; today the
  second filing fails with a logged ValueError and the first list alone runs. The key must follow the binding all
  the same: a plan reads an existing-object dependency from the owner store by the step's store key and publishes
  what it finds missing, so an object filed under the bare spell_id would be filed a second time by the first meld.
  Bound again under the same binding, the object is refused as today (one key).

## Dependency and Ordering Constraints
1. melder_1's OK for the edit (mailbox claim), or its S2 landing first.

## Validation Expectations
- The component and integration tests that bind existing objects, the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: one key.
- Remaining risks: an edit collision in conduit.py; resolved by the claim.
- Next entrypoint: the red tests.
