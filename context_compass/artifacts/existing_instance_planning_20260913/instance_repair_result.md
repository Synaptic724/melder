# Existing-instance planning repair

Implemented locally on Melder 0.2.40, Python 3.14.7 free-threaded. Annotation repair was accepted
and turned in separately as TASK-2026-09-13-repair-deferred-annotation-acquisition.

## Change

Both Phase-8/9 contract-default scanners now return no constructor contracts for an existing
creation. The consumer-to-provider edge remains in the graph, and runtime injection uses the
registered object. Ordinary class/factory contract discovery is preserved.

The analyzer's existing missing-contract error path also received its missing MeldExecutionError
import, with two negative controls. Five older integration tests that asserted the planning bug
now verify exact instance selection, frame/binding lookup and mixed collection lifetimes.

## Native verification

- Fresh baseline: 14 failures, seven passing controls in the existing-object regressions.
- Final selected suite: 140 passed in 1.41 seconds, including all 21 existing-object regressions,
  15 accepted annotation regressions, legacy resolution tests, overrides, contracts, compiler
  strategy/family controls and both missing-provider error controls.
- Source correctness lint and new-test F/I lint passed. Intentional undefined names in legacy
  annotation tests were preserved; those inputs are part of their error-path tests.
- Refreshed only the two touched scanner descriptors, then rebuilt and checked graph/index.
- All durable source asset checks pass. Source/test bundle fingerprint/output proofs pass.

Evidence:
- instance_repair_red.log/xml
- instance_repair_final.log/xml
- instance_source_assets_check.log
- instance_graph_check.log
- instance_src_bundle_check.log
- instance_test_bundle_check.log

## Original CommandOps / Iris result

Ran the original, unchanged dedicated-logger test using CommandOps .venv314, with process-local
PYTHONPATH pointing at this Melder source. A preflight assertion verified the exact import path.
PYTHONDONTWRITEBYTECODE was enabled and no installed package/environment was replaced.

The test gets through logger binding, ActivityBuilder creation, defaults and two distinct
GeneralActivity creations. It then fails at test_area_bootstraps.py:244: builder.cleaned is False
after root.cleanup(). Therefore the original end-to-end test is NOT passing yet.

The cleanup root cause has not been established; it remains a separate investigation. The terse
console output is explained by CommandOps tests/conftest.py calling os._exit at sessionfinish;
JUnit preserves the assertion and shows one failed case with no setup errors.

Evidence:
- iris_source_preflight.log
- iris_existing_logger_acceptance.log/xml

## Remaining boundaries

Provider matching, automatic type exposure, frame validation, callable-object classification,
disposal policy and the separate provider-artifact ownership bug were not changed. Existing
instances must still be registered with metadata matching the requested dependency.
No new wheel was built. The owning instance task stays open for review and downstream acceptance.
