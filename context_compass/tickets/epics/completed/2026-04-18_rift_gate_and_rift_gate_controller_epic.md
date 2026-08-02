# Epic: Rift Gate And Rift Gate Controller
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after the RiftGate implementation task landed.

## Metadata
- Epic ID: EPIC-2026-04-18-rift-gate-and-rift-gate-controller
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T17:29:47Z
- Updated: 2026-04-19T16:54:36Z
- Target Window: 2026-04
- Related Program/Initiative: Rift runtime correctness and agent management

## Problem / Opportunity
The current Rift runtime has no dedicated admission/drain primitive for
viewer/command/codegen operations while ACL-driven or state-driven refresh work
is happening. The user wants a gate similar to the meld gate model, but owned
at the Rift layer and controlled by `Nexus`, with optional validation-step
callbacks that can execute while threads are marshalled.

## MRP Alignment (Most Reasonable Product)
The next MRP is:
- add `RiftGate`
- add `RiftGateController`
- make `Nexus` own the controller
- make each `Rift` own one gate instance registered with the controller
- support pause/resume, close-and-drain with timeout, and optional validation
  step callbacks keyed by named operation groups

That gives the Rift runtime a real coordination primitive before the later
projection split lands.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a gate modeled after the current
  meld/creation gate pattern before the larger projection split implementation.
- EXECUTION_BOUNDARY: investigate the existing gate pattern, stage the Rift
  gate/control design, then implement the first bounded gate/controller slice.
- DEPENDENCIES:
  - src/melder/utilities/synchronization/creation_gate.py
  - src/melder/utilities/synchronization/creation_gate_controller.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
- EXIT_GATE: a first Rift-gate implementation exists and the control surface
  ownership between `Nexus` and `Rift` is explicit.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the validation-step behavior
  requires a larger state-machine design than this first gate slice should
  absorb.

## Goals (Outcomes)
- Reuse the proven creation-gate control model at the Rift layer.
- Give `Nexus` a direct control plane for Rift admission/drain behavior.
- Add optional validation-step callbacks for state-check or state-update work
  while a gate transition is happening.

## Non-Goals (Explicit Exclusions)
- full projection split implementation
- full command/view/codegen refresh integration
- global whole-process thread control

## Scope Boundaries
- In scope:
  - `RiftGate`
  - `RiftGateController`
  - controller ownership on `Nexus`
  - one gate per `Rift`
  - validation-step registration contract
- Out of scope:
  - applying the gate to every viewer/command/codegen call in the same slice
  - broader workstation or projection redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a Rift-layer gate modeled on
  the meld gate before the larger projection split implementation.

## Success Metrics
- one code-grounded gate design based on the existing creation gate model
- one accepted implementation plan for Rift gate + controller
- one bounded first implementation slice staged cleanly

## Requirements (Functional + Non-Functional)
- `RiftGate` should support:
  - `open()`
  - `close()`
  - `wait()`
  - ticket registration/unregistration
  - `close_and_wait_until_free(timeout=30.0, interval=0.1)`
- `RiftGate` should add optional validation-step callbacks keyed by named
  operation groups.
- `RiftGateController` should support:
  - creating/registering one gate per Rift
  - looking up gates by Rift id
  - enable/disable all
  - close-and-drain by Rift id
- `Nexus` should own the controller.
- `Rift` should own the actual gate instance for its own runtime.

## Milestones (Track Progress)
- [ ] Milestone 1: investigate and define the Rift-gate model
- [ ] Milestone 2: implement the first Rift-gate/controller slice

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-18-investigate-and-plan-rift-gate-model
      - investigate the gate pattern and define the Rift-gate design

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: complete the Rift-gate investigation and planning story
- [ ] Task: stage the bounded implementation task for the first Rift-gate slice

## Acceptance Criteria (Epic Done)
- The existing creation-gate model is mapped and reused intentionally.
- The Rift-gate/controller ownership model is explicit.
- The first bounded implementation slice is accepted.

## Risks / Mitigations
- Risk: mixing global thread control with frame/rift-local control will widen
  the problem too early.
  Mitigation: keep the first gate scoped per Rift and controller-owned by
  `Nexus`.

## Validation / Test Approach
- source investigation first
- then focused unit ring for the first gate/controller implementation

## Open Questions
- Should validation-step callbacks run before or after drain completes, or both?
- Should the first gate be purely per-Rift, or eventually per-Rift plus
  per-frame?

## Decision Log
- 2026-04-18T17:29:47Z: stage the Rift-gate lane as a separate mechanism from
  the projection split so the synchronization primitive is designed cleanly
  first.

## Notes
- DATETIME: 2026-04-18T17:29:47Z
  TYPE: PLAN
  CLAIM: The user wants a Rift-layer gate modeled after the current creation
    gate, but with optional validation-step callbacks and `Nexus`-owned
    control. That is a separate runtime mechanism from the later projection
    split, so it should be staged as its own lane.
  EVIDENCE:
  - user_instruction: "I want a RiftGate similar to the meldgate"
  - user_instruction: "we can host the controllers for these in Nexus"
  - user_instruction: "the rift will just implement it and nexus will own all the riftgate controls"
  IMPACT: We should design the gate/control primitive first instead of hiding
    it inside the projection split.
  NEXT: create the investigation story/task and map the existing creation-gate
    model against the requested Rift behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This epic owns the next synchronization primitive for Rift: `RiftGate` and
`RiftGateController`.
