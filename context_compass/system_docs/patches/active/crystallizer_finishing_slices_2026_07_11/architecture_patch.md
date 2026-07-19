# Architecture Patch: crystallizer finishing slices

- Patch ID: crystallizer_finishing_slices_2026_07_11
- Ticket: TASK-2026-07-11-crystallizer-finishing-slices
- Status: active

## Objective
Close the crystallizer's last analyzer leaves and ship the decided
merge-graft mode. All additive.

## Slice 1: site-package distribution provenance (source-verified design)
- SitePackageCustodyStrategy gains harvest_provenance(module_name,
  module_path) -> Optional[Dict]: {distribution_name,
  distribution_version} resolved via importlib.metadata
  .packages_distributions() from the module's TOP-LEVEL name, version()
  per distribution; honest None when unresolvable (namespace packages,
  vendored trees). NOT harvest_payload - that seam is retention-only
  and gated to user_source in the walk (crystal_analyzer.py:512); a
  separate verb keeps the retention law untouched.
- Walk branch beside the S2 harvest (crystal_analyzer.py:~522): when
  custody.kind == "site_package", harvest provenance ->
  result.record_distribution_provenance(module_name, payload).
  ALWAYS-ON (provenance is identity, not retention - no config knob).
- CrystalAnalysisResult: _distribution_provenance store + record verb +
  property + describe() key "distribution_provenance" + cleanup del +
  analyze_payload REFOLD (the MR re-analysis seam keeps parity).
- SpellCrystal: delegating property + describe passthrough (carrier
  law: carries the result, owns no logic).

## Slice 2: binary/dynamic identity capture
- BinaryUnknownCustodyStrategy: record the backing path + file-bytes
  sha256 for .so/.pyd leaves (identity only - NO parsing) into the same
  provenance channel under {"binary_path", "binary_sha256"}.
- Dynamic imports stay honest leaves this slice (importer-edge capture
  deferred until impact-engine consumers exist; recorded as residue).

## Slice 3: merge-graft mode (dial DECIDED - owner-delegated)
- GraftRunner(record, host_spellbook, skip_resident=False,
  merge_into_index_id=None): when merge target given, members enter the
  TARGET live index via the PUBLIC Spellbook.add_spell_into_spellindex
  verb (+ opt-in notch_spell when adopt_recorded_selection=True);
  fresh-index-only remains the DEFAULT; overlap rules unchanged
  (resident members refuse/skip identically). No index internals
  touched - public verbs only.

## Non-goals
No retention semantics changes; no loud-refusal weakening; no config
knobs for provenance (identity is unconditional).

## Validation expectations
Unit: provenance resolution hit/None lanes; binary sha capture;
merge-mode round trip via public verbs + refusal parity. Owner runs
3.14t; agent reports "Not run."

## Rollback
All additive: delete the verbs/channel/mode kwarg.
