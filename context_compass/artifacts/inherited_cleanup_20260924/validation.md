# Inherited cleanup investigation

- Recorded: 2026-09-24T10:48:04Z
- Agent: workflows_0
- Ticket: tickets/tasks/completed/2026-09-24_investigate_inherited_cleanup_profiling_task.md
- Production source: unchanged by this investigation.

## Reproduction

The artifact test uses the real Spellbook, Bind, compiler, Conduit and cleanup path. It reuses the
existing configured_book test helper with disk caching disabled and isolated runtime singletons.

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src') + [IO.Path]::PathSeparator + (Get-Location).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
& '.venv_new/Scripts/python.exe' -m pytest `
  'context_compass/artifacts/inherited_cleanup_20260924/test_inherited_cleanup_reproduction.py' `
  -q --tb=short -p no:cacheprovider
```

Result: **5 failed, 5 passed in 0.54s** on Python 3.14.7. The failures assert the desired contract;
they are retained as investigation artifacts, outside normal tests/ collection.

| Case | Result |
| --- | --- |
| Direct cleanup, explicit and configured candidates | 2 passed |
| Inherited cleanup, explicit and configured candidates | 2 failed: stored [] |
| Direct cleanup, many and unique teardown | 2 passed |
| Inherited cleanup, many and unique teardown | 2 failed: no cleanup call |
| Cleanup inherited from second base | 1 failed: stored [] |
| Subclass non-callable shadow | 1 passed: excluded |

Receipts: reproduction.log and reproduction.xml in this directory.

## Existing tests

```powershell
& '.venv_new/Scripts/python.exe' -m pytest `
  'tests/component/melder/spellbook/test_ordered_disposal_binding.py' `
  'tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py' `
  'tests/integration/melder/conduit/test_ordered_disposal_runtime.py' `
  -q --tb=short -p no:cacheprovider
```

Result: **58 passed in 2.21s**. Receipts: existing_tests.log and existing_tests.xml.
Coverage was not measured.

## Exact application reproduction

command_0 supplied the original registration-only cases and independently reproduced both failures
with installed Melder 0.2.50. Its receipt lives under priv_commandops/context_compass/artifacts/
2026-09-24_reported_area_and_center_failures/native_disposal_handoff.md.

workflows_0 then ran the exact same two cases with priv_commandops/.venv314/Scripts/python.exe -B
and this checkout's src first on sys.path. The driver asserted melder.__file__ resolves to this
checkout's src/melder/__init__.py before calling pytest. It reported Melder 0.2.51, CPython 3.14.7
free-threaded. Both tests fail at test_area_bootstraps.py:206, naming the two reported classes.

Result: **2 failed in 0.24s**. Receipts: application_dev.log and application_dev.xml.

Node IDs relative to priv_commandops:

```text
tests/component/spectrum/test_area_bootstraps.py::test_area_build_conjures_named_definitions_without_domain_instances[registration-AgentPoolsBootstrap-agent_pools-expected_names4]
tests/component/spectrum/test_area_bootstraps.py::test_area_build_conjures_named_definitions_without_domain_instances[registration-AgentsBootstrap-agents-expected_names5]
```

pytest options: -q -o pythonpath= -o addopts= --rootdir=<priv_commandops>
--confcutdir=<priv_commandops>/tests/component -p no:cacheprovider --tb=short --show-capture=no
--timeout=40. JUnit and basetemp paths were directed into this Melder investigation directory.
sys.path also included priv_commandops/src for the application imports. No external files were edited.

Source reads verify both bootstrap register_spells methods supply ["cleanup"]. The implementations
are inherited from BasePerformancePolicy.cleanup and BaseThoughtStream.cleanup; neither subclass
declares cleanup or a class-level shadow.

## Diagnosis and implementation constraints

- BindingProfileStrategy._build_class_profile scans cls.__dict__ only (lines 111-117).
- Bind._bind_logic filters both groups against method_names (lines 685-703).
- Spell stores the resulting list and derives has_disposal_methods (lines 444-447).
- Creations._attempt_cleanup already uses instance lookup (lines 205-226).
- test_ordered_disposal_binding.py:209-217 expressly expects inherited methods to be excluded;
  that case must be separated from its factory/prebuilt-object companions in a future correction.
- Bind.sha256_profile also hashes method_names (lines 900-910). A broad profile expansion changes
  IDs for unrelated subclass registrations; targeted disposal discovery can preserve that boundary.
- Any inherited lookup must honor first-match MRO precedence, including non-callable shadows,
  while keeping book priority and deduplication unchanged. Avoid executing arbitrary descriptors
  during an indiscriminate scan.
