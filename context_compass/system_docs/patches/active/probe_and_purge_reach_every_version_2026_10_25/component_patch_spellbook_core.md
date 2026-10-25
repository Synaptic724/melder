# component_patch_spellbook_core

## Metadata
- Patch ID: probe_and_purge_reach_every_version_2026_10_25
- Component: Spellbook Core - the Book's id maps (`src/melder/aether/spellbook/spellbook.py`)
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T03:03:37Z
- Updated: 2026-10-25T03:03:37Z

## Component Purpose and Boundary
- Current boundary: the Book keeps each version in exactly one of four id maps - `_spells_by_id` (owned, active),
  `_inactive_spells` (owned, parked), `_contracted_spells_by_id[lender]` (borrowed, active) and
  `_inactive_contracted_spells[lender]` (borrowed, parked) - and every writer moves a version between them under
  the Book lock, taking it out of one map before putting it in the other (`_deactivate_owned_spell`,
  `_reactivate_owned_spell` and their borrowed twins). `find_spell_by_spell_id` reads the two owned maps without a
  lock and can miss a version between a move's two steps; `_get_owned_spell` reads them under the lock.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:332-352
  - src/melder/aether/spellbook/spellbook.py:1594-1716
  - src/melder/aether/spellbook/spellbook.py:1717-1869
  - src/melder/aether/spellbook/spellbook.py:2146-2222
  - src/melder/aether/spellbook/spellbook.py:3441-3456
- Target boundary: `_find_visible_version(spell_id) -> Optional[Spell]` reads the four maps once under the Book
  lock and returns the version found, owned before borrowed, or None.

## Before/After Behavior Summary
- Before: no lookup covers the borrowed maps by spell_id with the parked ones; `_find_contracted_spell_by_id`
  answers a parked borrowed copy with the index's active copy.
- After: one internal lookup answers exactly the version a spell_id names, wherever the Book keeps it.

## Interface Deltas
- Inputs: `spell_id: str`.
- Outputs: the Spell, or None.
- Error semantics: RuntimeError from `check_cleaned` on a cleaned Book; nothing else.

## State and Lifecycle Deltas
- Owned state changes: none (reads only).
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none in the Book itself.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The Book lock is taken alone: the caller holds no Melder lock (the Meld's miss path, before any store, slot or
   spell lock), and nothing runs under it but dict reads.
2. Callers: `Meld._resolve_visible_version_by_id` only.

## Validation Expectations
- Test/validation item 1: through the Meld doors (component and integration files); no separate Book test, since
  the lookup is internal and its whole contract shows through purge and the probes.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none beyond the lock note in code_description_patch_meld_resolution_runtime.
- Next entrypoint: beside `Spellbook._get_owned_spell`.
