# Component patch: a refused notch moves nothing (failed_notch_refusal_2026_10_18)

## Before / after behavior
- Before: `Spellbook._notch_spell` calls the seam `_apply_notch` - park the outgoing version and clean its creation
  context, promote the incoming, repoint the index and the frame claim, emit the index crystal, journal the
  promotion, re-register the lineage, mark its dependents, register the incoming with the RiskManager, publish it to
  Nexus, invalidate it, gate its verdicts - and returns. Phases 1-4 for a never-compiled incoming version run at the
  transaction's commit, after the strategy's commit delta; a broken version raises there and nothing undoes the seam.
- After: `_notch_spell` records the before-state, calls the seam, and - for an incoming version with no Phase-4
  result and no Phase-5 root blueprint, the commit validator's own test - runs its phases 1-4 at once, still inside
  the window. A version that passes is journaled and returned as before. A version that fails is refused:
  `_revert_refused_notch` puts the before-state back, the refused version's Phase 1-4 artifacts are reset, and
  SpellbookValidationError is raised with the refusal line before the report, chained from the check's error.
  `Conduit.notch_spell`'s `try` then ends the transaction as failed: no commit delta, no dirty marker, no fan-out.

## Interface deltas
- None public in this component (the error's `preface` has its own patch). Internal:
  `_revert_refused_notch(spell_index, refused, restored, before)`; `_apply_notch` no longer journals.

## State and failure deltas
- New transient state only: the before-state the entry records - the index's active version (or None), its
  `selected_spell_id`, the Book's address lookup and the frame claim for the incoming version's key, whether
  SpellSystemStates tracked the index, the lineage's direct dependencies and the outgoing version's registered
  topology.
- Reversal when there was an active version: the seam run toward it (`_apply_notch(restored)`, change reason
  `mutation_rolled_back`), which repoints the restored version's key - its Book lookup and frame claim - as a
  notch back does. The lineage's direct dependencies and the outgoing version's topology, with the collection
  and contract indexes it feeds, are registered again: the check's Phase 3 put the refused version's there,
  and another Book's resolution would read the restored version as depending on them. When the refused
  version's key differs, that key's lookup and claim are then set back to
  their before-values (released when they had none), since the seam repoints only the key of the version it
  promotes. A key the two share is left as the promotion set it: setting it back would release the restored
  version's claim and lookup wherever staging the refused version had dropped them
  (STORY-2026-10-17-staged_version_releases_active_signature), and the old version could not be melded by
  address.
- Reversal when there was none (an index `remove_from_spell_index` minted, whose version is selected but parked):
  park the refused version and clean its creation context; the selection back to its before-id; the lineage
  unregistered when SpellSystemStates did not track it; its RiskManager entry removed; its Nexus record removed; the
  index crystal emitted; the key's lookup and claim set back.
- Failure: a reversal that raises is a Melder bug - RuntimeError naming both versions, chained from the reversal's
  error, whose context is the check's error. Any other error from the check (not a validation verdict) is re-raised
  as it is, after the reversal has run.

## Dependency and ordering
- Called only from `Conduit.notch_spell`, inside its `notch` window; restore and graft notch through it too.
- The commit validator (`ChangeControlManager._default_structural_validator`) keeps its notch branch and finds the
  Phase-4 result present; its docstring says so.

## Validation expectations
- Component: English active, SelfMade staged (its constructor takes its own class). `notch_spell` to SelfMade raises
  SpellbookValidationError whose first line says the notch did not happen and names English as active; afterwards
  the index selects English, English is in the active maps and SelfMade parked, the frame claim and the Book lookup
  name English, Nexus holds English's record, English melds by address and by spell_id, and SelfMade's Phase-4
  result is None; a second `notch_spell` to SelfMade is checked and refused the same way.
- Component: the same with an index-linked borrower: its copies are untouched (English active, SelfMade parked) and
  its consumer melds English.
- Component: both refusals again with a version broken for an ordinary reason - TimedGreeter, whose `clock: Clock`
  parameter has two registered providers ([AMBIGUOUS_PROVIDER]) - so the refusal does not depend on what the
  check finds.
- Component: a minted index (no active version) refused: nothing active, the selection and the claim as before, no
  SpellSystemState and no Nexus record for it.
- Component: MutationResearch active - a refused notch journals nothing, a standing notch journals once.
- Component: after a refusal and one meld of English, the Book's validation-required flag is down and the next meld
  takes the warm door.
- Integration: probe N1-N3 as tests - N1 unchanged; N2 ends with the lender and the borrower on English; N3's notch
  back to English is a no-op; GIL off and on.
