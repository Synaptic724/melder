# Task: Investigate And Plan Rift Gate Model
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the RiftGate implementation task landed.

## Metadata
- Task ID: TASK-2026-04-18-investigate-and-plan-rift-gate-model
- Story: STORY-2026-04-18-investigate-and-plan-rift-gate-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T17:29:47Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Map the existing creation-gate model and define the first Rift-gate plus
Rift-gate-controller implementation plan for `Nexus` and `Rift`.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a Rift-layer gate modeled after the
  creation gate before the larger projection split implementation.
- EXECUTION_BOUNDARY: investigation and planning only across the existing gate
  model, `Nexus`, and `Rift`.
- DEPENDENCIES:
  - src/melder/utilities/synchronization/creation_gate.py
  - src/melder/utilities/synchronization/creation_gate_controller.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
- EXIT_GATE: the Rift-gate/controller design is explicit enough to implement
  next.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if validation-step behavior needs
  a larger orchestration model than this first gate cut should absorb.

## Scope Boundaries
- In scope:
  - existing creation-gate model
  - Rift/Nexus ownership placement
  - validation-step callback behavior
  - first implementation plan
- Out of scope:
  - actual code patching
  - projection split implementation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested the Rift-gate planning pass as the next
  immediate step.

## Steps / Checklist
- [ ] Read the existing creation gate and controller in full.
- [ ] Read the current Rift/Nexus creation and cleanup points relevant to gate ownership.
- [ ] Define the Rift-gate and controller delta from the existing gate model.
- [ ] Propose the first implementation slice.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- code-grounded Rift-gate/controller plan
- explicit proposed ownership model

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-18_investigate_and_plan_rift_gate_model_task.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: accidentally widening the gate into global process control.
- Rollback: keep the first gate per-Rift and controller-owned by `Nexus`.

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
- DATETIME: 2026-04-18T17:29:47Z
  TYPE: PLAN
  CLAIM: The right first step is to treat `RiftGate` as a near-copy of the
    current creation gate model, then define only the Rift-specific deltas:
    one gate per Rift, `Nexus`-owned controller, and optional validation-step
    callbacks keyed by named operation groups.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:1-389
  - src/melder/utilities/synchronization/creation_gate_controller.py:1-938
  - user_instruction: "it can be a literal carbon copy"
  - user_instruction: "one big difference being we want to ensure that we have a special feature"
  IMPACT: The next proposal can stay concrete and avoid speculative state
    machine sprawl.
  NEXT: return the proposed Rift-gate/controller design and the first
  implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:29:47Z
  TYPE: FACT
  CLAIM: The existing `CreationGate` and `CreationGateController` already
    implement the exact first-cut synchronization model we want for Rift:
    open/close/wait, ticket registration, and close-and-drain with timeout,
    plus controller-owned registry and aggregate enable/disable operations.
    The only approved delta for v1 is scope and ownership: one gate per Rift,
    controller owned by `Nexus`, gate owned by `Rift`. The optional
    validation-step callback idea is intentionally deferred.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:9-389
  - src/melder/utilities/synchronization/creation_gate_controller.py:8-938
  - src/melder/aether/nexus/nexus.py:191-205
  - src/melder/aether/nexus/nexus.py:628-701
  - src/melder/aether/nexus/rift/rift.py:24-151
  - user_instruction: "it can be a literal carbon copy"
  - user_instruction: "if we're going to build that projection idea out"
  IMPACT: The next implementation can stay narrowly scoped to a copy-style
    gate/controller slice instead of widening into a larger state machine.
  NEXT: stage the bounded implementation task for `RiftGate` and
    `RiftGateController`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the investigate-first pass for `RiftGate` and
`RiftGateController`.
