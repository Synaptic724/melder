# component_patch_conduit_runtime

## Metadata
- Patch ID: meld_by_spell_index_id_2026_11_28
- Component: Conduit Runtime (Normal and Lesser) and, for `SpellSpace.meld`, Creations and SpellSpace
- Status: implemented at 0.2.8317; merged into src_architecture, src_components, tests_components and the
  source graph
- Owner: Mark (owner); executor melder_0
- Created: 2026-11-28T18:59:59Z
- Updated: 2026-11-28T19:55:00Z

## Component Purpose and Boundary
- Current boundary: `Conduit.meld`, `SpellSpace.meld` and `Conduit.managed_spell_meld` take `spell`, `spell_id`,
  `spellframe`, `binding_name` and `override`.
- Target boundary: each also takes keyword-only `spell_index_id=None`.

## Before/After Behavior Summary
- Before: a meld names a version by spell_id, or an index's active version by name, class or address.
- After: `spell_index_id=` names an index; the door asks its Book for the version the index selects and melds that
  spell_id through the existing lane - on an automatic conduit and in a SpellSpace through the warm id lane, in a
  dynamic conduit with the conduit's ticket held from before the read until the door returns, as a name is resolved
  under it today. `managed_spell_meld(spell_index_id=...)` resolves its target the same way and leases as before.

## Interface Deltas
- Inputs: `spell_index_id: Optional[str]`, exclusive with `spell`, `spell_id`, `spellframe` and `binding_name`.
- Outputs: what a meld of the selected spell_id returns.
- Error semantics: ValueError for a mixed call, TypeError for a non-str id, the Book's KeyError for an unknown id;
  every other error is the existing lane's.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: the three refusals above.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The new keyword is tested once, at the door's entry, before the warm lanes; a call that does not pass it runs the
   same code as before.
2. The index form re-enters the door's id form, so its results, errors, lifetimes and hooks are the id form's.

## Validation Expectations
- Each door by index id: the active version, the incoming version after a notch, a borrowed index, the refusals.
- Warm-meld timings of the existing forms before and after, the GIL off.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: implemented at 0.2.8317 as specified; the refinements and the measured cost are in
  architecture_patch.md; merged into the canonical system documents.
- Remaining risks: none in this patch; C9 of #209 is a defect found in passing, not introduced here.
- Next entrypoint: none (completed).
