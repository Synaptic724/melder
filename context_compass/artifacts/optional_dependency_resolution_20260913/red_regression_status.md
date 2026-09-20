# Default-first red regression baseline

Owner requested failing regression tests before changing runtime behavior.
The canonical test file is:
`tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py`.
Runtime CI includes `tests/integration`, so this file participates in normal CI discovery.

## Executed result

**40 cases: 20 failed, 20 passed, 0 errors, 0 skipped; 1.73 seconds.**
All twenty failures were checked against their intended defect categories.
There are no skip/xfail markers and no production monkeypatches.
The runtime source remains unchanged; this is the deliberately red baseline.

| Failing regression | Cases |
| --- | ---: |
| Preserve None despite a registered provider | 9 |
| Use None without any provider | 3 |
| Preserve the exact selected default instance despite a provider | 3 |
| Use the selected default instance without any provider | 3 |
| Classify ordinary None/instance defaults as PLAIN | 2 |

The registered-provider cases also require the unused provider to remain uncreated, so a fix
cannot construct it unnecessarily and only replace the final argument. The Phase-1 assertions
require the graph-building classification itself to change.

Passing controls cover:
- Plain numeric/falsy/string/tuple defaults and Optional[object] = None.
- Required class DI and nullable annotations without a Python default.
- Missing required providers still raising.
- Explicit SpellMap injection and SpellMap/SpellContract classifications.

Behavior tests cover automatic prebind, dynamic prebind and dynamic postbind. Registered None-default
cases include normal, named-only and named-plus-spellframe providers.

## Validation and reproduction

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
& '.venv_new/Scripts/python.exe' -m pytest tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py -p no:cacheprovider -o addopts= -q --tb=short
```

Expected current exit status: 1. Logs and JUnit: `red_regressions.log`, `red_regressions.xml`.
Scoped Ruff correctness checks pass. The original experimentation path now forwards to this same
regression suite; its collection was checked and returns the same 40 cases.

The earlier 27-case bug-characterization source is retained as
`default_characterization_before_regressions.py` alongside its original logs. It is outside normal
test discovery and is historical evidence, not a competing current contract.

## Next implementation boundary

Apply the agreed Phase-1 default precedence while preserving explicit DI descriptors and required DI.
Account for stale .melc payloads when changing compiler semantics. Turn all twenty red cases green
and keep the twenty controls green. No runtime patch was part of this red-test step.
