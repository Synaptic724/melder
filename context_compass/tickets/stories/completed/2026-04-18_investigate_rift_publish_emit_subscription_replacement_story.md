# Story: Investigate Rift Publish Emit Subscription Replacement
- Completed: 2026-04-18T16:45:44Z
- Summary: Investigation story is complete; the publish/emit plan was accepted and fully carried through the event-system implementation and memory follow-on.

## Metadata
- Story ID: STORY-2026-04-18-investigate-rift-publish-emit-subscription-replacement
- Epic: EPIC-2026-04-18-rift-event-publication-and-subscription-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:38:19Z
- Updated: 2026-04-18T16:45:44Z

## User Narrative
As the Rift runtime maintainer, I want the current queue/thread event seam
replaced by direct event publication and explicit subscription, so that Rift
emits high-signal events outward without owning orchestration.

## Value / MRP Alignment
This story keeps the Rift event lane bounded to one structural improvement:
Rift emits, external systems subscribe.

## Ticket Contract
- ENTRY_GATE: the epic is active and the user explicitly redirected to this
  next Rift issue after closing the per-frame contract lane.
- EXECUTION_BOUNDARY: investigate the live queue/event surface and propose the
  publish/emit replacement plan before implementation.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-04-18_investigate_rift_event_queue_replacement_and_subscription_contract_task.md
- EXIT_GATE: the replacement plan is explicit enough for implementation and
  the user has accepted it.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if subscriber enforcement needs
  a deeper mode/configuration redesign first.

## Requirements (Functional)
- Identify every live queue API and direct runtime producer.
- Identify the direct test surfaces that will change.
- Decide what must replace the queue/thread API.

## Requirements (Non-Functional)
- No backward-compat queue shim.
- Keep orchestration outside Rift.

## Scope Boundaries
- In scope:
  - queue/thread API
  - subscriber/publication replacement
  - hook configuration implications
- Out of scope:
  - broader `Rift`/`RiftSpace` ownership redesign
  - codegen behavior beyond event/subscriber requirements

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-investigate-rift-event-queue-replacement-and-subscription-contract
      - map the live event queue shape and propose the replacement
- [x] Enforce Ticket Microcycle across the active event-lane task.

## Acceptance Criteria
- The live event queue/thread shape is documented from source evidence.
- The publish/emit replacement is concrete enough to implement next.
- The user accepts the plan before code edits start.

## Risks / Mitigations
- Risk: current event configuration semantics are too underdefined to preserve.
  Mitigation: make that contract a first-class decision point in the plan.

## Notes
- DATETIME: 2026-04-18T11:38:19Z
  TYPE: PLAN
  CLAIM: This story is intentionally narrow: queue/thread event ownership and
    its replacement with event publication and explicit subscription.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:653-816
  - src/melder/utilities/interfaces/interfaces.py:7352-7379
  IMPACT: We can fix the wrong event shape without mixing it with the larger
    one-space-per-rift or space-ownership refactors.
  NEXT: complete the investigation task and return with the replacement plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This story owns the investigate-first pass for replacing Rift's queue/thread
event seam with outbound event publication and subscription.
