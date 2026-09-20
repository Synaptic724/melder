# Constructor-default precedence: measured current behavior

The defect is inferred class DI taking precedence over an ordinary explicit Python default.
Numeric and other plain-data defaults are already honored. This is not a failure of every default.

The expanded experiment completed **27 characterization tests in 0.49 seconds** on the upgraded
CPython 3.14.7 free-threaded environment. These tests describe current behavior, including defects;
they do not mean the requested default-first policy has been implemented. Runtime source is unchanged.

## Measured cases

| Parameter/default | Provider condition | Current outcome |
| --- | --- | --- |
| `count: int = 42` | Something registered | 42 preserved |
| `zero: int = 0`, `enabled: bool = False` | Something registered | 0 and False preserved |
| float 1.5, strings including empty, tuple (1, 2), Optional[int] = None | Something registered | Every selected value preserved |
| `dependency: Optional[object] = None` | Something registered | None preserved; provider not created |
| `dependency: Optional[Something] = None` | Something registered | Something injected; None ignored |
| `dependency: Optional[Something] = None` | No Something registered | Phase-3 failure; constructor never runs |
| `dependency: Something = chosen_instance` | Something registered | Chosen default replaced by the registered provider |
| `dependency: Something = chosen_instance` | No Something registered | Phase-3 failure despite the usable default object |
| Explicit `SpellMap(Something)` default | Something registered | Explicit DI request injects Something |

All cases ran in automatic pre-conjure binding, dynamic pre-conjure binding and dynamic post-conjure
binding. For the Optional user-class case, default, named-only and named-plus-spellframe registrations
all inject: annotation matching checks class identity and does not require the public meld lookup key.

Missing providers fail during `conjure` for prebind, with PhaseExecutionError for local_frame; dynamic
postbind fails during consumer `bind`, with the underlying no-DI-candidate RuntimeError.

## Cause

1. Phase 1 recognizes the user-class annotation as SINGLE_BY_ANNOTATION even when has_default is true.
   The default only contributes to is_optional; it does not prevent inferred injection.
2. Phase 2 preserves that DI classification and optional flag.
3. Phase 3 resolves the annotation to a provider and builds a dependency edge. With no match, it
   raises unconditionally rather than allowing the constructor default.
4. A matching provider therefore overrides both None and valid non-None instance defaults.

Source evidence:
- `src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1087-1306`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:105-176`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-255`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:434-510`

## Owner's proposed corrected rule

Honor ordinary explicit defaults regardless of whether an inferred provider is registered.
Keep explicit DI descriptors such as SpellMap/SpellContract as requests for injection/contract behavior.
Continue inferring DI for eligible parameters without a Python default.

This points to correcting Phase-1 classification precedence using **has_default**, not truthiness.
Only relaxing Phase 3's zero-candidate error would leave the registered-provider override defect intact.
Required DI and ambiguity handling should retain their contracts; those need regression checks in the patch.

The patch must also invalidate older .melc plans or otherwise version the semantic change: the binding
signature has not changed, so an old cached plan could still inject a provider. Current CachingSystem
version 7 invalidates bundles by cache-format/version metadata; this is an existing compatibility mechanism.

No runtime patch is applied during the owner-requested discussion/testing phase.

## Separate observed issue

With dynamic postbind, consumer injection succeeded, but a subsequent ordinary direct meld of the
provider failed because its own spell_codegen_creation was absent. That is separate from default
precedence. The identity assertion now uses the public reuse-only meld_existing_spell(spell=SHA)
to observe the existing provider without triggering another root compile. The original failure is
retained in `late_provider_root_failure.log`; its runtime cause remains to be triaged separately.

## Reproduce the historical characterization

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& '.venv_new/Scripts/python.exe' -m pytest context_compass/artifacts/optional_dependency_resolution_20260913/default_characterization_before_regressions.py -p no:cacheprovider -o addopts= -q -s
```

Evidence: `default_matrix.log`, `default_matrix.xml`. Scoped Ruff correctness checks pass.
The initial 15-case run is retained in `results.log` and `results.xml`.

The owner subsequently requested desired-contract red regressions. Those now live in
`tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py`, with the
original experiment path forwarding to that suite. See `red_regression_status.md` for the
20-fail/20-pass baseline; the earlier characterization source is archived beside this report.
