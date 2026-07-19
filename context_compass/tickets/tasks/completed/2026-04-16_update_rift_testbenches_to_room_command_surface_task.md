# Task: Update Rift Testbenches To Room Command Surface
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-16-update-rift-testbenches-to-room-command-surface
- Story: STORY-2026-04-16-migrate-rift-conduit-access-onto-room-command-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-16T23:43:31Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Reroute tests and testbench helpers that still call the legacy `Rift` conduit
facade onto the proper room-owned command surface.

## Ticket Contract
- ENTRY_GATE: the investigation task is accepted and the runtime-removal task
  is approved.
- EXECUTION_BOUNDARY: tests, integration helpers, and support files directly
  relying on the old `Rift` facade.
- DEPENDENCIES:
  - tickets/tasks/2026-04-16_investigate_legacy_rift_conduit_facade_consumers_and_migration_task.md
  - tickets/tasks/2026-04-16_remove_legacy_rift_conduit_facade_methods_task.md
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
- EXIT_GATE: all identified consumers use `space.command_system` or another
  approved room-owned path and validation is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any consumer cannot move to a
  room-owned path cleanly.

## Scope Boundaries
- In scope:
  - direct test/helper callers of the removed `Rift` conduit facade
  - related validation commands
- Out of scope:
  - unrelated test cleanup
  - broader integration redesign

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the identified test/helper callers were migrated in the
  same implementation pass as the runtime removal and validated together.

## Steps / Checklist
- [ ] Update unit/runtime-contract tests to use the room command surface.
- [ ] Update static/capability JSON testbench helpers to use the room command surface.
- [ ] Run focused validation and record results.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated tests/helper utilities
- focused validation evidence

## Files / Paths Impacted
- tests/unit/melder/aether/test_rift_runtime_contracts.py
- tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
- tests/integration/melder/aether/rift/static_rift_json_testbench_support.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Integration helpers may encode assumptions about `Rift` convenience access
  that need a small helper abstraction over `space.command_system`.

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
- DATETIME: 2026-04-17T00:01:08Z
  TYPE: FACT
  CLAIM: The caller migration is complete in the same pass as the runtime
    removal. The runtime-contract unit test now asserts the room command
    surface, the static/capability JSON testbench helpers route `"cloud"`
    through `self.command`, and the static JSON scenario data now targets
    `"surface": "command"` for the removed conduit-discovery family.
  EVIDENCE:
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:397-438
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:341-350
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:485-494
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:241-289
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:542-639
  IMPACT: The companion task does not need a second edit pass; it is ready for
    review alongside the runtime-removal task.
  NEXT: rely on the shared focused validation evidence from the runtime-removal
    task and return this task for acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the caller migration and validation tranche for the legacy
`Rift` conduit facade removal.