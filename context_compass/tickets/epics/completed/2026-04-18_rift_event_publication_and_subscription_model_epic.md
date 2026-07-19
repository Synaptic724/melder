# Epic: Rift Event Publication And Subscription Model
- Completed: 2026-04-18T16:45:44Z
- Summary: Closed the Rift event lane after replacing queue/thread ownership with room-owned event publication and landing executed-step memory emission on top of the cleaned event boundary.

## Metadata
- Epic ID: EPIC-2026-04-18-rift-event-publication-and-subscription-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:38:19Z
- Updated: 2026-04-18T16:45:44Z
- Target Window: 2026-04
- Related Program/Initiative: Rift finishing pass

## Problem / Opportunity
The current Rift event system is shaped as a room-owned queue:
- `RiftSpace` owns `_event_queue`, `_event_queue_thread`, and `_event_queue_stop_event`
- `IRiftSpace` exposes queue inspection and queue-thread control
- `Workstation` publishes weak-binding collection into that queue

That shape conflicts with the intended architecture. Rift should emit
high-signal events outward so an external system can subscribe and orchestrate
them. Rift should not own its own queue consumer thread.

## MRP Alignment (Most Reasonable Product)
The next MRP is not a full observability platform. It is:
- strip queue/thread ownership out of `RiftSpace`
- replace it with publish/emit semantics
- require an external subscriber for the modes that depend on event-driven
  orchestration

That gives Rift a clean outbound event seam without turning it into a runtime
scheduler.

## Ticket Contract
- ENTRY_GATE: the per-frame contract lane is accepted and closed, and the user
  explicitly redirected to the Rift event system next.
- EXECUTION_BOUNDARY: investigate and then refactor the current queue/thread
  event shape into a publish/emit + subscription contract.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: the replacement plan is accepted and the queue/thread model is
  removed in favor of event publication and explicit subscription.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the subscription requirement
  needs a broader mode or configuration redesign before the queue can be
  removed cleanly.

## Goals (Outcomes)
- Define the real live Rift event surface from current code.
- Replace the queue/thread shape with an outbound publish/emit contract.
- Make the subscriber requirement explicit for the modes that need external
  orchestration.

## Non-Goals (Explicit Exclusions)
- one-space-per-rift refactor
- codegen-system implementation
- broad room/workstation ownership refactors beyond the event seam

## Scope Boundaries
- In scope:
  - `RiftSpace` event ownership
  - `IRiftSpace` event API
  - `RiftEventConfiguration` event hook shape
  - direct unit-test implications
- Out of scope:
  - broader `Rift`/`RiftSpace` ownership redesign
  - ticket cleanup for stale old artifacts

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected focus to replacing the
  current Rift event queue with a publish/emit subscription model.

## Success Metrics
- one evidence-backed investigation of the current queue/event seam
- one accepted implementation plan for the publish/emit replacement
- no lingering queue/thread API on `IRiftSpace` after implementation

## Requirements (Functional + Non-Functional)
- Investigation must identify the real producers, real consumers, and direct
  test surfaces.
- The replacement must avoid backward-compat queue shims.
- The plan must keep orchestration outside Rift.

## Constraints / Assumptions
- The current queue/thread behavior is still directly unit-tested.
- `RiftEventConfiguration` is currently cloned by both `Rift` and `Nexus`.

## Milestones (Track Progress)
- [x] Milestone 1: investigation and replacement plan accepted
- [x] Milestone 2: queue/thread model replaced by publish/emit subscription

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-18-investigate-rift-publish-emit-subscription-replacement
      - investigate the live queue/event surface and define the replacement

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-04-18-investigate-rift-publish-emit-subscription-replacement
- [x] Task: Verify Ticket Microcycle enforcement across the active event lane.

## Acceptance Criteria (Epic Done)
- The current queue/thread shape is documented from source evidence.
- The user accepts the replacement plan before implementation begins.
- The queue/thread API is later removed and replaced cleanly.

## Risks / Mitigations
- Risk: removing the queue reveals that the current enrichers/observers shape
  is too fake to preserve.
  Mitigation: make the hook contract a first-class part of the investigation
  instead of silently carrying it forward.

## Validation / Test Approach
- source evidence + focused unit-ring changes in `test_rift_space.py` and
  `test_nexus.py`

## Open Questions
- Which `space_kind` values must require a subscriber before use:
  `capability`, `codegen`, or both?
- Should the current action/memory split survive, or collapse into one generic
  event publication contract?

## Decision Log
- 2026-04-18T11:38:19Z: stage the event-system replacement as an
  investigate-first lane before any queue/thread removal.

## Notes
- DATETIME: 2026-04-18T11:38:19Z
  TYPE: PLAN
  CLAIM: The next Rift finishing lane is the event system itself. The live code
    still treats it as a room-owned queue with an optional consumer thread,
    while the intended design is outbound publication that external
    orchestrators subscribe to.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:68-85
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:653-816
  - user_instruction: "replace it with a publish/emit system where something can and must subscribe to the API"
  IMPACT: We need an explicit investigation and plan before stripping the queue
    out of `RiftSpace`.
  NEXT: map the live queue/event dependencies and propose the replacement
    contract before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This epic owns the Rift event-system replacement lane: from room-owned queue to
publish/emit with explicit subscription.
