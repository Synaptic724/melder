# Task: Remove Legacy Rift Conduit Facade Methods
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-16-remove-legacy-rift-conduit-facade-methods
- Story: STORY-2026-04-16-migrate-rift-conduit-access-onto-room-command-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-16T23:43:31Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the duplicated conduit-access facade from `Rift` and update any
interface/doc contracts that still claim it exists.

## Ticket Contract
- ENTRY_GATE: the investigation task is accepted and the migration plan is
  explicit.
- EXECUTION_BOUNDARY: only the legacy `Rift` conduit facade family and the
  directly affected interface/doc surfaces.
- DEPENDENCIES:
  - tickets/tasks/2026-04-16_investigate_legacy_rift_conduit_facade_consumers_and_migration_task.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: the facade methods are removed, contracts/docs match, and the
  room-command migration task has no remaining blocked callers.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a compatibility shim is
  required instead of direct removal.

## Scope Boundaries
- In scope:
  - `Rift` direct conduit facade family
  - interface/doc updates required by their removal
- Out of scope:
  - test/helper rerouting itself
  - unrelated `Rift` API cleanup

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the legacy facade is removed, current repo consumers are
  rerouted, and the focused validation ring is green.

## Steps / Checklist
- [ ] Remove the legacy direct conduit facade family from `Rift`.
- [ ] Update interface contracts/docstrings that still expose the removed surface.
- [ ] Record implementation evidence in notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- cleaned `Rift` surface
- updated interface/doc contract

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- src/melder/utilities/interfaces/interfaces.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Removing a still-needed public contract could widen the migration unexpectedly.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-16T23:43:31Z
  TYPE: PLAN
  CLAIM: The runtime removal cut is now ready. The direct `Rift` conduit facade
    family is duplicated by the room-owned command surface, and the current
    repo consumers are already identified in the unit/runtime-contract tests
    plus the static/capability JSON testbench helpers.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:433-611
  - src/melder/aether/nexus/rift/command_system/command_system.py:306-430
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:424-432
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:350-350
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:494-494
  IMPACT: We can delete the facade and update the `IRift` contract in the same
    implementation tranche instead of carrying a compatibility shim.
  NEXT: remove the methods from `Rift` and `IRift`, then reroute the identified
    consumers to `space.command_system`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-16T23:58:32Z
  TYPE: FACT
  CLAIM: The runtime removal is now implemented without a compatibility shim.
    The commented legacy conduit facade block and the dead
    `_resolve_conduit_frame_name(...)` helper are removed from `Rift`, the
    `IRift` contract no longer advertises that surface, and the direct
    repo consumers were rerouted to `space.command_system` instead:
    the runtime-contract unit test now asserts the room-owned command path, and
    the static/capability JSON testbench helpers resolve `"cloud"` through the
    room command surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:433-611
  - src/melder/aether/nexus/rift/rift.py:1333-1359
  - src/melder/utilities/interfaces/interfaces.py:7697-7757
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:397-438
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:341-350
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:485-494
  IMPACT: `Rift` now stops duplicating the room-owned conduit surface and the
    current test/helper callers already speak the newer command-system path.
  NEXT: run the focused validation ring and record the result before deciding
    whether the companion test-migration task still needs separate execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-17T00:01:08Z
  TYPE: MEASURE
  CLAIM: The facade removal and caller reroute are green on a focused
    validation ring. This same pass covered the identified unit/runtime-
    contract test plus the capability/static JSON bench helpers and static JSON
    scenario data, so the migration is ready for review rather than another
    implementation pass.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> 234 passed
  IMPACT: The removal lane is validated and can return for acceptance.
  NEXT: move the companion test-migration task to review state with shared
    evidence and update the board to reflect review instead of active
    implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the actual `Rift` runtime/interface cleanup once the migration
plan is approved.