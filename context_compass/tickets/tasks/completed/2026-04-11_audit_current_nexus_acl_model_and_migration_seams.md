# Task: Audit Current Nexus ACL Model And Migration Seams
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-11-audit-current-nexus-acl-model-and-migration-seams
- Story: STORY-2026-04-11-investigate-multi-contract-frame-policy-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T00:12:09Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Audit the current single-current-ACL Nexus model and identify the concrete
migration seams for moving to many contracts per frame.

## Ticket Contract
- ENTRY_GATE: the new discovery story is staged and this is the first bounded
  investigation slice.
- EXECUTION_BOUNDARY: investigation only across current ACL ownership, frame
  scoping, and Rift binding seams.
- DEPENDENCIES:
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/rift/frame_link/
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- EXIT_GATE: the current single-current-ACL model and the migration seams are
  recorded with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current ACL ownership model
  is too ambiguous to map cleanly.

## Scope Boundaries
- In scope:
  - current frame ACL ownership
  - current frame-scoped chain model
  - current Rift/frame-link coupling points
  - migration seam identification
- Out of scope:
  - runtime edits
  - target-model proposal

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the first active discovery cut in the new lane.

## Steps / Checklist
- [ ] Inspect current frame ACL ownership and storage.
- [ ] Inspect current compiled access and descriptor validation path.
- [ ] Inspect current Rift/frame-link consumption of ACL-derived state.
- [ ] Record the concrete migration seams in `## Notes`.

## Deliverables
- evidence-backed current-model audit

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-11_audit_current_nexus_acl_model_and_migration_seams.md
- codex/context_compass/attention_board.md

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: this task drifts into proposing the new model too early.
  Rollback: keep this task on current-state evidence only.

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
  CLAIM: The first step is to prove exactly how the current single-current-ACL
    model is owned and consumed. We should not propose the new registry shape
    until the current seams are explicit.
  EVIDENCE:
  - tickets/epics/2026-04-11_frame_scoped_contract_registries_and_rift_binding_epic.md:1-155
  - user_instruction: "the ACLs are not universal for 1 frame, but they are registered to a frame"
  IMPACT: This keeps the new lane grounded in the real code instead of design-only instinct.
  NEXT: inspect the current frame ACL manager/container/chain and Rift binding seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: FACT
  CLAIM: The current Nexus-owned ACL model is explicitly frame-scoped and
    single-current by design. `FrameACLManager` owns one
    `frame_name -> FrameACLContainer` registry. Each container owns exactly one
    `FrameACLConfigurationChain`, one validator, and one builder. The chain
    seeds one default locked configuration as both head and current, and the
    manager surfaces one current selected configuration per frame through
    `_get_current_frame_acl_configuration(...)`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_acl_manager.py:24-47
  - src/melder/aether/nexus/frame_acl_manager.py:181-195
  - src/melder/aether/nexus/frame_acl_manager.py:233-246
  - src/melder/aether/nexus/acl/frame_acl_container.py:17-27
  - src/melder/aether/nexus/acl/frame_acl_container.py:78-87
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:13-27
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:73-81
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:155-167
  IMPACT: The migration target is clear at the base seam: we are not replacing
    a many-contract model, we are replacing a one-frame / one-current-selection
    model backed by historical chain nodes.
  NEXT: inspect how Nexus compiles and consumes that current selected configuration
    against descriptor truth, then inspect how Rift/frame-link consume the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: FACT
  CLAIM: The current consumer side is also single-selection. `Nexus.create_frame_viewer(...)`
    always pulls the frame's current selected ACL configuration, validates that
    one configuration against descriptor truth, and compiles one access surface
    from it. `Rift.target_frame(...)` only chooses a frame; it does not choose
    an ACL contract or a codegen contract. `FrameLinkContract` currently stores
    only assigned frame names, one default frame name, and metadata, so it has
    no place to carry selected contract identities yet.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1457-1525
  - src/melder\aether\nexus\rift\rift.py:177-185
  - src/melder\aether\nexus\rift\rift.py:383-404
  - src/melder\aether\nexus\rift\rift.py:406-465
  - src/melder\aether\nexus\rift\frame_link\frame_link_contract.py:17-28
  - src/melder\aether\nexus\rift\frame_link\frame_link_contract.py:38-83
  IMPACT: The migration seam is now explicit: we need to change both the
    frame-side policy ownership model and the Rift binding model, because the
    current system has no selected-contract slot between "frame" and "compiled
    access surface."
  NEXT: inspect the current typed ACL configuration object to see how view and
    codegen policy are already paired, then use that to define the target registry shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: FACT
  CLAIM: The current typed ACL model already pairs view and codegen policy, but
    only inside one frame-local configuration node plus one manager-wide reusable
    profile library. `FrameACLConfiguration` owns both `view_configuration` and
    `codegen_configuration` together, builder edits replace those two child configs
    together, and `FrameACLProfileBuilder` owns global reusable view/codegen
    profile registries. What does not exist yet is a per-frame registry of many
    named contract pairs that a Rift could select from.
  EVIDENCE:
  - src/melder\aether\nexus\acl\frame_acl_configuration.py:74-83
  - src/melder\aether\nexus\acl\frame_acl_configuration.py:138-164
  - src/melder\aether\nexus\acl\frame_acl_configuration.py:223-252
  - src/melder\aether\nexus\acl\frame_acl_builder.py:154-166
  - src/melder\aether\nexus\acl\profiles\frame_acl_profile_builder.py:42-45
  - src/melder\aether\nexus\acl\profiles\frame_acl_profile_builder.py:74-81
  - src/melder\aether\nexus\acl\profiles\frame_acl_profile_builder.py:139-164
  - src/melder\aether\nexus\acl\profiles\frame_acl_profile_builder.py:218-281
  IMPACT: The target model should not start from zero. It should likely preserve
    the existing paired view/codegen shape while changing where named selections
    are registered and how Rift binds to them.
  NEXT: conclude the current-model audit and move into the target-model task,
    focusing on how to add many per-frame contract pairs without throwing away
    the typed configuration work that already exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: DECISION
  CLAIM: The target model should likely add only one new abstraction layer:
    a per-frame named contract registry, probably dictionary-backed, with a
    simple default-name convention. The user direction is to keep contract
    registration simple:
    - contracts are registered to one descriptor/frame
    - names default to `"default"` when omitted
    - the named registry then allows multiple ACL/codegen contract layers for
      the same frame without mutating one universal frame ACL
  EVIDENCE:
  - user_instruction: "we just need to add a single abstraction layer"
  - user_instruction: "I think we should just use a dictionary and keep it simple"
  - user_instruction: "leave the name as \"default\" as an optional str"
  - user_instruction: "it gets set to a specific descriptor"
  IMPACT: The next target-model task should start from a dictionary-backed
    per-frame registry with optional-name defaulting rather than a more complex
    registry system.
  NEXT: define the exact dictionary shape and how `FrameLinkContract` should
    point at one selected named contract pair for a frame.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: MEASURE
  CLAIM: The current-model audit is now strong enough to hand off. We proved
    the three key seams:
    1) one container and one current selected ACL config per frame,
    2) Nexus viewer projection always consumes that one current selected config,
    3) `FrameLinkContract` currently carries only frame identity/default-frame
       state and no contract-name selection.
    We also proved that typed ACL nodes already pair view and codegen policy,
    so the target model does not need to invent that pairing from scratch.
  EVIDENCE:
  - src/melder/aether/nexus/frame_acl_manager.py:181-246
  - src/melder/aether/nexus/acl/frame_acl_container.py:17-27
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:13-27
  - src/melder/aether/nexus/nexus.py:1457-1525
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:17-28
  - src/melder/aether/nexus/rift/rift.py:177-185
  - src/melder/aether/nexus/rift/rift.py:406-465
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:74-83
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py:74-81
  IMPACT: The next task can now stay narrow and define the target per-frame
    named contract registry plus Rift binding model without re-auditing the
    current subsystem first.
  NEXT: switch the active lane to the target-model task and define the exact
    dictionary-backed registry and selected-contract binding shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task audits the current model first before any target-model proposal is made.