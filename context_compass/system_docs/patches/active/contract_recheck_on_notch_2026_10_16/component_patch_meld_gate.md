# Component patch: the meld gate stops scanning contracts (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Component: Meld (`src/melder/aether/conduit/meld/meld.py`): `_ensure_lineage_resolvable`,
  `_check_contracts_and_force_revalidation`, `_iter_spell_contract_defaults`, `_force_resolution_revalidation`
- Status: active
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of this file)
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T10:32:18Z

## Component purpose and boundary
- Current boundary: the meld-time validation gate, entered by `ConduitMeld.meld` and `SpellSpaceMeld.meld` only
  while the Book's validation-required flag is up. It has three steps: rerun phases 1-4 for an `unknown` or
  `gated` lineage; for every spell with a SpellContract default, scan the signature, look each contract key up in
  the Book's active contracted maps (MeldExecutionError on a miss) and gate the conduit verdict; rerun phases 5-11
  for an `unknown` or `gated` conduit verdict.
- Target boundary: two steps. The structural step is the contract recheck: it runs because a provider change marked
  the consumer `gated` + `contract_unvalidated` (component_patch_borrower_contracted_maps.md), and Phase 4's
  ContractProviderPresenceStrategy is the presence check.

## Before / after
- Before: every gated meld of a contract consumer reads `inspect.signature(call_target,
  annotation_format=Format.FORWARDREF)`, makes one `_resolve_contracted_by_lookup_key` call per contract and gates
  the conduit verdict (`contract_unvalidated`), so phases 5-11 rerun every time: 1470-1650 us a warm meld.
- After: `_ensure_lineage_resolvable` keeps its structural branch and its resolution branch unchanged and drops the
  call between them. A consumer whose lineage and verdict are `valid` passes with the two state reads every spell
  pays. A marked consumer reruns phases 1-4: a present provider makes the lineage `valid`, the branch gates the
  conduit verdict (`structure_changed`, as today) and phases 5-11 rebuild against the provider now active; a
  missing one leaves it `gated` and the branch raises `SpellbookValidationError([spell])`, the first meld's error.
- `_check_contracts_and_force_revalidation` and `_iter_spell_contract_defaults` are deleted; the Phase 8 analyzer
  and the Phase 9 processor keep their own `_iter_spell_contract_defaults`.
- `_force_resolution_revalidation`: code unchanged; its docstring stops naming contract callers (the structural
  branch is its only caller and passes `structure_changed`; the default stays).
- `_ensure_lineage_resolvable`'s docstring: the contract bullet becomes "a SpellContract consumer is rechecked by
  the structural step when a change of its provider has marked it; a satisfied contract costs nothing per meld".
- Imports: `from annotationlib import Format` and the `SpellContract` import leave meld.py (no other use);
  `inspect` stays (`_resolve_purge_spell` uses it).
- Comment: `ConduitWard._get_spell_contract_keys` says its signature read "Mirrors Meld._iter_spell_contract_defaults";
  it will name the Phase 8 analyzer's copy instead (the comment is updated, not removed).

## Interface deltas
- Inputs and outputs: none public; two private methods removed.
- Error semantics: a meld of a consumer whose provider is gone raises SpellbookValidationError from the structural
  branch where the scan raised MeldExecutionError ("SpellContract could not be resolved. Missing contracted provider
  for key (frame_key=..., binding_key=...) on param ..."). A first meld with no provider already raised
  SpellbookValidationError; every later meld now raises the same. Both are RuntimeError. A failing contracted lookup
  is no longer wrapped, because the meld makes none. D1 decides the message.

## State and lifecycle deltas
- None: the gate reads the same states and writes the same verdicts.

## Failure mode deltas
- Removed: the per-meld signature read, lookup and rebuild of every contract consumer.
- Changed: the lost-provider error type, as above.

## Dependency and ordering constraints
1. Lands with the Book marking in one notch; alone it stops consumers following their provider (measured
   2026-10-15).
2. The structural branch's `_force_resolution_revalidation(structure_changed)` stays: it is what rebuilds a
   consumer whose structure revalidated after a mark.

## Validation expectations
- Unit (`tests/unit/melder/aether/conduit/meld/test_meld.py`): the three scan tests and the two
  `_iter_spell_contract_defaults` tests are replaced by: a `valid` contract consumer passes the gate with no
  contracted lookup and no verdict write; a `gated` consumer that Phase 4 validates gates its verdict with
  `structure_changed` and reruns resolution once; a `gated` consumer still `gated` after Phase 4 raises
  SpellbookValidationError and no MeldExecutionError.
- Integration: the first-meld tests that expect SpellbookValidationError for a missing provider stay green
  (`test_conduit_integration_spell_contract_variants.py`); new ones meld after a notch, an index destroy and an
  uncontract and assert follow or the first meld's error.
- The probes: a warm borrower contract consumer at about 2 us, no scan, one 5-11 pass per provider change.

## Unknowns and open decisions
- UNKNOWN: none.
- DECISION_REQUEST: D1 (the message for a lost provider).

## Context / Handoff Summary
- What changed: written before any edit.
- Remaining risks: see the architecture patch.
- Next entrypoint: component_patch_contract_presence_report.md.
