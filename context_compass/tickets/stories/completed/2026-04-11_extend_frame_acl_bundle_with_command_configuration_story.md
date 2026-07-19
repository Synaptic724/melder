# Story: Extend Frame ACL Bundle With Command Configuration
- Completed: 2026-04-13T11:43:06Z
- Summary: Completed the first command-configuration bundle story after the command sibling and compatibility-validator slices both landed.

## Metadata
- Story ID: STORY-2026-04-11-extend-frame-acl-bundle-with-command-configuration
- Epic: EPIC-2026-04-11-frame-scoped-contract-registries-and-rift-binding
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T11:08:44Z
- Updated: 2026-04-13T11:43:06Z

## User Narrative
As the Rift runtime designer, I want the named frame ACL bundle to carry a
separate command configuration with its own validator pass, so that static and
capability command permissions are not forced through view or codegen policy.

## Value / MRP Alignment
This is the smallest trustworthy next slice after the named-contract cut:
- keep `FrameACLConfiguration` as the bundle
- add `command_configuration` as a first-class sibling
- validate it separately

That gives us the substrate we need for static/capability command policy
without collapsing everything into codegen or viewer rules.

## Ticket Contract
- ENTRY_GATE: the first named-contract selection seam is landed and green, and
  the user explicitly approved starting with `command_configuration` plus its
  validator counterpart.
- EXECUTION_BOUNDARY: typed command configuration, validator support, bundle
  wiring, focused tests, and ticket/patch sync only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_frame_scoped_contract_registries_and_rift_binding_epic.md
  - tickets/tasks/2026-04-11_implement_frame_scoped_named_acl_contracts_and_rift_selection.md
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- EXIT_GATE: `FrameACLConfiguration` carries `view + command + codegen`,
  validation recognizes the new command layer, and the focused test slice is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first cut forces command,
  view, and codegen into independent selection instead of one bundled config.

## Requirements (Functional)
- add `FrameACLCommandConfiguration`
- add validator support for the command configuration
- wire command config into the existing ACL bundle
- preserve named-contract bundle selection

## Requirements (Non-Functional)
- keep the bundle model explicit
- keep codegen separate from command policy
- keep the first cut narrow and testable

## Scope Boundaries
- In scope:
  - typed command configuration object
  - `FrameACLConfiguration` bundle extension
  - validator support
  - builder/default wiring
  - focused tests
- Out of scope:
  - static runtime execution
  - capability runtime execution
  - viewer/runtime consistency warning pipeline
  - separate per-type selection on the frame link

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved the first
  `command_configuration` implementation slice.

## Dependencies / Related Work
- tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
- tickets/artifacts/nexus_acl_builder_and_persistence_model.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-11-add-frame-acl-command-configuration-and-validation
- [x] Task: TASK-2026-04-11-add-frame-acl-set-compatibility-validator
- [x] Enforce Ticket Microcycle across linked task work.

## Acceptance Criteria
- The named frame ACL bundle now includes `command_configuration`.
- The frame ACL validator validates command configuration separately.
- The focused unit slice passes.

## Validation / Test Plan
- targeted unit tests for ACL configuration/builder/validator paths

## UX / API / Data Notes
- `FrameACLConfiguration` remains the selected bundle.
- `command_configuration` is a sibling of `view_configuration` and
  `codegen_configuration`, not an independent selected contract.

## Risks / Mitigations
- Risk: the implementation silently drifts toward independent per-type
  selection.
  Mitigation: keep one named bundle per frame and add command as another child
  of that bundle only.

## Applicable Anti-Patterns
- [ ] No story-state transition without task evidence.
- [ ] No closure while required task remains active or unaccepted.
- [ ] No bundled-policy claims without code evidence and focused tests.

## Open Questions
- Which command operations should be allowed in the first validation whitelist?
- Do we need cross-config warnings in the same slice or later?

## Decision Log
- This story exists because the current bundle model is right, but the bundle
  is incomplete without a first-class command layer.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_acl_command_configuration/architecture_patch.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_command_configuration.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_configuration.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_validator.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_builder.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the command-config runtime model is merged into
  canonical ACL docs or intentionally retired.

## Notes
- DATETIME: 2026-04-11T11:08:44Z
  TYPE: PLAN
  CLAIM: The next ACL slice should extend the existing named-contract bundle
    instead of changing how bundle selection works. The user explicitly wants
    `FrameACLConfiguration` to remain the set while adding a command sibling
    with its own validator pass.
  EVIDENCE:
  - user_instruction: "The FrameACLConfiguration is the set"
  - user_instruction: "and in there it has all the acls and the validation cycle too?"
  - user_instruction: "go ahead and add the command_Config and its validator counterpart"
  IMPACT: The implementation should preserve one selected named bundle per frame
    and add command config inside it, not as an independently selected contract.
  NEXT: create the implementation task and patch docs, then wire the new typed
    command layer into the bundle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: This story is complete. The named frame ACL bundle now carries a
    first-class command configuration sibling and a separate bundle
    compatibility validator, which is exactly the bounded substrate this story
    was created to land.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_add_frame_acl_command_configuration_and_validation_task.md:1-177
  - tickets/tasks/completed/2026-04-11_add_frame_acl_set_compatibility_validator_task.md:1-165
  IMPACT: The command-config bundle story can move to the completed lane.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the first typed `command_configuration` slice inside the
existing named ACL bundle model.
