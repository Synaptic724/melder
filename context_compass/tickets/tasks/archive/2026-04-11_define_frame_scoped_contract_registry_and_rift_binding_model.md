# Task: Define Frame-Scoped Contract Registry And Rift Binding Model

## Metadata
- Task ID: TASK-2026-04-11-define-frame-scoped-contract-registry-and-rift-binding-model
- Story: STORY-2026-04-11-investigate-multi-contract-frame-policy-model
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-11T00:12:09Z
- Updated: 2026-04-11T00:12:09Z

## Objective
Define the target frame-scoped ACL/codegen contract registry model and the
selected Rift binding shape over it.

## Ticket Contract
- ENTRY_GATE: the current-model audit exists with concrete migration seams.
- EXECUTION_BOUNDARY: target-model definition only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
- EXIT_GATE: the target multi-contract model is explicit enough to plan implementation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if multiple target ownership models
  remain equally plausible after the audit.

## Scope Boundaries
- In scope:
  - frame-scoped ACL registry shape
  - frame-scoped codegen registry shape
  - selected Rift binding shape
  - descriptor/registry separation
- Out of scope:
  - runtime edits
  - final migration plan

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the current-model audit is complete enough to define the
  target registry and Rift binding shape.

## Steps / Checklist
- [ ] Read the current-model audit.
- [ ] Define the target registry containers and ownership.
- [ ] Define the selected `FrameLinkContract` binding shape.
- [ ] Record the model in `## Notes`.

## Deliverables
- evidence-backed target model

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: target model still blurs descriptor truth with selected policy lenses.
  Rollback: keep the descriptor/contract split explicit in every note.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: This task should only define the target model after the current seams
    are audited. The core design target is descriptor truth plus many policy
    lenses, with Rift binding to one selected pair rather than owning policy truth.
  EVIDENCE:
  - user_instruction: "we could have multiple acls for the same frame"
  - user_instruction: "the framelink contract or whatever we called it can easily map to that specific acl contract and codegen contract"
  IMPACT: The target model can stay explicit and avoid collapsing back into one
    universal frame ACL.
  NEXT: wait for the current-model audit and then define the registry/binding shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: The current-model audit is now complete enough that this task can stay
    narrow and define the target shape directly. The current typed ACL node already
    pairs view and codegen policy, so the most likely target is a dictionary-backed
    per-frame registry of named paired configs plus selected contract names carried
    on `FrameLinkContract`.
  EVIDENCE:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md:1-146
  - user_instruction: "we just need to add a single abstraction layer"
  - user_instruction: "I think we should just use a dictionary and keep it simple"
  - user_instruction: "leave the name as \"default\" as an optional str"
  IMPACT: The next discovery pass can focus on exact dictionary shape, naming
    defaults, and selected-contract binding without reopening the current-model audit.
  NEXT: define the per-frame contract dictionary shape and the exact additional
    state `FrameLinkContract` should carry.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: DECISION
  CLAIM: The target model should add only one new abstraction layer and keep it
    frame-first. The simplest correct shape is:
    - `FrameACLManager` still owns `frame_name -> FrameACLContainer`
    - each `FrameACLContainer` gains a named config dictionary, not a new object tree
    - the dictionary values should be `FrameACLConfiguration`, because that type
      already pairs view and codegen policy
    - names are local to the frame, not global across Nexus
    - omitted name defaults to `"default"`
    - `FrameLinkContract` should store the selected contract name per frame so
      Rift binds to one named contract for the frame it targets
  EVIDENCE:
  - tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md:1-170
  - user_instruction: "we just need to add a single abstraction layer"
  - user_instruction: "I think we should just use a dictionary and keep it simple"
  - user_instruction: "leave the name as \"default\" as an optional str"
  - user_instruction: "isn't an ACL container supposed to be a single ACL and codegen ACL?"
  IMPACT: The implementation can stay narrow and incremental. We do not need a
    separate binding class or separate ACL/codegen registries in the first cut.
  NEXT: define the exact field additions on `FrameACLContainer`,
    `FrameACLManager`, and `FrameLinkContract`, then sequence the implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task defines the target model only after the current seams are audited.
