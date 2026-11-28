# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: meld_by_spell_index_id_2026_11_28
- Component: Meld Resolution Runtime
- Status: implemented at 0.2.8317; merged into src_architecture, src_components, tests_components and the
  source graph
- Owner: Mark (owner); executor melder_0
- Created: 2026-11-28T19:00:37Z
- Updated: 2026-11-28T19:55:00Z

## Component Purpose and Boundary
- Current boundary: `Meld._resolve_spell_by_id` reads the active pool, the active versions and the borrowed copies,
  then raises KeyError "[MELD] No spell found with spell_id: <id>".
- Target boundary: unchanged, but for the text of that KeyError.

## Before/After Behavior Summary
- Before: a parked version's spell_id reads as missing.
- After: on that miss only, the door reads its Book's parked maps lock-free - `_inactive_spells`, then each
  borrowed conduit's `_inactive_contracted_spells` through a one-call snapshot - and when one holds the id, the
  KeyError keeps its first words and adds:
  "'<Name>' (spell_id <id>) is a parked version of SpellIndex <index id>, and a meld builds only an active version.
  Meld spell_index_id='<index id>' for the version that index has active, or notch this one active first."

## Interface Deltas
- Inputs: none.
- Outputs: none.
- Error semantics: the KeyError text above; its type and first words are unchanged.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none.
- Changed failure mode: the parked spell_id miss names its index.

## Dependency and Ordering Constraints
1. The parked reads run only after the three active reads miss and take no lock (single `dict.get` calls and a
   one-call snapshot), so no lock-order edge is added on a path that may hold a conduit's or an index's ticket.

## Validation Expectations
- A parked version's spell_id melded: KeyError with the index id; an unknown spell_id: the text as before.

## Unknowns and Open Decisions
- Settled 2026-11-28: the callers of `_resolve_spell_by_id` are the meld doors' entry lanes
  (conduit_meld.py, spellspace_meld.py) and `Meld._resolve_spell` / `_resolve_visible_version_by_id`; the miss text
  takes no lock, so none of them gains a lock edge. Every test that checks the text matches its first words
  (`match="No spell found with spell_id"`, five files).
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: implemented at 0.2.8317 as specified; the refinements and the measured cost are in
  architecture_patch.md; merged into the canonical system documents.
- Remaining risks: none in this patch; C9 of #209 is a defect found in passing, not introduced here.
- Next entrypoint: none (completed).
