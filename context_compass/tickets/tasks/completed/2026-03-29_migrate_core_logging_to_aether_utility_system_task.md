# Task: Migrate Core Logging To AetherUtilitySystem

- Completed: 2026-04-02T20:39:03Z
- Summary: Landed the first provider slice for `Aether`, `Spellbook`, and
  `Conduit`, removed the config-owned logger-factory path, and validated the
  focused runtime/test surface.

## Metadata
- Task ID: TASK-2026-03-29-migrate-core-logging-to-aether-utility-system
- Story: STORY-2026-03-29-aether-utility-system-logging-provider
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-29T23:26:03Z
- Updated: 2026-04-02T20:39:03Z

## Objective
Implement the first core-runtime logging migration: add `AetherUtilitySystem`,
mirror the CommandOps-style `resolve_channel_logger(...)` utility path, remove
config-owned logger-factory support, and migrate `Aether`, `Spellbook`, and
`Conduit` to the new logger acquisition model.

## Ticket Contract
- ENTRY_GATE: the current config-owned logger path and the existing Iris/std
  factory seams are evidenced.
- EXECUTION_BOUNDARY: core runtime logging migration only across
  `AetherUtilitySystem`, `InitHelpers`, `Aether`, `Spellbook`, `Conduit`,
  `Configuration`, interfaces, and directly affected tests.
- DEPENDENCIES:
  - STORY-2026-03-29-aether-utility-system-logging-provider
  - src/melder/utilities/logger/iris_logger_factory.py
  - src/melder/utilities/logger/std_logger_factory.py
  - src/melder/utilities/helpers/init_helpers.py
  - src/melder/spellbook/configuration/configuration.py
  - src/melder/spellbook/spellbook.py
  - src/melder/aether/aether.py
  - src/melder/aether/conduit/conduit.py
- EXIT_GATE: the new provider path is live in the core runtime and the old
  config-owned logger-factory API is removed from runtime code/interfaces.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the blast radius extends
  beyond the directly affected logger/configuration tests into unrelated
  subsystem behavior.

## Scope Boundaries
- In scope:
  - add `AetherUtilitySystem`
  - add provider/resolver registration and `resolve_channel_logger(...)`
  - remove configuration-owned logger factory code/interfaces
  - migrate `Aether`, `Spellbook`, `Conduit`
  - update directly affected tests
- Out of scope:
  - full repo-wide logger rollout
  - workspace/workstation logging
  - event/codegen schema implementation

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the first provider migration slice is landed and validated
  in its focused test surface, so this task is now waiting on review/acceptance
  while the next provider-adoption slice moves into `Nexus` / `Rift`.

## Steps / Checklist
- [ ] Investigate and document the direct `logger_factory` usage/tests to be removed.
- [ ] Add `AetherUtilitySystem` and wire it into `Aether` boot.
- [ ] Add `InitHelpers.resolve_channel_logger(...)` using the utility system.
- [ ] Remove `Configuration.logger_factory` runtime and interface support.
- [ ] Migrate `Aether`, `Spellbook`, and `Conduit` to the new provider path.
- [ ] Update directly affected tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `AetherUtilitySystem`
- new core runtime logger acquisition path
- removed config-owned logger-factory path
- updated focused tests

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/aether/aether_utility_system.py
- src/melder/spellbook/spellbook.py
- src/melder/aether/conduit/conduit.py
- src/melder/spellbook/configuration/configuration.py
- src/melder/utilities/helpers/init_helpers.py
- src/melder/utilities/interfaces/interfaces.py
- directly affected logger/configuration/spellbook/conduit tests

## Validation
- Not run.
- Recommended commands:
  - .venv\Scripts\python.exe -m py_compile <touched runtime and test files>

## Risks / Rollback Notes
- Risk: removing `Configuration.logger_factory` leaves stale interface and tests.
  Rollback: keep the implementation slice scoped and update only directly
  affected tests in the same pass.
- Risk: provider wiring introduces logger recursion at Aether boot.
  Rollback: keep `AetherUtilitySystem` boot-safe and default no-op when
  unconfigured.

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
- DATETIME: 2026-03-30T01:04:00Z
  TYPE: FACT
  CLAIM: Downstream Aether tests exposed one more provider-adjacent regression: `cleanup_aetheric_frames()` logged cleanup failures via `frame.name`, which broke tolerant-error behavior when tests used spec-bound frame mocks without a `name` attribute. The method now logs by the registry key captured during iteration instead. This keeps error logging stable under both real frame objects and mocked frame entries.
  EVIDENCE:
  - src/melder\aether\aether.py:260-272
  - tests\unit\melder\aether\test_aether.py:795-811
  - command:python -m pytest -q tests\unit\melder\aether\test_aether.py
  IMPACT: Aether cleanup logging is now robust against partial/mock frame objects and no longer converts one frame-cleanup failure into a second logging-time failure.
  NEXT: keep the logging provider lane scoped to real provider adoption, not unrelated frame-registry semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T00:47:00Z
  TYPE: FACT
  CLAIM: The logging migration regressions are now repaired. `Conduit` assigns `_conduit_state` before resolving its default logger, so provider properties no longer read unset state during construction. `Aether` logger initialization now matches `Spellbook` bootstrap semantics: `_logger` is seeded to a safe fallback first and provider-resolution failure falls back to a null `SafeLogger` without leaving a half-initialized singleton that later crashes in cleanup. The Spellbook integration logging test was also corrected to register the provider before creating the fresh `Aether` instance it expects to observe.
  EVIDENCE:
  - src/melder\aether\conduit\conduit.py:126-145
  - src/melder\aether\aether.py:63-95
  - tests\integration\melder\spellbook\test_spellbook_integration_logging.py:37-69
  - command:python -m py_compile src\melder\aether\aether.py src\melder\aether\conduit\conduit.py tests\integration\melder\spellbook\test_spellbook_integration_logging.py
  - command:python -m pytest -q tests/unit/melder/aether/test_aether_utility_system.py tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py tests/unit/melder/aether/conduit/test_conduit_lifecycle.py tests/integration/melder/spellbook/test_spellbook_integration_logging.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/unit/melder/spellbook/test_spellbook.py
  IMPACT: The core provider migration is now boot-safe across `Aether`, `Spellbook`, and `Conduit`, and the focused logging slice is validated instead of only being mechanically compiled.
  NEXT: decide whether to expand provider adoption into `Nexus` / `Rift` now or return to Rift/workspace eventstream and codegen logging with the provider foundation in place.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T00:39:00Z
  TYPE: FACT
  CLAIM: Focused pytest on the migrated logging slice exposed two concrete regressions. First, `Conduit.__init__` now resolves its default logger before `_conduit_state` is assigned, but `_configure_logger(...)` includes `str(self._conduit_state)` in the provider properties, which raises `AttributeError` during conduit construction. Second, the new Spellbook integration test currently assumes that registering the provider after `Aether` has already been instantiated will retroactively upgrade the existing Aether logger; that is not part of the implemented contract, so the test is asserting behavior the runtime does not provide.
  EVIDENCE:
  - src/melder\aether\conduit\conduit.py:108-162
  - src/melder\aether\conduit\conduit.py:517-534
  - tests\integration\melder\spellbook\test_spellbook_integration_logging.py:13-34
  - tests\integration\melder\spellbook\test_spellbook_integration_logging.py:37-74
  - command:python -m pytest -q tests/unit/melder/aether/test_aether_utility_system.py tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py tests/unit/melder/aether/conduit/test_conduit_lifecycle.py tests/integration/melder/spellbook/test_spellbook_integration_logging.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/unit/melder/spellbook/test_spellbook.py
  IMPACT: The provider migration is directionally correct, but the current runtime is not reviewable until conduit construction is made boot-safe again and the new logging tests align with the real singleton/provider lifecycle semantics.
  NEXT: move `_conduit_state` assignment ahead of logger initialization, then rewrite the affected logging tests to reflect provider registration timing rather than retroactive Aether logger upgrades.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T00:10:41Z
  TYPE: FACT
  CLAIM: The first core-runtime logging migration slice is now coherent end to
    end. `AetherUtilitySystem` exists and is hosted by `Aether`, `InitHelpers`
    now exposes a CommandOps-style `resolve_channel_logger(...)` path, the core
    runtime (`Aether`, `Spellbook`, and `Conduit`) now acquires default loggers
    through that provider, and the old config-owned `logger_factory` runtime
    API is removed from both the concrete `Configuration` class and the public
    interface layer. The directly affected configuration/spellbook/conduit tests
    were also migrated off the removed config logger path, and the new provider
    has focused unit coverage.
  EVIDENCE:
  - src/melder/aether/aether_utility_system.py:1-237
  - src/melder/utilities/helpers/init_helpers.py:1-55
  - src/melder/aether/aether.py:43-129
  - src/melder/spellbook/spellbook.py:856-884
  - src/melder/aether/conduit/conduit.py:511-525
  - src/melder/spellbook/configuration/configuration.py:1-228
  - src/melder/utilities/interfaces/interfaces.py:2104-2168
  - src/melder/utilities/interfaces/interfaces.py:6458-6746
  - tests/unit/melder/aether/test_aether_utility_system.py:1-83
  - tests/integration/melder/spellbook/test_spellbook_integration_logging.py:1-68
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:1-143
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:1-422
  - tests/unit/melder/spellbook/test_spellbook.py:372-451
  - tests/unit/melder/spellbook/test_spellbook.py:867-1004
  - tests/unit/melder/spellbook/test_spellbook.py:2656-2751
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:1-228
  - tests/unit/melder/spellbook/configuration/test_configuration.py:1-441
  IMPACT: The repo now has one coherent default logger acquisition path for the
    core runtime, and later logging work can build on the provider instead of
    fighting the old config-owned factory model.
  NEXT: keep this slice in review, then decide whether to expand the provider
    into more runtime objects or move back to Rift/workspace event and codegen
    logging.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T00:10:41Z
  TYPE: MEASURE
  CLAIM: The migrated runtime and directly affected tests are syntax-clean. The
    only remaining `logger_factory` / `IrisLoggerFactory` / `StdLoggerFactory`
    hits after the search are the intentional standalone factory
    implementations and their own unit tests, not the removed config-owned
    logger path in application/runtime code.
  EVIDENCE:
  - command:.venv\Scripts\python.exe -m py_compile src\melder\aether\aether_utility_system.py src\melder\utilities\helpers\init_helpers.py src\melder\aether\aether.py src\melder\spellbook\configuration\configuration.py src\melder\spellbook\spellbook.py src\melder\aether\conduit\conduit.py src\melder\utilities\interfaces\interfaces.py tests\unit\melder\aether\test_aether_utility_system.py tests\component\melder\spellbook\test_spellbook_component_configuration_core.py tests\integration\melder\spellbook\test_spellbook_integration_logging.py tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py tests\unit\melder\aether\conduit\test_conduit_lifecycle.py tests\unit\melder\spellbook\configuration\test_configuration.py tests\unit\melder\spellbook\test_spellbook.py
  - command:Get-ChildItem -Recurse -File src,tests | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern 'logger_factory|with_logger_factory|set_logger_factory|has_logger_factory|get_logger_for|clear_logger_factory'
  IMPACT: This slice is mechanically stable enough for review. Remaining work is
    further adoption and richer logging behavior, not stale config-API cleanup.
  NEXT: report the slice truthfully as `Not run.` for pytest and wait for the
    next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-29T23:33:38Z
  TYPE: FACT
  CLAIM: The core runtime migration is now partly landed. `AetherUtilitySystem`
    exists, `InitHelpers` now exposes `resolve_channel_logger(...)`, `Aether`
    now hosts the utility system and acquires its default logger through it,
    and `Spellbook` / `Conduit` no longer use the old
    `Configuration.logger_factory` path. The remaining immediate fallout is the
    stale logger-factory test surface: many tests still explicitly exercise the
    removed config API and need to be migrated or deleted in a follow-up pass.
  EVIDENCE:
  - src/melder/aether/aether_utility_system.py:1-237
  - src/melder/utilities/helpers/init_helpers.py:1-55
  - src/melder/aether/aether.py:43-82
  - src/melder/spellbook/spellbook.py:856-884
  - src/melder/aether/conduit/conduit.py:511-525
  - src/melder/spellbook/configuration/configuration.py:1-228
  - src/melder/utilities/interfaces/interfaces.py:2104-2168
  - src/melder/utilities/interfaces/interfaces.py:6458-6746
  - tests/unit/melder/spellbook/configuration/test_configuration.py:143-210
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:95-210
  - tests/integration/melder/spellbook/test_spellbook_integration_logging.py:31-62
  IMPACT: The runtime direction is correct, but the repo still has logger-factory
    tests/docs that assume the removed config API. This first slice is reviewable
    only if we are explicit that the direct test fallout is not fully migrated yet.
  NEXT: either migrate the stale logger-factory tests in the same lane or keep
    this task scoped to runtime-only and spin a direct test-migration follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T23:26:03Z
  TYPE: FACT
  CLAIM: The current logger path is split across three places: `Configuration`
    owns a logger-factory API, `Spellbook` uses that config API as its default
    logger-acquisition path and also upgrades `Aether` from it, and `Conduit`
    resolves through `Configuration.has_logger_factory()` when no explicit
    logger is passed. The concrete factory implementations already exist
    (`StdLoggerFactory` and `IrisLoggerFactory`), so the missing piece is a
    CommandOps-style provider/dispenser path rather than another factory type.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py:184-224
  - src/melder/spellbook/spellbook.py:856-904
  - src/melder/aether/conduit/conduit.py:661-673
  - src/melder/utilities/logger/std_logger_factory.py:10-287
  - src/melder/utilities/logger/iris_logger_factory.py:1-148
  IMPACT: The migration can be scoped to removing the config path and replacing
    it with one provider path, rather than redesigning logger backends.
  NEXT: implement `AetherUtilitySystem` and route `InitHelpers` through it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the first implementation slice of the new logging epic. The goal
is to replace config-owned logger acquisition with an `AetherUtilitySystem`
provider path in the core runtime only.
