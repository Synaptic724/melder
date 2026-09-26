# Inherited disposal correction: final validation

- Agent: workflows_0
- Recorded: 2026-09-24T11:15:11Z
- Task: TASK-2026-09-24-investigate-inherited-cleanup-profiling
- Source version: 0.2.51, local uncommitted correction; no new release or installed-package update.

## Implementation

Bind._matches_disposal_method retains the existing direct-profile eligibility, then checks only
requested non-dunder names against raw class namespaces in Python MRO order. The first declaration
is authoritative, including a non-callable shadow. Profile-excluded local members remain excluded;
the helper does not invoke member descriptors or admit metaclass-only members. Existing staticmethod
eligibility is retained; raw classmethod/property exclusions are unchanged.

Both configured and per-spell groups use the same helper. Their existing order, overlap ownership
and deduplication loops remain intact. ClassBindingProfile.method_names, the fingerprint schema,
compiler/runtime disposal execution and public signatures are unchanged. Affected disposal lists
correctly produce changed IDs when rebound; unrelated base methods do not perturb identity.

Implementation:
- src/melder/aether/spellbook/bind/bind.py:623-634,689-707,801-834
- tests/component/melder/spellbook/test_inherited_disposal_binding.py
- tests/component/melder/spellbook/test_ordered_disposal_binding.py:209-230

## Behavioral evidence

| Validation | Result | Receipt |
| --- | --- | --- |
| Permanent regressions before production fix | 17 failed, 11 passed | fixed_before.log / .xml |
| Native binding/profile/compiler/disposal selection | 393 passed; 23 replay setup errors | fixed_native.log / .xml |
| Replay-only retry with normal filesystem access | 23 passed in 177.96s | fixed_replay_approved.log / .xml |
| Original minimal reproduction plus final inheritance test module | 37 passed in 0.89s | fixed_reproduction.log / .xml |
| Both exact CommandOps registration cases | 2 passed in 0.12s | fixed_application.log / .xml |

The 393 and 23 results cover **416 unique native tests**. The 37-case run includes the same 27 new
native inheritance cases and the 10 original reproduction cases; it must not be added wholesale
to the 416 total. No repository-wide suite or coverage result is claimed.

Windows sandbox access to pytest temporary directories caused all replay setup errors, including
the isolated workspace attempt in fixed_replay.log. The approved retry passed without source changes.

Native selection, run with .venv_new/Scripts/python.exe -m pytest -q --tb=short -p no:cacheprovider:
- tests/component/melder/spellbook/test_inherited_disposal_binding.py
- tests/component/melder/spellbook/test_ordered_disposal_binding.py
- tests/unit/melder/spellbook/bind
- tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_binding_profile_strategy.py
- tests/unit/melder/spellbook/spell_crafter/spell_examiner/profiles/test_binding_profile.py
- tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py
- tests/integration/melder/conduit/test_ordered_disposal_runtime.py
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_references.py
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py

The replay retry uses the same pytest options plus an isolated --basetemp under this artifact directory.
The reproduction run explicitly adds src and the repository root to PYTHONPATH and sets
PYTHONDONTWRITEBYTECODE=1. JUnit receipts capture the full collected identities and outcomes.

## CommandOps acceptance

Used priv_commandops/.venv314/Scripts/python.exe -B with local melder_private/src ahead of the
application's src on sys.path. Asserted melder.__file__ before running pytest; output identifies
the development checkout and CPython 3.14.7 free-threaded. No CommandOps source/environment edits.

```text
tests/component/spectrum/test_area_bootstraps.py::test_area_build_conjures_named_definitions_without_domain_instances[registration-AgentPoolsBootstrap-agent_pools-expected_names4]
tests/component/spectrum/test_area_bootstraps.py::test_area_build_conjures_named_definitions_without_domain_instances[registration-AgentsBootstrap-agents-expected_names5]
```

Options: -q -o pythonpath= -o addopts= --rootdir=<priv_commandops>
--confcutdir=<priv_commandops>/tests/component -p no:cacheprovider --tb=short --show-capture=no
--timeout=40. The JUnit output was directed to fixed_application.xml here.

Installed CommandOps Melder 0.2.50 remains unchanged; these results qualify the corrected local source.
No duplicate GeneralPerformancePolicy or AsyncioThoughtStream cleanup implementation was added.

## Lint and documentation

- New test module: full Ruff passes.
- Bind: 33 existing Ruff findings before and after; ordered disposal tests: 5 before and after.
  No introduced findings by code/message multiset comparison (fixed_lint_comparison.json).
- Binding contract and measured Bind C1 ranges updated in the canonical source maps; both indexes
  validate. Existing broader document content was preserved, with only 11 accounted contract/range
  lines replaced across the two maps (fixed_document_preservation.json).
- Bind's descriptor semantics and source stamp updated; graph and index rebuilt and checked.
  Nine incidental extractor refreshes/reformats were restored only after exact pre-run hash proof,
  including original CRLF bytes where applicable. Only Bind's descriptor changed from the baseline.
- Qualified source/test hashes are in fixed_source_hashes.json. Packaged assets were not regenerated.

The scoped binding contract is verified from source and tests. This is not a new whole-system
documentation quality audit; existing unrelated stale references and style debt are outside the fix.

## Independent consumer acceptance

command_0 independently reran both exact registration-only cases against the corrected development
checkout: **2 passed in 0.13s**. Its driver verified the local Melder import path and version first.
Receipt in priv_commandops: context_compass/artifacts/2026-09-24_reported_area_and_center_failures/
inherited_disposal_native_fixed.txt and .xml. This repeats the two application checks above and does
not increase the unique test count. The peer retained the handoff and consumed its mailbox alert.
