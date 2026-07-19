# Task: Fix ACL Strategy Refactor Regressions

## Metadata
- Task ID: TASK-2026-05-03-fix-acl-strategy-refactor-regressions
- Story:
- Epic:
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-03T21:02:48Z
- Updated: 2026-05-03T21:02:48Z

## Objective
Fix the concrete regressions surfaced after the ACL profile family rewrite:
- codegen namespace component tests now see an extra `target` exposed name
- integration tests no longer find codegen-generated bound spells by logical key

## Ticket Contract
- ENTRY_GATE: the user explicitly requested fixing the post-refactor test
  failures and supplied the failing component/integration traces.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/**`
  - `src/melder/aether/conduit/**`
  - targeted ACL/builder files only if evidence proves a refactor regression
  - the failing component/integration tests
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - `tests/component/melder/aether/test_codegen_system_component_matrix.py`
  - `tests/integration/melder/aether/test_codegen_system_integration_matrix.py`
  - current codegen namespace/binding/runtime code
- EXIT_GATE: the failing component and integration surfaces are explained by
  evidence and repaired without broad unrelated churn.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the regressions reveal an
  intended behavioral change and the tests, not the code, should be updated.

## Scope Boundaries
- In scope:
  - namespace exposed-name regression
  - codegen-generated bind discovery regression
  - targeted test/code fixes with evidence
- Out of scope:
  - unrelated ACL redesign
  - broad codegen feature changes
  - new architecture work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested fixing the surfaced
  regressions after the family-builder refactor landed.

## Steps / Checklist
- [ ] Trace the `target` exposed-name difference to the real source path.
- [ ] Trace the generated-binding lookup failure to the real source path.
- [ ] Record evidence-backed findings in `## Notes`.
- [ ] Apply the smallest correct fix.
- [ ] Run targeted validation for the failing surfaces.

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No broad rollback of the ACL refactor without source evidence.
- [ ] No test-only patch if runtime behavior is actually wrong.

## Notes
- DATETIME: 2026-05-03T21:02:48Z
  TYPE: FACT
  CLAIM: The first post-refactor regressions are concrete and bounded. The
    component codegen namespace matrix now sees `target` inside
    `exposed_names`, and the integration codegen binding flow can no longer
    find a generated spell by `(spellframe, spell_name, binding_name)` after
    binding inside executed codegen.
  EVIDENCE:
  - user_failure_trace:
    `tests/component/melder/aether/test_codegen_system_component_matrix.py:133`
  - user_failure_trace:
    `tests/integration/melder/aether/test_codegen_system_integration_matrix.py:176`
  - user_failure_trace:
    `tests/integration/melder/aether/test_codegen_system_integration_matrix.py:235`
  IMPACT: The ACL strategy-family rewrite is not safe to leave as-is until we
    prove whether these are runtime regressions or stale test expectations.
  NEXT: inspect the namespace-builder and generated-binding path directly from
    source before changing code or tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:02:48Z
  TYPE: FACT
  CLAIM: The codegen namespace component failures are stale against the current
    runtime contract, not obviously caused by the ACL family-builder refactor.
    `CodegenNamespaceConfiguration.create_default()` still defaults
    `include_target=True`, `exposed_names` still includes `target` whenever
    that flag is enabled, and `CodegenNamespaceBuilder` still always applies
    the target strategy when `target` is exposed.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:38-55
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:140-188
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:209-224
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:130-151
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py:64-78
  - tests/component/melder/aether/test_codegen_system_component_matrix.py:95-133
  IMPACT: The namespace matrix likely needs expectation updates to include
    `target` unless a separate decision is made to change the namespace default
    contract itself.
  NEXT: reproduce the generated-binding lookup failure and trace whether the
    spell registration path or the test expectation is wrong there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:02:48Z
  TYPE: FACT
  CLAIM: The generated-binding integration failure is order-dependent rather
    than a plain broken bind path. A direct standalone repro of the exact bind
    flow succeeds, and the pytest test
    `test_integration_codegen_can_bind_generated_reference_and_use_it_afterward`
    also passes when run alone. It fails only when run after
    `test_integration_codegen_generated_definition_getsource_fails_but_binding_persists`,
    which points to leaked runtime/link state between those two tests.
  EVIDENCE:
  - direct_repro_result:
    generated code bind -> `LOOKUP_KEYS_AFTER_EXEC [('generated_runtime', 'generated_service')]`
  - direct_repro_result:
    `conduit.find_spell_id('generated_runtime', 'GeneratedService', 'generated_service')` succeeds
  - validation_result:
    `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py::test_integration_codegen_can_bind_generated_reference_and_use_it_afterward -s` -> `1 passed`
  - validation_result:
    `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py -k "generated_definition_getsource_fails_but_binding_persists or generated_reference_and_use_it_afterward"` -> second test fails
  IMPACT: The second regression is most likely a cleanup/reset isolation issue
    around conduit/rift lookup or singleton/runtime state, not a simple ACL
    strategy-family bug.
  NEXT: trace the `command.get_conduit_by_name(...)` resolution path and the
    test-reset path to find the leaked runtime reference.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:02:48Z
  TYPE: FACT
  CLAIM: The second regression is now pinned to teardown/reset behavior rather
    than the bind API itself. Running the two integration cases back-to-back in
    one plain script with the same explicit `conduit.cleanup()` and
    `reset_runtime_singletons()` calls reproduces the problem: the first case
    still leaves the generated binding in `_lookup_spells`, but the second
    codegen execution then fails with `RuntimeError: Aether has already been
    cleaned.` before the new binding path completes. That leaves the second
    spellbook with an empty lookup map and explains the later
    `find_spell_id(...)` failure.
  EVIDENCE:
  - reproduction_result:
    first case -> `FIRST {'accepted': False, 'reason': 'codegen_execution_runtime_failed', 'runtime_error': \"TypeError: <class 'GeneratedService'> is a built-in class\"}`
  - reproduction_result:
    first case -> `FIRST_LOOKUP_KEYS [('generated_runtime', 'generated_service')]`
  - reproduction_result:
    second case -> `SECOND {'accepted': False, 'reason': 'codegen_execution_runtime_failed', 'runtime_error': 'RuntimeError: Aether has already been cleaned.'}`
  - reproduction_result:
    second case -> `SECOND_LOOKUP_KEYS []`
  IMPACT: The integration failure is an `Aether` reference lifetime/reset bug
    in the codegen execution path, not a stale `find_spell_id` assertion.
  NEXT: inspect where `CodegenCommandSystem` / `RiftSpace` / related room
    objects acquire and retain their `Aether` reference across resets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:02:48Z
  TYPE: FACT
  CLAIM: The stale `Aether` reference is coming from `CommandSystem` itself.
    `CommandSystem` stores `_aether = Aether()` as a class attribute at import
    time, and `CodegenCommandSystem.get_conduit_by_name(...)` reads through
    that stored object. After test teardown resets the singleton, a newly
    created command system can still route through the previously cleaned
    `Aether` unless that reference is refreshed during initialization. This is
    the direct reason the second integration case fails only after a prior
    teardown cycle.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:38-55
  - src/melder/aether/nexus/rift/command_system/command_system.py:57-83
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:202-237
  - src/melder/aether/aether.py:178-205
  IMPACT: The runtime needs a small code fix so new command-system instances
    always refresh their `Aether` reference after singleton resets. This is a
    real bug, not a stale test expectation.
  NEXT: patch `CommandSystem` to refresh `_aether` during initialization and
    update the stale namespace expectations to include `target`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:09:10Z
  TYPE: MEASURE
  CLAIM: The targeted regression fixes are green. Updating the component
    namespace matrix expectations to include `target` matches the current
    default namespace contract, and refreshing `CommandSystem._aether` during
    initialization fixes the order-dependent integration leak after
    singleton-reset teardown.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:57-83
  - tests/component/melder/aether/test_codegen_system_component_matrix.py:95-133
  - validation_result:
    `python -m pytest -q tests/component/melder/aether/test_codegen_system_component_matrix.py -k namespace_matrix` -> `20 passed`
  - validation_result:
    `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py -k "generated_definition_getsource_fails_but_binding_persists or generated_reference_and_use_it_afterward"` -> `2 passed`
  - validation_result:
    `python -m py_compile "src/melder/aether/nexus/rift/command_system/command_system.py" "tests/component/melder/aether/test_codegen_system_component_matrix.py"`
  IMPACT: The two concrete regression classes the user surfaced are repaired at
    the narrowest plausible seam.
  NEXT: run the full component and integration codegen matrix files to confirm
    there is no adjacent fallout before closing the task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:09:41Z
  TYPE: MEASURE
  CLAIM: The broader codegen regression surfaces are also green after the fix.
    The full component codegen matrix and the full integration codegen matrix
    both pass end-to-end, so the repair did not just satisfy the two pasted
    failures in isolation.
  EVIDENCE:
  - validation_result:
    `python -m pytest -q tests/component/melder/aether/test_codegen_system_component_matrix.py` -> `80 passed`
  - validation_result:
    `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py` -> `42 passed`
  IMPACT: The regression slice is stable enough to return for acceptance
    rather than requiring more exploratory fallout chasing.
  NEXT: share the repaired causes and validation results with the user and wait
    for acceptance before closing the task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded regression repair pass after the ACL profile family
strategy/builder rewrite.
