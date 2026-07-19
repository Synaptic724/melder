# Task: Design Command ACL Enforcement Plan
- Completed: 2026-04-13T12:00:15Z
- Summary: Archived the command ACL design-plan slice after later command ACL enforcement and capability/runtime work made it historical planning context.

## Metadata
- Task ID: TASK-2026-04-11-design-command-acl-enforcement-plan
- Story: STORY-2026-04-11-design-command-acl-enforcement-for-static-and-capability
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T16:48:03Z
- Updated: 2026-04-11T16:48:03Z

## Objective
Investigate the live `RiftSpace` command surface and propose the first ACL
enforcement plan for `static` and `capability` modes.

## Ticket Contract
- ENTRY_GATE: the general command system is landed and green, and the user
  explicitly asked for investigation plus a proposed plan before ACL
  implementation.
- EXECUTION_BOUNDARY: investigation and proposal only. No ACL implementation in
  this task.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_design-command-acl-enforcement-for-static-and-capability_story.md
  - tickets/tasks/2026-04-11_add-command-system-to-rift-space_task.md
  - tickets/tasks/2026-04-11_add-frame-acl-command-configuration-and-validation_task.md
  - tickets/tasks/2026-04-11_add-frame-acl-set-compatibility-validator_task.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
  - src/melder/aether/nexus/rift/rift_space/command_system.py
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
- EXIT_GATE: one explicit design/implementation plan exists for ACL
  enforcement on the live command system and is ready for user review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the live command surface still
  leaves multiple materially different ACL models plausible.

## Scope Boundaries
- In scope:
  - map current command methods to ACL categories
  - define static/capability permit model
  - define runtime enforcement shape
  - define implementation order
- Out of scope:
  - code edits to ACL enforcement
  - runtime command-system changes
  - dynamic codegen enforcement

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested investigation and a plan for
  the ACL layer before implementation continues.

## Validation
- Not run.
- Recommended commands:
  - `Get-Content src/melder/aether/nexus/rift/rift_space/command_system.py`
  - `Get-Content src/melder/aether/nexus/acl/frame_acl_command_configuration.py`

## Notes
- DATETIME: 2026-04-11T16:48:03Z
  TYPE: FACT
  CLAIM: The general command system is now complete enough to support a real
    ACL plan. The room has:
    - selected-target getters
    - runtime-object getters for frame/conduit/spell
    - workstation-target attribute/method getters
    - explicit target-method execution
    and the ACL substrate already has:
    - `FrameACLCommandConfiguration`
    - child/type validation
    - set compatibility validation
    So the missing piece is no longer substrate or runtime shape. It is the
    actual permit model and enforcement order.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:10-410
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:11-334
  - src/melder/aether/nexus/acl/frame_acl_validator.py:18-631
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:26-365
  IMPACT: We can propose a real enforcement plan now instead of designing ACLs
    in the abstract.
  NEXT: map the current command methods into concrete ACL permit categories and
    propose the first implementation sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T16:48:03Z
  TYPE: PLAN
  CLAIM: The first static/capability ACL enforcement cut should constrain the
    live command system we already have instead of inventing another command
    surface. The clean model is:
    1) keep viewer discovery outside ACL enforcement for now
    2) treat command ACL as surface permissions over command-system methods and
       target classes
    3) forbid raw runtime-object getters by default in static/capability
    4) allow selected-target record getters and workstation-target
       member/method operations first
    5) add explicit object-get permission only when intentionally enabled
    6) enforce mode-specific gates (`static` live-only, `capability`
       published-execution) in the command system rather than in workstation
    7) use compatibility validator warnings for suspicious view/command gaps but
       keep hard failures for malformed or over-broad command policy
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:10-410
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:11-334
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:26-365
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:1-190
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md:210-337
  IMPACT: We can implement ACL enforcement incrementally on top of the current
    command surface instead of redesigning the surface again.
  NEXT: bring this plan to the user for review before starting enforcement
    implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is design-only and should end with a proposed ACL-enforcement plan.
