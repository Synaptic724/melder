# Task: Remove Legacy Logger Factory Components

- Completed: 2026-04-02T20:39:03Z
- Summary: Removed the remaining dead logger-factory layer, added provider-level
  stdlib fallback registration, and aligned the focused logger tests/docs with
  the final provider model.

## Metadata
- Task ID: TASK-2026-03-30-remove-legacy-logger-factory-components
- Story: STORY-2026-03-29-aether-utility-system-logging-provider
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-30T23:00:45Z
- Updated: 2026-04-02T20:39:03Z

## Objective
Remove the last dead logger-factory components under the new provider model and
add one system-wide plain-logger registration path so users can register a
basic logger without passing it into every constructor.

## Ticket Contract
- ENTRY_GATE: the provider rollout is landed for the runtime objects and the
  remaining logger-factory behavior is now clearly evidenced as dead or
  misplaced.
- EXECUTION_BOUNDARY: `AetherUtilitySystem`, `IrisLoggerFactory`, dead
  `StdLoggerFactory` removal, focused logger tests, and directly affected docs
  only.
- DEPENDENCIES:
  - STORY-2026-03-29-aether-utility-system-logging-provider
  - TASK-2026-03-29-migrate-core-logging-to-aether-utility-system
  - TASK-2026-03-30-migrate-nexus-rift-logging-to-aether-utility-system
  - src/melder/aether/aether_utility_system.py
  - src/melder/utilities/logger/iris_logger_factory.py
  - src/melder/utilities/logger/std_logger_factory.py
- EXIT_GATE: `StdLoggerFactory` is gone, `IrisLoggerFactory` no longer owns
  baked-in object defaults, and `AetherUtilitySystem` can use either a channel
  resolver or a registered plain logger as the system-wide fallback.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the remaining
  factory layer would break a required public API or force a broader logging
  redesign than this cleanup slice.

## Scope Boundaries
- In scope:
  - add provider-level plain-logger registration
  - remove baked-in object defaults from `IrisLoggerFactory`
  - remove dead `StdLoggerFactory`
  - update focused logger tests
- Out of scope:
  - event/codegen schema work
  - wider runtime logging rollout
  - workspace/workstation logging

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the cleanup slice is landed and validated, so it is now
  waiting for review/acceptance.

## Steps / Checklist
- [ ] Document the remaining dead/misplaced factory behavior in `## Notes`.
- [ ] Add system-wide plain-logger registration to `AetherUtilitySystem`.
- [ ] Remove baked-in object defaults from `IrisLoggerFactory`.
- [ ] Remove dead `StdLoggerFactory` runtime/tests.
- [ ] Update focused logger tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- cleaned `AetherUtilitySystem` provider fallback model
- simplified `IrisLoggerFactory`
- removed `StdLoggerFactory`
- updated focused logger tests

## Files / Paths Impacted
- src/melder/aether/aether_utility_system.py
- src/melder/utilities/logger/iris_logger_factory.py
- src/melder/utilities/logger/std_logger_factory.py
- tests/unit/melder/aether/test_aether_utility_system.py
- tests/unit/melder/utilities/logger/test_iris_logger_factory.py
- tests/unit/melder/utilities/logger/test_std_logger_factory.py

## Validation
- Not run.
- Recommended commands:
  - python -m py_compile <touched runtime and test files>
  - python -m pytest -q tests\unit\melder\aether\test_aether_utility_system.py tests\unit\melder\utilities\logger\test_iris_logger_factory.py

## Risks / Rollback Notes
- Risk: deleting `StdLoggerFactory` removes a still-needed test or helper path.
  Rollback: only remove it if the live runtime truly has no remaining usage.
- Risk: general plain-logger registration weakens the explicit object-owned
  logger details.
  Rollback: keep object-owned `groups/system_groups/props/channels` on the
  channel path and let the plain-logger path stay message-only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: MEASURE
  CLAIM: The stale Spellbook test-double regression is repaired too. Extending
    `DummySafeLogger` and its inner `DummyLogger` with the missing
    `info` / `warning` / `critical` / `exception` methods brings the local
    test support back in line with the current runtime `SafeLogger` surface, and
    the full `tests/unit/melder/spellbook/test_spellbook.py` file now passes
    again.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook.py:490-676
  - command:python -m py_compile tests\unit\melder\spellbook\test_spellbook.py
  - command:python -m pytest -q tests\unit\melder\spellbook\test_spellbook.py
  IMPACT: The cleanup slice no longer leaves a stale logger test-double behind
    in the big Spellbook unit suite.
  NEXT: keep the task in review and move to the next actual logging problem
    instead of more logger-surface cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: One more test-surface drift appeared after removing the logger factory
    layer. The large Spellbook unit file carries its own `DummySafeLogger`
    test double, and that stub only implemented `debug(...)`, `error(...)`,
    and `cleanup()`. The current runtime now legitimately calls
    `self._logger.info(...)` from `Nexus.cleanup()` and other lifecycle
    methods, so the teardown fixture in `tests/unit/melder/spellbook/test_spellbook.py`
    now explodes even though the runtime contract is valid.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook.py:559-621
  - src/melder/aether/nexus/nexus.py:271-271
  - command:python -m pytest -q tests\unit\melder\spellbook\test_spellbook.py
  IMPACT: The remaining work is to update the stale logger test double to the
    current `SafeLogger` surface, not to weaken the runtime back down.
  NEXT: extend the Spellbook test doubles with the missing logger methods and
    rerun the full Spellbook unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: MEASURE
  CLAIM: After removing the adapter file itself, the final live runtime/test
    sweep is clean. `AetherUtilitySystem` still compiles and its focused tests
    still pass, and there are now zero remaining `IrisLoggerFactory` or
    `StdLoggerFactory` references anywhere in the live `src` / `tests` tree.
  EVIDENCE:
  - command:python -m py_compile src\melder\aether\aether_utility_system.py tests\unit\melder\aether\test_aether_utility_system.py
  - command:python -m pytest -q tests\unit\melder\aether\test_aether_utility_system.py
  - command:Get-ChildItem -Recurse -File @('src','tests') | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern '\bIrisLoggerFactory\b|\bStdLoggerFactory\b'
  IMPACT: The old factory layer is fully gone from live code, not just sidelined.
  NEXT: keep the task in review and move on to the next actual logging problem
    instead of more cleanup churn.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: One active documentation seam also drifted with the adapter removal.
    The synaptic overlay logging guidance in the user-defined onboarding docs
    still tells the old story that project channel logging flows through
    `IrisLoggerFactory`, but that adapter file is now gone. The active guidance
    needs to point at the real provider pattern instead:
    `InitHelpers.resolve_channel_logger(...)` for the system channel path,
    `InitHelpers.resolve_safe_logger(...)` for explicit logger objects, and the
    new provider-level default stdlib logger fallback for basic output.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:301-302
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/logging.md:13-20
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/synaptic_python_developer.md:301-302
  IMPACT: Leaving those docs untouched would preserve a stale logging rule in
    active onboarding policy even though the runtime no longer supports that
    adapter.
  NEXT: patch the active synaptic logging guidance to the provider-based model
    before closing this cleanup slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: MEASURE
  CLAIM: The cleanup slice is syntax-clean and the focused validation passes.
    The updated provider/runtime files compile, the focused
    `AetherUtilitySystem` and `IrisLoggerFactory` pytest slice passes, and a
    final source-tree sweep shows no remaining `StdLoggerFactory` references or
    the old baked-in default maps in the live `src` / `tests` tree.
  EVIDENCE:
  - command:python -m py_compile src\melder\aether\aether_utility_system.py src\melder\utilities\logger\iris_logger_factory.py tests\unit\melder\aether\test_aether_utility_system.py tests\unit\melder\utilities\logger\test_iris_logger_factory.py
  - command:python -m pytest -q tests\unit\melder\aether\test_aether_utility_system.py tests\unit\melder\utilities\logger\test_iris_logger_factory.py
  - command:Get-ChildItem -Recurse -File @('src','tests') | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern '\bStdLoggerFactory\b|_CONDUIT_DEFAULTS|_SPELLBOOK_DEFAULTS|_AETHER_DEFAULTS|_GENERIC_DEFAULTS'
  IMPACT: The runtime logging foundation is now cleaner: dead factory code is
    gone, provider fallback is explicit, and object-owned logger details are no
    longer duplicated inside a factory layer.
  NEXT: hold the task in review and decide whether the next logging work is
    event/codegen schema design or broader runtime adoption outside the current
    object set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: The runtime cleanup half of the task is now landed. `AetherUtilitySystem`
    now supports one system-wide registered stdlib logger fallback via
    `register_default_logger(...)`, and `resolve_channel_logger(...)` now falls
    back to that logger when no channel resolver exists or the channel resolver
    fails. `IrisLoggerFactory` is now a pure adapter that forwards the
    caller-supplied metadata directly instead of owning baked-in object
    defaults. The dead `StdLoggerFactory` component and its standalone test file
    are removed.
  EVIDENCE:
  - src/melder\aether\aether_utility_system.py:1-234
  - src/melder\utilities\logger\iris_logger_factory.py:1-138
  - src/melder\utilities\logger\std_logger_factory.py:deleted
  - tests\unit\melder\aether\test_aether_utility_system.py:1-144
  - tests\unit\melder\utilities\logger\test_iris_logger_factory.py:1-93
  - tests\unit\melder\utilities\logger\test_std_logger_factory.py:deleted
  IMPACT: The provider model now cleanly supports both paths we actually want:
    first-class channel logging and one globally registered basic stdlib logger,
    without the old factory layer deciding object defaults for us.
  NEXT: run focused compile and pytest validation, then sweep for stale
    `StdLoggerFactory` / default-filling assumptions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: The remaining factory-layer cleanup is now well-bounded. The old
    config-owned logger-factory API is already gone from the live runtime, but
    one dead component and one misplaced concern remain. `StdLoggerFactory` has
    no remaining runtime call sites and only survives in its own standalone
    test file. `IrisLoggerFactory` still owns baked-in object defaults even
    though current runtime objects now hardcode those details themselves.
    `AetherUtilitySystem` also still lacks a system-wide default plain-logger
    registration path, so users cannot yet register one basic stdlib logger and
    have the provider use it as the fallback.
  EVIDENCE:
  - src/melder\aether\aether_utility_system.py:1-206
  - src/melder\utilities\logger\iris_logger_factory.py:1-191
  - src/melder\utilities\logger\std_logger_factory.py:1-334
  - tests\unit\melder\utilities\logger\test_iris_logger_factory.py:1-100
  - tests\unit\melder\utilities\logger\test_std_logger_factory.py:1-149
  - command:Get-ChildItem -Recurse -File @('src','tests','codex\context_compass') | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern '\bIrisLoggerFactory\b|\bStdLoggerFactory\b'
  IMPACT: We can now remove the remaining factory debris without touching the
    object-owned logging details that were the real migration goal.
  NEXT: add the provider-level default plain-logger registration path, then
    simplify/remove the old factory components and update focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task removes the last dead logger-factory layer under the new provider
model. The next step is to add system-wide plain-logger registration to
`AetherUtilitySystem`, then remove dead `StdLoggerFactory` and strip baked-in
defaults out of `IrisLoggerFactory`.
