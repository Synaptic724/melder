# Task: Start unit tests for spell analyzer artifact processor and codegen planner

## Metadata
- Task ID: TASK-2026-05-31-start-unit-tests-for-spell-analyzer-artifact-processor-and-codegen-planner
- Story: STORY-2026-05-31-port-direct-object-tests-for-compiler-analysis-and-codegen-planning
- Status: done
- Owner: codex
- Agent Name: tester_0
- Priority: p1
- Created: 2026-05-31T21:51:49Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Land the first direct unit-test slice for the new compiler object stack:
- `SpellAnalyzer`
- `SpellArtifactProcessor`
- `SpellCodegenPlanner`
- their core builder/discovery helper objects

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to start with the object surfaces and
  not drift into phase-centric test migration.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation/`
  - `tests/unit/melder/spellbook/spell_compiler/`
  - `tests/component/melder/spellbook/spell_compiler/`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-31_migrate_compiler_object_tests_from_blueprint_surfaces_epic.md`
  - `tickets/stories/2026-05-31_port_direct_object_tests_for_compiler_analysis_and_codegen_planning_story.md`
- EXIT_GATE:
  - new or updated direct unit tests exist for analyzer / processor / planner
  - at least one current stale assumption is removed from the direct object
    test surface
  - focused validation status is reported truthfully
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a needed test intent cannot
  be expressed without falling back to old phase naming.

## Scope Boundaries
- In scope:
  - direct unit tests for facades
  - builder/discovery helper tests
  - minimal supporting doubles/stubs
- Out of scope:
  - component migration
  - broad phase-file rewrites
  - production-code redesign unless a test reveals a real contract bug

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the first bounded object-centric migration slice.

## Steps / Checklist
- [x] Reconfirm the direct facade and helper contracts from source.
- [x] Add or update direct analyzer unit tests.
- [x] Add or update direct artifact processor unit tests.
- [x] Add or update direct codegen planner unit tests.
- [x] Run focused pytest on the touched unit files or report `Not run.`
- [x] Port first blueprint-derived strategy/data intent into direct object tests.
- [x] Port next blueprint-derived strategy/data intent into direct strategy and lane-plan helper tests.
- [x] Add the first intentional component seam for the new object pipeline.
- [x] Port another helper-heavy tranche from old occurrence/patch/execution semantics into direct replacement-object tests.
- [x] Start direct `codegen_creation` object tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further expansion.

## Deliverables
- direct unit tests for the new object stack
- one explicit note on what remains for strategy/data or component migration

## Files / Paths Impacted
- `tests/unit/melder/spellbook/spell_compiler/`
- `codex/context_compass/tickets/tasks/2026-05-31_start_unit_tests_for_spell_analyzer_artifact_processor_and_codegen_planner_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Ran:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_compiler\test_spell_occurrence_analyzer_strategy.py tests\unit\melder\spellbook\spell_compiler\test_spell_analyzer_core.py tests\unit\melder\spellbook\spell_compiler\test_spell_artifact_processor_core.py tests\unit\melder\spellbook\spell_compiler\test_spell_codegen_planner_core.py tests\unit\melder\spellbook\spell_compiler\test_spell_artifact_processor_data_migrations.py tests\unit\melder\spellbook\spell_compiler\test_spell_strategy_migrations.py tests\unit\melder\spellbook\spell_compiler\test_spell_generalized_codegen_lane_plan_core.py tests\unit\melder\spellbook\spell_compiler\test_codegen_creation_core.py tests\component\melder\spellbook\spell_compiler\test_spell_codegen_pipeline_component.py`
- Result:
  - `57 passed, 1 warning`
- Warning:
  - `PytestCacheWarning` on existing `.pytest_cache\v\cache` path creation.
- Ran:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_compiler\test_spell_occurrence_analyzer_strategy.py tests\unit\melder\spellbook\spell_compiler\test_spell_artifact_processor_data_migrations.py tests\unit\melder\spellbook\spell_compiler\test_spell_strategy_migrations.py tests\unit\melder\spellbook\spell_compiler\test_spell_generalized_codegen_lane_plan_core.py tests\unit\melder\spellbook\spell_compiler\test_spell_compiler_artifact.py tests\unit\melder\spellbook\spell_compiler\test_spell_compiler_system.py tests\unit\melder\spellbook\spell_compiler\test_codegen_creation_core.py tests\unit\melder\spellbook\spell_compiler\test_codegen_creation_compilers_core.py tests\unit\melder\spellbook\spell_compiler\test_creation_context_core.py`
- Result:
  - `137 passed, 1 warning`
- Warning:
  - `PytestCacheWarning` on existing `.pytest_cache\v\cache` path creation.

## Risks / Rollback Notes
- Risk: a direct test accidentally bakes in temporary phase naming.
- Rollback: keep assertions at the object contract level and delete any
  phase-proxy assertions added by mistake.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No phase-name assertions as the primary proof surface.
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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: direct object contracts, replaced phase assumptions, and the next
- migration seam.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-31T21:51:49Z
  TYPE: FACT
  CLAIM: The direct object contracts are small and testable right now. The
    current object files for `SpellAnalyzer`, `SpellArtifactProcessor`, and
    `SpellCodegenPlanner` are each under the read limit and expose narrow
    facade methods plus builder/discovery seams, while current direct test
    coverage is uneven: analyzer has one direct unit file, processor/planner
    are still mostly covered indirectly through `test_compiler_phase_12.py`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-122
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-156
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-117
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-103
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:1-256
  IMPACT: We can land immediate value by adding direct unit coverage for the
    new objects before touching the larger indirect phase surface.
  NEXT: add or update direct unit tests for analyzer / processor / planner and
    their helper registries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:01:56Z
  TYPE: MEASURE
  CLAIM: The first direct unit slice is landed and green. New direct tests now
    cover the analyzer facade, analyzer builder failure behavior, artifact
    processor facade/model/builder behavior, and planner discovery/plan shell/
    facade/builder behavior without leaning on old phase names as the primary
    contract. The focused pytest ring passed `14 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_analyzer_core.py:1-106
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py:1-243
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-196
  IMPACT: We now have a real direct proof surface for the new object stack, so
    the next slice can focus on blueprint-derived strategy/data migration and
    intentional component seams instead of proving the facades through
    Phase 12.
  NEXT: define the next bounded slice around strategy/data objects coming from
    occurrence, injection, patch-map, and execution-plan source intent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:09:00Z
  TYPE: MEASURE
  CLAIM: The direct object slice is now extended with the first actual
    blueprint-intent migration tests. The new tests no longer only prove the
    facades and builders; they now also prove the new processor-owned data
    containers and strategy behavior that replace old occurrence-plan,
    injection-plan, patch-map, and execution-plan assumptions. The full new
    object-centric test ring passed `28 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_analyzer_core.py:1-106
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_core.py:1-243
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-196
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py:1-247
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:1-404
  IMPACT: We now have a real migration pattern: move old blueprint-era intent
    into strategy/data object tests directly, instead of keeping that proof
    trapped in phase files.
  NEXT: move to the next bounded seam by porting more old blueprint-class
    assertions into direct tests for the remaining processor strategies and the
    generalized lane-plan data builder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:14:38Z
  TYPE: MEASURE
  CLAIM: The next blueprint-intent tranche is landed and green. The direct
    test surface now also covers:
    - `SpellOccurrenceInstanceProcessorStrategy`
    - `SpellOccurrenceContractProcessorStrategy`
    - `SpellGeneralizedCodegenLanePlan`
    - `SpellGeneralizedCodegenPlanBuilder` helper semantics
    This means the migration is no longer limited to facade smoke tests or
    coarse data-container summaries; it now ports more of the old
    occurrence/injection/patch/execution behavior onto the new replacement
    object layer itself. The full object-centric ring passed
    `34 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py:1-247
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:1-515
  - tests/unit/melder/spellbook/spell_compiler/test_spell_generalized_codegen_lane_plan_core.py:1-190
  IMPACT: We now have real migrated proof for more of the blueprint-derived
    seams and can move next into the remaining processor strategies and then
    intentional component coverage without first revisiting phase files.
  NEXT: continue with the remaining processor strategy surfaces and start
    defining the first real component seam under
    `tests/component/melder/spellbook/spell_compiler/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:23:28Z
  TYPE: MEASURE
  CLAIM: The tranche is now broader again. The direct analyzer strategy file
    now carries migrated helper/cache semantics from the old occurrence-plan
    surface, and the first intentional component seam now exists for the real
    `SpellArtifactProcessor -> SpellCodegenPlanner` pipeline over a minimal
    rooted artifact slice. The full object-centric ring passed
    `40 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-263
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:1-145
  IMPACT: The migration is no longer only unit-level; it now includes the
    first object-pipeline component proof and more of the old occurrence-plan
    helper intent is anchored on the new analyzer strategy instead of phase 8.
  NEXT: continue porting the remaining old blueprint-class intent onto the new
    replacement strategies and decide which additional component seams deserve
    direct coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:28:57Z
  TYPE: MEASURE
  CLAIM: The migration tranche is broader again. The direct test surface now
    also covers:
    - analyzer helper-level fast-key/input-signature/cache semantics
    - override/mutation target-key helper rules
    - runtime-processor fallback/error behavior
    - generalized lane-plan step accessors
    - generalized lane-plan helper behavior for canonical-occurrence recovery
      and transient-plan rejection
    The combined object-centric ring passed `47 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-263
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:1-608
  - tests/unit/melder/spellbook/spell_compiler/test_spell_generalized_codegen_lane_plan_core.py:1-309
  IMPACT: More of the old helper-level occurrence/patch/execution semantics are
    now anchored on the replacement objects instead of phase wrappers.
  NEXT: continue porting the remaining old blueprint-class intent and expand
    component seams where the new object boundaries are real.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:33:58Z
  TYPE: MEASURE
  CLAIM: The task now includes the first direct `codegen_creation` object
    tranche. New tests cover `CodegenCreationDiscoverySystem`,
    `CodegenCreationSystem`, `SpellCodegenCreation`,
    `SpellCodegenStrategyBuilder`, `SpellOverrideTargetingCodegenCreation`,
    and the first generalized creation strategies. The full object-centric ring
    now passes `57 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-346
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:1-145
  IMPACT: The migration no longer stops at planner outputs; it now proves the
    first part of the post-planner creation layer too.
  NEXT: keep porting the remaining old creation/compiler intent onto the
  `codegen_creation` strategies and compilers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T23:33:58Z
  TYPE: FACT
  CLAIM: The remaining old blueprint test failure cluster is now explicit. The
    attachment-driven rerun shows the old suites still assert removed
    blueprint/phase outputs like `_occurrence_plan_phase8` and legacy phase13
    helper/module seams, while the live runtime now routes through
    `SpellCompilerArtifact` analysis/model/plan/creation fields and the
    spell-owned `CreationContext` stack. The next migration cut therefore has
    to port the old `execution_plan`, phase13 no-overrides, phase13
    overrides, injection-plan kwargs, patch-map, and occurrence-plan
    assertions onto the current phase-11/codegen-creation/creation-context
    objects before the old files can be deleted.
  EVIDENCE:
  - <local-path>/.codex/attachments/938bb50e-7dc1-44e2-ba6e-8327af33cdee/pasted-text.txt:1-2782
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_execution_plan_core.py:1-494
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase13_no_overrides_executor.py:1-1210
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase13_overrides_executor.py:1-1372
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-79
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-58
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-61
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-68
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:1-368
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1267
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-178
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:1-255
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:1-1083
  IMPACT: The remaining migration should target real live ownership seams
    instead of wrapper phases, and the old blueprint files should only be
    deleted after equivalent proof exists on those new runtime surfaces.
  NEXT: port the old phase11/phase13/creation-context assertions into new
    `spell_compiler` test files, rerun the focused ring, then delete the
    superseded old blueprint suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T23:44:18Z
  TYPE: MEASURE
  CLAIM: The live-target migration pass is now landed and green. The new suite
    adds direct override-helper/compiler proofs on
    `generalized_overrides_codegen_creation_compiler.py` plus direct
    spell-owned `CreationContext` / builder / factory tests, and the obsolete
    old blueprint suites for occurrence plan, injection plan, patch maps, and
    execution plan have been removed. The replacement ring passed
    `137 passed, 1 warning`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:1-1317
  - tests/unit/melder/spellbook/spell_compiler/test_creation_context_core.py:1-358
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-353
  - tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py:1-247
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:1-729
  - tests/unit/melder/spellbook/spell_compiler/test_spell_generalized_codegen_lane_plan_core.py:1-338
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:1-211
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_system.py:1-331
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-924
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_execution_plan_core.py:1-494
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_injection_plan_core.py:1-156
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_injection_plan_kwargs.py:1-258
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py:1-794
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan_core.py:1-213
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_patch_maps.py:1-156
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_patch_maps_core.py:1-213
  IMPACT: The remaining live proof surface now sits on `spell_compiler` and
    `creation_context` objects instead of the removed blueprint-plan tests,
    and `test_root_resolution_blueprint.py` remains the only kept old
    blueprint suite because the rooted blueprint object is still live.
  NEXT: get user review on this migration cut, then either close the old
    blueprint lane or continue with any remaining legacy phase/component test
    surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This is the first direct object unit-test slice under the compiler test-migration
epic. It is intentionally narrow: facades and helper registries first.

