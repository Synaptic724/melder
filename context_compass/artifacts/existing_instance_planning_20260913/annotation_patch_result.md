# Annotation-only repair result

Implemented locally on Python 3.14.7 free-threaded, Melder source version 0.2.40.
The existing-instance planner, frame validation and disposal changes remain parked.

## Behavior

TYPE_CHECKING controls whether imports execute. It does not create a runtime type binding.
Python 3.14 partial annotation evaluation supplies ForwardRef values for unavailable names,
allowing Melder's existing normalization and provider matching to process the dependency.

Three production modules changed:
- BindingProfileStrategy: class and callable signatures use Format.FORWARDREF.
- SpellRequirementsFinder: fresh signatures and raw/fallback annotation acquisition preserve
  unresolved names. Existing namespace-aware string evaluation and DI classification remain.
- Meld: its late-bind contract-default signature check uses the same partial format.

Known signature objects/text, ordinary defaults, explicit overrides and missing-provider
validation retain their tested behavior. No compatibility layer for Python before 3.14 was added.

## Verification

- New live regressions: 15 cases covering class/function/collection DI before and after conjure,
  None and chosen-object defaults, explicit overrides, missing providers and compatibility controls.
- Initial unpatched baseline: 9 failed, 2 passed (before adding four runtime override cases).
- Final selected suite: 271 passed in 1.29 seconds; no in-memory prototype patches installed.
- Scoped test lint F/I and source correctness checks E9/F63/F7/F82 passed.
- Three touched source descriptors refreshed using the canonical extractor/merge functions;
  graph/index assembly check passed. Unrelated descriptors were not regenerated.
- All three durable source asset builders regenerated; all three --check results passed.
- Source and test LLM bundles regenerated; fingerprint/output proofs match.
  A transient Windows atomic-replace denial on the test bundle succeeded on retry.

Final test command:
```powershell
.venv_new/Scripts/python.exe -m pytest tests/integration/melder/spellbook/test_deferred_annotations.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/spell_requirements_finder tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy_future_annotations.py tests/integration/melder/spellbook/test_spellbook_integration_future_annotations.py tests/integration/melder/spellbook/test_spellbook_integration_future_annotations_more.py tests/unit/melder/aether/conduit/meld/test_meld.py tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py tests/integration/melder/spellbook/test_spellbook_integration_overrides.py -q --tb=short -p no:cacheprovider -o faulthandler_timeout=30
```

Evidence:
- annotation_red.log/xml
- annotation_patch_validation.log/xml: first patch, exposed the late-bind reader.
- annotation_patch_final.log/xml: annotation NameErrors gone; unrelated oracle failures preserved.
- annotation_patch_green.log/xml: final 271 passing checks.
- annotation_source_assets_check.log
- annotation_src_bundle_check.log
- annotation_live_tests_bundle_check.log
- annotation_acquisition_probe_before_fix.py: archived diagnostic, not a live regression suite.

## Scope limits

The original existing-object injection defect is not repaired by this annotation patch.
The late-bind provider-remeld missing-codegen observation was recorded in the ownership task.
Original CommandOps/Iris acceptance and the full repository suite were not rerun.
The previously delivered wheel predates this patch; no replacement wheel was built in this lane.
