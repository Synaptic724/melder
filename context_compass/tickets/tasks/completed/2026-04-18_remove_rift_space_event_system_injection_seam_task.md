# Task: Remove RiftSpace Event System Injection Seam
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-remove-rift-space-event-system-injection-seam
- Story: STORY-2026-04-18-rift-event-system-ownership-cleanup
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-18T19:23:23Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the optional `event_system` constructor seam from `RiftSpace` and its
room subclasses so room-local event ownership is internal and truthful.

## Ticket Contract
- ENTRY_GATE: user approved the bounded cleanup after investigation.
- EXECUTION_BOUNDARY: `RiftSpace`, `StaticRiftSpace`, `CapabilityRiftSpace`,
  `CodegenRiftSpace`, directly affected interfaces, and focused tests.
- DEPENDENCIES:
  - tickets/stories/2026-04-18_rift_event_system_ownership_cleanup_story.md
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
  - tests/unit/melder/aether/test_rift_space.py
- EXIT_GATE: no constructor accepts `event_system`, focused validation is
  green, and board/task state is synced.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a real runtime dependency on
  injected event systems is discovered.

## Scope Boundaries
- In scope:
  - remove `event_system` constructor args and forwarding
  - keep `space.event_system` property
  - port focused tests
- Out of scope:
  - event payload redesign
  - event callback semantics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the investigation proved the seam is dead and the user
  approved removing it.

## Steps / Checklist
- [x] Remove `event_system` constructor injection from `RiftSpace`.
- [x] Remove `event_system` pass-through from concrete room subclasses.
- [x] Port focused tests to internal event-system ownership.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- room-local event-system ownership with no constructor injection seam
- updated focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
- src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py
- tests/unit/melder/aether/test_rift_space.py

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_rift_space.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_nexus.py`
- Result: `117 passed`

## Risks / Rollback Notes
- Risk: a focused test may still assume custom injection.
- Rollback: none planned; this lane is explicitly no-backward-compat.

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
- DATETIME: 2026-04-18T19:25:29Z
  TYPE: FACT
  CLAIM: `RiftSpace` now always constructs and owns its `RiftEventSystem`, and
    the concrete room subclasses no longer accept or forward an `event_system`
    constructor argument.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:103-178
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:35-77
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:35-85
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:29-71
  IMPACT: Room event ownership is now truthful and the dead DI seam is gone.
  NEXT: hold the task for review/acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T19:25:29Z
  TYPE: MEASURE
  CLAIM: The focused room/event validation ring is green after removing the
    constructor seam.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_rift_space.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_nexus.py` -> 117 passed
  IMPACT: The cleanup is stable enough to review without reopening broader event work.
  NEXT: wait for user acceptance or follow-on direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T19:23:23Z
  TYPE: FACT
  CLAIM: No meaningful runtime path injects a custom `event_system`; the seam
    exists only as constructor pass-through and one unit-test setup hook.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:112-178
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:35-83
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:35-91
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:29-77
  - tests/unit/melder/aether/test_rift_space.py:30-46
  IMPACT: We can remove the seam cleanly without widening into broader runtime redesign.
  NEXT: patch the constructors and rewrite the focused test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task removes the dead `event_system` constructor seam from room creation
while preserving the live `space.event_system` surface.