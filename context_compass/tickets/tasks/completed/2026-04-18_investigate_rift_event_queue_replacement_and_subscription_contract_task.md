# Task: Investigate Rift Event Queue Replacement And Subscription Contract
- Completed: 2026-04-18T16:45:44Z
- Summary: Completed the event-lane investigation by mapping the queue/config seams, defining the publish/emit replacement, and using that plan to drive the landed event-system and memory-system slices.

## Metadata
- Task ID: TASK-2026-04-18-investigate-rift-event-queue-replacement-and-subscription-contract
- Story: STORY-2026-04-18-investigate-rift-publish-emit-subscription-replacement
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:38:19Z
- Updated: 2026-04-18T16:45:44Z

## Objective
Map the live Rift queue/thread event system from source evidence and define the
bounded replacement plan for publish/emit plus explicit subscription.

## Ticket Contract
- ENTRY_GATE: the user redirected to the Rift event system immediately after
  accepting the per-frame contract lane.
- EXECUTION_BOUNDARY: investigation and planning only; no runtime/test edits
  yet.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/nexus.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: the replacement plan is explicit enough to implement after user
  approval.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the mode-specific subscriber
  requirement cannot be expressed cleanly with the current room/configuration
  shape.

## Scope Boundaries
- In scope:
  - queue/thread event ownership
  - real producers and direct tests
  - event configuration contract implications
  - proposed publish/emit + subscriber model
- Out of scope:
  - actual runtime patching
  - general room ownership redesign

## Steps / Checklist
- [ ] Read the live queue/thread API and cleanup path on `RiftSpace`.
- [ ] Identify the real event producers and direct test consumers.
- [ ] Read the current event-configuration and clone paths.
- [ ] Propose the replacement API and subscriber requirement boundary.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed dependency inventory
- concrete replacement plan

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the current queue/thread API is more visible in tests than in runtime.
  Rollback: stay investigation-only until the user accepts the replacement
  contract.

## Notes
- DATETIME: 2026-04-18T11:38:19Z
  TYPE: FACT
  CLAIM: The live event system is still shaped as a room-owned queue. `RiftSpace`
    owns `_event_queue`, `_event_queue_thread`, and `_event_queue_stop_event`,
    exposes `describe_event_queue()`, `manage_event_queue()`, and
    `stop_managing_event_queue()`, and cleans the queue/thread path during
    `cleanup()`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:68-85
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:171-205
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:653-816
  - src/melder/utilities/interfaces/interfaces.py:7352-7379
  IMPACT: Replacing the current event system means deleting public queue/thread
    surface area from both `RiftSpace` and `IRiftSpace`, not just swapping one
    helper function.
  NEXT: map the real producers and direct tests, then define the replacement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:38:19Z
  TYPE: FACT
  CLAIM: The only concrete runtime producer currently found is the workstation
    weak-binding collection callback. `Workstation` publishes a
    `binding_collected` payload through the room-owned event publisher, and the
    direct tests assert both queued inspection and queue-thread draining around
    that event.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/workstation.py:772-808
  - tests/unit/melder/aether/test_nexus.py:1032-1102
  - tests/unit/melder/aether/test_rift_space.py:190-300
  IMPACT: The queue replacement can stay narrow initially: prove the publish/
    emit contract on `binding_collected` first, then widen to later event types.
  NEXT: inspect the current event-configuration seam and decide whether it
    survives the replacement unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:38:19Z
  TYPE: FACT
  CLAIM: `RiftEventConfiguration` is currently only a callback bag for action
    and memory enrichers/observers. `Rift` and `Nexus` both clone those four
    callback lists, but the runtime does not actually execute them anywhere in
    the live event path.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py:8-106
  - src/melder/aether/nexus/rift/rift.py:951-1002
  - src/melder/aether/nexus/nexus.py:3116-3141
  - src/melder/aether/nexus/configuration/rift_configuration.py:410-426
  IMPACT: The replacement plan must decide whether to keep this hook seam,
    collapse it into a generic event hook model, or delete it instead of
    blindly carrying forward a fake action/memory split.
  NEXT: propose the replacement API and the mode-specific subscription rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:38:19Z
  TYPE: PLAN
  CLAIM: The bounded replacement plan is:
    1. remove queue/thread state and queue methods from `RiftSpace` and `IRiftSpace`
    2. add direct publish/emit plus subscriber registration on the room surface
    3. route workstation weak-binding events through that publisher
    4. rewrite queue-based tests to prove subscription delivery instead
    5. decide whether `capability`, `codegen`, or both must require an attached
       subscriber before use
    6. either collapse `RiftEventConfiguration` to generic event hooks or
       delete the fake action/memory split in the same lane
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:653-816
  - src/melder/utilities/interfaces/interfaces.py:6268-6299
  - user_instruction: "replace it with a publish/emit system where something can and must subscribe to the API in order to use the rift in specific modes"
  IMPACT: The next implementation lane is now concrete enough to stage, but it
    still needs your approval on the subscription requirement and the fate of
    the current action/memory hook split.
  NEXT: return this plan to the user and get the contract accepted before
    removing the queue.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T14:17:49Z
  TYPE: PLAN
  CLAIM: The first implementation cut should stay very small and callback-driven.
    `RiftSpace` should own a callback registry, not a queue. The recommended
    shape is:
    1. one base `IRiftEvent` protocol plus one concrete `RiftEvent` runtime class
    2. `RiftSpace` subscriber registration by token/id in a dict
    3. optional event-type filtering on subscription
    4. synchronous callback execution during emit
    5. no local queue, no thread, no drain loop
    6. no fake `IRiftAction` / `IRiftMemory` split in the first cut unless a
       real runtime need appears
  EVIDENCE:
  - user_instruction: "maybe we use a protocol for this and just define a simple IRiftEvent"
  - user_instruction: "allow a registration of various callbacks into a dictionary"
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:653-816
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py:8-106
  IMPACT: We can replace the current queue/thread seam without prematurely
    inventing a full event bus or rebuilding the same fake action/memory split.
  NEXT: propose the concrete `IRiftEvent` fields and the subscription API to
    the user before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T14:17:49Z
  TYPE: DECISION
  CLAIM: The final investigation proposal for the first event-system cut is:
    1. one base `IRiftEvent` protocol plus one concrete `RiftEvent`
    2. `RiftSpace` owns a callback registry keyed by subscription id
    3. `RiftSpace` exposes:
       - `subscribe_events(callback, *, event_types: Optional[Sequence[str]] = None) -> str`
       - `unsubscribe_events(subscription_id: str) -> None`
       - `emit_event(event: IRiftEvent) -> None`
       - `emit_runtime_event(event_type: str, payload: Dict[str, object], frame_name: Optional[str] = None, metadata: Optional[Dict[str, object]] = None) -> None`
    4. callback execution is synchronous
    5. queue/thread methods and queue/thread state are removed
    6. `Workstation` weak-binding collection is the first real producer and
       emits `binding_collected`
    7. `IRiftAction` / `IRiftMemory` are not used in v1
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:653-816
  - src/melder/utilities/interfaces/interfaces.py:6268-6299
  - src/melder/utilities/interfaces/interfaces.py:7352-7379
  - src/melder/aether/nexus/rift/rift_space/workstation.py:772-808
  - user_instruction: "start with the IRiftEvent"
  - user_instruction: "allow a registration of various callbacks into a dictionary"
  IMPACT: The lane is now specific enough to stage the implementation task next
    without reopening design drift around action/memory placeholder types or
    queue-thread ownership.
  NEXT: return this final proposal to the user for approval before creating the
    implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: DECISION
  CLAIM: The follow-on memory model is now constrained more tightly. `IRiftMemory`
    should remain distinct from `IRiftEvent`, `frame_name` is mandatory on every
    memory record, and `RiftSpace` should own two execution counters:
    - `step_counter`
    - `epoch_counter`
    Those counters must be incrementable and resettable through explicit
    `RiftSpace` APIs, and emitted memories should carry both values so command
    execution can be sequenced deterministically.
  EVIDENCE:
  - user_instruction: "frame name is not optional"
  - user_instruction: "have a step counter and an epoch counter that you can reset and increment via the rift_space"
  - user_instruction: "ensure that memory has these features"
  IMPACT: The next implementation plan for `IRiftMemory` must include
    `RiftSpace` counter ownership and a command-memory emission path that
    records `frame_name`, `step_counter`, and `epoch_counter` on every memory.
  NEXT: return the tightened memory plan to the user before staging or
    implementing the follow-on task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: DECISION
  CLAIM: `IRiftMemory` should also carry three optional CommandOps-facing
    context fields:
    - `task_name`
    - `activity_name`
    - `mission_name`
    These stay optional because they are external orchestration details, while
    `frame_name`, `step_counter`, and `epoch_counter` stay part of the core
    memory contract emitted by Rift.
  EVIDENCE:
  - user_instruction: "task_name, activity_name, and mission_name as optional please"
  - user_instruction: "they are commandops details"
  - user_instruction: "epoch counter can be there too to signal a macro signal"
  IMPACT: The next `IRiftMemory` implementation plan must preserve a clean
    split between mandatory Rift execution coordinates and optional
    CommandOps-supplied orchestration context.
  NEXT: return the final memory contract shape with required vs optional fields
    called out explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: DECISION
  CLAIM: The final `IRiftMemory` contract for the next lane is:
    Required:
    - `memory_id`
    - `memory_type`
    - `created_at`
    - `rift_id`
    - `space_id`
    - `space_kind`
    - `frame_name`
    - `surface`
    - `operation_name`
    - `status`
    - `step_counter`
    - `epoch_counter`
    - `payload`
    - `metadata`
    Optional:
    - `task_name`
    - `activity_name`
    - `mission_name`
    - `agent_name`
    - `agent_id`
    `RiftSpace` owns the step/epoch counters and exposes explicit reset /
    increment APIs. `IRiftAction` is removed, actions stay external, and
    command execution emits `IRiftMemory` records when memory emission is
    enabled.
  EVIDENCE:
  - user_instruction: "frame name is not optional"
  - user_instruction: "step counter and an epoch counter"
  - user_instruction: "task_name, activity_name, and mission_name as optional"
  - user_instruction: "add optional agent_name and agent_id"
  - user_instruction: "actions should live outside the system"
  IMPACT: The memory lane is now explicit enough to stage as the next
    implementation slice under the existing event epic.
  NEXT: create the follow-on story/task for removing `IRiftAction`,
    implementing real `IRiftMemory` / `RiftMemory`, and wiring the counters
    plus command-memory emission.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the investigation and replacement plan for stripping the Rift
event queue/thread model out of `RiftSpace` and replacing it with outbound
event publication plus explicit subscription.
