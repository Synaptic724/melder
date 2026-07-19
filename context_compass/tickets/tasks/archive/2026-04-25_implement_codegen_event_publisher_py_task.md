# Task: Implement codegen_event_publisher.py

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-event-publisher-py
- Story: STORY-2026-04-25-codegen-system-observability-directory
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-04-25T11:19:06Z
- Updated: 2026-04-25T11:19:06Z

## Objective
Implement the room-event publisher that emits descriptive codegen lifecycle
signals through the owning room's `RiftEventSystem`.

## Ticket Contract
- ENTRY_GATE: the observability story is active and the observability model was
  corrected to reuse the existing Rift event/memory systems instead of a
  private codegen history/logger cache.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/observability/codegen_event_publisher.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_observability_directory_story.md`
  - `src/melder/aether/nexus/rift/rift_space/event_system/rift_event_system.py`
- EXIT_GATE: one explicit publisher file exists for descriptive codegen
  lifecycle events and it does not retain its own history/cache state.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the existing room event
  system proves insufficient for codegen lifecycle publication.

## Scope Boundaries
- In scope:
  - descriptive room-event publication only
- Out of scope:
  - full-source history storage
  - workflow buffering/orchestration
  - generic hook-dispatch abstractions

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the event publisher is now implemented as part of the
  first observability slice.

## Steps / Checklist
- [x] Implement `CodegenEventPublisher`.
- [x] Keep it room-event-backed and publish-only.
- [x] Add focused unit coverage.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- room-event-backed codegen lifecycle publisher

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/observability/codegen_event_publisher.py
- src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py
- src/melder/aether/nexus/rift/codegen_system/codegen_system.py
- src/melder/aether/nexus/rift/command_system/codegen_command_system.py
- tests/unit/melder/aether/test_nexus.py

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/nexus/rift/codegen_system/codegen_system.py src/melder/aether/nexus/rift/codegen_system/observability/codegen_event_publisher.py src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py src/melder/aether/nexus/rift/command_system/codegen_command_system.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"`
- Result:
  - `30 passed, 105 deselected, 2 warnings`

## Risks / Rollback Notes
- Risk: event publication grows into a second retained history layer.
  Rollback: keep full code only on room-memory records and keep events
  descriptive.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
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
- DATETIME: 2026-04-25T11:19:06Z
  TYPE: DECISION
  CLAIM: The right codegen observability model is publish-only inside Melder.
    Full source belongs on room-memory artifacts, while room events remain
    lightweight and descriptive. No codegen-owned logger/history cache is
    needed.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/event_system/rift_event_system.py:1-221
  - src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py:1-322
  - src/melder/aether/nexus/rift/command_system/command_system.py:916-1087
  - user_instruction: "we don't need a tarnsaction logger or history recorder because we're publishing events right?"
  IMPACT: Codegen observability should plug into the existing room systems
    instead of inventing another retained subsystem.
  NEXT: keep `CodegenMonitor` as the thin lifecycle bridge over this publisher.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T11:19:06Z
  TYPE: FACT
  CLAIM: `codegen_event_publisher.py` is now implemented and emits descriptive
    validate/execute lifecycle events through the owning room's
    `RiftEventSystem` without carrying full source text or a retained local
    buffer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/observability/codegen_event_publisher.py:1-178
  - src/melder/aether/nexus/rift/codegen_system/observability/codegen_monitor.py:1-129
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-378
  - tests/unit/melder/aether/test_nexus.py:2129-2200
  IMPACT: Codegen now has explicit room-event lifecycle publication without a
    private cache/history subsystem.
  NEXT: close this task when the user accepts the observability slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the room-event-backed codegen lifecycle publisher.
