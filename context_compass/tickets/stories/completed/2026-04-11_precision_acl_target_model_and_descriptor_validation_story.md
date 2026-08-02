# Story: Precision ACL Target Model And Descriptor Validation
- Completed: 2026-04-13T21:43:06Z
- Summary: Completed the precision ACL investigation/model story after the retained model and its first runtime tranches all landed.

## Metadata
- Story ID: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Epic: EPIC-2026-04-11-precision-acl-targets-and-spell-access
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T19:40:43Z
- Updated: 2026-04-13T21:43:06Z

## User Narrative
As the Rift runtime designer, I want the precision ACL model and its
descriptor-backed validation flow to be explicit before implementation, so that
the next ACL slice is grounded in the real validator, descriptor, and compile
surfaces instead of chat-only reasoning.

## Ticket Contract
- ENTRY_GATE: the precision ACL epic and retained design artifact are staged,
  and the user explicitly asked for implementation investigation focused on
  validator and descriptor-backed existence checks.
- EXECUTION_BOUNDARY: investigation, synthesis, and implementation planning
  only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_precision_acl_targets_and_spell_access_epic.md
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md
  - tickets/tasks/2026-04-11_investigate_precision_acl_implementation_and_descriptor_validation_task.md
- EXIT_GATE: the precision target model, descriptor-backed validation flow, and
  implementation order are explicit enough to drive the next code slice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the model still leaves
  multiple materially different implementation directions plausible.

## Acceptance Criteria
- The current validator and descriptor surfaces are mapped.
- The precision config placement inside the ACL bundle is explicit.
- The descriptor-backed validation flow is explicit.
- The implementation order is explicit.

## Notes
- DATETIME: 2026-04-11T19:40:43Z
  TYPE: PLAN
  CLAIM: The next step is implementation investigation, not more runtime patch
    churn. The main question is how to fit a typed precision target layer into
    the current ACL shell objects and how the validator should query descriptor
    truth to confirm that authored frame/conduit/spell/member targets actually
    exist.
  EVIDENCE:
  - user_instruction: "go ahead and investigate how to implement all this stuff"
  - user_instruction: "we'd need a validation effort by the ACL validator"
  - user_instruction: "during this validation step we would need to query the descriptor to ensure those elements exist"
  IMPACT: The next move is a focused design read of the current ACL validator,
    descriptor indexes, and compile surface.
  NEXT: create the task and inspect the relevant ACL/descriptor sources.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T21:43:06Z
  TYPE: DECISION
  CLAIM: This story is complete. The current validator and descriptor surfaces
    were mapped, the retained precision model was written, and the first
    runtime slices already landed on top of that model.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_investigate_precision_acl_implementation_and_descriptor_validation_task.md:1-160
  - tickets/tasks/completed/2026-04-11_implement_acl_family_precision_profiles_and_validator_strategies_task.md:1-165
  - tickets/tasks/completed/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md:1-145
  - tickets/tasks/completed/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md:1-131
  - tickets/tasks/completed/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md:1-146
  IMPACT: The story no longer needs to remain in active planning state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the design and implementation-planning tranche for the
precision ACL layer and descriptor-backed validation.
