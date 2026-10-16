# Component patch: a notch back reactivates parked borrowed copies (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Components: Conduit (`src/melder/aether/conduit/conduit.py`: `notch_spell`, new `_activate_borrowed_spell`);
  ConduitWard (`src/melder/aether/conduit/conduit_ward/conduit_ward.py`: `_add_spell_to_contract` docstring)
- Status: active; the fan-out only with D3, the docstring correction in every option
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of both files)
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T10:32:18Z

## Component purpose and boundary
- Current boundary: after a notch's transaction ends, `Conduit.notch_spell` has every linked peer park its copy of
  the outgoing version (`_deactivate_borrowed_spell` -> `Spellbook._inactivate_contract_spell`) and has the ward
  move index-link contracts to the incoming version (`ConduitWard._emit_index_notch`: park the old copy, then
  `_ensure_contracted_active` for the new one). A version-anchored copy (a grant of one version) is parked when its
  version leaves and nothing makes it active again: `Spellbook._activate_contract_spell` has no caller, although the
  docstrings of `_add_inactive_contracted_spell` and `_activate_contract_spell` say the owning Conduit drives it at a
  notch. The grant's docstring says lookups "will resolve to the new version", which no code does for a grant.
- Target boundary (D3): the notch fan-out also reactivates, on every linked peer, a parked copy of the incoming
  version - the mirror of the deactivate fan-out - so a version-anchored copy is active exactly while its version is
  the lineage's active member. Index links keep following every version through `_emit_index_notch`.

## Before / after
- Before: grant of A; notch to B parks the copy of A; notch back to A leaves it parked, so the consumer has no
  provider until someone grants A again (probe S2, every mode).
- After (D3): `notch_spell`, when the active member changed: `_deactivate_borrowed_spell(outgoing_id)`, then
  `_activate_borrowed_spell(spell.spell_id)`, then `_emit_index_notch(...)`. `_activate_borrowed_spell` walks
  `ward._get_links()` as the deactivate fan-out does and calls `peer._spellbook._activate_contract_spell(owner_id,
  spell_id)`, which is idempotent (a no-op for a peer holding no parked copy of that version). The reactivation is a
  `_reactivate_contracted_spell`, so rule 2's mark rechecks the consumers (component_patch_borrower_contracted_maps.md).
  On an index-link receiver holding a parked copy of the incoming version the copy is reactivated here and
  `_ensure_contracted_active` then finds it active: the same end state as today.
- Grant docstring (every option): "It contracts one version of the spell's SpellIndex lineage. The borrower holds a
  copy of that version: active while the version is the lineage's active member, parked while it is not - a notch
  away parks it on every linked peer and a notch back reactivates it [D3; without D3: "and nothing reactivates it;
  grant the active version again, or link the index"]. An index link (`_add_index_to_contract`) follows the lineage
  to every new version instead."
- Without D3 the two Spellbook docstrings that promise the reactivation are corrected too (spellbook.py, inside
  melder_0's handoff).

## Interface deltas
- Inputs and outputs: `notch_spell` unchanged; one private method added.
- Error semantics: unchanged; `_activate_contract_spell` raises only on a cleaned Book (or, through rule 2's mark,
  a cleaned registry), as the deactivate fan-out's call does.

## State and lifecycle deltas
- None beyond the copy's map moves: the lineage, its index and its contracts are untouched.

## Failure mode deltas
- Removed (D3): a version-anchored borrower stays without a provider after a notch back to its version.

## Dependency and ordering constraints
1. Runs after the notch transaction, like the deactivate fan-out; outgoing first, so a peer never holds two active
   copies under one key.
2. Rule 2's mark must land with it, or a reactivated copy changes nothing a consumer sees until its next unrelated
   recheck.

## Validation expectations
- Component, both GIL modes: grant A, notch to B (the consumer fails with the first meld's error), notch back to A
  (the consumer builds A with one 5-11 pass); a grant of a parked B followed by a notch to B activates it; an index
  link behaves as today; a peer that never borrowed the version is untouched.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: D3.

## Context / Handoff Summary
- What changed: written before any edit.
- Next entrypoint: code_description_patch_contract_recheck.md.
