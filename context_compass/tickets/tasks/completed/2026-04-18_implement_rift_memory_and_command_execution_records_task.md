# Task: Implement Rift Memory And Command Execution Records
- Completed: 2026-04-18T16:45:44Z
- Summary: Finished the event-lane follow-on by landing the room-owned memory system, callback-driven memory emission, and top-level command-memory recording with a green focused validation ring.

## Metadata
- Task ID: TASK-2026-04-18-implement-rift-memory-and-command-execution-records
- Story: STORY-2026-04-18-implement-rift-memory-and-command-execution-records
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T15:23:03Z
- Updated: 2026-04-18T16:45:44Z

## Objective
Remove `IRiftAction`, implement real `IRiftMemory` / `RiftMemory`, add
`RiftSpace` step/epoch counters, and emit execution records from command
methods when memory emission is enabled.

## Ticket Contract
- ENTRY_GATE: the investigation task finalized the `IRiftMemory` contract and
  the user explicitly asked to begin documenting this as the next event-lane
  implementation.
- EXECUTION_BOUNDARY: interfaces, `RiftMemory`, `RiftSpace` counter ownership,
  `RiftEventConfiguration`, command execution memory emission, and the directly
  affected tests.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-04-18_investigate_rift_event_queue_replacement_and_subscription_contract_task.md
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/nexus.py
  - tests/unit/melder/aether/test_rift_event_configuration.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_command_system_direct.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `IRiftAction` is gone, `IRiftMemory` is real, counters live on
  `RiftSpace`, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the command-memory emission
  cut reveals a wider viewer/workstation emission scope than this task is meant
  to cover.

## Scope Boundaries
- In scope:
  - remove `IRiftAction`
  - real `IRiftMemory` + `RiftMemory`
  - `RiftSpace.step_counter`
  - `RiftSpace.epoch_counter`
  - explicit reset/increment APIs
  - command execution memory emission when enabled
  - clone-path updates for `RiftEventConfiguration`
- Out of scope:
  - external deferred action model
  - viewer/workstation memory emission unless needed by shared command paths
  - event bus expansion

## Steps / Checklist
- [x] Remove `IRiftAction`.
- [x] Add real `IRiftMemory` and concrete `RiftMemory`.
- [x] Add `RiftSpace` counter ownership plus reset/increment APIs.
- [x] Update `RiftEventConfiguration` away from action hooks.
- [x] Wire command execution memory emission.
- [x] Rewrite direct tests.
- [x] Validate the focused ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- real `IRiftMemory` contract
- `RiftMemory` runtime object
- `RiftSpace` counters
- command execution memory emission

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_memory_system.py tests/unit/melder/aether/test_command_system_direct.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_memory_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`
- Result: `159 passed`

## Risks / Rollback Notes
- Risk: the command surface is broad enough that memory emission may touch more
  methods than expected.
- Rollback: keep the first cut bounded to shared command methods and fail fast
  on any wider dependency instead of improvising more runtime semantics.

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
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-04-18T16:45:44Z
  TYPE: FACT
  CLAIM: The remaining memory lane is now landed. `RiftMemorySystem` owns the
    locked counters, shared memory context, memory callback registry, and
    `create_memory(...)` / `create_and_emit_memory(...)` flow; `CommandSystem`
    now wraps top-level public command calls and emits one `IRiftMemory` per
    successful command when memory callbacks are registered; nested public
    command calls are suppressed so a composite command like
    `create_cluster(...)` records only the top-level action.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py:1-323
  - src/melder/aether/nexus/rift/command_system/command_system.py:1-2264
  - src/melder/utilities/interfaces/interfaces.py:6268-6466
  - tests/unit/melder/aether/test_rift_memory_system.py:1-108
  - tests/unit/melder/aether/test_command_system_direct.py:1-514
  IMPACT: The broader task objective is now satisfied: `IRiftAction` is gone,
    `IRiftMemory` is real, the counters/context live in the room-owned memory
    system, and command execution emits memory records when enabled.
  NEXT: return the task for review and acceptance instead of widening the
    scope further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T16:45:44Z
  TYPE: MEASURE
  CLAIM: The focused memory-emission validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_memory_system.py tests/unit/melder/aether/test_command_system_direct.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_memory_system.py tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 159 passed
  IMPACT: The command-memory cut is stable enough for review.
  NEXT: wait for acceptance before closing the task and syncing completed-state routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T16:42:00Z
  TYPE: FACT
  CLAIM: The remaining memory-emission cut is almost entirely concentrated in
    the shared `CommandSystem`. The file exposes roughly 45 public command
    methods, and most of them already normalize to one concrete frame context
    through `_resolve_runtime_frame_name(...)` or selected-target resolution.
    That means the sane implementation is one shared command-memory emission
    helper plus a bounded mechanical pass over the public command methods,
    rather than inventing a second dynamic dispatch layer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/command_system.py:132-1582
  - src/melder/aether/nexus/rift/command_system/command_system.py:1583-1629
  - src/melder/aether/nexus/rift/command_system/command_system.py:1645-2119
  IMPACT: The remaining task is large but mechanically bounded to the shared
    command surface, and it does not require reopening the event-system
    architecture again.
  NEXT: add memory callback/emission support to `RiftMemorySystem`, then wire
    `CommandSystem` public methods to emit one `IRiftMemory` per successful
    command execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T16:36:02Z
  TYPE: FACT
  CLAIM: The event cleanup tranche is now landed. `IRiftAction` and
    `RiftEventConfiguration` are gone, `RiftSpace` now owns a real
    `RiftEventSystem` under `rift_space/event_system/`, the room-level event
    callback registry/create/emit behavior now lives in that object instead of
    on `RiftSpace`, `RiftConfiguration` no longer carries event config state,
    and `Rift` / `Nexus` no longer clone an obsolete room-event bag during
    room or profile creation.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:6363-6466
  - src/melder/aether/nexus/rift/rift_space/event_system/rift_event.py:1-126
  - src/melder/aether/nexus/rift/rift_space/event_system/rift_event_system.py:1-258
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-699
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:1-93
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:1-87
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:1-80
  - src/melder/aether/nexus/configuration/rift_configuration.py:1-427
  - src/melder/aether/nexus/rift/rift.py:1-861
  - src/melder/aether/nexus/nexus.py:1-4317
  IMPACT: The room event surface is now coherent and owned in one place, so
    the remaining work under this broader task can focus on command-memory
    emission without dragging old action/config baggage forward.
  NEXT: wire `IRiftMemory` emission into the command surface on top of the new
    `RiftEventSystem` boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T16:36:02Z
  TYPE: MEASURE
  CLAIM: The focused event-system migration ring is green after removing the
    old config/action seam.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/configuration/rift_configuration.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py src/melder/aether/nexus/rift/rift_space/event_system/rift_event.py src/melder/aether/nexus/rift/rift_space/event_system/rift_event_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_event_system.py tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 142 passed
  IMPACT: The event-system replacement is stable enough to build command-memory
    emission on top of it.
  NEXT: keep the broader task active for the `IRiftMemory` command-emission cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T16:35:00Z
  TYPE: FACT
  CLAIM: The live runtime already has the callback-driven `IRiftEvent`
    behavior on `RiftSpace`, so the remaining event cleanup is not "build an
    event API from scratch." The real obsolete seam is
    `RiftEventConfiguration`: it still depends on `IRiftAction`, stores
    action/memory enrichers and observers, is cloned by both `Rift` and
    `Nexus`, is threaded through `RiftConfiguration`, and is still asserted by
    direct unit tests. The correct next cut is to replace that seam with a real
    `rift_space/event_system` object and remove `IRiftAction` entirely.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_event_configuration.py:1-106
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:23-23
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:162-175
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:685-810
  - src/melder/utilities/interfaces/interfaces.py:6393-6415
  - src/melder/aether/nexus/nexus.py:3107-3132
  - src/melder/aether/nexus/rift/rift.py:725-776
  - src/melder/aether/nexus/configuration/rift_configuration.py:62-62
  - src/melder/aether/nexus/configuration/rift_configuration.py:218-218
  - src/melder/aether/nexus/configuration/rift_configuration.py:410-426
  - tests/unit/melder/aether/test_rift_event_configuration.py:1-21
  - tests/unit/melder/aether/test_rift_space.py:34-47
  - tests/unit/melder/aether/test_nexus.py:745-778
  IMPACT: The event/memory lane should be split cleanly: first migrate the
    runtime to a real `event_system` and remove `IRiftAction`; then wire
    `IRiftMemory` onto the command surface without carrying the old config bag
    forward.
  NEXT: add `rift_space/event_system`, migrate `RiftSpace` to own it, remove
    `RiftEventConfiguration` / `IRiftAction`, and rewrite the direct tests to
    the new surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: PLAN
  CLAIM: The implementation cut will keep both `IRiftEvent` and `IRiftMemory`,
    but remove `IRiftAction`. `IRiftMemory` becomes the executed-step record,
    `frame_name` is required, `step_counter` and `epoch_counter` live on
    `RiftSpace`, and the optional CommandOps context fields are:
    `task_name`, `activity_name`, `mission_name`, `agent_name`, and `agent_id`.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_rift_event_queue_replacement_and_subscription_contract_task.md:146-185
  - user_instruction: "I want both IRiftEvent and IRiftMemory"
  - user_instruction: "frame name is not optional"
  - user_instruction: "task_name, activity_name, and mission_name as optional"
  - user_instruction: "add optional agent_name and agent_id"
  IMPACT: The memory lane is fully specified and ready for implementation once
    you want code changes.
  NEXT: wait for approval, then patch interfaces, `RiftEventConfiguration`,
    `RiftSpace`, `RiftMemory`, and command execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: DECISION
  CLAIM: `IRiftMemory` should be backed by a dedicated `RiftMemorySystem`
    owned by `RiftSpace`. That system is the locked mutable source of truth for
    memory sequencing and shared memory metadata. The concrete plan is:
    1. `RiftSpace` owns `memory_system: RiftMemorySystem`
    2. `RiftMemorySystem` owns:
       - `rift_id`
       - `space_type`
       - `step_counter`
       - `epoch_counter`
       - optional CommandOps context:
         `task_name`, `activity_name`, `mission_name`, `agent_name`, `agent_id`
       - extra shared metadata dict
       - one lock
    3. `IRiftMemory` / `RiftMemory` become immutable snapshots with top-level fields:
       - `memory_id`
       - `created_at`
       - `frame_name`
       - `action_name`
       - `step_counter`
       - `epoch_counter`
       - `metadata`
    4. `metadata` is derived from `RiftMemorySystem` plus per-call overrides and
       always includes:
       - `rift_id`
       - `space_type`
       - optional CommandOps context fields
       - action-specific extras
    5. No `space_id`, `space_kind`, `status`, `payload`, or `operation_name`
       survive in the memory contract
    6. `RiftMemorySystem` exposes:
       - `create_memory(...)`
       - `increment_step()`
       - `reset_step()`
       - `increment_epoch(reset_step=True)`
       - `reset_epoch()`
       - `update_context(...)`
       - `clear_context()`
       - `describe_state()`
  EVIDENCE:
  - user_instruction: "we have a special object in riftspace for memories"
  - user_instruction: "call it like RiftMemorySystem"
  - user_instruction: "put all the details in there and then the IRiftMemory Interface can just use that"
  - user_instruction: "move everything into metadata"
  - user_instruction: "space_id is pointless"
  - user_instruction: "space_type not kind"
  - user_instruction: "action_name instead of operation name"
  IMPACT: The memory lane now has a clear ownership model and a compact memory
    record shape instead of scattering memory-related fields across the room and
    command layers.
  NEXT: implement `RiftMemorySystem`, then `RiftMemory`, then wire command
    emission through that system.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: FACT
  CLAIM: The first bounded implementation slice is now landed. A new
    `rift_space/memory_system/` package exists with `RiftMemory` and
    `RiftMemorySystem`, `IRiftMemory` and `IRiftMemorySystem` are real
    interfaces, and `RiftSpace` now owns and exposes `memory_system`. The
    memory system owns the locked counters and shared context, and creates
    immutable memory snapshots with the agreed required/optional fields through
    metadata. This slice intentionally stops before `IRiftAction` removal and
    command-memory emission.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory.py:1-99
  - src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py:1-212
  - src/melder/aether/nexus/rift/rift_space/memory_system/__init__.py:1-9
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-760
  - src/melder/utilities/interfaces/interfaces.py:6263-6372
  - tests/unit/melder/aether/test_rift_memory_system.py:1-82
  - tests/unit/melder/aether/test_rift_space.py:34-99
  IMPACT: The memory lane now has its core state owner and immutable record
    type, so the next cut can focus on the remaining event/config cleanup and
    command-memory emission instead of inventing the model further.
  NEXT: decide whether to continue directly into `IRiftAction` removal and
    command-memory emission or pause at this bounded milestone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: MEASURE
  CLAIM: The bounded memory-system slice is green on a focused unit ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/memory_system/__init__.py src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory.py src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_memory_system.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_memory_system.py` -> 13 passed
  IMPACT: The foundational memory objects are stable enough to build on.
  NEXT: keep the broader task active for the remaining `IRiftAction` removal
    and command-memory emission scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: FACT
  CLAIM: The first bounded slice is now implemented: `RiftMemory` and
    `RiftMemorySystem` exist under `rift_space/memory_system`, and `RiftSpace`
    now owns and exposes a live `memory_system` object. The system owns
    `rift_id`, `space_type`, `step_counter`, `epoch_counter`, optional
    CommandOps context fields, shared metadata, and immutable memory creation.
    This slice intentionally does not yet remove `IRiftAction` or wire command
    execution memory emission.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory.py:1-99
  - src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py:1-212
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-760
  - src/melder/utilities/interfaces/interfaces.py:6263-6372
  - tests/unit/melder/aether/test_rift_memory_system.py:1-82
  - tests/unit/melder/aether/test_rift_space.py:30-86
  IMPACT: The memory lane now has its core state owner and immutable record
    type, so the next cut can focus on event/config cleanup and command-memory
    emission instead of inventing the model further.
  NEXT: decide whether to continue directly into `IRiftAction` removal and
    command-memory emission or pause at this bounded milestone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T15:23:03Z
  TYPE: MEASURE
  CLAIM: The bounded memory-system slice is green on a focused unit ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/memory_system/__init__.py src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory.py src/melder/aether/nexus/rift/rift_space/memory_system/rift_memory_system.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_memory_system.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space.py tests/unit/melder/aether/test_rift_memory_system.py` -> 13 passed
  IMPACT: The foundational memory objects are stable enough to build on.
  NEXT: keep the task active for the remaining `IRiftAction` removal and
    command-memory emission scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task owns the next event-lane implementation slice after callback
publication: removing `IRiftAction` and making `IRiftMemory` real.
