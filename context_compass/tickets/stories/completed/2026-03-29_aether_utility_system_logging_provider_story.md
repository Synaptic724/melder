# Story: Migrate Core Logging To AetherUtilitySystem

- Completed: 2026-04-02T20:39:03Z
- Summary: Finished the provider migration story across the core runtime and
  the new AR runtime root, then removed the dead factory layer so the logging
  foundation is ready for future event/codegen work.

## Metadata
- Story ID: STORY-2026-03-29-aether-utility-system-logging-provider
- Epic: EPIC-2026-03-29-iris-first-class-logging-integration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-29T23:26:03Z
- Updated: 2026-04-02T20:39:03Z

## User Narrative
As the project owner, I want Melder to acquire loggers through an
`AetherUtilitySystem` instead of through `Configuration.logger_factory`, so
that the runtime has one coherent system-wide logging path, first-class Iris
integration can be registered after the fact, and explicit per-object logger
overrides still remain possible.

## Value / MRP Alignment
The smallest coherent slice is:
- create `AetherUtilitySystem` as the hosted singleton utility/provider
- add a `resolve_channel_logger(...)` path like CommandOps
- remove config-owned logger-factory behavior
- migrate the core runtime path first:
  - `Aether`
  - `Spellbook`
  - `Conduit`
  - `ConduitWard` inherits the `Conduit` logger automatically

This lands the right infrastructure without forcing a full repo-wide logging
retrofit in one pass.

## Ticket Contract
- ENTRY_GATE: the Iris field model, existing Melder factories, and CommandOps
  utility acquisition model are all evidenced.
- EXECUTION_BOUNDARY: core runtime logging migration only; no full workspace
  event/codegen logging rollout in this story.
- DEPENDENCIES:
  - EPIC-2026-03-29-iris-first-class-logging-integration
  - src/melder/utilities/logger/iris_logger_factory.py
  - src/melder/utilities/logger/std_logger_factory.py
  - src/melder/utilities/helpers/init_helpers.py
  - src/melder/spellbook/configuration/configuration.py
  - src/melder/spellbook/spellbook.py
  - src/melder/aether/aether.py
  - src/melder/aether/conduit/conduit.py
- EXIT_GATE: core runtime logger acquisition no longer depends on
  `Configuration.logger_factory`, and `AetherUtilitySystem` owns the default
  provider path with no-op fallback when unconfigured.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing config-owned logger
  factories forces a broader configuration API rewrite than this slice should
  absorb.

## Requirements (Functional)
- Add `AetherUtilitySystem`.
- Ensure `Aether` creates/hosts it immediately at boot.
- Add `InitHelpers.resolve_channel_logger(...)`.
- Allow late registration of an Iris-backed resolver/factory into the utility
  system.
- Keep explicit logger override precedence.
- Remove config-owned logger factory methods/usage.
- Migrate `Spellbook`, `Conduit`, and `Aether` to the new acquisition path.

## Requirements (Non-Functional)
- No backward compatibility shims for the removed config logger-factory API.
- Keep plain logger fallback message-first only.
- Keep the implementation scoped to the core runtime path.

## Scope Boundaries
- In scope:
  - `AetherUtilitySystem`
  - `InitHelpers`
  - `Aether`
  - `Spellbook`
  - `Conduit`
  - configuration/logger-factory removal
  - affected interfaces/tests
- Out of scope:
  - full runtime event schema
  - full codegen logging rollout
  - workspace/workstation logging

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the dead factory cleanup slice is landed and validated, so
  the provider story is back in review awaiting acceptance or the next logging
  lane decision.

## Dependencies / Related Work
- codex/context_compass/tickets/epics/2026-03-29_iris_first_class_logging_integration_epic.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-03-29-migrate-core-logging-to-aether-utility-system - implement the core runtime migration
- [ ] Task: TASK-2026-03-30-migrate-nexus-rift-logging-to-aether-utility-system - extend the provider path into the new public AR runtime root
- [ ] Task: TASK-2026-03-30-remove-legacy-logger-factory-components - remove dead logger-factory components and add system-wide plain-logger registration
- [ ] Enforce Ticket Microcycle across the linked task.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `AetherUtilitySystem` exists and is hosted by `Aether`.
- `InitHelpers.resolve_channel_logger(...)` exists.
- `Configuration.logger_factory` support is removed.
- `Spellbook`, `Conduit`, and `Aether` use the new logger acquisition path.
- Plain logger fallback remains available as message-first behavior.

## Validation / Test Plan
- syntax compile of touched runtime and tests
- focused logging tests for core runtime surfaces if feasible

## Risks / Mitigations
- Risk: config logger-factory removal breaks too many tests at once.
  Mitigation: update the direct configuration/spellbook/conduit tests in the
  same pass.
- Risk: `AetherUtilitySystem` turns into a second god object immediately.
  Mitigation: keep this slice to logger-provider responsibilities only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Decision Log
- 2026-03-29: `AetherUtilitySystem` will host the logger provider, while
  `Configuration.logger_factory` is removed instead of preserved.
- 2026-03-29: explicit logger override remains valid, but the default path
  comes from the utility system.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-02T20:39:03Z
  TYPE: FACT
  CLAIM: One narrow cleanup mismatch remained in the live Conduit/ConduitWard
    logging path after the provider story was otherwise finished. `ConduitWard`
    correctly borrows the owning `Conduit` logger and uses masked log calls for
    its own presentation, but its teardown still probes `hasattr(self._logger,
    "_cleanup")` and calls `_cleanup()` even though the current logger wrapper
    surface is `SafeLogger.cleanup()`. This is a small cleanup-surface bug, not
    a reason to change the shared logger identity model.
  EVIDENCE:
  - src/melder\aether\conduit\conduit_ward\conduit_ward.py:83-89
  - src/melder\aether\conduit\conduit_ward\conduit_ward.py:162-165
  - src/melder\utilities\logger\safe_logger.py:49-56
  IMPACT: The runtime logger model stays correct, but ConduitWard cleanup should
    be patched so logger teardown actually follows the current SafeLogger
    contract.
  NEXT: replace the `_cleanup` probe with `cleanup()` and validate against the
    focused ConduitWard tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: The provider story no longer has any live logger-factory residue in
    runtime code. The story now leaves a simpler model behind: object-owned
    logger details on the channel path, explicit object overrides via
    `resolve_safe_logger(...)`, and one provider-level registered stdlib logger
    fallback for basic output. The deleted `IrisLoggerFactory` / `StdLoggerFactory`
    names now survive only in historical notes and planning history.
  EVIDENCE:
  - src/melder\aether\aether_utility_system.py:1-232
  - command:Get-ChildItem -Recurse -File @('src','tests') | Where-Object { $_.FullName -notmatch '__pycache__' } | Select-String -Pattern '\bIrisLoggerFactory\b|\bStdLoggerFactory\b'
  IMPACT: The provider story is actually complete at the runtime layer, so the
    next logging step should be a new problem, not more factory cleanup.
  NEXT: keep the story in review and pick the next lane: event/codegen schema or
    broader runtime adoption.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: The provider story is now cleanly review-ready. Across its three child
    tasks, the config-owned logger-factory API is removed, the provider rollout
    reaches `Aether`, `Spellbook`, `Conduit`, `Nexus`, and `Rift`, the dead
    `StdLoggerFactory` component is gone, `IrisLoggerFactory` is reduced to a
    thin adapter, and `AetherUtilitySystem` now supports one system-wide
    registered plain stdlib logger as the message-only fallback when no channel
    resolver is present.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-03-29_migrate_core_logging_to_aether_utility_system_task.md:1-255
  - codex/context_compass/tickets/tasks/2026-03-30_migrate_nexus_rift_logging_to_aether_utility_system_task.md:1-176
  - codex/context_compass/tickets/tasks/2026-03-30_remove_legacy_logger_factory_components_task.md:1-176
  IMPACT: The logging foundation is now coherent enough to stop doing provider
    plumbing and move to the next true logging problem instead of continuing
    cleanup churn.
  NEXT: keep the story in review and choose between event/codegen schema work
    or broader runtime logging adoption outside the current object set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T23:00:45Z
  TYPE: FACT
  CLAIM: The provider rollout is still missing one cleanup slice. The old
    config-owned logger-factory API is gone, but the story still leaves one dead
    component (`StdLoggerFactory`), one misplaced concern
    (`IrisLoggerFactory` still owns baked-in object defaults even though the
    objects now own those details), and one missing capability (a system-wide
    registered plain logger for message-only fallback without per-object
    constructor injection).
  EVIDENCE:
  - src/melder\aether\aether_utility_system.py:1-206
  - src/melder\utilities\logger\iris_logger_factory.py:1-191
  - src/melder\utilities\logger\std_logger_factory.py:1-334
  - tests\unit\melder\utilities\logger\test_iris_logger_factory.py:1-100
  - tests\unit\melder\utilities\logger\test_std_logger_factory.py:1-149
  IMPACT: The story should stay in progress for one more narrow cleanup task
    instead of pretending the provider lane is completely finished.
  NEXT: run the new legacy-factory cleanup task, then bring the story back to
    review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T22:46:31Z
  TYPE: FACT
  CLAIM: The story is now review-ready across both intended slices. The first
    child task removed the config-owned logger-factory path and moved the core
    runtime onto `AetherUtilitySystem`; the second child task extended that same
    provider model into `Nexus` and `Rift`, including focused tests for provider
    registration and explicit logger overrides. The story still intentionally
    stops before event/codegen schema work.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-03-29_migrate_core_logging_to_aether_utility_system_task.md:1-255
  - codex/context_compass/tickets/tasks/2026-03-30_migrate_nexus_rift_logging_to_aether_utility_system_task.md:1-176
  IMPACT: The next logging decision is now cleanly downstream of the provider
    rollout instead of mixed into it.
  NEXT: hold the story in review and choose between wider provider adoption or
    the event/codegen schema lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-30T22:46:31Z
  TYPE: FACT
  CLAIM: The story now needs a second child task. The first provider slice is
    complete enough for review at the `Aether` / `Spellbook` / `Conduit`
    boundary, but the newly established public AR runtime root (`Nexus` /
    `Rift`) still does not own or acquire loggers through the provider path.
    Finishing the story cleanly now requires a narrow follow-up task for those
    two objects instead of silently widening the completed first task.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-03-29_migrate_core_logging_to_aether_utility_system_task.md:137-150
  - src/melder/aether/nexus/nexus.py:1-119
  - src/melder/aether/nexus/rift/rift.py:1-133
  IMPACT: Story scope is still coherent, but it now spans two sequential tasks:
    the landed core slice and the new `Nexus` / `Rift` adoption slice.
  NEXT: implement the new child task and keep the story in progress until both
    provider-adoption slices are review-ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-29T23:26:03Z
  TYPE: PLAN
  CLAIM: This story exists to move Melder from the current fragmented
    config/ad hoc logger acquisition model to one coherent system-wide provider
    path hosted by `AetherUtilitySystem`, without trying to retrofit the whole
    repo at once.
  EVIDENCE:
  - src/melder/spellbook/configuration/configuration.py:184-224
  - src/melder/spellbook/spellbook.py:856-904
  - src/melder/aether/conduit/conduit.py:661-673
  - src/melder/utilities/logger/iris_logger_factory.py:1-148
  - <local-workspace>\src\command_ops\utilities\general_helpers\init_helpers.py:23-84
  IMPACT: The active task can stay tightly scoped to core runtime logger acquisition.
  NEXT: implement the task and update the focused runtime/tests in the same pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story covers the first implementation slice of the Iris logging epic:
replace config-owned logger acquisition with an `AetherUtilitySystem` provider
path for the core runtime.
