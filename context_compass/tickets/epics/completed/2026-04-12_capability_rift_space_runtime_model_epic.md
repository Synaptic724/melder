# Epic: Capability RiftSpace Runtime Model
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Epic ID: EPIC-2026-04-12-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T19:35:00Z
- Updated: 2026-04-19T16:37:39Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift room-mode completion

## Problem / Opportunity
`CapabilityRiftSpace` exists in runtime, but it is still only a placeholder.

Current state:
- [capability_rift_space.py](/<local-workspace>/src/melder/aether/nexus/rift/rift_space/capability_rift_space.py)
  exists and composes a room
- [capability_command_system.py](/<local-workspace>/src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py)
  currently just denies raw runtime-object access
- target-frame validation only adds extra requirements for `dynamic`, not for
  `capability`

So capability is real in type shape but not real in behavior.

The user direction is now clear:
- capability should be broad manual runtime access
- no codegen
- strong refs allowed
- bind anything
- use conduit cloud, linking, clusters, and runtime object access
- it should work on top of both automatic and dynamic frames
- frame truth still wins; room mode does not override Melder system_state

## MRP Alignment (Most Reasonable Product)
The MRP is not a fake capability sandbox.

It is:
- capability = manual dynamic-style room
- no codegen
- no proxy/handle theater
- no post-bind policing
- no frame-state override

That gives us one honest middle room:
- static
- capability
- dynamic (later codegen/opener superset)

## Ticket Contract
- ENTRY_GATE: static room semantics and testing are complete enough, and the
  user explicitly redirected the next room lane to capability.
- EXECUTION_BOUNDARY: capability room/runtime model only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/nexus.py
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
- EXIT_GATE: one explicit capability runtime model exists, with implementation
  order and a retained artifact.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if capability still has multiple
  materially different viable meanings after investigation.

## Goals (Outcomes)
- Define what capability actually permits.
- Define how capability differs from static and dynamic.
- Define frame compatibility and non-override rules.
- Define the first implementation order.

## Non-Goals (Explicit Exclusions)
- Capability implementation in this epic ticket itself.
- Codegen-room redesign.
- Renaming `dynamic` to `codegen`.

## Scope Boundaries
- In scope:
  - capability room semantics
  - capability command surface
  - capability/frame interaction model
  - implementation order
- Out of scope:
  - codegen tooling surface
  - static redesign
  - unrelated ACL/compiler redesign

## Success Metrics
- One durable artifact captures the accepted capability model.
- One implementation task exists that can execute the model directly.

## Stories (Required to Complete)
- [x] Story: investigate and lock the capability runtime model
- [x] Story: implement the capability command/runtime surface

## Notes
- DATETIME: 2026-04-12T19:35:00Z
  TYPE: FACT
  CLAIM: The current code already proves two important boundaries for
    capability. First, room type is still chosen by `RiftConfiguration.space_type`,
    not by frame system_state. Second, target-frame validation only adds extra
    requirements for `dynamic` rooms, not for `capability`. That means a
    capability room can sit on top of either automatic or dynamic frames
    without the frame forcing the room into dynamic/codegen behavior.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_configuration.py:197-214
  - src/melder/aether/nexus/rift/rift.py:1072-1088
  - src/melder/aether/nexus/nexus.py:2362-2423
  IMPACT: Capability can be defined as a room-surface policy without becoming
    a frame-state override.
  NEXT: create the design story/task and write the retained capability model
    artifact before implementation starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T22:32:47Z
  TYPE: FACT
  CLAIM: The capability implementation tranche is now landed and cleaned out of
    active task routing. The first capability cut, focused operation proof,
    shared command-surface expansion, reusable capability harness, and later
    helper/harness follow-ons all moved to completed state, so this epic no
    longer reflects open implementation work. It is now in `review` pending a
    final decision on whether to close the epic itself.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-12_implement_capability_room_manual_runtime_access_task.md:1-127
  - tickets/tasks/completed/2026-04-12_expand_capability_room_runtime_operations_task.md:1-123
  - tickets/tasks/completed/2026-04-12_expand_shared_command_system_manual_runtime_surface_task.md:1-157
  - tickets/tasks/completed/2026-04-12_implement_capability_rift_json_testbench_task.md:1-143
  - tickets/tasks/completed/2026-04-12_add_command_level_meld_helpers_task.md:1-242
  - tickets/tasks/completed/2026-04-12_align_command_surface_names_to_lower_runtime_api_task.md:1-156
  - tickets/tasks/completed/2026-04-12_extend_capability_json_harness_with_meld_helpers_task.md:1-179
  - tickets/tasks/completed/2026-04-12_add_command_level_conduit_introspection_helpers_task.md:1-191
  - tickets/tasks/completed/2026-04-12_add_command_level_spell_query_and_snapshot_helpers_task.md:1-137
  - tickets/tasks/completed/2026-04-12_extend_capability_json_harness_with_query_helpers_task.md:1-149
  IMPACT: The epic can either close next or remain as a short-lived review
    anchor, but it should not stay `in_progress` anymore.
  NEXT: ask whether to close the epic now that the implementation tranche is
    cleaned up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic owns the capability room lane: define it clearly, then implement it
without drifting into fake sandbox semantics.