# Story: Implement Codegen System Namespace Strategies Directory
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after the namespace strategy surfaces landed and the old
  builtins-only remainder was no longer a real open lane.

## Metadata
- Story ID: STORY-2026-04-25-codegen-system-namespace-strategies-directory
- Epic: EPIC-2026-04-25-implement-codegen-system-runtime
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-26T11:39:24Z

## User Narrative
As an engineer, I want namespace exposure split into strategies, so that room
objects, workstation, command, target, and builtins can be composed cleanly.

## Value / MRP Alignment
Namespace exposure is too important to leave as one giant builder method.
Strategies give us real composition without turning the builder into a blob.

## Ticket Contract
- ENTRY_GATE: the namespace directory story is staged and namespace strategy
  boundaries are explicit.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/strategies/`
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_codegen_room_objects_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_workstation_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_command_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_target_strategy_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_builtins_strategy_py_task.md`
- EXIT_GATE: namespace exposure strategy tasks are fully staged and non-overlapping.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any exposure concern proves
  too small to justify a standalone file.

## Requirements (Functional)
- Implement room-objects exposure strategy.
- Implement workstation exposure strategy.
- Implement command exposure strategy.
- Implement target exposure strategy.
- Implement builtins exposure strategy.

## Requirements (Non-Functional)
- Keep strategy responsibilities narrow.
- Avoid a fallback “misc exposure” file.

## Scope Boundaries
- In scope:
  - namespace exposure strategies
- Out of scope:
  - namespace builder
  - validation strategies
  - execution

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the namespace strategy split is explicit enough to stage
  file-by-file planning.

## Dependencies / Related Work
- `tickets/stories/2026-04-25_codegen_system_namespace_directory_story.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-implement-codegen-room-objects-strategy-py - expose room/runtime objects
- [ ] Task: TASK-2026-04-25-implement-codegen-workstation-strategy-py - expose workstation bindings/surfaces
- [ ] Task: TASK-2026-04-25-implement-codegen-command-strategy-py - expose command surface
- [ ] Task: TASK-2026-04-25-implement-codegen-target-strategy-py - expose active target surface
- [ ] Task: TASK-2026-04-25-implement-codegen-builtins-strategy-py - expose approved builtins
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- All planned namespace strategy files have tasks.
- The namespace exposure split is explicit and non-overlapping.

## Validation / Test Plan
- Focused namespace-builder integration tests.

## UX / API / Data Notes
- Strategies are internal and are composed by `CodegenNamespaceBuilder`.

## Risks / Mitigations
- Risk: exposure strategies overlap and hide policy decisions.
  Mitigation: keep each strategy aligned to one exposure concern only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether builtins exposure should stay one file or later split into safe vs
  permissive profiles.

## Decision Log
- 2026-04-25: namespace exposure remains strategy-based.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: Namespace exposure concerns are already distinct enough that they
    should be implemented as strategies instead of one giant builder file.
  EVIDENCE:
  - user_instruction: agreement on namespace builder concerns and strategy layout
  IMPACT: The namespace story stays coherent and extendable.
  NEXT: stage the five namespace strategy tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T10:37:18Z
  TYPE: FACT
  CLAIM: Four of the five staged namespace-strategy files are already landed as
    part of the namespace foundation slice: room objects, workstation,
    command, and target. The only remaining file in this story is the deferred
    builtins strategy.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_room_objects_strategy.py:1-76
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_workstation_strategy.py:1-51
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_command_strategy.py:1-52
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py:1-58
  - tickets/stories/2026-04-25_codegen_system_namespace_directory_story.md:108-132
  IMPACT: This story remains open, but only for the builtins exposure file.
  NEXT: keep the story routed until `codegen_builtins_strategy.py` is either
    implemented or explicitly dropped.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The old builtins-only remainder is no longer accurate. The namespace
    lane now includes a landed builtins strategy plus a landed `codegen`
    control strategy, and the namespace contract itself has shifted away from
    `rift/space/target/frame_name` toward `viewer/command/workstation/codegen`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:1-74
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_control_strategy.py:1-65
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:25-35
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:10-23
  IMPACT: This story is now in review and needs either closure or a narrowed
    follow-on definition rather than staying routed as a builtins-only
    remainder.
  NEXT: return the namespace-strategy lane for review and decide whether to
    close it or split the newer namespace contract work into a separate story.
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
This story owns the namespace strategy directory beneath the namespace
subsystem.
