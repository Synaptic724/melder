# Task: Investigate Legacy Rift Conduit Facade Consumers And Migration
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after downstream facade-removal implementation landed.

## Metadata
- Task ID: TASK-2026-04-16-investigate-legacy-rift-conduit-facade-consumers-and-migration
- Story: STORY-2026-04-16-migrate-rift-conduit-access-onto-room-command-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-16T23:43:31Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Identify the live repo consumers of the legacy `Rift` conduit facade and lock
the exact runtime/interface/test migration plan before implementation.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a staged epic/story/task plan
  before runtime/test edits.
- EXECUTION_BOUNDARY: investigation and plan only; no runtime/test edits.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
- EXIT_GATE: all current consumers are identified and the implementation plan
  is explicit enough to propose before edits.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real external/public
  compatibility requirement appears.

## Scope Boundaries
- In scope:
  - current `Rift` facade methods for conduit access
  - current repo consumers/tests/helpers
  - exact migration plan
- Out of scope:
  - removing the methods
  - editing tests/helpers
  - validation beyond evidence gathering

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: a user-approved staged investigation is required before
  implementation.

## Steps / Checklist
- [ ] Reconfirm the legacy facade methods and their duplication in `CommandSystem`.
- [ ] Inventory current repo consumers of the legacy facade.
- [ ] Decide what must move to `space.command_system` versus what should remain on `Rift`.
- [ ] Produce the implementation plan and impacted files list for approval.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidenced consumer inventory
- explicit implementation plan for runtime/interface/test migration

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-16_investigate_legacy_rift_conduit_facade_consumers_and_migration_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: we miss a deliberate contract dependency and plan a removal that is too
  aggressive.
  Rollback: keep this task investigation-only and raise `DECISION_REQUEST`
  before edits if a compatibility seam is still required.

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
  TYPE: FACT
  CLAIM: The legacy direct conduit facade on `Rift` is duplicated by the
    room-owned command surface, and current failures are already evidenced in
    unit/runtime-contract tests plus static/capability testbench helpers.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:433-611
  - src/melder/aether/nexus/rift/command_system/command_system.py:306-430
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:424-432
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:350-350
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:494-494
  IMPACT: We can plan the migration as a concrete runtime + testbench reroute
    instead of a blind API deletion.
  NEXT: inventory all current repo consumers and produce the exact implementation
    plan before editing runtime code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the investigation/planning tranche for removing the legacy
`Rift` conduit facade.
