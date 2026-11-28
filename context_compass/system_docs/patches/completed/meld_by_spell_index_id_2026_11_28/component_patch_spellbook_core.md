# component_patch_spellbook_core

## Metadata
- Patch ID: meld_by_spell_index_id_2026_11_28
- Component: Spellbook Core (Binding and Conjure), with the Ownership Transfer subcomponent's writes of `_spells`
- Status: implemented at 0.2.8317; merged into src_architecture, src_components, tests_components and the
  source graph
- Owner: Mark (owner); executor melder_0
- Created: 2026-11-28T18:59:59Z
- Updated: 2026-11-28T19:55:00Z

## Component Purpose and Boundary
- Current boundary: the Book keeps its own indexes only as the keys of `_spells` (index -> active spell) and finds
  one by id by scanning them under the Book lock (`_find_spell_index_by_index_id`); borrowed indexes are keyed by id
  in `_contracted_indexes`.
- Target boundary: the Book also keeps `_spell_indexes_by_id` (index id -> SpellIndex) over exactly `_spells`' keys,
  and answers an index id with the id of the version it selects (`_selected_spell_id_for_index_id`).

## Before/After Behavior Summary
- Before: no meld path takes an index id; `get_spell_by_index_id` scans.
- After: `_selected_spell_id_for_index_id(spell_index_id)` reads `_spell_indexes_by_id`, then `_contracted_indexes`,
  and returns the index's `selected_spell_id`; an id neither holds raises KeyError naming it, and when one of the
  Book's parked versions belongs to that index the text says the index has no active version. `get_spell_by_index_id`
  is unchanged (no drive-by change).

## Interface Deltas
- Inputs: `spell_index_id: str`.
- Outputs: the selected version's spell_id.
- Error semantics: KeyError "[MELD] No SpellIndex found with spell_index_id: <id>" plus a sentence naming the remedy
  (an index of this Book or one borrowed by it; a parked-only index: notch a version active first).

## State and Lifecycle Deltas
- Owned state changes: `_spell_indexes_by_id` in `__slots__`, built in `__init__`, written beside every `_spells`
  write - `bind`, `_reactivate_owned_spell`, `_deactivate_owned_spell`, `cleanup_and_remove_spell`,
  `_destroy_spell_index`, `_pop_unwound_book_maps`, `_cleanup_components` - and at the four ownership-transfer sites
  that write a Book's `_spells` directly (the flip and its rollback).
- Lifecycle/cleanup changes: cleared with `_spells` in `_cleanup_components`, deleted with it in cleanup.

## Failure Mode Deltas
- New failure mode: the KeyError above for an unknown or parked-only index id.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Every map write sits in the same Book-locked section as its `_spells` write (the transfer holds both Books' locks).
2. Readers are lock-free single `dict.get` calls, as the meld doors read `_spells_by_id`.

## Validation Expectations
- The map equals `{index.id for index in _spells}` after bind, notch, cleanup_spell, a refused late bind, the index
  moves, a transfer (and a failed one) and teardown.
- Evidence target: the new component test file.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: implemented at 0.2.8317 as specified; the refinements and the measured cost are in
  architecture_patch.md; merged into the canonical system documents.
- Remaining risks: none in this patch; C9 of #209 is a defect found in passing, not introduced here.
- Next entrypoint: none (completed).
