# Task: Investigate Precision ACL Implementation And Descriptor Validation
- Completed: 2026-04-13T21:43:06Z
- Summary: Completed the precision ACL investigation/planning task after the retained model and the first implementation tranches made the direction explicit and executable.

## Metadata
- Task ID: TASK-2026-04-11-investigate-precision-acl-implementation-and-descriptor-validation
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T19:40:43Z
- Updated: 2026-04-13T21:43:06Z

## Objective
Investigate how to implement the proposed precision ACL target layer inside the
current ACL shell objects, and define how descriptor-backed validation should
confirm authored frame/conduit/spell/member targets.

## Ticket Contract
- ENTRY_GATE: the precision ACL epic/artifact are staged and the user
  explicitly asked for implementation investigation centered on validator and
  descriptor-backed existence checks.
- EXECUTION_BOUNDARY: investigation and planning only. No precision ACL code
  implementation in this task.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_precision_acl_targets_and_spell_access_epic.md
  - tickets/stories/2026-04-11_precision_acl_target_model_and_descriptor_validation_story.md
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/rift/frame_viewer/
  - src/melder/aether/nexus/rift/rift_space/command_system.py
- EXIT_GATE: one explicit implementation model exists for:
  - typed precision ACL placement
  - descriptor-backed validation flow
  - compiled spell target identity
  - viewer/command consumption order
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the real code still leaves
  multiple materially different viable implementations.

## Scope Boundaries
- In scope:
  - precision config placement in `FrameACLConfiguration`
  - validator responsibilities and method expansion
  - descriptor lookup and existence validation flow
  - compile target identity and consumption order
- Out of scope:
  - code implementation
  - unrelated runtime hardening
  - UI/HUD implications

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested implementation investigation
  for the precision ACL layer and validator/descriptor integration.

## Steps / Checklist
- [ ] Inspect the current ACL configuration and validator shells.
- [ ] Inspect descriptor lookup/index surfaces relevant to frame/conduit/spell existence.
- [ ] Inspect viewer/command compiled-consumption surfaces.
- [ ] Record findings and propose one implementation direction.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- precision ACL implementation plan
- descriptor-backed validation flow
- compiled target identity recommendation

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-11_investigate_precision_acl_implementation_and_descriptor_validation_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content src/melder/aether/nexus/acl/frame_acl_validator.py`
  - `Get-Content src/melder/aether/nexus/frame_descriptor/frame_descriptor.py`
  - `Get-Content src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`

## Risks / Rollback Notes
- Risk: we overfit the model to the current viewer/command code and make the
  precision layer too rigid.
  Rollback: keep the plan at the contract and flow level rather than freezing a
  premature concrete class graph.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until implementation starts and the model is either
  accepted, superseded, or merged into canonical docs.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T19:40:43Z
  TYPE: PLAN
  CLAIM: The implementation investigation should answer four concrete questions:
    1) where the precision configuration lives in the ACL bundle
    2) how authored selectors are validated against descriptor truth
    3) what spell identity is compiled internally
    4) how viewer and command consume the compiled precision layer
  EVIDENCE:
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md:1-220
  - user_instruction: "we'd need a validation effort by the ACL validator"
  - user_instruction: "during this validation step we would need to query the descriptor to ensure those elements exist"
  IMPACT: Investigation can stay bounded to the ACL, descriptor, viewer, and command surfaces instead of expanding into unrelated runtime work.
  NEXT: inspect the current ACL validator, descriptor indexes, and viewer/command surfaces in parallel.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:49:18Z
  TYPE: FACT
  CLAIM: The current compile/consume model is still too coarse for the
    precision lane. `CompiledFrameACLAccessSurface` only carries:
    - `allowed_kinds`
    - `allowed_commands`
    - `visible_conduit_ids`
    - `visible_spell_keys`
    - payload-section visibility maps
    The compiler derives those entirely from coarse view/codegen rulesets.
    There is no compiled concept yet for:
    - exact published frame/conduit/spell/member targets
    - executable spell/member surface
    - compiled `spell_index_id` target sets
    Viewer and command therefore cannot consume a shared precision truth
    without extending the compiled surface.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:1-226
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:1-308
  - src/melder/aether/nexus/rift/rift_space/command_system.py:1-320
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1-362
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:1-342
  IMPACT: The new precision layer cannot just be “validated config.” It must
    also extend the compiled access surface so viewer and command can consume
    one shared derived target model.
  NEXT: map the validator and descriptor lookup surfaces to the precision
    selector-resolution flow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:49:18Z
  TYPE: FACT
  CLAIM: The current validator already has the right expansion seam, but it is
    only using it for descriptor contract floors. `FrameACLValidator` has:
    - `validate_configuration(...)` for typed child validation
    - `validate_configuration_against_descriptor(...)` for descriptor-backed
      checks
    Today the descriptor-backed pass only verifies:
    - frame/conduit/spell Nexus contract labels
    - minimum spell payload type/version
    It does not validate target existence, selector ambiguity, or member
    existence. So the clean implementation path is to extend
    `validate_configuration_against_descriptor(...)` rather than inventing a
    second validator class for precision existence checks.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_validator.py:1-420
  - src/melder/aether/nexus/acl/frame_acl_validator.py:420-680
  IMPACT: Descriptor-backed precision validation should live in the existing
    validator family, with typed config validation first and selector/member
    existence validation second.
  NEXT: inspect descriptor indexes and published spell fields to define the
    actual selector-resolution algorithm.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:49:18Z
  TYPE: FACT
  CLAIM: The current descriptor substrate is sufficient for v1 precision
    selector validation without adding new published records. `FrameDescriptor`
    already owns:
    - `conduit_records_by_id`
    - `spell_records_by_key`
    - `spell_keys_by_conduit_id`
    - `spell_keys_by_spellbook_id`
    And each published `SpellRecord` already carries the fields needed for
    exact spell validation:
    - `spell_id`
    - `spell_index_id`
    - `spell_name`
    - `spellframe`
    - `binding_name`
    - `owner_conduit_id`
    - `origin_spellbook_id`
    So v1 selector resolution can search the published spell records directly
    to mirror Meld-style logical selection and then compile to `spell_index_id`
    without adding a new publish lane first.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:274-430
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:1-167
  - src/melder/utilities/helpers/general_helpers.py:32-215
  IMPACT: We do not need a new descriptor record type to start the precision
    ACL lane. The published spell record plus descriptor indexes are enough for
    v1 selector validation.
  NEXT: propose the exact placement of the precision configuration inside the
    ACL bundle and the implementation order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:49:18Z
  TYPE: PLAN
  CLAIM: The clean implementation path is:
    1) add `precision_configuration` as a fourth typed child on
       `FrameACLConfiguration`
    2) give it typed frame/conduit/spell/member precision rules, with spell
       selectors accepting exact `spell_id` or Meld-style logical selectors
    3) extend `FrameACLValidator.validate_configuration_against_descriptor(...)`
       to resolve those selectors against published descriptor truth and compile
       spells to `spell_index_id`
    4) extend `CompiledFrameACLAccessSurface` with precision-derived target and
       member sets/maps
    5) update `FrameACLCompiler` so viewer and command both consume the
       precision-derived compiled surface
    6) extend `FrameACLBuilder` with a typed fluent API over the precision
       child rather than forcing users to author generic rulesets directly
    Also, spellbook-level precision ACLs should stay out of v1 because we still
    do not have a stable spellbook selector contract beyond runtime ids.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:1-360
  - src/melder/aether/nexus/acl/frame_acl_builder.py:1-260
  - src/melder/aether/nexus/acl/frame_acl_validator.py:1-680
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:1-226
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:1-308
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md:1-220
  IMPACT: We now have one concrete implementation order that fits the real ACL,
    descriptor, viewer, and command surfaces instead of inventing a second
    subsystem.
  NEXT: present this implementation model to the user and then begin the first
    code slice if approved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:55:38Z
  TYPE: DECISION
  CLAIM: The agreed next implementation order is now fixed for this lane:
    1) add `FrameACLPrecisionConfiguration`
    2) add typed frame/conduit/spell precision rules
    3) extend `FrameACLValidator` with descriptor-backed precision validation
    4) compile spells to `spell_index_id`
    5) project viewer from the compiled precision layer
    6) enforce command availability from the same compiled precision layer
    7) add the fluent builder surface last
    This keeps the lane grounded in one shared compiled truth before user-facing
    fluency or wider enforcement work.
  EVIDENCE:
  - user_instruction: "add this to your plans"
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md:1-220
  IMPACT: The next thread can resume with the agreed tranche order already
    written into repo memory instead of reconstructing it from chat.
  NEXT: start the first code tranche with `FrameACLPrecisionConfiguration` and
    typed precision rule objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:59:41Z
  TYPE: FACT
  CLAIM: The retained precision artifact now includes the full precision set
    agreed in chat, not just the shorter summary. It explicitly captures:
    - one `FrameACLPrecisionConfiguration`
    - full frame/conduit/spell precision rule families
    - descriptor-backed validation order
    - compiled surface additions
    - viewer/command consumption model
    - the fluent builder shape
    The remaining open design topic is the exact configuration-object
    composition, not the overall precision set itself.
  EVIDENCE:
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md:1-999
  - user_instruction: "Put all this in your fucken plan but we still need to talk about the configuration objects"
  IMPACT: The next thread can resume with the full agreed precision set in repo
    memory, and the remaining discussion can stay focused on configuration
    object composition instead of replaying the whole model again.
  NEXT: talk through the exact configuration-object composition for
    `FrameACLPrecisionConfiguration` and its rule objects before coding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T21:43:06Z
  TYPE: DECISION
  CLAIM: This investigation task is complete. The retained precision artifact
    captures the model clearly enough to implement, and the first landed
    precision tasks already executed against that model: separate-family chain
    migration, family-profile precision, selector resolution, stable-lineage
    runtime lookup, and command ACL access enforcement.
  EVIDENCE:
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md:1-284
  - tickets/tasks/completed/2026-04-11_refactor_frame_acl_container_to_separate_family_chains_task.md:1-187
  - tickets/tasks/completed/2026-04-11_implement_acl_family_precision_profiles_and_validator_strategies_task.md:1-165
  - tickets/tasks/completed/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md:1-145
  - tickets/tasks/completed/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md:1-131
  - tickets/tasks/completed/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md:1-146
  IMPACT: The investigation/planning lane no longer needs to remain active on
    the board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is design-only and should end with one explicit implementation model
for the precision ACL layer and descriptor-backed validation flow.
