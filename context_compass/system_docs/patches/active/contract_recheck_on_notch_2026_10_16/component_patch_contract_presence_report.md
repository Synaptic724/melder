# Component patch: the contract presence check and the lost-provider report (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Components: ContractProviderPresenceStrategy
  (`src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py`);
  SpellbookValidationError (`src/melder/utilities/custom_exceptions/spellbook_validation_error.py`)
- Status: active; the snapshot is recommended in every option, the message and the renderer only with D1 option B
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of both files)
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T10:32:18Z

## Component purpose and boundary
- ContractProviderPresenceStrategy, Phase 4: for each SpellContract socket of a resolvable spell it counts the
  providers its Book's active contracted maps hold under the contract key - none is the warning
  SPELL_CONTRACT_MISSING_PROVIDER, which is the one warning Phase 4 gates a lineage on (`gated` +
  `contract_unvalidated`), several are an error. With this patch it is also the recheck a marked consumer's next
  meld runs. Boundary unchanged.
- SpellbookValidationError: renders the message once from the spells' Phase-4 and Phase-6 results and the conduit
  diagnostics. It shows errors and only counts warnings, so a spell held `gated` by that warning is rendered "No
  validation error was recorded for this spell; its validity is invalid, gated or disabled." Boundary unchanged.

## Before / after
- Snapshot (every option): the strategy walks `spellbook._contracted_spells` and each peer's map live, without the
  Book lock, while the mutators write them under it. After: it walks one-call snapshots,
  `list(spellbook._contracted_spells.values())` and `list(contracted.items())`, once per validation pass (the map
  is pass-cached). Reason: under rule 2 this walk is the recheck that follows a provider change, so it can meet the
  rest of the same change still writing the Book's maps (a notch parks the old copy, marks, then activates the new
  one), and a live walk can raise "dictionary changed size during iteration" - the rule of 0.2.8230 for walks that
  cannot hold the Book lock.
- Message (D1-B): before, "Spell 'Consumer' parameter 'service' has no provider for contract key ('iservice',
  'svc')."; after, "Spell 'Consumer' parameter 'service' has no provider for its SpellContract
  (frame_key='iservice', binding_key='svc'): no active spell with that frame and binding name is contracted to
  this Spellbook. Contract one from a linked conduit (add_index_to_contract, or add_spell_to_contract for one
  version) and meld again." Code, severity and details unchanged.
- Renderer (D1-B):
  - `GATING_WARNING_CODES: ClassVar[FrozenSet[str]] = frozenset({"SPELL_CONTRACT_MISSING_PROVIDER"})` - the Phase-4
    warnings that hold a lineage `gated`.
  - `_spell_errors` returns the spell's errors, its gating warnings (code and message, in issue order) and the
    count of its other warnings.
  - `_compose`: a block whose errors, after the existing filters, are empty and whose gating warnings are not lists
    them as its reasons ("  - <message> [CODE]", never `[internal]`) instead of the generic line; the gating warnings
    of a block that shows errors, or of a block not shown, join the hidden-warning count. A block is shown when it
    has errors or gating warnings, or when no diagnostics were handed in (the meld path), as today.
  - The first line and the type are unchanged, so "Spellbook validation failed" and "Broken spells:" matchers pass.
  - The meld message for the probe's index destroy becomes: "Spellbook validation failed. Broken spells: Consumer." /
    "Consumer:" / "  - Spell 'Consumer' parameter 'service' has no provider for its SpellContract (...) ...
    [SPELL_CONTRACT_MISSING_PROVIDER]", with no footer.

## Interface deltas
- Inputs and outputs: none public. A public class constant `SpellbookValidationError.GATING_WARNING_CODES` (D1-B).
- Error semantics: messages only (D1-B). Conjure is unchanged: a spell held `gated` by this warning is not broken,
  so conjure never hands it to the error.

## State and lifecycle deltas
- None.

## Failure mode deltas
- Removed: a recheck racing a provider change on the same Book raising "dictionary changed size during iteration"
  from Phase 4.
- Changed (D1-B): a lost provider is named, with its remedy, where the meld said only that no error was recorded.

## Dependency and ordering constraints
1. `GATING_WARNING_CODES` must name the codes Phase 4 gates on (`CompilerPhase4.run`); a unit test pins it.
2. The snapshot keeps the pass cache: one snapshot per validation pass, not per spell.

## Validation expectations
- Unit (`test_spellbook_validation_error.py`, D1-B): no error plus the gating warning lists the warning with its
  code and no footer; plus another warning, the footer counts only the other; an error plus the gating warning
  lists the error and counts the warning; a spell with neither keeps the generic line (the existing test); with
  diagnostics, a block with only a gating warning is listed; the constant holds exactly the code Phase 4 gates on.
- Unit (`test_contract_provider_presence_strategy.py`): the D1-B message names the parameter, the key and the
  remedy; the existing code, severity and detail assertions stay.
- Component, GIL off: melds racing notches back and forth never raise from Phase 4's walk.
- The existing report tests (`test_spellbook_integration_validation_report.py`) stay green: their warnings are not
  gating.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: D1 (A keeps the message and the renderer; the snapshot is recommended in every option).

## Context / Handoff Summary
- What changed: written before any edit.
- Next entrypoint: component_patch_notch_reactivation.md.
