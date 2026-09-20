# Existing-instance Protocol admission repair

Task: TASK-2026-09-19-repair-existing-instance-protocol-admission
Runtime: local Melder 0.2.40 source, Python 3.14.7 free-threading.

## Delivered behavior
Bind now validates the actual supplied value for InstanceBindingProfile/OtherBindingProfile when its
spellframe is a Protocol, using the same direct-public-member helper as class bindings. Missing or
non-callable required members raise TypeError before Spell publication. Instance-only members work;
shadowing a class method with None fails. Class error prefix and prior lifecycle/guard ordering remain.

No compiler, lifetime, fingerprint, disposal, cache or ownership policy changed. Compatible instances
remain the exact references injected into consumers. This does not add continuous post-bind checking
or expand Protocol inheritance, annotation-only data or signature compatibility coverage.

## Native test evidence
- red.log/xml: 10 failed, 247 passed before production changes. Failures match the admission defect.
- green.log/xml: 267 passed after the patch, including the retained existing-instance planner tests.
- binding_controls.log/xml: 67 passed for fluent binding, component Bind and internal-registration controls.
- Total successful focused checks: 334; no diagnostic admission plugin enabled.
- Full repository suite and coverage: Not run.

Commands, from the repository root:

```powershell
.venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/bind/test_bind.py tests/component/melder/spellbook/test_existing_instance_protocol_admission.py tests/integration/melder/spellbook/test_existing_instance_protocol_injection.py tests/integration/melder/spellbook/test_existing_instance_planning.py -q -p no:cacheprovider --tb=short
.venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/test_spellbinder.py tests/component/melder/spellbook/test_spellbook_component_bind.py tests/unit/melder/test_melder_registration_guard.py -q -p no:cacheprovider --tb=short
```

## Generated assets and documentation
- Architecture/components and the Bind graph descriptor reflect the boundary and checker limits.
- Bind source extent measured at 932 lines; affected C1 ranges and guard call citations updated.
- The canonical extractor/merge refreshed only Bind; its class semantics were verified and accepted.
- Architecture/components indexes and the assembled graph/index verify successfully.
- All three source build assets regenerated and --check passed; source_assets_build.log/check.log.
- All three repository corpora regenerated and --include-untracked --check passed; bundles_build.log/check.log.
  The explicit include-untracked mode includes the new permanent integration test without changing Git staging.
- Patch contracts have generated indexes and remain active until owner acceptance/closure.
- New component/integration tests pass Ruff F checks; source passes E9/F63/F7/F82 correctness checks.
- git diff --check passes.

## Content preservation and pre-existing limitations
doc_line_baseline.json was captured before authored system-document changes. Removed-line accounting
in doc_removed_lines.json contains only updated dates, measured Bind LOC/citations and the accompanying
historical guard-line clarification. All other prior nonblank normalized lines remain present.

The source's unused ClassVar import predates this repair; a full Ruff F run reports that existing F401.
It is left unchanged. Full graph preflight also exposes unrelated stale/unverified nodes; those are
not accepted or refreshed by this task. Existing system-document tooling-path leaks prevent claiming
a new whole-document quality pass or score. The targeted additions introduce no such paths.

## Review boundary
The implementation is ready for review. The existing-object lifecycle epic retains its broader open
design work. No version bump, replacement wheel, package publication or provider-artifact repair is included.
