# Story: Design Command ACL Enforcement For Static And Capability
- Completed: 2026-04-13T12:00:15Z
- Summary: Archived the command ACL design/proposal story after the enforcement plan and later runtime enforcement slices landed.

## Metadata
- Story ID: STORY-2026-04-11-design-command-acl-enforcement-for-static-and-capability
- Epic: EPIC-2026-04-10-rift-access-modes-static-capability-dynamic
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T16:48:03Z
- Updated: 2026-04-11T16:48:03Z

## User Narrative
As the Rift runtime designer, I want the command-system ACL model for `static`
and `capability` to be explicit before implementation, so that the new command
surface is constrained by real policy rather than handwaved later.

## Ticket Contract
- ENTRY_GATE: the general command system is landed and the user explicitly
  asked for investigation and a plan before ACL implementation begins.
- EXECUTION_BOUNDARY: design and proposal only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_design_command_acl_enforcement_plan.md
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
- EXIT_GATE: one explicit plan exists for how command ACLs constrain the
  current `RiftSpace` command system in `static` and `capability`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current command surface is
  still too incomplete for coherent ACL design.

## Acceptance Criteria
- The current command surface is mapped to ACL categories.
- The static/capability enforcement model is explicit.
- A concrete implementation sequence is proposed.

## Notes
- DATETIME: 2026-04-11T16:48:03Z
  TYPE: PLAN
  CLAIM: The new command-system surface is now concrete enough that ACL design
    can stop being abstract. The next design step is to map the current
    getters/execute methods to permit categories for `static` and `capability`
    instead of designing ACLs against hypothetical future tools.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:10-410
  - tickets/tasks/2026-04-11_add-command-system-to-rift-space_task.md:1-144
  - user_instruction: "go ahead and plan out the ACL shit and remember it should be conducive of static and capability rift spaces"
  IMPACT: The next move is design/proposal, not another runtime patch.
  NEXT: create the task and write the proposed ACL-enforcement plan against the
    live command system.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the design/proposal slice for command ACL enforcement on the
live `RiftSpace` command system.
