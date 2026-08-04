# Task: Audit Command System Surface And Plan Cleanup
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass as a retained audit reference; no follow-on command-surface cleanup slice is active right now.

## Metadata
- Task ID: TASK-2026-04-18-audit-command-system-surface-and-plan-cleanup
- Story: STORY-2026-04-18-separate-view-command-codegen-projections
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T19:42:55Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Audit the live command surface for fake policy hooks, public-to-public method
chaining, and the current RiftGate integration shape so we can choose the next
bounded cleanup slice from evidence.

## Ticket Contract
- ENTRY_GATE: user requested a command-method audit and cleanup planning pass.
- EXECUTION_BOUNDARY: `CommandSystem`, `StaticCommandSystem`, `Workstation`,
  `FrameViewer`, and directly relevant interfaces/tests for audit evidence only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_implement_separate_view_command_codegen_projections_task.md
  - tickets/tasks/2026-04-18_implement_rift_gate_and_rift_gate_controller_task.md
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/command_system/static_command_system.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- EXIT_GATE: concrete design issues are documented with evidence and a bounded
  cleanup proposal is ready before implementation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the cleanup would widen into
  a full command-surface redesign beyond one bounded slice.

## Scope Boundaries
- In scope:
  - audit of command surface structure
  - gate-entry integration audit across viewer/command/workstation
  - cleanup-slice planning
- Out of scope:
  - implementing the cleanup before the user sees the proposal
  - unrelated projection/runtime redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested a deep command-method audit before the
  next cleanup slice is implemented.

## Steps / Checklist
- [ ] Read the command-system classes and relevant gate/workstation/viewer seams.
- [ ] Record concrete design problems with evidence in `## Notes`.
- [ ] Produce the bounded cleanup recommendation before implementation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed command-surface audit
- bounded cleanup recommendation

## Files / Paths Impacted
- src/melder/aether/nexus/rift/command_system/command_system.py
- src/melder/aether/nexus/rift/command_system/static_command_system.py
- src/melder/aether/nexus/rift/rift_space/workstation.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py`

## Risks / Rollback Notes
- Risk: the audit may reveal that the command surface needs a wider structural cleanup than the gate-integration slice alone.
- Rollback: none; this task is investigation/planning only.

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
- DATETIME: 2026-04-18T19:42:55Z
  TYPE: FACT
  CLAIM: The current command gate wrapper is compensating for extensive
    public-to-public method chaining inside `CommandSystem`, not just adding
    gate admission. Many public methods call `get_conduit_by_id(...)`,
    `get_spell_by_index_id(...)`, or other public methods directly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:347-954
  - src/melder/aether/nexus/rift/command_system/command_system.py:1032-1488
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:124-154
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:436-451
  IMPACT: Naive per-method RiftGate try/finally would double-ticket nested public calls.
  NEXT: classify the current gate integration across viewer, command, and workstation before proposing the cleanup slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T19:42:55Z
  TYPE: FACT
  CLAIM: The command surface is also carrying fake policy seams and uneven gate
    coverage. Base `CommandSystem` exposes no-op policy hooks
    (`_assert_raw_runtime_object_access_allowed`, `_assert_topology_mutation_allowed`,
    `_assert_spell_activation_allowed`) that are only meaningful in subclasses,
    `FrameViewer` currently gates only `execute_method(...)`, and `Workstation`
    has no RiftGate integration at all.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:1682-1754
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:25-80
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2653-2724
  - src/melder/aether/nexus/rift/rift_space/workstation.py:67-761
  IMPACT: The next slice cannot just "copy the current command wrapper everywhere";
    it needs to decide which public entrypoints are truly top-level and how to
    represent room-policy checks honestly.
  NEXT: propose the bounded cleanup slice before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task audits the command surface and gate integration before the next
bounded cleanup slice is implemented.
