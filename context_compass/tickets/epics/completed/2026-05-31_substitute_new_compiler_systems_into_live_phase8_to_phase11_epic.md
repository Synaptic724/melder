# Epic: Substitute New Compiler Systems Into Live Phase 8 To Phase 11

## Metadata
- Epic ID: EPIC-2026-05-31-substitute-new-compiler-systems-into-live-phase8-to-phase11
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-05-31T22:30:11Z
- Updated: 2026-06-01T11:05:49Z
- Target Window: 2026-Q2
- Related Program/Initiative: Replace legacy compiler phases with new analyzer/processor/planner/creator flow

## Problem / Opportunity
The new compiler seams now exist:
- `SpellAnalyzer`
- `SpellArtifactProcessor`
- `SpellCodegenPlanner`
- `CodegenCreationSystem`

But the live compiler path still routes through the old phase chain:
- old phase 8 occurrence plan
- old phase 9 injection plan
- old phase 10 patch maps
- old phase 11 execution plan
- old phase 13 no-overrides compile

That leaves the real `run_all_phases(...)` path stale relative to the new
runtime seam, especially now that `CreationContextBuilder` expects
`artifact._spell_codegen_creation`.

The opportunity is to substitute the new systems into the live compiler path in
bounded steps instead of leaving the repo with two competing execution chains.

## MRP Alignment (Most Reasonable Product)
The MRP is not deleting all old phase files in one pass.

It is:
- switch the live compiler path over step by step
- keep each substitution bounded
- remove stale live-path dependencies only after their replacement is actually
  running

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to migrate the live spell compiler so
  phase 8 is analyzer, phase 9 is processor, phase 10 is planner, and phase 11
  is codegen creation.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation/`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-31_reorganize_phase8_to_phase11_compiler_ownership_epic.md`
  - `tickets/epics/2026-05-31_port_phase13_and_creation_context_into_codegen_creation_strategies_epic.md`
- EXIT_GATE:
  - one explicit step order exists for substituting the live compiler path
  - the first live substitution slice is landed
  - later substitutions are staged instead of attempted all at once
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one substitution reveals a
  hidden live dependency that must be migrated before the next step can proceed.

## Desired Live Mapping
- Live phase 8 -> `SpellAnalyzer`
- Live phase 9 -> `SpellArtifactProcessor`
- Live phase 10 -> `SpellCodegenPlanner`
- Live phase 11 -> `CodegenCreationSystem`

## Proposed Implementation Order
1. Substitute live phase 8 with `SpellAnalyzer`.
2. Substitute live phase 9 with `SpellArtifactProcessor`.
3. Substitute live phase 10 with `SpellCodegenPlanner`.
4. Substitute live phase 11 with `CodegenCreationSystem`.
5. Remove old live calls to legacy phase-12/13 strategy/executor compile
   surfaces once the new path is producing `artifact._spell_codegen_creation`.
6. Remove stale direct compiler-system methods that are no longer part of the
   live path.

## Milestones
- [ ] Milestone 1: live phase 8 uses analyzer
- [ ] Milestone 2: live phase 9 uses processor
- [ ] Milestone 3: live phase 10 uses planner
- [ ] Milestone 4: live phase 11 uses codegen creation
- [ ] Milestone 5: old live phase-12/13 path is no longer part of `run_all_phases(...)`

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
- DATETIME: 2026-06-01T09:52:23Z
  TYPE: FACT
  CLAIM: The old blueprint-module dependency chain is now severed. The last
    live production coupling was the `ExecutionPlanCallMode` /
    `ExecutionPlanTargetKind` enum carrier import inside the codegen-creation
    compiler helpers; that was moved onto the planner-owned generalized
    lane-plan carriers. After that, the only remaining direct imports of
    `execution_plan.py`, `injection_plan.py`, `occurrence_plan.py`, and
    `patch_maps.py` were in stale old tests, so those tests and the 4 blueprint
    files were removed. The repo still has textual legacy mentions
    (`ExecutionPlan-like`, `OverridePatchMap-like`, `phase13` helper names),
    but the direct module imports are gone.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_no_overrides_codegen_creation_compiler.py:1-20
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/generalized_overrides_codegen_creation_compiler.py:1-20
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:60-72
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:1-15
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py (deleted)
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py (deleted)
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py (deleted)
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py (deleted)
  IMPACT: The substituted compiler/codegen-creation path no longer needs the
    old blueprint module family to exist. Any remaining cleanup here is naming
    and commentary polish, not live import removal.
  NEXT: if desired, do a bounded naming cleanup pass to remove `phase13` and
    `ExecutionPlan-like` wording from current helper names and comments now
    that the old blueprint files are gone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-01T00:34:58Z
  TYPE: FACT
  CLAIM: The documentation sync tranche is landed. The live phase-8-to-phase-11
    wrapper classes now have richer contract docstrings that explicitly name
    the new artifact outputs, `CreationContextBuilder` and `CreationContext`
    now document the compiler-owned `SpellCodegenCreation` handoff versus the
    remaining runtime-only specialization responsibilities, and the
    architecture/components docs now describe the live 8-11 mapping as
    analyzer -> processor -> planner -> codegen creation instead of the old
    occurrence/injection/patch/execution artifact chain.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:17-95
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:15-78
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:15-81
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-90
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:11-78
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:111-334
  - codex/context_compass/system_docs/src_architecture.md:823-853
  - codex/context_compass/system_docs/src_components.md:1142-1231
  IMPACT: The source docstrings and the durable architecture/component docs now
    tell the same story about the substituted compiler and the thinner
    creation-context boundary, which reduces future drift while we optimize
    the new system.
  NEXT: continue performance and drift work from the new analyzer/processor/
    planner/codegen-creation surfaces instead of the removed legacy artifact
    chain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T23:52:22Z
  TYPE: FACT
  CLAIM: The next drift batch split into one production bug plus stale unit
    expectations. The production bug was that conduit-wide and target-local
    plan-phase scheduling still queued existing-creation spells into phases
    8-11, even though the analyzer intentionally returns no graph truth for
    those spells; that is now fixed by plan-phase eligibility filtering in
    `SpellbookCreationSystem`. The remaining failures in the pasted cluster
    were stale unit assumptions: phase-5 test stubs needed the real
    `_cleanup_creation_context` spell hook, and several Spellbook resolution
    tests still expected the deleted `executor_compile` phase/result.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1117-1199
  - src/melder/aether/spellbook/spellbook_creation_system.py:1650-1685
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5.py:232-257
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_5_local.py:143-168
  - tests/unit/melder/spellbook/test_spellbook.py:2556-2586
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:257-371
  IMPACT: Existing-object conjure and post-conjure bind flows should no longer
    die in live Phase 9, and the remaining unit coverage in this area is now
    aligned to the removed `executor_compile` seam and the current phase-5
    invalidation contract.
  NEXT: continue through the next remaining pasted failures, with the same
    rule: fix real `src/` regressions first, then remove stale test
    expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T23:39:32Z
  TYPE: FACT
  CLAIM: The next failure cluster was a real runtime regression in the live
    substituted path, not stale tests. `SpellbookCreationSystem` was still
    scheduling phases 8-11 for existing-creation spells during both
    conduit-wide conjure and target-local revalidation. The new analyzer
    intentionally returns early for existing-creation spells, so Phase 9 then
    crashed on `SpellOccurrenceOrderProcessorStrategy requires graph_shape
    first.` The fix is at the scheduler boundary: plan-phase factories now
    filter to plan-phase-eligible spells only, and the target-local phase-8-to
    phase-11 runner now returns early for ineligible targets instead of
    queueing analyzer/processor/planner/creation work that can never succeed.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-126
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:48-57
  - src/melder/aether/spellbook/spellbook_creation_system.py:1117-1199
  - src/melder/aether/spellbook/spellbook_creation_system.py:1650-1685
  IMPACT: Existing-object conjure and post-conjure existing-object bind flows
    should no longer die in live Phase 9 simply because the new compiler stack
    correctly has no occurrence graph for those spells.
  NEXT: validate this boundary in the real 3.14t test environment once pytest
    and runtime deps are present there, then continue clearing any remaining
    stale integration expectations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T23:39:32Z
  TYPE: FACT
  CLAIM: The first direct drift-repair tranche is landed. The stale wrapper
    unit tests for phases 8-11 were rewritten against the current analyzer /
    processor / planner / codegen-creation facades, the current
    `SpellCompilerArtifact` unit file now asserts the live analyzer/model/plan/
    creation slots instead of deleted legacy phase8-13 fields, the component /
    integration compiler tests now assert `_occurrence_graph_analysis`,
    `_spell_codegen_model`, `_spell_codegen_plan`, and
    `_spell_codegen_creation`, and the fully obsolete phase12/13 plus old
    blueprint Phase13 tests were removed. In production code, the dormant
    `SharedCompilerExecutions` phase8_11 IR export/reset helpers were rewritten
    to stop dereferencing deleted legacy artifact fields.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py:1-58
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py:1-58
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py:1-58
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py:1-61
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:1-186
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py:587-770
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1320-1644
  - tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:360-520
  - tests/integration/melder/spellbook/test_spell_compiler_system_integration.py:150-343
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1380-1590
  IMPACT: The high-noise failure cluster from deleted legacy artifact-field
    assertions is now aligned to the current compiler contract, and the one
    dormant source-side helper seam no longer carries an obvious latent crash
    if it is touched again.
  NEXT: run the touched ring in the repo’s real test environment once pytest
    is available there, then classify any remaining failures as real runtime
    bugs versus deeper stale coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T23:21:53Z
  TYPE: FACT
  CLAIM: The current post-cutover failure cluster is mostly stale test drift,
    not evidence that the live compiler/runtime path is still reading the old
    phase-8-to-phase-11 artifact family. The failing component/integration
    tests and cprofile harness are asserting deleted legacy fields such as
    `_occurrence_plan_phase8`, `_injection_plan_phase9`,
    `_override_patch_map_phase10`, `_execution_plan_phase11*`, and
    `_execution_plan_step_count_phase11`, while the live substituted path now
    publishes `_occurrence_graph_analysis`, `_spell_codegen_model`,
    `_spell_codegen_plan`, and `_spell_codegen_creation`. One real source-side
    hazard remains: `SharedCompilerExecutions.capture_phase8_11_codegen_ir(...)`
    and `reset_phase8_11_codegen_ir(...)` still dereference removed legacy
    artifact fields and would raise if they were called again, but current
    `src/` callers no longer route there.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py:607-770
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1321-1641
  - tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:440-450
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:67-96
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-79
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-58
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-61
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-68
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:63-125
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1380-1679
  IMPACT: The immediate cleanup target is test/harness expectation repair plus
    retirement of the dead phase8_11 IR helper path. I do not currently see
    evidence from these traces that the live `run_all_phases(...)` path is
    still depending on the deleted legacy artifact family.
  NEXT: classify remaining failing tests into stale expectation groups and then
    remove or rewrite the dead `phase8_11` IR helper surface before wider
    cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:53:08Z
  TYPE: PLAN
  CLAIM: The next correction slice is on the phase files themselves.
    `compiler_phase_8.py` through `compiler_phase_11.py` are still the old
    implementations, which makes the substitution misleading even though the
    live path was already partially routed onto the new systems. This slice
    will rewrite those phase classes into the actual wrappers over analyzer,
    processor, planner, and codegen creation, then repoint `SpellCompiler` to
    own and delegate through those converted phase classes directly.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-482
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-209
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-216
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-822
  IMPACT: This makes the live phase substitution explicit and truthful in the
    actual phase files the user is inspecting, not just in the higher-level
    compiler facade.
  NEXT: rewrite phase 8-11 classes as wrappers and route `SpellCompiler`
    through them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:56:45Z
  TYPE: FACT
  CLAIM: The actual phase files are now substituted too. `compiler_phase_8.py`
    through `compiler_phase_11.py` are no longer the old implementations; they
    are the live wrappers over analyzer, processor, planner, and codegen
    creation. `SpellCompiler` was repointed back through those phase classes,
    so the substitution is explicit both in the live path and in the concrete
    phase files the user is inspecting.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-80
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:1-71
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:1-72
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-74
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:1-734
  IMPACT: The live substitution is now truthful at the phase-file level, not
    just in the higher-level compiler control path.
  NEXT: continue retiring the remaining old compiler-path artifact fields and
    dead helper code now that both the live path and the phase classes are on
    the new systems.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:36:50Z
  TYPE: FACT
  CLAIM: The first live cutover slice is landed. `SpellCompiler` now owns the
    new analyzer / processor / planner / codegen-creation facades directly for
    live phases 8-11, and `SpellCompilerSystem.run_all_phases(...)` now stops
    after the new phase-11 codegen creation step instead of continuing into the
    stale old phase-12/13 chain. The only remaining `CompilerPhase12` /
    `CompilerPhase13` references are the old class files themselves, not the
    live compiler path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:1-734
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:334-909
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-132
  IMPACT: The live compiler execution path now matches the intended mapping:
    phase 8 analyzer, phase 9 processor, phase 10 planner, phase 11 codegen
    creation. The next removal seam is the old compiler-phase surfaces/files
    and any remaining compatibility fields they still own.
  NEXT: remove or retire the remaining old phase-12/13 class files and the old
    compiler-path artifact fields they are no longer responsible for.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T22:30:11Z
  TYPE: PLAN
  CLAIM: The first bounded cut under this epic should switch the live
    `run_all_phases(...)` flow off the stale old `8 -> 13` chain and onto the
    new analyzer -> processor -> planner -> creation path. That cut should
    stop there and not try to delete the old phase classes/files in the same
    pass.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:989-1007
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-90
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-132
  IMPACT: This turns the new compiler seam into the actual live path instead of
    leaving it as a side-car system that the runtime builder expects but the
    compiler never produces.
  NEXT: patch `SpellCompiler` and `SpellCompilerSystem` to use the new live
    mapping and stop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic is the live cutover umbrella. The new compiler systems exist, but the
old live phase chain is still what `run_all_phases(...)` executes. The next
work is bounded substitution of the live path, one step at a time, starting by
making the new analyzer -> processor -> planner -> creation flow the real phase
8-11 chain.

