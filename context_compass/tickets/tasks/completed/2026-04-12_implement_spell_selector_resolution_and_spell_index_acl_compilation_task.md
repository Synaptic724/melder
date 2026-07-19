# Task: Implement Spell Selector Resolution And Spell Index ACL Compilation
- Completed: 2026-04-13T11:51:25Z
- Summary: Closed the selector-resolution tranche after later runtime consumers built on its compiled `spell_index_id` outputs.

## Metadata
- Task ID: TASK-2026-04-12-implement-spell-selector-resolution-and-spell-index-acl-compilation
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T08:15:24Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Implement the next precision ACL slice by validating authored spell selectors
against descriptor truth and compiling resolved spell targets to
`spell_index_id` while preserving the current viewer path that still needs
record-key visibility.

## Ticket Contract
- ENTRY_GATE: the family-profile precision ACL substrate is landed and green,
  and the user explicitly approved building the next phases:
  selector-based spell targeting and `spell_index_id` compilation.
- EXECUTION_BOUNDARY: ACL validator/compiler/compiled-surface work, focused
  viewer-compatible payload wiring, tests, and ticket/board/artifact sync only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_precision_acl_targets_and_spell_access_epic.md
  - tickets/stories/2026-04-11_precision_acl_target_model_and_descriptor_validation_story.md
  - tickets/tasks/2026-04-11_investigate_precision_acl_implementation_and_descriptor_validation_task.md
  - tickets/tasks/2026-04-11_implement_acl_family_precision_profiles_and_validator_strategies_task.md
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/acl/
- EXIT_GATE: spell selector conditions are validated against descriptor truth,
  the compiled ACL surface includes resolved spell-index targets, and the
  widened ACL/Nexus validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if selector semantics require a
  broader descriptor-schema redesign than this tranche should own.

## Scope Boundaries
- In scope:
  - spell selector conditions on precision rules
  - descriptor-backed selector validation
  - compilation to `spell_index_id`
  - compiler/compiled-surface extensions that preserve current viewer use of
    record keys
  - focused tests
- Out of scope:
  - conduit/frame selector redesign beyond what spell validation needs
  - command runtime enforcement changes
  - viewer UI redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved the next precision phases
  after the family-profile substrate landed.

## Steps / Checklist
- [ ] Stage patch docs and route this next precision task from the board.
- [ ] Add selector-aware spell rule validation against descriptor truth.
- [ ] Add compiled spell-index outputs while preserving record-key visibility.
- [ ] Update focused ACL/viewer-compatible tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- spell selector validation
- compiled `spell_index_id` ACL outputs
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py
- src/melder/aether/nexus/acl/frame_acl_compiler.py
- src/melder/aether/nexus/acl/validator/frame_acl_validator.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_validator.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py`

## Risks / Rollback Notes
- Risk: we break the current viewer path by switching too aggressively from
  record keys to spell-index ids.
  Rollback: keep both record-key and spell-index outputs in the compiled ACL
  surface until downstream consumers are fully migrated.

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
  - system_docs/patches/active/frame_acl_spell_selector_resolution/architecture_patch.md
  - system_docs/patches/active/frame_acl_spell_selector_resolution/component_patch_frame_acl_validator.md
  - system_docs/patches/active/frame_acl_spell_selector_resolution/component_patch_frame_acl_compiler.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the spell-selector resolution model is merged into
  canonical ACL docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T08:15:24Z
  TYPE: FACT
  CLAIM: The current ACL/compiler substrate still stops short of the earlier
    spell-selector design. The compiled ACL surface still exposes
    `visible_spell_keys` keyed by `(spellbook_id, spell_id)`, the compiler
    still derives spell visibility from generic allow/deny rule operations
    without selector resolution, and the validator still only does record
    contract/payload-floor checks instead of validating authored spell
    selectors against descriptor truth. That means the next slice is not more
    profile work. It is selector-aware spell validation and `spell_index_id`
    compilation.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:35-40
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:131-181
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:314-345
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:37-52
  IMPACT: We need one more ACL tranche before the earlier precision design is
    actually true in runtime terms.
  NEXT: add selector-aware spell validation and compile resolved spell targets
    to `spell_index_id` without breaking the current viewer record-key path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T08:25:06Z
  TYPE: FACT
  CLAIM: The selector-aware spell precision tranche is now landed in source.
    The validator now recognizes selector-aware spell rules with:
    - `spell_id`
    - `spell_index_id`
    - `spellframe`
    - `spell_name`
    - `binding_name`
    and validates them against published `SpellRecord`s. The compiler now
    preserves viewer-facing `visible_spell_keys` while also compiling
    `visible_spell_index_ids` so later runtime consumers can target stable
    spell lineages directly.
  EVIDENCE:
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:314-345
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:512-746
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:131-181
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:260-338
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:35-40
  IMPACT: The earlier precision design is now materially true in the ACL
    runtime instead of just in repo planning docs.
  NEXT: review the landed selector-resolution tranche and decide whether the
    next slice should widen selector semantics further or start consuming the
    spell-index outputs in higher runtime surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T08:25:06Z
  TYPE: MEASURE
  CLAIM: The widened ACL/Nexus/viewer validation ring is green after the
    selector-resolution patch. The updated validator, compiled surface,
    compiler, viewer clone/helpers, and the new selector tests all pass
    together on the targeted broader slice.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_profile_contract_matrix.py tests/unit/melder/aether/test_frame_acl_command_configuration.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py` -> 318 passed
  IMPACT: This tranche is ready for review instead of more migration cleanup.
  NEXT: present the landed selector-aware spell precision model and test result
    to the user for the next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: The selector-aware spell precision tranche is complete and can move to
    the completed lane. The later stable-lineage runtime lookup and command ACL
    access-enforcement tasks already consume its compiled `spell_index_id`
    outputs as settled precision behavior.
  EVIDENCE:
  - tickets/tasks/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md:1-131
  - tickets/tasks/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md:1-146
  IMPACT: This selector-resolution task no longer belongs on the active board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first real selector-aware spell precision slice on top
of the landed family-profile ACL substrate.
